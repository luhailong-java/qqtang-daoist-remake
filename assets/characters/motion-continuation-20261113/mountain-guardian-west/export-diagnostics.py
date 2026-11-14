"""Gate and register the original Mountain Guardian west-walk drawings."""
from importlib import util
from pathlib import Path
import json

from PIL import Image, ImageDraw

MOTION = Path(__file__).resolve().parent.parent
ROOT = MOTION.parents[2]
spec = util.spec_from_file_location('walk_export', MOTION / 'daoist-child-west/export-diagnostics.py')
walk = util.module_from_spec(spec)
spec.loader.exec_module(walk)
record, read_json, save_json = walk.record, walk.read_json, walk.save_json
BASE = Path(__file__).resolve().parent
FRAMES = list(range(12, 18))


def preview(base, frames):
    board = Image.new('RGBA', (1280, 440), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 220, 1279, 439), fill='#173e36')
    draw.text((16, 12), 'Mountain Guardian / west walk / visual review pending', fill='#26463c')
    draw.text((16, 232), 'Same source order / dark background / no timing inferred', fill='#f6f0df')
    for i, frame in enumerate(frames):
        x = 16+i*210
        label = f"f{frame['sourceFrameIndex']}  112 / 64 / 48 / 32px"
        with Image.open(ROOT / frame['file']) as image:
            for y, ink in ((0, '#26463c'), (220, '#f6f0df')):
                draw.text((x, y+35), label, fill=ink)
                for size, dx, dy in ((112, 0, 60), (64, 124, 55), (48, 132, 118), (32, 140, 166)):
                    board.alpha_composite(walk.resize(image, (size, size)), (x+dx, y+dy))
    path = base / 'review-light-dark.png'
    board.convert('RGB').save(path)
    save_json(path.with_suffix('.png.source.json'), {
        **record(path), 'sourcePositions': [{k: f[k] for k in ('sourceFrameIndex', 'file', 'sha256')} for f in frames],
        'operation': 'Dual-background 112px, 64px, 48px and 32px diagnostic composites',
        'newModelGeneration': False, 'userReviewStatus': 'pending',
    })
    return record(path)


def main():
    walk.BASE = walk.helpers.BASE = BASE
    source_path = BASE / 'source-west-evidence.json'
    source = read_json(source_path)
    for key in ('directionEvidence', 'phaseBoard', 'lowerBodyBoard'):
        info = source[key]
        if record(ROOT / info['file']) != info:
            raise ValueError(f'Source board digest changed: {key}')
    positions = {p['frameIndex']: p for p in source['positions']}
    if list(positions) != FRAMES or source['declaredCanvas'] != [100, 100]:
        raise ValueError('Unexpected source phase order or declared canvas')
    if source['sourceDirectionGroupIndex'] != 2 or any(len(p['layers']) != 7 for p in positions.values()):
        raise ValueError('Unexpected group or declared layer count')
    pairs = source['encodedLayerPairComparisons']['pairs']
    if len(pairs) != 15 or any(p['eightDeclaredLayersEqual'] for p in pairs):
        raise ValueError('Expected six distinct eight-layer source positions')

    layout_path = BASE / 'diagnostic-layout.json'
    layout = read_json(layout_path)
    (BASE / 'frames').mkdir(exist_ok=True)
    by_frame, generations = {}, []
    for mother in layout['mothers']:
        version = mother['version']
        path = BASE / f'mother-{version}.png'
        with Image.open(path) as image:
            if list(image.size) != mother['nativeSize'] or image.mode != 'RGBA' or image.getchannel('A').getextrema() != (0, 255):
                raise ValueError('Unexpected native mother geometry or transparency')
            cells = [(image.width*i//3, 0, image.width*(i+1)//3, image.height) for i in range(3)]
            walk.helpers.validate_visible_boundaries(image, cells, threshold=8)
            generation = walk.helpers.generation_record(version, path, image)
            generations.append(generation)
            walk.SOURCE_BASELINE = mother['diagnosticBaseline']
            walk.WORK = mother['workingCanvas']
            for pick in mother['picks']:
                frame = pick['frame']
                if frame in by_frame:
                    raise ValueError(f'Invalid repeated frame selection {frame}')
                bounds = cells[pick['slot']]
                by_frame[frame] = walk.export_frame(image.crop(bounds), bounds, positions[frame], path, generation,
                                                    pick['hipX'])
    if len({f['sha256'] for f in by_frame.values()}) != len(FRAMES):
        raise ValueError('Missing or duplicate original diagnostic rasters')
    frames = [by_frame[i] for i in FRAMES]
    save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'characterId': 'mountain-guardian', 'sourceRoleId': 1, 'direction': 'W',
        'sourceDirectionGroupIndex': 2, 'sourceFrameOrder': FRAMES, 'sourceDeclaredCanvas': [100, 100],
        'sourceEvidence': record(source_path), 'diagnosticLayout': record(layout_path),
        'sourceFrameDurationMs': None, 'originalLoop': None, 'nativeActorAnchor': None, 'frames': frames,
        'exportCanvas': [walk.OUT, walk.OUT], 'generatedMothers': generations, 'preview': preview(BASE, frames),
        'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False, 'motionContinuityConfirmed': False,
        'userReviewStatus': 'pending',
    })
    print(json.dumps({'direction': 'W', 'sourcePositions': len(frames),
                      'uniqueCandidateRasters': len(FRAMES),
                      'nativeMothers': len(generations), 'alphaThreshold': 8, 'humanReview': 'pending'}))


if __name__ == '__main__':
    main()
