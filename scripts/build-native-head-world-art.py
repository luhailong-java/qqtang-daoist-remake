"""Encode five complete original head-world candidate sets into their ten native paths."""
from importlib import util
from pathlib import Path
import argparse
import json
import zipfile

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'assets/native-client-heads/world-v1'
IDS = (39, 114, 407, 2000, 408)
CATALOG = ROOT / 'references/qqtang-item-data/catalog.json'
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
spec = util.spec_from_file_location('native_world_io', ROOT / 'scripts/build-native-inventory-art.py')
io = util.module_from_spec(spec)
spec.loader.exec_module(io)
codec = io.codec


def checked(path, expected):
    record = io.ref(path)
    if record['sha256'] != expected:
        raise ValueError(f'Input changed: {path}')
    return record


def provenance(frame):
    proof = frame['provenanceRecord']
    if isinstance(proof, str):
        proof_path = ROOT / proof
        proof = io.ref(proof_path)
    else:
        checked(ROOT / proof['file'], proof['sha256'])
    mother = frame['derivedFrom']
    mother_path = ROOT / mother['file']
    checked(mother_path, mother['sha256'])
    generation_path = ROOT / mother['generationRecord']
    return {'paintedProvenance': proof, 'paintedMother': io.ref(mother_path),
            'generationRecord': io.ref(generation_path)}


def convert_state(archive, native_path, item, source_contract, check, decoded_cache):
    member = 'QQTang-Local/runtime/client-patched/' + native_path
    original = archive.read(member)
    if io.sha(original) != item['sourceSha256'] or io.sha(original) != source_contract['sourceSha256']:
        raise ValueError('Native source no longer matches the registered painted frame contract')
    metadata, _ = codec.reader.inspect_dimg(original, metadata_only=True)
    if metadata['trailingByteLength'] or not metadata['strictDeclaredStructureAccepted']:
        raise ValueError('World native framing requires explicit additional handling')
    if metadata['declaredCanvas'] != item['sourceDeclaredCanvas']:
        raise ValueError('Registered source canvas changed')
    frame_map = {f['sourceFrameIndex']: f for f in item['frames']}
    if list(frame_map) != item['sourceFrameOrder'] or len(frame_map) != metadata['frameCount']:
        raise ValueError('Incomplete original source positions')
    pictures, origins = {}, {}
    for frame in metadata['frames']:
        index = frame['index']
        if frame['empty']:
            continue
        art = frame_map[index]
        painted = ROOT / art['file']
        checked(painted, art['sha256'])
        with Image.open(painted) as source:
            target_size = (frame['width'], frame['height'])
            expected_size = (target_size[0]*4, target_size[1]*4)
            if source.mode != 'RGBA' or source.size != expected_size:
                raise ValueError(f'World art must retain its complete registered density4 extent: {painted}')
            if art['exportDensity'] != 4 or art['logicalFrameSize'] != list(target_size):
                raise ValueError('Painted world density or logical size changed')
            if art['frameOffsetRaw'] != frame['frameOffset']:
                raise ValueError('Painted world raw offset differs from native source')
            # The whole registered frame already contains its original placement.
            # Preserve it with one exact 4x to 1x resize.
            image = source.convert('RGBa').resize(target_size, Image.Resampling.LANCZOS).convert('RGBA')
        pictures[index] = image
        origins[index] = {
            'derivedFrom': {**io.ref(painted), **provenance(art)},
            'sourceRasterAliasOfSourceFrameIndex': art.get('rasterAliasOfSourceFrameIndex'),
            'operation': {'type': 'whole registered density4 world frame to native 1x',
                          'inputSize': list(expected_size), 'outputSize': list(target_size),
                          'uniformScale': 0.25, 'resampler': 'premultiplied-alpha LANCZOS',
                          'sourceRectLTRB': [0, 0, *expected_size], 'placementPx': [0, 0],
                          'newModelGeneration': False},
        }
    output, _, decoded = codec.replace_frames(original, pictures)
    output_path = HERE / 'patch' / native_path
    io.save_bytes(output_path, output, check)
    state = 'stand' if native_path.endswith('_stand.img') else 'walk'
    frame_records = {}
    for native, picture in decoded:
        index = native['index']
        raster_key = (item['itemId'], picture.width, picture.height, io.sha(picture.tobytes()))
        shared = decoded_cache.get(raster_key)
        if shared is None:
            path = HERE / 'decoded' / str(item['itemId']) / f'{index:03}.png'
            io.save_image(path, picture, check)
            shared = (io.ref(path), index)
            decoded_cache[raster_key] = shared
        raster, representative = shared
        frame_records[index] = {
            **raster, 'index': index, 'sourceFrameIndex': index, 'empty': False,
            'width': picture.width, 'height': picture.height, 'pixelMode': native['pixelMode'],
            'frameOffset': native['frameOffset'], 'alphaExtrema': list(picture.getchannel('A').getextrema()),
            'sourceEncodedPixelSha256': native['encodedPixelSha256'],
            'nativeRasterAliasOfSourceFrameIndex': representative if representative != index else None,
            **origins[index], 'sourceFrameDurationMs': None, 'nativeHeadAttachment': None,
        }
    for native in metadata['frames']:
        if native['empty']:
            index = native['index']
            frame_records[index] = {'index': index, 'sourceFrameIndex': index, 'empty': True,
                                     'width': native['width'], 'height': native['height'],
                                     'pixelMode': native['pixelMode'], 'frameOffset': native['frameOffset']}
    source = {'nativePath': native_path, 'itemId': item['itemId'], 'state': state,
              'sourceArchiveMember': member, 'sourceSha256': io.sha(original), 'metadata': metadata}
    resource = {**io.ref(output_path), 'nativePath': native_path, 'itemId': item['itemId'],
                'state': state, 'projectDisplayName': item['projectDisplayName'],
                'sourceSha256': io.sha(original), 'sourceLoose': True, 'sourcePacked': False,
                'frames': [frame_records[f['index']] for f in metadata['frames']],
                'sourceFrameDurationMs': None, 'nativeHeadAttachment': None,
                'visualAccepted': False, 'nativeRuntimeVerified': False, 'accepted': False}
    return source, resource


def preview(items, check):
    stand = [item for item in items if item['state'] == 'stand']
    board = Image.new('RGB', (1480, len(stand)*640), '#ece5d1')
    draw = ImageDraw.Draw(board)
    for row, item in enumerate(stand):
        y = row*640
        draw.text((12, y+8), f"{item['itemId']} / native world frame pixels / stand = walk / pending user review",
                  fill='#284f40')
        draw.rectangle((0, y+320, 1479, y+639), fill='#173e36')
        for frame in item['frames']:
            if frame['empty']:
                continue
            index = frame['index']
            x, dy = index%12*122+8, index//12*150+32
            with Image.open(ROOT / frame['file']) as image:
                for background_y, ink in ((y, '#284f40'), (y+320, '#f5eddb')):
                    board.paste(image, (x+5, background_y+dy+21), image)
                    draw.text((x, background_y+dy), f"f{index} off{tuple(frame['frameOffset'])}", fill=ink)
    path = HERE / 'contact-native-light-dark.png'
    io.save_image(path, board, check)
    return io.ref(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    with ARCHIVE.open('rb') as stream:
        if io.hashlib.file_digest(stream, 'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Pinned reference archive changed')
    catalog = {e['item_id']: e for e in json.loads(CATALOG.read_bytes())['items']}
    sources, resources, inputs, cache = [], [], [], {}
    with zipfile.ZipFile(ARCHIVE) as archive:
        index = archive.read('QQTang-Local/runtime/client-patched/data/object.idx')
        package = archive.read('QQTang-Local/runtime/client-patched/data/object.pkg')
        packed_paths = {p['path'].replace(chr(92), '/').lower()
                        for p in codec.reader.parse_index(index, len(package))['entries']}
        for item_id in IDS:
            path = ROOT / f'assets/items/head-adornments/world-{item_id}-art.json'
            item = json.loads(path.read_bytes())['items'][0]
            contract_path = ROOT / item['sourceContract']
            source_contract = json.loads(contract_path.read_bytes())
            inputs.extend((io.ref(path), io.ref(contract_path)))
            states = []
            for state in ('stand', 'walk'):
                native_path = next(p for p in catalog[item_id]['installed_files'] if p.endswith('_'+state+'.img'))
                if native_path.lower() in packed_paths:
                    raise ValueError('A selected head world resource became packaged')
                source, resource = convert_state(archive, native_path, item, source_contract, check, cache)
                sources.append(source)
                resources.append(resource)
                states.append(resource)
            if states[0]['sourceSha256'] != states[1]['sourceSha256'] or states[0]['sha256'] != states[1]['sha256']:
                raise ValueError('Registered stand/walk byte equivalence changed')
    contract_path = HERE / 'source-contract.json'
    io.save_json(contract_path, {'schemaVersion': 1, 'sourceArchiveSha256': ARCHIVE_SHA, 'catalog': io.ref(CATALOG),
                                'items': sources}, check)
    result = {
        'schemaVersion': 1, 'scope': 'Native world head-adornment stand/walk resources for five selected items',
        'sourceContract': io.ref(contract_path), 'inputManifestsAndContracts': inputs, 'items': resources,
        'convertedItemCount': len(IDS), 'convertedNativeResourceCount': len(resources),
        'sourceFramePositions': sum(len(item['frames']) for item in resources),
        'uniqueNativeRasters': len(cache), 'exportDensity': 1,
        'converterSources': [io.ref(Path(__file__).resolve()), io.ref(ROOT / 'scripts/native-ui-format.py'),
                             io.ref(ROOT / 'scripts/build-native-inventory-art.py')],
        'newModelGeneration': False, 'sourceFrameDurationMs': None, 'nativeHeadAttachment': None,
        'visualAccepted': False, 'nativeRuntimeVerified': False, 'installedToClient': False,
        'allHeadArtComplete': False, 'preview': preview(resources, check),
    }
    io.save_json(HERE / 'manifest.json', result, check)
    print(json.dumps({'items': len(IDS), 'nativeResources': len(resources),
                      'sourcePositions': result['sourceFramePositions'], 'uniqueNativeRasters': len(cache),
                      'nativeGeometryRetained': True, 'pixelReplay': check}))


if __name__ == '__main__':
    main()
