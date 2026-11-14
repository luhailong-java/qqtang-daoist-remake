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
PATHS = ('object/ui/kintotem/000.img', 'object/ui/kintotem/001.img', 'object/ui/kintotem/002.img', 'object/ui/kintotem/003.img', 'object/ui/kintotem/004.img', 'object/ui/kintotem/005.img', 'object/ui/kintotem/006.img', 'object/ui/kintotem/007.img', 'object/ui/kintotem/008.img', 'object/ui/kintotem/009.img', 'object/ui/kintotem/010.img', 'object/ui/kintotem/011.img', 'object/ui/kintotem/012.img', 'object/ui/kintotem/013.img', 'object/ui/kintotem/014.img', 'object/ui/kintotem/015.img', 'object/ui/kintotem/016.img', 'object/ui/kintotem/017.img', 'object/ui/kintotem/018.img', 'object/ui/kintotem/019.img', 'object/ui/kintotem/020.img', 'object/ui/kintotem/021.img', 'object/ui/kintotem/022.img', 'object/ui/kintotem/023.img', 'object/ui/kintotem/024.img', 'object/ui/kintotem/025.img', 'object/ui/kintotem/026.img', 'object/ui/kintotem/027.img', 'object/ui/kintotem/028.img', 'object/ui/kintotem/029.img', 'object/ui/kintotem/030.img', 'object/ui/kintotem/031.img', 'object/ui/kintotem/032.img', 'object/ui/kintotem/033.img', 'object/ui/kintotem/034.img', 'object/ui/kintotem/035.img', 'object/ui/kintotem/036.img', 'object/ui/kintotem/037.img', 'object/ui/kintotem/038.img', 'object/ui/kintotem/039.img', 'object/ui/kintotem/040.img', 'object/ui/kintotem/041.img', 'object/ui/kintotem/042.img', 'object/ui/kintotem/043.img', 'object/ui/kintotem/044.img', 'object/ui/kintotem/045.img', 'object/ui/kintotem/046.img', 'object/ui/kintotem/047.img', 'object/ui/kintotem/048.img', 'object/ui/level/medal/001.img', 'object/ui/level/medal/002.img', 'object/ui/level/medal/003.img', 'object/ui/level/medal/004.img', 'object/ui/level/medal/005.img', 'object/ui/level/medal/006.img', 'object/ui/level/medal/007.img', 'object/ui/level/medal/008.img', 'object/ui/level/medal/009.img', 'object/ui/level/medal/010.img', 'object/ui/level/medal/011.img', 'object/ui/level/medal/012.img', 'object/ui/level/medal/013.img', 'object/ui/level/medal/014.img', 'object/ui/level/medal/015.img', 'object/ui/level/medal/016.img', 'object/ui/level/medal/017.img', 'object/ui/level/medal/018.img', 'object/ui/level/medal/019.img', 'object/ui/level/medal/020.img', 'object/ui/level/medal/021.img', 'object/ui/level/medal/022.img', 'object/ui/level/medal/023.img', 'object/ui/level/medal/024.img', 'object/ui/level/medal/025.img', 'object/ui/level/medal/026.img', 'object/ui/level/medal/027.img', 'object/ui/level/medal/028.img', 'object/ui/level/medal/029.img', 'object/ui/level/medal/030.img', 'object/ui/level/tie/a01.img', 'object/ui/level/tie/a02.img', 'object/ui/level/tie/a03.img', 'object/ui/level/tie/a04.img', 'object/ui/level/tie/a05.img', 'object/ui/level/tie/a06.img', 'object/ui/level/tie/b01.img', 'object/ui/level/tie/b02.img', 'object/ui/level/tie/b03.img', 'object/ui/level/tie/b04.img', 'object/ui/level/tie/b05.img', 'object/ui/level/tie/b06.img', 'object/ui/level/tie/c01.img', 'object/ui/level/tie/c02.img', 'object/ui/level/tie/c03.img', 'object/ui/level/tie/c04.img', 'object/ui/level/tie/c05.img', 'object/ui/level/tie/c06.img', 'object/ui/level/tie/d01.img', 'object/ui/level/tie/d02.img', 'object/ui/level/tie/d03.img', 'object/ui/level/tie/d04.img', 'object/ui/level/tie/d05.img', 'object/ui/level/tie/d06.img', 'object/ui/level/tie/e01.img', 'object/ui/level/tie/e02.img', 'object/ui/level/tie/e03.img', 'object/ui/level/tie/e04.img', 'object/ui/level/tie/e05.img', 'object/ui/level/tie/e06.img', 'object/ui/level/tie/f01.img', 'object/ui/level/tie/f02.img', 'object/ui/level/tie/f03.img', 'object/ui/level/tie/f04.img', 'object/ui/level/tie/f05.img', 'object/ui/level/tie/f06.img', 'object/ui/level/tie/t01.img', 'object/ui/level/tie/t02.img', 'object/ui/level/tie/t03.img', 'object/ui/level/tie/t04.img', 'object/ui/level/tie/t05.img', 'object/ui/level/tie/t06.img', 'object/ui/map/midicon/all.img', 'object/ui/map/midicon/bomb.img', 'object/ui/map/midicon/box.img', 'object/ui/map/midicon/bun.img', 'object/ui/map/midicon/desert.img', 'object/ui/map/midicon/field.img', 'object/ui/map/midicon/match.img', 'object/ui/map/midicon/mine.img', 'object/ui/map/midicon/normal.img', 'object/ui/map/midicon/pig.img', 'object/ui/map/midicon/rand.img', 'object/ui/map/midicon/sculpture.img', 'object/ui/map/midicon/snow.img', 'object/ui/map/midicon/tank.img', 'object/ui/map/midicon/town.img', 'object/ui/map/midicon/treasure.img', 'object/ui/map/midicon/water.img', 'object/ui/cursor/arror.img', 'object/ui/cursor/dianji.img')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


PATHS += ('object/ui/cursor/fight.gsa',)
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
        loose = {path:archive.read('QQTang-Local/runtime/client-patched/'+path) for path in PATHS if path not in by_path}
        for name in ('uiMain', 'uiTemplate', 'uiRoom', 'uiSelSect', 'uiSelRoom', 'levelCFG'):
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
        entry = by_path.get(path)
        raw, compressed_sha = reader.unpack_resource(package_bytes, entry) if entry else (loose[path],None)
        if entry and (sha(raw) != resources[path]['sourceSha256'] or compressed_sha != resources[path]['compressedSha256']):
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
    board = Image.new('RGB', (1200, 120 * len(output)), '#eae3d1')
    draw = ImageDraw.Draw(board)
    for i, resource in enumerate(output):
        y = i * 120
        draw.text((7, y+4), resource['nativePath'], fill='#204638')
        for j, frame in enumerate(resource['frames']):
            image = Image.open(ROOT / frame['file']).convert('RGBA')
            scale = min(2, 275 / image.width, 88 / image.height)
            image = image.resize((round(image.width*scale),round(image.height*scale)), Image.Resampling.NEAREST)
            x = 7 + j * 296
            draw.text((x,y+19), str(frame['sourceFrameIndex']), fill='#204638')
            board.paste(image,(x+18,y+27),image)
    panel_path = HERE / 'source-all-states.png'
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
