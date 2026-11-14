"""Encode/replay all112 shop-extra candidates without install or client execution."""
import argparse
import hashlib
from importlib import util
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ART = module('shopextra_export_art', 'scripts/native-ui-shopextra-art.py')
HELP = module('shopextra_export_helpers', 'assets/native-client-ui/common-reference/export-common.py')
CODEC = HELP.CODEC
FONT = Path('C:/Windows/Fonts/msyh.ttc')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def alpha_summary(alpha):
    box = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
    return {'sha256': sha(alpha.tobytes()), 'extrema': list(alpha.getextrema()),
            'alpha8BBoxXYXY': list(box) if box else None}


def check_nonpixels(before, after, metadata):
    a, b = bytearray(before), bytearray(after)
    for frame in metadata['frames']:
        if frame['empty']:
            continue
        start, size = frame['pixelDataOffset'], frame['pixelByteLength']
        a[start:start + size], b[start:start + size] = bytes(size), bytes(size)
    if a != b:
        raise ValueError('Shop-extra native header/frame/offset or other nonpixel bytes changed')


def alpha_reason(family):
    if family in ('role-name', 'glyph', 'digit', 'point'):
        return 'Own font/dot raster replaces old glyph alpha inside the complete source frame; no old letter mask is retained'
    if family == 'category-icon':
        return 'Own small category glyph replaces the old decorative silhouette; native crop/offset/hit rectangle remain exact'
    if family == 'badge':
        return 'Own jade/cloud badge replaces legacy flame/letter design; the native overlay frame and offset remain exact'
    if family == 'lucky-button':
        return 'Own scroll-seal surface replaces the old bear-head cosmetic silhouette; source state slots and widget geometry remain exact'
    if family == 'egg-title':
        return 'Own title lettering and eight distinct gloss samples replace old glyph/spark alpha; source raw slot order retained, native timing unknown'
    if family in ('lucky-machine', 'lucky-tip'):
        return 'Own cosmetic title/chest illustration removes old glyph/NPC silhouette; original native crop/offset and proven live reward/button positions retained'
    if family == 'hammer-icon':
        return 'Existing own gold-hammer PNG uniformly resampled into original tiny status-symbol frame'
    raise ValueError('Unclassified whole-frame cosmetic alpha redraw')


def state_observation(family, index):
    if family in ('button4', 'hammer-slot', 'lucky-button'):
        appearance = ('base surface', 'gray dim surface', 'bright surface', 'depressed surface')[index]
    elif family in ('button3', 'stack3'):
        appearance = ('base surface', 'bright surface', 'depressed surface')[index]
    elif family == 'security-radio':
        appearance = ('hollow colored center', 'gray filled center', 'bright filled center', 'filled center')[index]
    elif family == 'currency-radio':
        appearance = ('base category surface', 'bright category surface')[index]
    elif family == 'tab-dark-paper':
        appearance = ('dark source tab', 'light source tab')[index]
    elif family == 'tab-paper-jade':
        appearance = ('short light source tab', 'taller colored source tab')[index]
    elif family == 'egg-title':
        appearance = f'source title flash position {index}; own gloss sample {index}'
    elif family == 'lucky-lights':
        appearance = f'exact source sparse bulb mask position {index}'
    else:
        appearance = 'single stored raster'
    return {'sourceRasterAppearance': appearance, 'sourceSlotOrderPreserved': True,
            'runtimeStateOrDurationVerified': False}


def previews(resources, check):
    result = []
    font = ImageFont.load_default(size=14)
    for page in range(math.ceil(len(resources) / 8)):
        subset = resources[page * 8:(page + 1) * 8]
        heights = []
        for item in subset:
            cell = max(92, min(340, max(frame['height'] for frame in item['frames']) * 2 + 24))
            heights.append(28 + 2 * math.ceil(len(item['frames']) / 4) * cell)
        board = Image.new('RGB', (1500, sum(heights)), '#eae3d0')
        draw, y = ImageDraw.Draw(board), 0
        for item, height in zip(subset, heights):
            rows = math.ceil(len(item['frames']) / 4)
            half = (height - 28) // 2
            cell = half // rows
            draw.text((8, y + 4), item['nativePath'] + ' / native candidate / pending review', font=font, fill='#214b3c')
            draw.rectangle((0, y + 28 + half, 1499, y + height - 1), fill='#193f35')
            for frame in item['frames']:
                with Image.open(ROOT / frame['file']) as image:
                    factor = min(2, 350 / image.width, (cell - 22) / image.height)
                    picture = HELP.scaled(image, tuple(max(1, round(axis * factor)) for axis in image.size))
                index = frame['index']
                x, top = 8 + index % 4 * 372, y + 28 + index // 4 * cell
                for top_y, ink in ((top, '#214b3c'), (top + half, '#fff3d5')):
                    draw.text((x, top_y), f"raw{index} off{tuple(frame['frameOffset'])}", font=font, fill=ink)
                    board.paste(picture, (x, top_y + 20), picture)
            y += height
        path = HERE / f'candidate-all-states-{page + 1:02}.png'
        HELP.png(path, board, check)
        result.append({**record(path), 'runtimeScreenshot': False,
                       'operation': 'Actual native-mode-decoded candidate frames on light/dark diagnostic grounds'})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    source_path = HERE / 'manifest.json'
    source = json.loads(source_path.read_bytes())
    by_path = {r['nativePath']: r for r in source['resources']}
    if set(by_path) != set(ART.PATHS) or len(ART.PATHS) != 112:
        raise ValueError('Full112 native shop-extra source/renderer scope differs')
    dynamic_path = HERE / 'dynamic-layout-evidence.json'
    dynamic = json.loads(dynamic_path.read_bytes())
    if {r['nativePath'] for r in dynamic['resources']} != set(by_path):
        raise ValueError('Independent source layout audit scope differs')
    role_path = ROOT / 'assets/native-client-ui/room-extra-reference/roster-mapping-audit.json'
    roles = ART.role_entries()
    if len(roles) != 18:
        raise ValueError('Concrete shop18 role allocation differs')
    for entry in roles.values():
        for key in ('portrait', 'portraitSourceRecord', 'master', 'masterSourceRecord'):
            expected = entry[key]
            if record(ROOT / expected['file']) != expected:
                raise ValueError('Own role image/provenance changed')
    package_path = ROOT / source['sourcePackage']['file']
    if record(package_path) != source['sourcePackage']:
        raise ValueError('Pinned packed source changed')
    package = package_path.read_bytes()
    paint_inputs = {key: filename for key, filename in HELP.ROOT_PAINTS.items() if key in ('panel', 'normal', 'hover', 'pressed')}
    paint_inputs.update(ART.PAINT_INPUTS)
    paints = {key: Image.open(ROOT / filename).convert('RGBA') for key, filename in paint_inputs.items()}
    resources = []
    for native, (kind, caption) in ART.PATHS.items():
        src, spec = by_path[native], ART.SPECS[kind]
        raw, _ = CODEC.reader.unpack_resource(package, src['packageEntry'])
        if sha(raw) != src['sourceSha256']:
            raise ValueError('Native shop-extra source SHA differs')
        pictures = {f['index']: ART.render(kind, caption, f['index'], (f['width'], f['height']), paints,
                                         FONT, HELP.nine_slice, HELP.scaled)
                    for f in src['metadata']['frames'] if not f['empty']}
        output, metadata, decoded = CODEC.replace_frames(raw, pictures)
        check_nonpixels(raw, output, metadata)
        if output == raw:
            raise ValueError('A selected source path has no own replacement pixels')
        patch = HERE / 'patch' / native
        if check:
            if patch.read_bytes() != output:
                raise ValueError('Native shop-extra byte replay differs')
        else:
            patch.parent.mkdir(parents=True, exist_ok=True)
            patch.write_bytes(output)
        frames = []
        for frame, picture in decoded:
            index = frame['index']
            before_record = src['frames'][index]
            with Image.open(ROOT / before_record['file']) as original:
                before_alpha = original.getchannel('A')
            after_alpha = picture.getchannel('A')
            difference = ImageChops.difference(before_alpha, after_alpha)
            box = difference.getbbox()
            if spec['alpha'] == 'source' and box is not None:
                raise ValueError('A declared exact structural shop alpha changed after native encoding')
            if after_alpha.getextrema()[1] < 8:
                raise ValueError('Own native shop frame lost all visible pixels')
            path = HERE / 'decoded' / f"{native.removeprefix('object/ui/').removesuffix('.img').replace('/', '__')}-{index:02}.png"
            HELP.png(path, picture, check)
            start = frame['pixelDataOffset']
            if CODEC.encode_pixels(picture, frame['pixelMode']) != output[start:start + frame['pixelByteLength']]:
                raise ValueError('Native shop pixel decode/re-encode roundtrip differs')
            frames.append({**record(path), 'index': index, 'sourceFrameIndex': index,
                           'width': frame['width'], 'height': frame['height'], 'pixelMode': frame['pixelMode'],
                           'frameOffset': frame['frameOffset'], 'decodedRgbaSha256': sha(picture.tobytes()),
                           'alphaPolicy': spec['alpha'], 'sourceAlphaExactlyPreserved': box is None,
                           'sourceAlpha': alpha_summary(before_alpha), 'candidateAlpha': alpha_summary(after_alpha),
                           'changedAlphaBBoxXYXY': list(box) if box else None,
                           'changedAlphaPixelCount': sum(v != 0 for v in difference.tobytes()),
                           'alphaRedrawRoiXYXY': [0, 0, frame['width'], frame['height']] if spec['alpha'] == 'redraw' else None,
                           'alphaRedrawReason': alpha_reason(spec['family']) if spec['alpha'] == 'redraw' else None,
                           'stateObservation': state_observation(spec['family'], index),
                           'sourceFrameDurationMs': None})
        resource = {**record(patch), 'nativePath': native, 'rendererKind': kind, 'family': spec['family'],
                    'caption': caption, 'sourceSha256': src['sourceSha256'], 'sourcePacked': True, 'sourceLoose': False,
                    'frames': frames, 'allNonPixelBytesIdenticalToSource': True,
                    'sourceAlphaPolicy': spec['alpha'], 'nativeRuntimeVerified': False, 'visualAccepted': False}
        if spec['family'] in ('character-banner', 'role-name'):
            role_id = int(caption) if spec['family'] == 'character-banner' else int(Path(native).stem.removeprefix('rolename'))
            entry = roles[role_id]
            resource['verifiedProjectRoleAllocation'] = {key: entry[key] for key in (
                'sourceRoleId', 'nativeAlias', 'identityId', 'projectName', 'uiShortName',
                'portrait', 'portraitSourceRecord', 'master', 'masterSourceRecord')}
            if spec['family'] == 'character-banner':
                resource['ownPortraitDerivative'] = {
                    'input': entry['portrait'], 'inputSize': [256, 256],
                    'cropXYXY': [0, 72, 256, 216], 'resampleSize': [73, 41],
                    'compositeAt': [42, -2], 'clipCanvasSize': [116, 35],
                    'operation': 'Existing verified own portrait facial band, premultiplied-alpha resize and fixed native banner clipping',
                    'nativeSourceGeometryChanged': False, 'worldAttachmentClaim': False}
        resources.append(resource)
    positions = sum(len(r['frames']) for r in resources)
    structural = sum(f['alphaPolicy'] == 'source' for r in resources for f in r['frames'])
    cosmetic = positions - structural
    if (len(resources), positions, structural, cosmetic) != (112, 168, 98, 70):
        raise ValueError('Full shop source positions/alpha-policy counts changed')
    previews_record = previews(resources, check)
    result = {'schemaVersion': 1, 'scope': 'All112 remaining native shop images,168 original positions; excludes existing20 controls',
              'sourceReferences': record(source_path), 'items': resources,
              'referenceContracts': [record(ROOT / filename) for filename in ART.REFERENCE_INPUTS],
              'nativeResourceCount': len(resources), 'sourceFramePositions': positions,
              'exactStructuralAlphaPolicyPositions': structural, 'cosmeticAlphaRedrawPositions': cosmetic,
              'actualExactAlphaPositions': sum(f['sourceAlphaExactlyPreserved'] for r in resources for f in r['frames']),
              'allSourceAlphaUnchanged': False, 'allNonpixelBytesPreserved': True,
              'confirmedCharacterBannerCount': 18, 'confirmedRoleNameCount': 18,
              'renderer': record(ROOT / 'scripts/native-ui-shopextra-art.py'), 'exporter': record(Path(__file__)),
              'captureScript': record(HERE / 'capture-source.py'), 'nativeCodec': record(ROOT / 'scripts/native-ui-format.py'),
              'paintInputs': [{'purpose': key, **record(ROOT / filename)} for key, filename in paint_inputs.items()],
              'structuralAlphaInputs': [{'purpose': key, **record(ROOT / filename)} for key, filename in ART.STRUCTURAL_ALPHA_INPUTS.items()],
              'font': {'family': 'Microsoft YaHei', 'sourcePath': str(FONT), 'sha256': sha(FONT.read_bytes())},
              'previews': previews_record, 'visualMappingAssumptions': ART.VISUAL_MAPPING_ASSUMPTIONS,
              'newModelGeneration': False, 'originalColorOrGlyphPixelsReused': False,
              'sourceTimingVerified': False, 'nativeRuntimeVerified': False, 'visualAccepted': False,
              'installedToClient': False, 'allShopUiOrRuntimeTextComplete': False}
    HELP.write_json(HERE / 'candidate-manifest.json', result, check)
    print(json.dumps({'resources': len(resources), 'positions': positions, 'exactStructuralAlpha': structural,
                      'cosmeticAlphaRedraws': cosmetic, 'roleBanners': 18, 'roleNames': 18,
                      'allNonpixelBytesIdentical': True, 'nativeReplay': check, 'installed': False}))


if __name__ == '__main__':
    main()
