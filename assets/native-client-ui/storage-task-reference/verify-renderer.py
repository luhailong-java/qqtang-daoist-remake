"""Export storage/task candidates and replay their original native frame geometry."""
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
art = load('storage_task_art', 'scripts/native-ui-storage-task-art.py')


def check_palette(source, check):
    prefix = '?.UI_children_shop.children.taskDlg.children.'
    expectations = {
        'taskName': [255, 255, 255, 255],
        'taskIntroduction': [102, 71, 39, 230],
        'deadLine': [102, 71, 39, 255],
        'progressDes': [102, 71, 39, 255],
        'awardDes': [229, 217, 184, 255],
        'taskBtn0.children.taskNameBtn': [102, 71, 39, 230],
    }
    bindings = []
    for suffix, color in expectations.items():
        scope = next(s for s in source['sourceScopes'] if s['module'] == 'uiShop' and s['scope'] == prefix+suffix)
        if scope['literalAssignments']['drawcolor'] != color:
            raise ValueError('Explicit native task text color changed')
        bindings.append(scope)

    def luminance(rgb):
        values = [v/255 for v in rgb]
        linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
        return sum(a*b for a, b in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))

    samples = []
    checks = [('btn_taskName', i, 'taskBtn0.children.taskNameBtn', (52, 15)) for i in range(4)]
    checks.extend(('dlg_task', 0, field, point) for field, point in (
        ('taskName', (162, 43)), ('taskIntroduction', (222, 99)),
        ('deadLine', (272, 205)), ('progressDes', (122, 234)), ('awardDes', (222, 329))))
    for stem, index, field, point in checks:
        path = HERE / 'candidate' / 'decoded' / f'{stem}-{index:02}.png'
        with Image.open(path) as image:
            background = image.convert('RGBA').getpixel(point)[:3]
        color = expectations[field]
        foreground = [round((v*color[3]+b*(255-color[3]))/255) for v, b in zip(color[:3], background, strict=True)]
        a, b = luminance(foreground), luminance(background)
        contrast = (max(a, b)+0.05)/(min(a, b)+0.05)
        if contrast < 4.5:
            raise ValueError('Native text sample lacks the selected contrast threshold')
        samples.append({'nativePreview': builder.record(path), 'field': field, 'samplePixel': list(point),
                        'nativeForegroundRgba': color, 'sampledBackgroundRgb': list(background),
                        'compositedForegroundRgb': foreground, 'contrastRatio': contrast})
    path = HERE / 'palette-evidence.json'
    builder.save_json(path, {
        'schemaVersion': 1, 'sourceReferences': builder.record(HERE / 'manifest.json'),
        'sourceColorBindings': bindings, 'samples': samples, 'sampleThreshold': 4.5,
        'interpretation': 'Explicit source task colors sampled against final native decoded backgrounds',
        'runtimeTextRenderingVerified': False, 'userVisualAccepted': False,
    }, check)
    return builder.record(path)


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
        raise ValueError('Storage/task controls conflict with an already registered renderer')
    package = (ROOT / sources['package']['file']).read_bytes()
    if builder.record(ROOT / sources['package']['file']) != sources['package']:
        raise ValueError('Source package changed')
    paint_paths = {k: builder.PAINTS[k] for k in ('panel', 'normal', 'hover', 'pressed')}
    paint_paths.update(art.PAINT_INPUTS)
    paints = {k: Image.open(ROOT / p).convert('RGBA') for k, p in paint_paths.items()}
    font = Path('C:/Windows/Fonts/msyh.ttc')
    row_heights = [320 if max(f['nativeSize'][1] for f in records[p.lower()]['frames']) > 100 else 120 for p in art.PATHS]
    contact = Image.new('RGB', (1200, sum(row_heights)), '#ede6d4')
    offset_y = 0
    draw = ImageDraw.Draw(contact)
    items = []
    for row, (path, (kind, caption)) in enumerate(art.PATHS.items()):
        evidence = records[path.lower()]
        raw, compressed_sha = builder.codec.reader.unpack_resource(package, evidence['packageEntry'])
        if builder.hashlib.sha256(raw).hexdigest() != evidence['sourceSha256'] or compressed_sha != evidence['compressedSha256']:
            raise ValueError('Source DIMG digest differs')
        metadata = evidence['metadata']
        pictures = {f['index']: art.render(kind, caption, f['index'], (f['width'], f['height']),
                                         paints, font, builder.nine_slice, builder.scaled)
                    for f in metadata['frames'] if not f['empty']}
        output, _, frames = builder.codec.replace_frames(raw, pictures)
        destination = HERE / 'candidate' / 'patch' / path
        if check:
            if destination.read_bytes() != output:
                raise ValueError('Encoded storage/task candidate changed')
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(output)
        row_height = row_heights[row]
        draw.text((10, offset_y+5), path, fill='#244f41')
        exports = []
        for frame, image in frames:
            target = HERE / 'candidate' / 'decoded' / f'{Path(path).stem}-{frame["index"]:02}.png'
            builder.save_image(target, image, check)
            index = frame['index']
            ratio = min(2, 250/image.width, (row_height-45)/image.height)
            extent = (max(1, round(image.width*ratio)), max(1, round(image.height*ratio)))
            enlarged = image.resize(extent, Image.Resampling.NEAREST)
            x, y = 15+index*290, offset_y+27
            contact.paste(enlarged, (x, y), enlarged)
            draw.text((x, offset_y+row_height-15), f"f{index} {image.width}x{image.height} offset{frame['frameOffset']}",
                      fill='#244f41')
            alpha_key = None
            if kind in ('storage-nav', 'storage-task-step'):
                alpha_key = f'{caption}-{index}'
            elif kind in ('storage-selection', 'storage-shadow', 'storage-grid-room'):
                alpha_key = {'storage-selection': 'selection', 'storage-shadow': 'shadow',
                             'storage-grid-room': 'room-grid'}[kind]
            if alpha_key:
                original_alpha = art.source_alpha(alpha_key, image.size)
                if image.getchannel('A').tobytes() != original_alpha.tobytes():
                    raise ValueError('Functional alpha changed after native encoding')
            exports.append({**builder.record(target), 'index': index, 'nativeSize': list(image.size),
                            'frameOffset': frame['frameOffset'], 'pixelMode': frame['pixelMode'],
                            'alphaExtrema': list(image.getchannel('A').getextrema())})
        items.append({**builder.record(destination), 'nativePath': path, 'sourceSha256': evidence['sourceSha256'],
                      'sourceBindings': evidence['sourceBindings'], 'rendererKind': kind, 'caption': caption,
                      'captionEvidence': 'Read from native rasters and source declarations; runtime text surfaces remain blank',
                      'frames': exports, 'visualAccepted': False, 'nativeRuntimeVerified': False})
        offset_y += row_height
    preview = HERE / 'candidate' / 'contact-native.png'
    builder.save_image(preview, contact, check)
    palette = check_palette(sources, check)
    candidate = {
        'schemaVersion': 1, 'scope': 'Twenty-two native storage and task control candidates',
        'sourceReferences': builder.record(source_path), 'renderer': builder.record(ROOT / 'scripts/native-ui-storage-task-art.py'),
        'verificationScript': builder.record(Path(__file__).resolve()),
        'codec': builder.record(ROOT / 'scripts/native-ui-format.py'),
        'paintInputs': [builder.record(ROOT / p) for p in paint_paths.values()],
        'font': {'family': 'Microsoft YaHei', 'sha256': builder.hashlib.sha256(font.read_bytes()).hexdigest()},
        'symbolFont': {'fileName': 'seguisym.ttf', 'sha256': builder.hashlib.sha256(Path(art.FONT_INPUTS['symbols']).read_bytes()).hexdigest()},
        'structuralAlphaInputs': [builder.record(ROOT / p) for p in art.STRUCTURAL_ALPHA_INPUTS.values()],
        'visualMappingAssumptions': art.VISUAL_MAPPING_ASSUMPTIONS,
        'paletteEvidence': palette,
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
