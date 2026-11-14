"""Check lobby art in the original DIMG positions and pixel formats without installation."""
from pathlib import Path
import hashlib
import importlib.util
import json

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    builder = load('lobby_build', 'scripts/build-native-login-art.py')
    renderer = load('lobby_render', 'scripts/native-ui-lobby-controls-art.py')
    source_path = HERE / 'manifest.json'
    source = json.loads(source_path.read_bytes())
    package = (ROOT / '.artifacts/reference-inputs/object.pkg').read_bytes()
    if sha(package) != source['package']['sha256']:
        raise ValueError('Pinned package changed')
    paints = {key: Image.open(ROOT / path).convert('RGBA') for key, path in builder.PAINTS.items()}
    font = Path('C:/Windows/Fonts/msyh.ttc')
    output = ROOT / '.artifacts/native-ui-audit-20261114/lobby-controls-preview'
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    for path, (kind, label) in renderer.PATHS.items():
        resource = next(r for r in source['resources'] if r['nativePath'] == path.lower())
        original = builder.codec.reader.unpack_resource(package, resource['packageEntry'])[0]
        if sha(original) != resource['sourceSha256']:
            raise ValueError('Pinned resource changed')
        pictures = {f['index']: renderer.render(kind, label, f['index'], (f['width'], f['height']), paints, font,
                    builder.nine_slice, builder.scaled) for f in resource['metadata']['frames'] if not f['empty']}
        encoded, metadata, decoded = builder.codec.replace_frames(original, pictures)
        if len(encoded) != len(original):
            raise ValueError('Native resource length changed')
        cursor = 0
        for frame in metadata['frames']:
            start = frame['pixelDataOffset']
            if encoded[cursor:start] != original[cursor:start]:
                raise ValueError('Native bytes outside pixel payload changed')
            cursor = start + frame['pixelByteLength']
        if encoded[cursor:] != original[cursor:]:
            raise ValueError('Native suffix changed')
        for frame, pixels in decoded:
            png = output / f'{Path(path).stem}-{frame["index"]:02}.png'
            pixels.save(png)
            checks.append({'nativePath': path, 'sourceFrameIndex': frame['index'], 'preview': str(png),
                           'width': pixels.width, 'height': pixels.height, 'pixelMode': frame['pixelMode'],
                           'rawOffset': frame['frameOffset'], 'nativeRgbaSha256': sha(pixels.tobytes()),
                           'nonpixelBytesUnchanged': True})
    resources = [path for path, (kind, _) in renderer.PATHS.items() if kind not in ('lobby-password-panel', 'lobby-map-filter-panel')]
    for page in range(2):
        paths = resources[page * 10:page * 10 + 10]
        board = Image.new('RGB', (1000, 1510), '#d6d4cb')
        draw = ImageDraw.Draw(board)
        for row, path in enumerate(paths):
            top = 8 + row * 150
            draw.text((10, top), path, fill='#172a24')
            for frame in (f for f in checks if f['nativePath'] == path):
                image = Image.open(frame['preview']).convert('RGBA')
                factor = 2 if image.width < 150 and image.height < 80 else 1
                image = image.resize((image.width * factor, image.height * factor), Image.Resampling.NEAREST)
                x = 10 + frame['sourceFrameIndex'] * 250
                draw.text((x, top + 18), str(frame['sourceFrameIndex']), fill='#172a24')
                board.paste(image, (x, top + 33), image)
        board.save(output / f'native-states-{page + 1}.png')
    record = {'rendererSha256': sha((ROOT / 'scripts/native-ui-lobby-controls-art.py').read_bytes()),
              'sourceManifestSha256': sha(source_path.read_bytes()), 'fontSha256': sha(font.read_bytes()),
              'paintInputs': [{'file': p, 'sha256': sha((ROOT / p).read_bytes())} for p in builder.PAINTS.values()],
              'resources': len(renderer.PATHS), 'frames': len(checks), 'checks': checks, 'nativeRuntimeVerified': False}
    (output / 'verification.json').write_bytes((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({key: record[key] for key in ('resources', 'frames', 'rendererSha256')}))


if __name__ == '__main__':
    main()
