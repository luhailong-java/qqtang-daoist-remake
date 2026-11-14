"""Export and replay the isolated entry controls batch before central integration."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ART = module('entry-controls_renderer', 'scripts/native-ui-entry-controls-art.py')
HELPERS = module('entry-controls_common_export_helpers', 'assets/native-client-ui/common-reference/export-common.py')
FONT = Path('C:/Windows/Fonts/msyh.ttc')


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source_path = HERE / 'manifest.json'
    sources = json.loads(source_path.read_bytes())
    by_path = {r['nativePath'].lower(): r for r in sources['resources']}
    package = (ROOT / '.artifacts/reference-inputs/object.pkg').read_bytes()
    paint_inputs = {key: value for key, value in HELPERS.ROOT_PAINTS.items() if key in ('panel', 'normal', 'hover', 'pressed')}
    paint_inputs.update(ART.PAINT_INPUTS)
    paints = {name: Image.open(ROOT / file).convert('RGBA') for name, file in paint_inputs.items()}
    exports = []
    board = Image.new('RGB', (1200, 128 * len(ART.PATHS)), '#eae3d1')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=16)
    for row, (native, (kind, label)) in enumerate(ART.PATHS.items()):
        source = by_path[native.lower()]
        raw, _ = HELPERS.CODEC.reader.unpack_resource(package, source['packageEntry'])
        if hashlib.sha256(raw).hexdigest() != source['sourceSha256']:
            raise ValueError('Source entry controls resource SHA differs')
        pictures = {f['index']: ART.render(kind, label, f['index'], (f['width'], f['height']), paints,
                    FONT, HELPERS.nine_slice, HELPERS.scaled)
                    for f in source['metadata']['frames'] if not f['empty']}
        encoded, _, frames = HELPERS.CODEC.replace_frames(raw, pictures)
        permitted = bytearray(len(raw))
        for frame in source['metadata']['frames']:
            if frame['empty']:
                continue
            start, length = frame['pixelDataOffset'], frame['pixelByteLength']
            permitted[start:start + length] = b'\x01' * length
        if any(a != b and not allowed for a, b, allowed in zip(raw, encoded, permitted, strict=True)):
            raise ValueError('Guide bar non-pixel source bytes changed')
        path = HERE / 'patch' / native
        if args.check:
            if path.read_bytes() != encoded:
                raise ValueError(f'Guide bar native replay differs at {native}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
        entries = []
        y = row * 128
        draw.text((7, y + 4), native, font=font, fill='#214b3c')
        for frame, image in frames:
            slug = native.removeprefix('object/ui/').removesuffix('.img').replace('/', '__')
            png = HERE / 'decoded' / f'{slug}-{frame["index"]:02}.png'
            HELPERS.png(png, image, args.check)
            entries.append({**record(png), 'index': frame['index'], 'width': image.width, 'height': image.height,
                            'frameOffset': frame['frameOffset'], 'pixelMode': frame['pixelMode']})
            scale = min(2, 270 / image.width, 90 / image.height)
            preview = HELPERS.scaled(image, tuple(max(1, round(v * scale)) for v in image.size))
            x = frame['index'] * 296 + 8
            draw.text((x, y + 24), str(frame['index']), font=font, fill='#214b3c')
            board.paste(preview, (x + 18, y + 28), preview)
        exports.append({**record(path), 'nativePath': native, 'rendererKind': kind, 'caption': label,
                        'sourceSha256': source['sourceSha256'], 'frames': entries,
                        'allNonPixelBytesIdenticalToSource': True, 'visualAccepted': False, 'nativeRuntimeVerified': False})
    preview = HERE / 'candidate-all-states.png'
    HELPERS.png(preview, board, args.check)
    result = {
        'schemaVersion': 1, 'scope': '16 login accessory, network-state and replay-file native resources',
        'sourceReferences': record(source_path), 'items': exports, 'renderer': record(ROOT / 'scripts/native-ui-entry-controls-art.py'),
        'exporter': record(Path(__file__)), 'exportHelpers': record(ROOT / 'assets/native-client-ui/common-reference/export-common.py'),
        'paintInputs': [record(ROOT / file) for file in paint_inputs.values()],
        'structuralAlphaInputs': [{'purpose':purpose, **record(ROOT/file)} for purpose,file in ART.STRUCTURAL_ALPHA_INPUTS.items()],
        'inputColorEvidence': record(HERE / 'input-color-evidence.json'),
        'font': {'family': 'Microsoft YaHei', 'sha256': hashlib.sha256(FONT.read_bytes()).hexdigest()},
        'previews': [record(preview)], 'newModelGeneration': False, 'visualAccepted': False, 'nativeRuntimeVerified': False,
    }
    HELPERS.write_json(HERE / 'candidate-manifest.json', result, args.check)
    print(json.dumps({'nativeResources': len(exports), 'sourcePositions': sum(len(e['frames']) for e in exports),
                      'nativeReplayChecked': args.check, 'allNativeHeadersAndOffsetsRetained': True}))


if __name__ == '__main__':
    main()
