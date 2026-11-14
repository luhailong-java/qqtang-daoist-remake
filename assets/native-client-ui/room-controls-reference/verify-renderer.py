"""Exercise the room renderer through native pixel modes without installing client files."""
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
    builder = load('room_native_builder', 'scripts/build-native-login-art.py')
    renderer = load('room_native_controls', 'scripts/native-ui-room-controls-art.py')
    source_path = HERE / 'manifest.json'
    source = json.loads(source_path.read_bytes())
    package = (ROOT / '.artifacts/reference-inputs/object.pkg').read_bytes()
    if sha(package) != source['package']['sha256']:
        raise ValueError('Native source package changed')
    font = Path('C:/Windows/Fonts/msyh.ttc')
    paints = {key: Image.open(ROOT / value).convert('RGBA') for key, value in builder.PAINTS.items()}
    output = ROOT / '.artifacts/native-ui-audit-20261114/room-controls-preview'
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    for path, (kind, label) in renderer.PATHS.items():
        resource = next(row for row in source['resources'] if row['nativePath'] == path.lower())
        original = builder.codec.reader.unpack_resource(package, resource['packageEntry'])[0]
        if sha(original) != resource['sourceSha256']:
            raise ValueError('Native source resource changed')
        pictures = {frame['index']: renderer.render(kind, label, frame['index'], (frame['width'], frame['height']),
                paints, font, builder.nine_slice, builder.scaled) for frame in resource['metadata']['frames'] if not frame['empty']}
        encoded, metadata, decoded = builder.codec.replace_frames(original, pictures)
        if len(encoded) != len(original):
            raise ValueError('Native DIMG length changed')
        cursor = 0
        for frame in metadata['frames']:
            start = frame['pixelDataOffset']
            if encoded[cursor:start] != original[cursor:start]:
                raise ValueError('Native DIMG bytes outside pixel planes changed')
            cursor = start + frame['pixelByteLength']
        if encoded[cursor:] != original[cursor:]:
            raise ValueError('Native DIMG suffix changed')
        for frame, image in decoded:
            target = output / f'{Path(path).stem}-{frame["index"]:02d}.png'
            image.save(target)
            checks.append({'nativePath': path, 'sourceFrameIndex': frame['index'], 'width': image.width, 'height': image.height,
                           'pixelMode': frame['pixelMode'], 'rawOffset': frame['frameOffset'], 'preview': str(target),
                           'nativeRgbaSha256': sha(image.tobytes()), 'nativeFrameStructurePreserved': True})
    buttons = [(path, kind) for path, (kind, _) in renderer.PATHS.items() if kind in ('room-toolbar', 'room-primary', 'room-storage')]
    board = Image.new('RGB', (1000, 1250), '#d6d4cb')
    draw = ImageDraw.Draw(board)
    for row, (path, _) in enumerate(buttons):
        top = 8 + row * 175
        draw.text((10, top), path, fill='#172a24')
        for frame in (r for r in checks if r['nativePath'] == path):
            image = Image.open(frame['preview']).convert('RGBA')
            image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)
            x = 10 + frame['sourceFrameIndex'] * 245
            draw.text((x, top + 20), str(frame['sourceFrameIndex']), fill='#172a24')
            board.paste(image, (x, top + 38), image)
    board.save(output / 'native-button-states.png')
    result = {'rendererSha256': sha((ROOT / 'scripts/native-ui-room-controls-art.py').read_bytes()),
              'sourceManifestSha256': sha(source_path.read_bytes()),
              'paintInputs': [{'file': path, 'sha256': sha((ROOT / path).read_bytes())} for path in builder.PAINTS.values()],
              'fontSha256': sha(font.read_bytes()), 'checks': checks, 'resources': len(renderer.PATHS), 'frames': len(checks),
              'nativeRuntimeVerified': False}
    (output / 'verification.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({key: result[key] for key in ('resources', 'frames', 'rendererSha256')}))


if __name__ == '__main__':
    main()
