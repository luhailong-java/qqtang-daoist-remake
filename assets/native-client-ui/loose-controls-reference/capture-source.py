"""Capture47 pinned loose UI controls without client or GUI execution."""
import argparse
import hashlib
from importlib import util
import json
import math
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


HELP = module('loose_controls_capture_helpers', 'assets/native-client-ui/forge-controls-reference/capture-source.py')


def selected(census):
    return [r for r in census['resources'] if r['storage'] == 'loose' and
            r['path'].startswith('res/uiRes/') and r['format'] == 'QQF/DIMG' and
            not r['path'].startswith(('res/uiRes/icon/', 'res/uiRes/face/faces/'))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    census_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    census = json.loads(census_path.read_bytes())
    scope = selected(census)
    if len(scope) != 47:
        raise ValueError('Exact47 loose UI control scope changed')
    archive_path = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7':
        raise ValueError('Pinned source archive changed')
    resources = []
    with zipfile.ZipFile(archive_path) as archive:
        for item in scope:
            raw = archive.read(item['archiveMember'])
            if hashlib.sha256(raw).hexdigest() != item['sourceSha256']:
                raise ValueError('Pinned loose control source hash changed')
            metadata, _ = HELP.CODEC.reader.inspect_dimg(raw, metadata_only=True)
            if metadata != item['metadata']:
                raise ValueError('Pinned loose control source metadata changed')
            frames = []
            for frame in metadata['frames']:
                if frame['empty']:
                    frames.append({'sourceFrame': frame, 'empty': True})
                    continue
                start = frame['pixelDataOffset']
                pixels = HELP.CODEC.reader.decode_frame_pixels(raw[start:start + frame['pixelByteLength']],
                            frame['pixelMode'], frame['width'], frame['height'])
                picture = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
                slug = item['path'].removeprefix('res/uiRes/').removesuffix('.img').replace('/', '__')
                path = HERE / 'source' / f'{slug}-{frame["index"]:02}.png'
                HELP.IO.png(path, picture, check)
                frames.append({**HELP.ref(path), 'sourceFrame': frame, 'decodedRgbaSha256': hashlib.sha256(pixels).hexdigest(),
                               'decodedAlpha': HELP.alpha(picture), 'empty': False})
            resources.append({'nativePath': item['path'], 'sourceSha256': item['sourceSha256'],
                              'archiveMember': item['archiveMember'], 'sourceZipCrc32': item['zipCrc32'],
                              'metadata': metadata, 'sourcePacked': False, 'sourceLoose': True,
                              'frames': frames, 'exactBindings': [b for b in census['bindings'] if b.get('canonicalPath') == item['canonicalPath']]})
    boards, font = [], ImageFont.load_default(size=14)
    for page in range(math.ceil(len(resources) / 8)):
        subset = resources[page * 8:(page + 1) * 8]
        heights = []
        for item in subset:
            cell = max(88, min(340, max(f['sourceFrame']['height'] for f in item['frames']) * 3 + 24))
            heights.append(26 + math.ceil(len(item['frames']) / 5) * cell)
        board = Image.new('RGB', (1500, sum(heights)), '#193f35')
        draw, y = ImageDraw.Draw(board), 0
        for item, height in zip(subset, heights):
            cell = (height - 26) // math.ceil(len(item['frames']) / 5)
            draw.line((0, y, 1499, y), fill='#a8ac85')
            draw.text((8, y + 4), item['nativePath'], font=font, fill='#fff3d5')
            for entry in item['frames']:
                frame, index = entry['sourceFrame'], entry['sourceFrame']['index']
                x, top = 8 + index % 5 * 300, y + 26 + index // 5 * cell
                draw.text((x, top), f'raw{index} off{tuple(frame["frameOffset"])}' + (' EMPTY' if entry['empty'] else ''), font=font, fill='#fff3d5')
                if entry['empty']:
                    continue
                with Image.open(ROOT / entry['file']) as image:
                    factor = min(4, 280 / image.width, (cell - 22) / image.height)
                    picture = HELP.IO.scaled(image, tuple(max(1, round(v * factor)) for v in image.size))
                board.paste(picture, (x, top + 20), picture)
            y += height
        path = HERE / f'source-all-states-{page + 1:02}.png'
        HELP.IO.png(path, board, check)
        boards.append(HELP.ref(path))
    declared = sum(len(r['frames']) for r in resources)
    nonempty = sum(not f['empty'] for r in resources for f in r['frames'])
    if (declared, nonempty) != (132, 131):
        raise ValueError('Pinned loose UI declared/nonempty slots changed')
    HELP.IO.write_json(HERE / 'manifest.json', {
        'schemaVersion': 1, 'scope': 'All47 loose res/uiRes controls, excluding168 face bodies,2 GIF portraits and all inventory icons',
        'sourceCensus': HELP.ref(census_path), 'sourceArchive': HELP.ref(archive_path),
        'resources': resources, 'declaredSourceFramePositions': declared, 'sourceFramePositions': nonempty,
        'sourceEmptyPositions': 1, 'sourceBoards': boards,
        'nativeProgramExecuted': False, 'providedDirectoryReadOrMutated': False,
        'sourceTimingVerified': False, 'visualAccepted': False, 'nativeRuntimeVerified': False}, check)
    print(json.dumps({'resources': len(resources), 'declaredPositions': declared, 'nonemptyPositions': nonempty,
                      'sourceEmptyPositions': 1, 'sourcePages': len(boards), 'readOnlyReplay': check}))


if __name__ == '__main__':
    main()
