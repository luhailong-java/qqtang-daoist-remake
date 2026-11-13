"""Register exact generation evidence and export diagnostic-only walk samples."""
from pathlib import Path, PureWindowsPath
from hashlib import sha256
from datetime import datetime, timezone
import json
import sys

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from painted_crop_gate import validate_visible_boundaries

CONFIG = ROOT / 'config/image-generation.json'
EVIDENCE = ROOT / 'assets/characters/motion-generated/daoist-child/native-role9-evidence'
BOARD = EVIDENCE / 'group0-six-phase-board-5x.png'
SOURCE = EVIDENCE / 'group0-six-phase-board.json'
IDLE = ROOT / 'assets/characters/idle/v1/daoist-child-E.png'
SAMPLE_SIZE = 256
WORK_SIZE = 804
ROOT_SAMPLE = (128, 232)
SOURCE_BASELINE = 686
# Manually estimated hips x within each 724px cell. This is diagnostic placement.
HIP_X = [411, 378, 342, 373, 384, 403]
MOTHERS = ['a-v1', 'b-v1', 'f5-v2']
OBSERVATIONS = [
    'Passing pose, close boots, visible eye open.',
    'Foreground right shoe ahead; near right hand behind the hip.',
    'Front shoe stays near the baseline while the rear shoe rises.',
    'Passing pose and eye closed. Original 0/3 visible layers differ.',
    'Foreground shoe is left and planted, raised far shoe is right; empty hand forward.',
    'Screen-left heel rises and screen-right shoe lowers; layer ownership under the hem remains ambiguous.',
]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def read_json(path):
    return json.loads(path.read_bytes())


def save_json(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def ref(path):
    return {'file': relative(path), 'sha256': digest(path)}


def alpha_box(image):
    return image.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()


def register_mothers():
    target = read_json(CONFIG)
    generated = {}
    for version in MOTHERS:
        mother = BASE / f'mother-{version}.png'
        submission = BASE / f'submission-{version}.json'
        returned = BASE / f'result-{version}.json'
        sent = read_json(submission)['input']
        output = read_json(returned)
        with Image.open(mother) as im:
            if im.format != 'PNG' or im.mode != 'RGBA' or im.getchannel('A').getextrema()[0] != 0:
                raise ValueError(f'Native true alpha required: {mother}')
            validate_visible_boundaries(im, [(0, 0, *im.size)], threshold=8)
            width, height = im.size
        records = []
        for sent_path in sent['referenced_image_paths']:
            reference = ROOT / PureWindowsPath(sent_path).as_posix().split('/qqtang-daoist-remake/', 1)[1]
            records.append(ref(reference))
        prompt = sent['prompt']
        generation_record = mother.with_suffix('.png.generation.json')
        save_json(generation_record, {
            'schemaVersion': 1, **ref(mother), 'width': width, 'height': height, 'format': 'PNG',
            'art_source': 'host_image', 'route': 'builtin', 'tool': 'image_gen.imagegen',
            'configSource': ref(CONFIG), 'configSnapshot': target, 'exactPrompt': prompt,
            'submittedPromptSha256': sha256(prompt.encode('utf-8')).hexdigest(),
            'submittedParameters': {
                'model': None, 'quality': None, 'transparent_background': sent['transparent_background'],
                'referenced_image_paths': sent['referenced_image_paths'],
            },
            'references': records, 'submission': ref(submission), 'returnedMetadata': ref(returned),
            'actualModel': None, 'actualQuality': None,
            'actualParametersEvidence': 'Builtin returned no verifiable model/quality values.',
            'hostSource': output['hostSource'], 'returnedFields': output['returnedFields'],
            'hostFileModifiedTimeUtc': datetime.fromtimestamp(
                mother.stat().st_mtime, tz=timezone.utc).isoformat(),
            'timeEvidence': 'Native image file modification time preserved by Copy-Item; model-side time undisclosed.',
            'selectionStatus': 'alternate-single-frame-review' if version == 'f5-v2' else 'diagnostic-export-source',
            'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
        })
        generated[version] = ref(generation_record)
    return generated


def source_frames():
    data = read_json(SOURCE)
    if digest(BOARD) != data['boardSha256'] or data['selectedIndices'] != list(range(6)):
        raise ValueError('Source phase-board evidence mismatch')
    records = []
    for frame in data['records']:
        if frame['nativeCanvas'] != [100, 100] or frame['directionGroupIndex'] != 0:
            raise ValueError('Source frame geometry mismatch')
        layers = []
        for layer in frame['layers']:
            original = EVIDENCE / PureWindowsPath(layer['png']).name
            if digest(original) != layer['pngSha256']:
                raise ValueError(f'Layer evidence hash changed: {original}')
            layers.append({
                'layer': layer['layer'], 'sourceResource': layer['sourceResource'],
                'sourceDimgSha256': layer['sourceDimgSha256'],
                'sourceNativeSize': layer['nativeSize'], 'frameOffsetRaw': layer['frameOffset'],
                'encodedPixelSha256': layer['encodedPixelSha256'], 'reference': ref(original),
            })
        records.append(layers)
    return records


def paste_preview(background, image, x, y, size):
    resized = image.convert('RGBa').resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
    background.alpha_composite(resized, (x, y))


def lower_body_preview():
    board = Image.new('RGB', (1410, 720), '#f6f0df')
    draw = ImageDraw.Draw(board)
    inputs = []
    for version, row in (('a-v1', 0), ('b-v1', 1)):
        mother = BASE / f'mother-{version}.png'
        with Image.open(mother) as image:
            for column in range(3):
                rect = (724 * column + 150, 290, 724 * column + 620, 701)
                cell = image.crop(rect)
                cell.thumbnail((470, 325), Image.Resampling.LANCZOS)
                sample = Image.new('RGBA', cell.size, '#f6f0df')
                sample.alpha_composite(cell)
                board.paste(sample.convert('RGB'), (column * 470, 36 + row * 350))
                index = column + row * 3
                draw.text((column * 470 + 15, 14 + row * 350), f'f{index} lower body', fill='#26463c')
                inputs.append({**ref(mother), 'sourceRectLTRB': list(rect), 'sourceFrameIndex': index})
    target = BASE / 'lower-body-diagnostic.png'
    board.save(target)
    save_json(target.with_suffix('.png.source.json'), {
        **ref(target), 'derivedFrom': inputs, 'operation': 'diagnostic crops and composites',
        'newModelGeneration': False, 'userReviewStatus': 'pending',
    })
    return ref(target)


def run():
    source = source_frames()
    edit_reference = BASE / 'reference-f4-from-b-v1.png'
    parent = BASE / 'mother-b-v1.png'
    with Image.open(parent) as original, Image.open(edit_reference) as cropped:
        if original.crop((724, 0, 1448, 724)).tobytes() != cropped.tobytes():
            raise ValueError('Edit reference crop does not match its parent')
    save_json(edit_reference.with_suffix('.png.source.json'), {
        **ref(edit_reference), 'derivedFrom': ref(parent), 'sourceRectLTRB': [724, 0, 1448, 724],
        'operation': 'pixel-exact ownership cell crop used as builtin edit reference',
        'resampled': False, 'newModelGeneration': False,
    })
    generated = register_mothers()
    preview_dir = BASE / 'frames'
    preview_dir.mkdir(exist_ok=True)
    board = Image.new('RGBA', (1280, 460), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 230, 1279, 459), fill='#173e36')
    for y, fill, title in ((0, '#26463c', 'Daoist child / east walking / diagnostic'),
                           (230, '#f6f0df', 'Same source order / dark background / no timings')):
        draw.text((15, y+13), title, fill=fill)
    frames = []
    for version, start in (('a-v1', 0), ('b-v1', 3)):
        path = BASE / f'mother-{version}.png'
        with Image.open(path) as im:
            if im.size != (2172, 724):
                raise ValueError('Three explicitly measured 724px cells required')
            rects = [(i * 724, 0, (i + 1) * 724, 724) for i in range(3)]
            validate_visible_boundaries(im, rects, threshold=8)
            for i, rect in enumerate(rects):
                index = start + i
                cell = im.crop(rect)
                placement = (WORK_SIZE // 2 - HIP_X[index],
                             round(ROOT_SAMPLE[1] * WORK_SIZE / SAMPLE_SIZE) - SOURCE_BASELINE)
                box = alpha_box(cell)
                if box is None or box[0]+placement[0] < 0 or box[2]+placement[0] > WORK_SIZE:
                    raise ValueError(f'Invalid diagnostic placement for phase {index}')
                work = Image.new('RGBA', (WORK_SIZE, WORK_SIZE))
                work.paste(cell, placement)
                painted = work.convert('RGBa').resize(
                    (SAMPLE_SIZE, SAMPLE_SIZE), Image.Resampling.LANCZOS).convert('RGBA')
                validate_visible_boundaries(painted, [(0, 0, SAMPLE_SIZE, SAMPLE_SIZE)], threshold=8)
                target = preview_dir / f'phase-{index}.png'
                painted.save(target)
                record = {
                    **ref(target), 'sourceFrameIndex': index, 'width': SAMPLE_SIZE, 'height': SAMPLE_SIZE,
                    'sourceDirectionGroupIndex': 0, 'directionEvidence': 'nose points screen right',
                    'sourceDeclaredCanvas': [100, 100], 'sourceLayers': source[index],
                    'originalFrameDurationMs': None, 'nativeActorAnchor': None,
                    'derivedFrom': ref(path), 'generationRecord': generated[version],
                    'operation': {
                        'type': 'bounded-crop-and-diagnostic-registration',
                        'sourceRectLTRB': list(rect), 'sourceCellAlpha8BBox': list(box),
                        'placement': list(placement), 'workingCanvas': [WORK_SIZE, WORK_SIZE],
                        'sharedScale': SAMPLE_SIZE / WORK_SIZE, 'manualDiagnosticHipX': HIP_X[index],
                        'sourceDiagnosticBaseline': SOURCE_BASELINE,
                        'diagnosticAnchor': list(ROOT_SAMPLE),
                        'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False,
                    },
                    'alphaExtrema': list(painted.getchannel('A').getextrema()),
                    'outputAlpha8BBox': list(alpha_box(painted)),
                    'observations': OBSERVATIONS[index], 'userReviewStatus': 'pending',
                    'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
                }
                sidecar = target.with_suffix('.png.provenance.json')
                save_json(sidecar, record)
                frames.append({**record, 'provenance': ref(sidecar)})
                for y, fill in ((0, '#26463c'), (230, '#f6f0df')):
                    x = 16 + index * 210
                    draw.text((x, y+35), f'f{index}  112px and 64px', fill=fill)
                    paste_preview(board, painted, x, y+60, 112)
                    paste_preview(board, painted, x+112, y+108, 64)
    if len({frame['sha256'] for frame in frames}) != 6:
        raise ValueError('Expected six distinct exported samples')
    preview = BASE / 'review-light-dark.png'
    board.convert('RGB').save(preview)
    save_json(preview.with_suffix('.png.source.json'), {
        **ref(preview), 'frames': [ref(ROOT / f['file']) for f in frames],
        'operation': 'dual-background compositing and isotropic diagnostic resizing',
        'sizes': [112, 64], 'newModelGeneration': False, 'userReviewStatus': 'pending',
    })
    save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'status': 'six-diagnostic-walk-poses-human-gait-review-pending',
        'characterId': 'daoist-child', 'sourceRoleId': 9, 'direction': 'E',
        'sourceDirectionGroupIndex': 0, 'sourceFrameOrder': list(range(6)),
        'sourceDeclaredCanvas': [100, 100], 'sourceBoard': ref(BOARD), 'sourceEvidence': ref(SOURCE),
        'originalFrameDurationMs': None, 'originalLoop': None, 'nativeActorAnchor': None,
        'nativeHeadLayerIncludedInSourceBoard': False,
        'idleIdentityReference': ref(IDLE), 'exportCanvas': [256, 256],
        'frames': frames, 'preview': ref(preview), 'lowerBodyPreview': lower_body_preview(),
        'generatedMothers': generated,
        'f5Alternative': ref(BASE / 'mother-f5-v2.png'),
        'f5AlternativeNotes': 'Single-frame redraw changed head scale; current mother B provides consistent candidate scale.',
        'motionContinuityConfirmed': False, 'userReviewStatus': 'pending',
        'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
    })
    print(json.dumps({'sourceLayersVerified': 36, 'generationRecords': 3, 'diagnosticRgbaFrames': 6,
                      'allDistinct': True, 'transparentBordersThreshold': 8,
                      'runtimeAdopted': False, 'userReviewStatus': 'pending'}))


if __name__ == '__main__':
    run()
