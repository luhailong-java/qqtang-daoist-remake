"""Decode selected native UI references and read their inert literal source bindings."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = ROOT / '.artifacts/reference-inputs'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
PATHS = ('object/ui/selroom/btn_commandprompt.img', 'object/ui/selroom/btn_flexdown.img', 'object/ui/selroom/btn_flexup.img', 'object/ui/selroom/btn_left.img', 'object/ui/selroom/btn_message.img', 'object/ui/selroom/btn_right.img', 'object/ui/selroom/dlg_chatmax.img', 'object/ui/selroom/dlg_chatmin.img', 'object/ui/selroom/dlg_chatnormal.img', 'object/ui/selroom/icon_vip.img', 'object/ui/selroom/img_popo.img', 'object/ui/selroom/mask_speaker.img', 'object/ui/selroom/num.img', 'object/ui/selroom/tip_guidemidright.img', 'object/ui/selroom/tip_guidemidunder.img', 'object/ui/selroom/tip_guidemidupper.img', 'object/ui/selroom/tip_entershop.img')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


reader = module('native_postlogin_dimg', 'scripts/inspect-reference-dimg.py')
constants = module('native_postlogin_constants', 'scripts/read-legacy-ui-constants.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def literal(value):
    if value['type'] in ('tuple', 'list'):
        return [literal(item) for item in value['values']]
    return value.get('text', value.get('value'))


def main():
    archive_path = INPUTS / 'QQTang-Local-v1.3.4.zip'
    with archive_path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Pinned archive mismatch')
    index_path, package_path = INPUTS / 'object.idx', INPUTS / 'object.pkg'
    index_bytes, package_bytes = index_path.read_bytes(), package_path.read_bytes()
    inventory_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    if sha(index_bytes) != inventory['index']['sha256'] or sha(package_bytes) != inventory['package']['sha256']:
        raise ValueError('Pinned package/index differs')
    entries = reader.parse_index(index_bytes, len(package_bytes))['entries']
    by_path = {entry['path'].replace('\\', '/').lower(): entry for entry in entries}
    resources = {r['canonicalPath']: r for r in inventory['resources'] if r['storage'] == 'packed'}
    source_modules = []
    scopes = []
    with zipfile.ZipFile(archive_path) as archive:
        for name in ('uiMain', 'uiTemplate', 'uiSelRoom', 'uiRoom'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            node, count = constants.decode(raw)
            decoded = constants.collect(node)
            source_modules.append({'module': name, 'archiveMember': member, 'sha256': sha(raw),
                                   'byteLength': len(raw), 'parsedObjects': count, 'scopeCount': len(decoded),
                                   'bytecodeExecuted': False})
            scopes.extend((name, scope) for scope in decoded)
    binding_rows = []
    for name, scope in scopes:
        assignments = {item['name']: literal(item['literalValue']) for item in scope['literalAssignments']}
        values = {item.get('text', '').replace('\\', '/').lower() for item in scope['constants']}
        paths = [path for path in PATHS if path in values]
        for path in paths:
            binding_rows.append({'module': name, 'scope': scope['scope'], 'firstSourceLine': scope['firstLine'],
                                 'bytecodeSha256': scope['bytecodeSha256'], 'nativePath': path,
                                 'literalAssignments': assignments, 'activeControlFlowConfirmed': False})
    output = []
    for path in PATHS:
        entry = by_path[path]
        raw, compressed_sha = reader.unpack_resource(package_bytes, entry)
        if sha(raw) != resources[path]['sourceSha256'] or compressed_sha != resources[path]['compressedSha256']:
            raise ValueError('Pinned resource mismatch')
        metadata, _ = reader.inspect_dimg(raw, reference_only_version65537_suffix=True, metadata_only=True)
        frames = []
        for frame in metadata['frames']:
            if frame['empty']:
                frames.append({'sourceFrameIndex': frame['index'], 'empty': True, 'frameOffsetRaw': frame['frameOffset']})
                continue
            start = frame['pixelDataOffset']
            pixels = reader.decode_frame_pixels(raw[start:start + frame['pixelByteLength']], frame['pixelMode'], frame['width'], frame['height'])
            image = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
            target = HERE / 'frames' / path.removeprefix('object/ui/').removesuffix('.img') / f'frame-{frame["index"]:03}.png'
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            if Image.open(target).convert('RGBA').tobytes() != pixels:
                raise ValueError('Saved source pixels differ')
            frames.append({**record(target), 'sourceFrameIndex': frame['index'], 'empty': False,
                           'nativeSize': list(image.size), 'frameOffsetRaw': frame['frameOffset'], 'pixelMode': frame['pixelMode'],
                           'decodedRgbaSha256': sha(pixels), 'alphaExtrema': list(image.getchannel('A').getextrema())})
        output.append({'nativePath': path, 'sourceSha256': sha(raw), 'compressedSha256': compressed_sha, 'packageEntry': entry,
                       'metadata': metadata, 'frames': frames, 'sourceBindings': [b for b in binding_rows if b['nativePath'] == path]})
    row_heights = [120*((len(r['frames'])+4)//5) for r in output]
    board = Image.new('RGB', (1200, sum(row_heights)), '#eae3d1')
    draw = ImageDraw.Draw(board)
    top = 0
    for resource,height in zip(output,row_heights,strict=True):
        draw.text((7,top+4),resource['nativePath'],fill='#204638')
        for j,frame in enumerate(resource['frames']):
            image = Image.open(ROOT/frame['file']).convert('RGBA')
            scale = min(2,205/image.width,88/image.height)
            image = image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))),Image.Resampling.NEAREST)
            x,y = 7+(j%5)*238,top+(j//5)*120
            draw.text((x,y+19),str(frame['sourceFrameIndex']),fill='#204638')
            board.paste(image,(x+18,y+27),image)
        top += height
    panel_path = HERE/'source-all-states.png'
    board.save(panel_path)
    source = {'archiveSha256': ARCHIVE_SHA, 'archiveFile': archive_path.relative_to(ROOT).as_posix(),
              'package': record(package_path), 'index': record(index_path), 'sourceModules': source_modules,
              'inventory': record(inventory_path)}
    manifest = {'schemaVersion': 1, 'scope': 'Read-only source image and literal UI reference evidence', 'source': source,
                'decodeScript': record(Path(__file__).resolve()),
                'resources': output, 'resourceCount': len(output), 'decodedNonemptyFrameCount': sum(len(r['frames']) for r in output),
                'previews': [record(panel_path)], 'sourcePixelsOnly': True,
                'sourceClientMutated': False, 'nativeRuntimeVerified': False,
                'interpretation': 'Static literal scope and decoded source pixels. Runtime active flow and button-state semantic ordering require further evidence.'}
    save(HERE / 'manifest.json', manifest)
    print(json.dumps({'resources': len(output), 'decodedFrames': manifest['decodedNonemptyFrameCount'],
                      'bindings': len(binding_rows), 'manifest': record(HERE / 'manifest.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
