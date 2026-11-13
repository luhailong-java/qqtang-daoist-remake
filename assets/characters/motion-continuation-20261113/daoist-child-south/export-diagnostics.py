"""Register the two original south-walk strips for human review."""
from importlib import util
from pathlib import Path
import json

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
spec = util.spec_from_file_location('walk_export', BASE.parent / 'daoist-child-west/export-diagnostics.py')
walk = util.module_from_spec(spec)
spec.loader.exec_module(walk)
walk.BASE = walk.helpers.BASE = BASE
record, read_json, save_json = walk.record, walk.read_json, walk.save_json
FRAMES = list(range(18, 24))
NATIVE_LAYOUT = {'a-v2': (2172, 724), 'b-v2': (2172, 724)}
SOURCE_BASELINES = {'a-v2': 693, 'b-v2': 682}
# Estimated centers at the belt, in each generated cell.
HIP_X = (353, 351, 352, 341, 341, 343)


def preview(frames):
    board = Image.new('RGBA', (1280, 440), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 220, 1279, 439), fill='#173e36')
    draw.text((16, 12), 'Daoist child / south walk / visual review pending', fill='#26463c')
    draw.text((16, 232), 'Same source order / dark background / no timing inferred', fill='#f6f0df')
    for i, frame in enumerate(frames):
        x = 16+i*210
        with Image.open(ROOT / frame['file']) as image:
            for y, ink in ((0, '#26463c'), (220, '#f6f0df')):
                draw.text((x, y+35), f"f{frame['sourceFrameIndex']}  112 / 64 / 48 / 32px", fill=ink)
                for size, dx, dy in ((112, 0, 60), (64, 124, 55), (48, 132, 118), (32, 140, 166)):
                    board.alpha_composite(walk.resize(image, (size, size)), (x+dx, y+dy))
    path = BASE / 'review-light-dark.png'
    board.convert('RGB').save(path)
    save_json(path.with_suffix('.png.source.json'), {
        **record(path), 'sourcePositions': [{k: f[k] for k in ('sourceFrameIndex', 'file', 'sha256')} for f in frames],
        'operation': 'Dual-background 112px, 64px, 48px and 32px diagnostic composites',
        'newModelGeneration': False, 'userReviewStatus': 'pending',
    })
    return record(path)


def main():
    source_path = BASE / 'source-south-evidence.json'
    source = read_json(source_path)
    for key in ('directionEvidence', 'phaseBoard', 'lowerBodyBoard'):
        info = source[key]
        if record(ROOT / info['file']) != info:
            raise ValueError(f'Source board digest changed: {key}')
    positions = source['positions']
    if [p['frameIndex'] for p in positions] != FRAMES or source['declaredCanvas'] != [100, 100]:
        raise ValueError('Unexpected source phase order or declared canvas')
    if source['sourceDirectionGroupIndex'] != 3 or any(len(p['layers']) != 6 for p in positions):
        raise ValueError('Unexpected group or declared layer count')
    pairs = source['encodedLayerPairComparisons']['pairs']
    if len(pairs) != 15 or any(p['sevenDeclaredLayersEqual'] for p in pairs):
        raise ValueError('Expected six distinct seven-layer source positions')

    (BASE / 'frames').mkdir(exist_ok=True)
    frames, generations = [], []
    for batch, (version, layout) in enumerate(NATIVE_LAYOUT.items()):
        path = BASE / f'mother-{version}.png'
        with Image.open(path) as image:
            if image.size != layout or image.mode != 'RGBA' or image.getchannel('A').getextrema() != (0, 255):
                raise ValueError('Unexpected native mother geometry or transparency')
            cells = [(image.width*i//3, 0, image.width*(i+1)//3, image.height) for i in range(3)]
            walk.helpers.validate_visible_boundaries(image, cells, threshold=8)
            generation = walk.helpers.generation_record(version, path, image)
            generations.append(generation)
            walk.SOURCE_BASELINE = SOURCE_BASELINES[version]
            for slot, bounds in enumerate(cells):
                index = batch*3+slot
                frames.append(walk.export_frame(image.crop(bounds), bounds, positions[index], path, generation,
                                                HIP_X[index]))
    if len({f['sha256'] for f in frames}) != len(FRAMES):
        raise ValueError('Expected six distinct diagnostic rasters')
    save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'characterId': 'daoist-child', 'sourceRoleId': 9, 'direction': 'S',
        'sourceDirectionGroupIndex': 3, 'sourceFrameOrder': FRAMES, 'sourceDeclaredCanvas': [100, 100],
        'sourceEvidence': record(source_path), 'sourceFrameDurationMs': None, 'originalLoop': None,
        'nativeActorAnchor': None, 'frames': frames, 'exportCanvas': [walk.OUT, walk.OUT],
        'generatedMothers': generations, 'preview': preview(frames), 'visualAccepted': False,
        'runtimeAdopted': False, 'accepted': False, 'motionContinuityConfirmed': False, 'userReviewStatus': 'pending',
    })
    print(json.dumps({'sourcePositions': len(FRAMES), 'uniqueCandidateRasters': len(frames),
                      'nativeMothers': len(generations), 'alphaThreshold': 8, 'humanReview': 'pending'}))


if __name__ == '__main__':
    main()
