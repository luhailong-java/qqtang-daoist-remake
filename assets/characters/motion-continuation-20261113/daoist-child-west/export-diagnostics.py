"""Export the original west-walk paint as six review-only RGBA frames."""
from importlib import util
from pathlib import Path
import json

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
OLD = ROOT / 'assets/characters/motion-continuation-20261112/moon-shadow-east'
spec = util.spec_from_file_location('pose_export_helpers', OLD / 'export-diagnostics.py')
helpers = util.module_from_spec(spec)
spec.loader.exec_module(helpers)
helpers.BASE = BASE
record, read_json, save_json = helpers.record, helpers.read_json, helpers.save_json
alpha_box, resize = helpers.alpha_box, helpers.uniform_resize

WORK = 804
OUT = 256
ROOT_POINT = (128, 232)
SOURCE_BASELINE = 674
NATIVE_LAYOUT = {'a-v1': (2188, 718), 'b-v1': (2172, 724)}
# Estimated x of each painted figure's hips within its cell, for diagnostic registration only.
HIP_X = (330, 337, 342, 347, 332, 319)
FRAMES = range(12, 18)


def export_frame(cell, bounds, source, mother, generation, hip):
    box = alpha_box(cell)
    placement = (WORK//2-hip, round(ROOT_POINT[1]*WORK/OUT)-SOURCE_BASELINE)
    if box is None or not (0 <= box[0]+placement[0] < box[2]+placement[0] <= WORK and
                           0 <= box[1]+placement[1] < box[3]+placement[1] <= WORK):
        raise ValueError(f"Unsafe diagnostic crop for source position {source['frameIndex']}")
    canvas = Image.new('RGBA', (WORK, WORK))
    canvas.paste(cell, placement)
    image = resize(canvas, (OUT, OUT))
    helpers.validate_visible_boundaries(image, [(0, 0, OUT, OUT)], threshold=8)
    if image.getchannel('A').getextrema() != (0, 255):
        raise ValueError('Diagnostic frame lacks the expected transparent and opaque pixels')
    path = BASE / 'frames' / f"phase-{source['frameIndex']:02d}.png"
    image.save(path)
    entry = {**record(path), 'derivedFrom': record(mother), 'generationRecord': generation,
             'sourceFrameIndex': source['frameIndex'], 'sourceDeclaredCanvas': [100, 100],
             'sourceLayers': source['layers'], 'sourceHeadLayer': source['headLayer'],
             'sourceFrameDurationMs': None, 'nativeActorAnchor': None, 'width': OUT, 'height': OUT,
             'alpha8BBox': list(alpha_box(image)), 'alphaExtrema': [0, 255],
             'operation': {'sourceRectLTRB': list(bounds), 'sourceCellAlpha8BBox': list(box),
                           'placement': list(placement), 'diagnosticHipX': hip,
                           'diagnosticSourceBaseline': SOURCE_BASELINE, 'workingCanvas': [WORK, WORK],
                           'sharedScale': OUT/WORK, 'diagnosticAnchor': list(ROOT_POINT),
                           'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False},
             'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False, 'userReviewStatus': 'pending'}
    sidecar = path.with_suffix('.png.provenance.json')
    save_json(sidecar, entry)
    return {**entry, 'provenance': record(sidecar)}


def preview(frames):
    board = Image.new('RGBA', (1280, 440), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 220, 1279, 439), fill='#173e36')
    draw.text((16, 12), 'Daoist child / west walk / visual review pending', fill='#26463c')
    draw.text((16, 232), 'Same source order / dark background / no timing inferred', fill='#f6f0df')
    for i, frame in enumerate(frames):
        x = 16+i*210
        with Image.open(ROOT / frame['file']) as image:
            for y, ink in ((0, '#26463c'), (220, '#f6f0df')):
                draw.text((x, y+35), f"f{frame['sourceFrameIndex']}  112 / 64 / 48 / 32px", fill=ink)
                board.alpha_composite(resize(image, (112, 112)), (x, y+60))
                board.alpha_composite(resize(image, (64, 64)), (x+124, y+55))
                board.alpha_composite(resize(image, (48, 48)), (x+132, y+118))
                board.alpha_composite(resize(image, (32, 32)), (x+140, y+166))
    path = BASE / 'review-light-dark.png'
    board.convert('RGB').save(path)
    save_json(path.with_suffix('.png.source.json'), {
        **record(path), 'sourcePositions': [{k: f[k] for k in ('sourceFrameIndex', 'file', 'sha256')} for f in frames],
        'operation': 'Dual-background 112px, 64px, 48px and 32px diagnostic composites',
        'newModelGeneration': False,
        'userReviewStatus': 'pending',
    })
    return record(path)


def main():
    evidence_path = BASE / 'source-west-evidence.json'
    source = read_json(evidence_path)
    for key in ('directionEvidence', 'allDirectionsEvidence', 'phaseBoard', 'lowerBodyBoard'):
        info = source[key]
        if record(ROOT / info['file']) != info:
            raise ValueError(f'Source board digest changed: {key}')
    positions = source['positions']
    if [p['frameIndex'] for p in positions] != list(FRAMES) or source['declaredCanvas'] != [100, 100]:
        raise ValueError('Unexpected source phase order or declared canvas')
    if source['sourceDirectionGroupIndex'] != 2 or any(len(p['layers']) != 6 for p in positions):
        raise ValueError('Unexpected group or declared layer count')
    pair_checks = source['encodedLayerPairComparisons']['pairs']
    if len(pair_checks) != 15 or any(p['sevenDeclaredLayersEqual'] for p in pair_checks):
        raise ValueError('Expected no repeated encoded seven-layer pose among source positions')

    (BASE / 'frames').mkdir(exist_ok=True)
    frames, generations = [], []
    for batch_index, version in enumerate(('a-v1', 'b-v1')):
        path = BASE / f'mother-{version}.png'
        with Image.open(path) as image:
            if image.size != NATIVE_LAYOUT[version] or image.mode != 'RGBA':
                raise ValueError('Unexpected native mother geometry or mode')
            if image.getchannel('A').getextrema() != (0, 255):
                raise ValueError('Mother lacks the expected transparent and opaque pixels')
            cells = [(image.width*i//3, 0, image.width*(i+1)//3, image.height) for i in range(3)]
            helpers.validate_visible_boundaries(image, cells, threshold=8)
            generation = helpers.generation_record(version, path, image)
            generations.append(generation)
            for cell_index, bounds in enumerate(cells):
                index = batch_index*3 + cell_index
                frames.append(export_frame(image.crop(bounds), bounds, positions[index], path, generation, HIP_X[index]))
    if len({f['sha256'] for f in frames}) != len(FRAMES):
        raise ValueError('Expected six distinct diagnostic rasters')

    save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'characterId': 'daoist-child', 'sourceRoleId': 9, 'direction': 'W',
        'sourceDirectionGroupIndex': 2, 'sourceFrameOrder': list(FRAMES), 'sourceDeclaredCanvas': [100, 100],
        'sourceEvidence': record(evidence_path), 'sourceFrameDurationMs': None, 'originalLoop': None,
        'nativeActorAnchor': None, 'frames': frames, 'exportCanvas': [OUT, OUT],
        'generatedMothers': generations, 'preview': preview(frames), 'visualAccepted': False,
        'runtimeAdopted': False, 'accepted': False, 'motionContinuityConfirmed': False, 'userReviewStatus': 'pending',
    })
    print(json.dumps({'sourcePositions': len(FRAMES), 'uniqueCandidateRasters': len(frames),
                      'nativeMothers': len(generations), 'alphaThreshold': 8, 'humanReview': 'pending'}))


if __name__ == '__main__':
    main()
