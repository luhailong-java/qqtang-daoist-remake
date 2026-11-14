"""Capture this exact source group as inert image bytes and static PYC literals."""
from pathlib import Path
from importlib import util
import argparse
import hashlib
import json
import zipfile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    out = util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


CODEC = module('forge_capture_codec', 'scripts/native-ui-format.py')
STATIC = module('forge_capture_static', 'scripts/read-legacy-ui-constants.py')
IO = module('forge_capture_io', 'assets/native-client-ui/common-reference/export-common.py')


def ref(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def alpha(image):
    a = image.getchannel('A')
    box = a.point(lambda v: 255 if v >= 8 else 0).getbbox()
    return {'sha256': hashlib.sha256(a.tobytes()).hexdigest(), 'extrema': list(a.getextrema()),
            'alpha8BBox': list(box) if box else None}


def nodes(node, parent=''):
    scope = parent + '.' + STATIC.text_value(node['name'])[0] if parent else STATIC.text_value(node['name'])[0]
    yield scope, node
    for child in node['consts']:
        if isinstance(child, dict) and child.get('inertCodeNode'):
            yield from nodes(child, scope)


def instructions(node):
    data, offset, result = node['bytecode'], 0, []
    names = {89: 'BUILD_CLASS', 90: 'STORE_NAME', 100: 'LOAD_CONST', 101: 'LOAD_NAME',
             102: 'BUILD_TUPLE', 105: 'LOAD_ATTR', 116: 'LOAD_GLOBAL', 131: 'CALL_FUNCTION', 132: 'MAKE_FUNCTION'}
    while offset < len(data):
        start, opcode = offset, data[offset]
        offset += 1
        argument, value = None, None
        if opcode >= 90:
            argument = int.from_bytes(data[offset:offset + 2], 'little')
            offset += 2
        if opcode in (90, 101, 105, 116):
            value = STATIC.text_value(node['names'][argument])[0]
        elif opcode == 100:
            value = STATIC.constant(node['consts'][argument])
        result.append({'byteOffset': start, 'opcode': opcode, 'name': names.get(opcode, str(opcode)),
                       'argument': argument, 'value': value})
    return result


def constant_rects(rows):
    # Recognize only adjacent literal integer arithmetic/tuple construction.
    # No variables, calls, jumps or downloaded code objects are evaluated.
    stack, stores, window = [], [], []
    for row in rows:
        op = row['opcode']
        window.append(row)
        if op == 100 and row['value'].get('type') == 'int':
            stack.append(row['value']['value'])
        elif op in (20, 23, 24) and len(stack) >= 2 and all(type(v) is int for v in stack[-2:]):
            right, left = stack.pop(), stack.pop()
            stack.append(left * right if op == 20 else left + right if op == 23 else left - right)
        elif op in (102, 103) and len(stack) >= row['argument']:
            count = row['argument']
            value = tuple(stack[-count:]) if count else ()
            if count:
                del stack[-count:]
            stack.append(value)
        elif op == 90:
            if row['value'] == 'rect' and len(stack) == 1 and isinstance(stack[0], tuple) and len(stack[0]) == 4 and all(type(v) is int for v in stack[0]):
                stores.append({'attribute': 'rect', 'value': list(stack[0]), 'instructionWindow': window})
            stack, window = [], []
        else:
            stack, window = [], []
    return stores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    census_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    census = json.loads(census_path.read_bytes())
    selected = [r for r in census['resources'] if r['path'].lower().startswith(('object/ui/forge/',))]
    if len(selected) != 21:
        raise ValueError('Forge source group changed')
    package_path = ROOT / '.artifacts/reference-inputs/object.pkg'
    package = package_path.read_bytes()
    resources = []
    for record in selected:
        raw, compressed_sha = CODEC.reader.unpack_resource(package, record['indexEntry'])
        if hashlib.sha256(raw).hexdigest() != record['sourceSha256'] or compressed_sha != record['compressedSha256']:
            raise ValueError('Packed forge source changed')
        metadata, _ = CODEC.reader.inspect_dimg(raw, metadata_only=True)
        frames = []
        for frame in metadata['frames']:
            if frame['empty']:
                frames.append({'sourceFrame': frame, 'empty': True})
                continue
            start = frame['pixelDataOffset']
            rgba = CODEC.reader.decode_frame_pixels(raw[start:start + frame['pixelByteLength']],
                      frame['pixelMode'], frame['width'], frame['height'])
            image = Image.frombytes('RGBA', (frame['width'], frame['height']), rgba)
            slug = record['path'].removeprefix('object/ui/').removesuffix('.img').replace('/', '__')
            path = HERE / 'source' / f'{slug}-{frame["index"]:02}.png'
            IO.png(path, image, check)
            frames.append({**ref(path), 'sourceFrame': frame, 'decodedRgbaSha256': hashlib.sha256(rgba).hexdigest(),
                           'decodedAlpha': alpha(image), 'empty': False})
        bindings = [b for b in census['bindings'] if b.get('canonicalPath') == record['canonicalPath']]
        resources.append({'nativePath': record['path'], 'sourceSha256': record['sourceSha256'],
                          'sourceCompressedSha256': compressed_sha, 'packageEntry': record['indexEntry'],
                          'sourcePacked': True, 'sourceLoose': False, 'metadata': metadata,
                          'exactBindings': bindings, 'frames': frames})
    pages = []
    font = ImageFont.load_default(size=15)
    for page in range(3):
        subset = resources[page * 9:(page + 1) * 9]
        row_heights = [max(105, min(250, max(f['sourceFrame']['height'] for f in r['frames']) + 44)) for r in subset]
        board = Image.new('RGB', (1500, sum(row_heights)), '#eae3d0')
        draw = ImageDraw.Draw(board)
        y = 0
        for resource, height in zip(subset, row_heights):
            draw.line((0, y, 1499, y), fill='#41695b')
            draw.text((8, y + 5), resource['nativePath'], font=font, fill='#214b3c')
            for f in resource['frames']:
                if f['empty']:
                    continue
                frame = f['sourceFrame']
                with Image.open(ROOT / f['file']) as image:
                    scale = min(2, 350 / image.width, (height - 38) / image.height)
                    picture = IO.scaled(image, tuple(max(1, round(v * scale)) for v in image.size))
                x = 8 + frame['index'] * 372
                draw.text((x, y + 24), f"raw{frame['index']} off{tuple(frame['frameOffset'])}", font=font, fill='#214b3c')
                board.paste(picture, (x, y + 43), picture)
            y += height
        path = HERE / f'source-all-states-{page + 1}.png'
        IO.png(path, board, check)
        pages.append(ref(path))
    confirm = next(r for r in resources if r['nativePath'] == 'object/ui/forge/dlg_forgeconfirm.img')
    with Image.open(ROOT / confirm['frames'][0]['file']) as original:
        dark = Image.new('RGBA', original.size, '#193f35')
        dark.alpha_composite(original)
        alpha_picture = original.getchannel('A')
    dark_path, alpha_path = HERE / 'source-confirm-dark-diagnostic.png', HERE / 'source-confirm-alpha-diagnostic.png'
    IO.png(dark_path, dark.convert('RGB'), check)
    IO.png(alpha_path, alpha_picture, check)
    evidence = []
    with zipfile.ZipFile(ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as archive:
        for name in ('uiConst', 'uiTemplate', 'uiMain', 'uiShop', 'uiSelRoom'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            node, count = STATIC.decode(raw)
            scopes = []
            by_scope = dict(nodes(node))
            for scope, value in by_scope.items():
                # Capture adjacent literals as inert data; no bytecode is run.
                stores = STATIC.literal_assignments(value)
                if scope == '?' or (name == 'uiTemplate' and scope.split('.')[-1] in ('TEdit', 'TLabel', 'TButton', 'TTree', 'TList')) or any(
                        part in scope.lower() for part in ('refinedlg', 'pawnshop')):
                    rows = instructions(value)
                    symbolic = [{'attribute': row['value'], 'valueGlobalName': rows[i - 1]['value'],
                                 'loadByteOffset': rows[i - 1]['byteOffset'], 'storeByteOffset': row['byteOffset']}
                                for i, row in enumerate(rows) if i and row['opcode'] == 90 and rows[i - 1]['opcode'] in (101, 116)]
                    parent_scope, _, class_name = scope.rpartition('.')
                    construction = []
                    if parent_scope in by_scope:
                        parent_rows = instructions(by_scope[parent_scope])
                        for i, row in enumerate(parent_rows):
                            if row['opcode'] == 90 and row['value'] == class_name and i and parent_rows[i - 1]['opcode'] == 89:
                                construction.append(parent_rows[max(0, i - 8):i + 1])
                    scopes.append({'scope': scope, 'firstLine': value['firstLine'],
                                   'bytecodeSha256': hashlib.sha256(value['bytecode']).hexdigest(),
                                   'names': [STATIC.text_value(v)[0] for v in value['names']],
                                   'literalAssignments': stores, 'adjacentSymbolicStores': symbolic,
                                   'classConstructionInParent': construction,
                                   'constantArithmeticRectStores': constant_rects(rows)})
            evidence.append({'module': name, 'sourceMember': member, 'sourceSha256': hashlib.sha256(raw).hexdigest(),
                             'completeInertParse': True, 'parsedObjects': count, 'scopes': scopes})
    IO.write_json(HERE / 'text-color-source-evidence.json', {'schemaVersion': 1,
                  'operation': 'Complete inert PYC parse and adjacent literal stores only; no runtime/import/CodeType',
                  'modules': evidence, 'nativeRuntimeVerified': False}, check)
    IO.write_json(HERE / 'manifest.json', {'schemaVersion': 1, 'scope': 'All21 packed object/ui/forge resources',
                  'sourceCensus': ref(census_path), 'sourcePackage': ref(package_path),
                  'sourceIndex': ref(ROOT / '.artifacts/reference-inputs/object.idx'),
                  'resources': resources, 'sourceFramePositions': sum(len(r['frames']) for r in resources),
                  'sourceBoards': pages, 'textColorSourceEvidence': ref(HERE / 'text-color-source-evidence.json'),
                  'sourceAlphaObservation': {'nativePath': confirm['nativePath'],
                      'observation': 'Original interior alpha visibly contains old sample confirmation glyphs, a button rectangle and close block; retain as reference, not as functional exterior mask',
                      'darkDiagnostic': ref(dark_path), 'alphaDiagnostic': ref(alpha_path)},
                  'providedDirectoryReadOrMutated': False, 'nativeProgramExecuted': False,
                  'visualAccepted': False, 'nativeRuntimeVerified': False}, check)
    print(json.dumps({'resources': len(resources), 'sourcePositions': sum(len(r['frames']) for r in resources),
                      'sourcePages': len(pages), 'readOnlyReplay': check}))


if __name__ == '__main__':
    main()
