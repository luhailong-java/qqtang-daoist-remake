"""Export pet candidates and replay their original native frame geometry."""
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
art = load('pet_controls_art', 'scripts/native-ui-pet-controls-art.py')


def check_palette(source, check):
    root_scope = next(s for s in source['sourceScopes'] if s['module'] == 'uiMain' and s['scope'] == '?')
    globals_ = root_scope['literalAssignments']
    if globals_['lightColor'] != [255, 255, 255, 255] or globals_['darkColor'] != [102, 51, 0, 255]:
        raise ValueError('Pinned global pet foreground colors changed')
    prefix = '?.UI_children_selRoom.children.petPan.children.'
    symbols = {'nameEdit': 'lightColor', 'level': 'darkColor', 'expValue': 'lightColor',
               'loyaltyValue': 'lightColor', 'baseSkillDlg.children.skill0': 'lightColor',
               'skillDlg.children.skill0': 'lightColor',
               'foodDlg.children.petItem0.children.itemNum': 'lightColor'}
    assignments = []
    for field, symbol in symbols.items():
        matches = [s for s in source['symbolicColorAssignments']
                   if s['scope'] == prefix+field and s['target'] == 'drawcolor']
        if len(matches) != 1 or matches[0]['symbol'] != symbol:
            raise ValueError('Native pet symbolic text-color assignment changed')
        assignments.append(matches[0])

    def luminance(rgb):
        values = [v/255 for v in rgb]
        linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
        return sum(a*b for a, b in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))

    samples = []
    checks = [('dlg_pet', 'nameEdit', (70, 164)), ('dlg_pet', 'level', (100, 191)),
              ('dlg_pet', 'expValue', (195, 213)), ('dlg_pet', 'loyaltyValue', (195, 231)),
              ('dlg_baseskill', 'baseSkillDlg.children.skill0', (50, 25)),
              ('dlg_skill', 'skillDlg.children.skill0', (50, 15)),
              ('dlg_food', 'foodDlg.children.petItem0.children.itemNum', (45, 48))]
    for stem, field, point in checks:
        path = HERE / 'candidate' / 'decoded' / f'{stem}-00.png'
        with Image.open(path) as image:
            background = image.convert('RGBA').getpixel(point)[:3]
        color = globals_[symbols[field]]
        a, b = luminance(color[:3]), luminance(background)
        contrast = (max(a, b)+0.05)/(min(a, b)+0.05)
        if contrast < 4.5:
            raise ValueError(f'Native pet text sample lacks contrast: {field} {contrast}')
        samples.append({'nativePreview': builder.record(path), 'field': field, 'samplePixel': list(point),
                        'sourceGlobal': symbols[field], 'nativeForegroundRgba': color,
                        'sampledBackgroundRgb': list(background), 'contrastRatio': contrast})
    path = HERE / 'palette-evidence.json'
    builder.save_json(path, {
        'schemaVersion': 1, 'sourceReferences': builder.record(HERE / 'manifest.json'),
        'sourceGlobalLiteralScope': root_scope, 'sourceSymbolicAssignments': assignments,
        'samples': samples, 'sampleThreshold': 4.5,
        'interpretation': 'Adjacent symbolic source stores and source global literals sampled against final native decoded backgrounds',
        'runtimeTextRenderingVerified': False, 'userVisualAccepted': False,
    }, check)
    return builder.record(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    check = args.check
    paths = {p: value for p, value in art.PATHS.items() if not args.controls_only or value[0] != 'pet-face'}
    source_path = HERE / 'manifest.json'
    sources = json.loads(source_path.read_bytes())
    records = {r['nativePath'].lower(): r for r in sources['resources']}
    if set(records) != {p.lower() for p in art.PATHS}:
        raise ValueError('Selected native paths differ from the decoded source evidence')
    if any(path in builder.PATHS and builder.PATHS[path] != value for path, value in art.PATHS.items()):
        raise ValueError('Pet controls conflict with an already registered renderer')
    package = (ROOT / sources['package']['file']).read_bytes()
    if builder.record(ROOT / sources['package']['file']) != sources['package']:
        raise ValueError('Source package changed')
    paint_paths = {k: builder.PAINTS[k] for k in ('panel', 'normal', 'hover', 'pressed')}
    paint_paths.update({k: p for k, p in art.PAINT_INPUTS.items() if not args.controls_only})
    paints = {k: Image.open(ROOT / p).convert('RGBA') for k, p in paint_paths.items()}
    font = Path('C:/Windows/Fonts/msyh.ttc')
    row_heights = [320 if max(f['nativeSize'][1] for f in records[p.lower()]['frames']) > 100 else 120 for p in paths]
    contact = Image.new('RGB', (1200, sum(row_heights)), '#ede6d4')
    offset_y = 0
    draw = ImageDraw.Draw(contact)
    items = []
    for row, (path, (kind, caption)) in enumerate(paths.items()):
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
                raise ValueError('Encoded pet candidate changed')
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
            if kind == 'pet-nav':
                alpha_key = f'{caption}-{index}'
            elif kind in ('pet-food-grid', 'pet-progress'):
                alpha_key = {'pet-food-grid': 'dlg_food', 'pet-progress': 'img_exp'}[kind]
            if alpha_key:
                original_alpha = art.source_alpha(alpha_key, image.size)
                if image.getchannel('A').tobytes() != original_alpha.tobytes():
                    raise ValueError('Functional alpha changed after native encoding')
            exports.append({**builder.record(target), 'index': index, 'nativeSize': list(image.size),
                            'frameOffset': frame['frameOffset'], 'pixelMode': frame['pixelMode'],
                            'alphaExtrema': list(image.getchannel('A').getextrema()),
                            'functionalAlphaSource': builder.record(ROOT / art.STRUCTURAL_ALPHA_INPUTS[alpha_key]) if alpha_key else None,
                            'functionalAlphaRetained': True if alpha_key else None})
        items.append({**builder.record(destination), 'nativePath': path, 'sourceSha256': evidence['sourceSha256'],
                      'sourceBindings': evidence['sourceBindings'], 'rendererKind': kind, 'caption': caption,
                      'captionEvidence': 'Read from native rasters and source declarations; runtime text surfaces remain blank',
                      'frames': exports, 'visualAccepted': False, 'nativeRuntimeVerified': False,
                      'derivedInputs': [builder.record(ROOT / art.PAINT_INPUTS[f'pet-face-{caption}']),
                                        builder.record((ROOT / art.PAINT_INPUTS[f'pet-face-{caption}']).with_suffix('.png.generation.json'))]
                                      if kind == 'pet-face' else [],
                      'emotionPacking': art.emotion_geometry(paints[f'pet-face-{caption}'], caption) if kind == 'pet-face' else None,
                      'emotionSecondSlot': {'brightnessFactor': 1.10, 'nativeGeometryRetained': True,
                                            'originalSubpixelPhaseEqualityVerified': False} if kind == 'pet-face' else None})
        offset_y += row_height
    preview = HERE / 'candidate' / 'contact-native.png'
    builder.save_image(preview, contact, check)
    emotion_preview = None
    if not args.controls_only:
        board = Image.new('RGB', (1000, 440), '#676b68')
        board_draw = ImageDraw.Draw(board)
        master_shas = {builder.record(ROOT / p)['sha256'] for p in art.PAINT_INPUTS.values()}
        if len(master_shas) != 5:
            raise ValueError('Five native emotion indices require five different original masters')
        native_hashes = set()
        for emotion in range(5):
            for phase in range(2):
                path = HERE / 'candidate' / 'decoded' / f'face{emotion}-{phase:02}.png'
                image = Image.open(path).convert('RGBA')
                native_hashes.add(builder.hashlib.sha256(image.tobytes()).hexdigest())
                x, y = emotion*200+15, phase*210+20
                enlarged = image.resize((136, image.height*4), Image.Resampling.NEAREST)
                board.paste(enlarged, (x, y), enlarged)
                board_draw.text((x, y+150), f'face{emotion} f{phase}', fill='white')
        if len(native_hashes) != 10:
            raise ValueError('Native emotion output contains repeated frames')
        emotion_path = HERE / 'candidate' / 'emotions-native.png'
        builder.save_image(emotion_path, board, check)
        emotion_preview = builder.record(emotion_path)
    palette = check_palette(sources, check)
    edge_evidence = None
    if not args.controls_only:
        edge_checker = load('pet_emotion_edges', (HERE / 'check-emotion-edges.py').relative_to(ROOT))
        edge_checker.build(check)
        edge_evidence = builder.record(HERE / 'edge-evidence.json')
    candidate = {
        'schemaVersion': 1, 'scope': 'Native pet control candidates; five mood indices keep distinct own emotion artwork',
        'sourceReferences': builder.record(source_path), 'renderer': builder.record(ROOT / 'scripts/native-ui-pet-controls-art.py'),
        'verificationScript': builder.record(Path(__file__).resolve()),
        'buildHelpers': builder.record(ROOT / 'scripts/build-native-login-art.py'),
        'codec': builder.record(ROOT / 'scripts/native-ui-format.py'),
        'paintInputs': [builder.record(ROOT / p) for p in paint_paths.values()],
        'font': {'family': 'Microsoft YaHei', 'sha256': builder.hashlib.sha256(font.read_bytes()).hexdigest()},
        'symbolFont': {'fileName': 'seguisym.ttf', 'sha256': builder.hashlib.sha256(Path(art.FONT_INPUTS['symbols']).read_bytes()).hexdigest()},
        'structuralAlphaInputs': [builder.record(ROOT / p) for p in art.STRUCTURAL_ALPHA_INPUTS.values()],
        'visualMappingAssumptions': art.VISUAL_MAPPING_ASSUMPTIONS,
        'paletteEvidence': palette,
        'emotionEdgeEvidence': edge_evidence,
        'sourceArtworkGeneration': [builder.record(ROOT / p) for p in art.ART_GENERATION_RECORDS] if not args.controls_only else [],
        'items': items, 'preview': builder.record(preview), 'nativeResources': len(items),
        'emotionPreview': emotion_preview,
        'sourcePositions': sum(len(item['frames']) for item in items),
        'functionalAlphaRetainedPositions': sum(f['functionalAlphaRetained'] is True for item in items for f in item['frames']),
        'nativeBuildInvokesImageModel': False, 'sourceArtworkNewGeneration': not args.controls_only,
        'includedEmotionCandidates': not args.controls_only, 'nativeGeometryRetained': True, 'nativeRuntimeVerified': False,
        'visualAccepted': False, 'installedToClient': False,
    }
    builder.save_json(HERE / 'candidate-manifest.json', candidate, check)
    print(json.dumps({'nativeResources': len(items), 'sourcePositions': candidate['sourcePositions'],
                      'nativeGeometryRetained': True, 'pixelReplay': check}))


if __name__ == '__main__':
    main()
