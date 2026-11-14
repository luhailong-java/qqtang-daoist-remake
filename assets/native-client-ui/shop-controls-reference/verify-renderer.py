"""Export shop candidates and replay their original native frame geometry."""
from pathlib import Path
import argparse
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


builder = load('shop_build_helpers', 'scripts/build-native-login-art.py')
art = load('shop_control_art', 'scripts/native-ui-shop-controls-art.py')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    source_path = HERE / 'manifest.json'
    sources = json.loads(source_path.read_bytes())
    records = {r['nativePath'].lower(): r for r in sources['resources']}
    if set(records) != {p.lower() for p in art.PATHS}:
        raise ValueError('Selected native paths differ from the decoded source evidence')
    if any(path in builder.PATHS and builder.PATHS[path] != value for path, value in art.PATHS.items()):
        raise ValueError('Shop controls conflict with an already registered renderer')
    package = (ROOT / sources['package']['file']).read_bytes()
    if builder.record(ROOT / sources['package']['file']) != sources['package']:
        raise ValueError('Source package changed')
    paints = {k: Image.open(ROOT / p).convert('RGBA') for k, p in builder.PAINTS.items()}
    font = Path('C:/Windows/Fonts/msyh.ttc')
    contact = Image.new('RGB', (1200, len(art.PATHS)*120), '#ede6d4')
    draw = ImageDraw.Draw(contact)
    items = []
    for row, (path, (kind, caption)) in enumerate(art.PATHS.items()):
        evidence = records[path.lower()]
        raw, compressed_sha = builder.codec.reader.unpack_resource(package, evidence['packageEntry'])
        if builder.hashlib.sha256(raw).hexdigest() != evidence['sourceSha256'] or compressed_sha != evidence['compressedSha256']:
            raise ValueError('Source DIMG digest differs')
        metadata = evidence['metadata']
        if not evidence['sourceBindings']:
            raise ValueError('A selected shop control has no exact uiShop source binding')
        pictures = {f['index']: art.render(kind, caption, f['index'], (f['width'], f['height']),
                                         paints, font, builder.nine_slice, builder.scaled)
                    for f in metadata['frames'] if not f['empty']}
        output, _, frames = builder.codec.replace_frames(raw, pictures)
        destination = HERE / 'candidate' / 'patch' / path
        if check:
            if destination.read_bytes() != output:
                raise ValueError('Encoded shop candidate changed')
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(output)
        draw.text((10, row*120+5), path, fill='#244f41')
        exports = []
        for frame, image in frames:
            target = HERE / 'candidate' / 'decoded' / f'{Path(path).stem}-{frame["index"]:02}.png'
            builder.save_image(target, image, check)
            index = frame['index']
            # These views are evidence of native frame positions, at 2x nearest pixel scale.
            enlarged = image.resize((image.width*2, image.height*2), Image.Resampling.NEAREST)
            x, y = 15+index*260, row*120+27
            contact.paste(enlarged, (x, y), enlarged)
            draw.text((x, row*120+105), f"f{index} {image.width}x{image.height} offset{frame['frameOffset']}",
                      fill='#244f41')
            exports.append({**builder.record(target), 'index': index, 'nativeSize': list(image.size),
                            'frameOffset': frame['frameOffset'], 'pixelMode': frame['pixelMode'],
                            'alphaExtrema': list(image.getchannel('A').getextrema())})
        items.append({**builder.record(destination), 'nativePath': path, 'sourceSha256': evidence['sourceSha256'],
                      'sourceBindings': evidence['sourceBindings'], 'rendererKind': kind, 'caption': caption,
                      'captionEvidence': 'Read from decoded native rasters; original blank tab remains blank',
                      'frames': exports, 'visualAccepted': False, 'nativeRuntimeVerified': False})
    preview = HERE / 'candidate' / 'contact-native-2x.png'
    builder.save_image(preview, contact, check)
    candidate = {
        'schemaVersion': 1, 'scope': 'Twenty native shop control candidates',
        'sourceReferences': builder.record(source_path), 'renderer': builder.record(ROOT / 'scripts/native-ui-shop-controls-art.py'),
        'verificationScript': builder.record(Path(__file__).resolve()),
        'codec': builder.record(ROOT / 'scripts/native-ui-format.py'),
        'paintInputs': [builder.record(ROOT / p) for p in builder.PAINTS.values()],
        'font': {'family': 'Microsoft YaHei', 'sha256': builder.hashlib.sha256(font.read_bytes()).hexdigest()},
        'items': items, 'preview': builder.record(preview), 'nativeResources': len(items),
        'sourcePositions': sum(len(item['frames']) for item in items),
        'newModelGeneration': False, 'nativeGeometryRetained': True, 'nativeRuntimeVerified': False,
        'visualAccepted': False, 'installedToClient': False,
    }
    builder.save_json(HERE / 'candidate-manifest.json', candidate, check)
    print(json.dumps({'nativeResources': len(items), 'sourcePositions': candidate['sourcePositions'],
                      'nativeGeometryRetained': True, 'pixelReplay': check}))


if __name__ == '__main__':
    main()
