"""Read-only source capture of all112 remaining packed native shop resources."""
from importlib import util
from pathlib import Path
import argparse
import hashlib
import json
import math

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


HELP = module('shopextra_capture_helpers', 'assets/native-client-ui/forge-controls-reference/capture-source.py')
OLD = module('shopextra_existing_controls', 'scripts/native-ui-shop-controls-art.py')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    census_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    census = json.loads(census_path.read_bytes())
    selected = [r for r in census['resources'] if r['path'].lower().startswith('object/ui/shop/') and r['path'] not in OLD.PATHS]
    if len(selected) != 112:
        raise ValueError('Exact remaining112 shop resource scope changed')
    package_path = ROOT / '.artifacts/reference-inputs/object.pkg'
    package = package_path.read_bytes()
    resources = []
    for record in selected:
        raw, compressed = HELP.CODEC.reader.unpack_resource(package, record['indexEntry'])
        if hashlib.sha256(raw).hexdigest() != record['sourceSha256'] or compressed != record['compressedSha256']:
            raise ValueError('Packed shop source changed')
        metadata, _ = HELP.CODEC.reader.inspect_dimg(raw, metadata_only=True)
        frames = []
        for frame in metadata['frames']:
            if frame['empty']:
                frames.append({'sourceFrame': frame, 'empty': True})
                continue
            start = frame['pixelDataOffset']
            pixels = HELP.CODEC.reader.decode_frame_pixels(raw[start:start + frame['pixelByteLength']],
                        frame['pixelMode'], frame['width'], frame['height'])
            picture = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
            slug = record['path'].removeprefix('object/ui/').removesuffix('.img').replace('/', '__')
            path = HERE / 'source' / f'{slug}-{frame["index"]:02}.png'
            HELP.IO.png(path, picture, check)
            frames.append({**HELP.ref(path), 'sourceFrame': frame, 'decodedRgbaSha256': hashlib.sha256(pixels).hexdigest(),
                           'decodedAlpha': HELP.alpha(picture), 'empty': False})
        resources.append({'nativePath': record['path'], 'sourceSha256': record['sourceSha256'],
                          'sourceCompressedSha256': compressed, 'packageEntry': record['indexEntry'],
                          'metadata': metadata, 'sourcePacked': True, 'sourceLoose': False, 'frames': frames,
                          'exactBindings': [b for b in census['bindings'] if b.get('canonicalPath') == record['canonicalPath']]})
    boards, font = [], ImageFont.load_default(size=14)
    for page in range(math.ceil(len(resources) / 8)):
        subset = resources[page * 8:(page + 1) * 8]
        heights = []
        for r in subset:
            cell_height = max(92, min(340, max(f['sourceFrame']['height'] for f in r['frames']) * 2 + 24))
            heights.append(26 + math.ceil(len(r['frames']) / 4) * cell_height)
        board = Image.new('RGB', (1500, sum(heights)), '#193f35')
        draw, y = ImageDraw.Draw(board), 0
        for r, height in zip(subset, heights):
            cell_height = (height - 26) // math.ceil(len(r['frames']) / 4)
            draw.line((0, y, 1499, y), fill='#a8ac85')
            draw.text((8, y + 4), r['nativePath'], font=font, fill='#fff3d5')
            for f in r['frames']:
                if f['empty']:
                    continue
                frame, index = f['sourceFrame'], f['sourceFrame']['index']
                with Image.open(ROOT / f['file']) as image:
                    scale = min(2, 350 / image.width, (cell_height - 22) / image.height)
                    picture = HELP.IO.scaled(image, tuple(max(1, round(v * scale)) for v in image.size))
                x, top = 8 + (index % 4) * 372, y + 26 + (index // 4) * cell_height
                draw.text((x, top), f"raw{index} off{tuple(frame['frameOffset'])}", font=font, fill='#fff3d5')
                board.paste(picture, (x, top + 20), picture)
            y += height
        path = HERE / f'source-all-states-{page + 1:02}.png'
        HELP.IO.png(path, board, check)
        boards.append(HELP.ref(path))
    HELP.IO.write_json(HERE / 'manifest.json', {
        'schemaVersion': 1, 'scope': 'All112 remaining packed object/ui/shop resources; excludes existing20 controls',
        'sourceCensus': HELP.ref(census_path), 'sourcePackage': HELP.ref(package_path),
        'sourceIndex': HELP.ref(ROOT / '.artifacts/reference-inputs/object.idx'),
        'excludedExistingRenderer': HELP.ref(ROOT / 'scripts/native-ui-shop-controls-art.py'),
        'excludedExistingPaths': list(OLD.PATHS), 'resources': resources,
        'sourceFramePositions': sum(len(r['frames']) for r in resources), 'sourceBoards': boards,
        'nativeProgramExecuted': False, 'providedDirectoryReadOrMutated': False,
        'visualAccepted': False, 'nativeRuntimeVerified': False}, check)
    print(json.dumps({'resources': len(resources), 'sourcePositions': sum(len(r['frames']) for r in resources),
                      'sourcePages': len(boards), 'readOnlyReplay': check}))


if __name__ == '__main__':
    main()
