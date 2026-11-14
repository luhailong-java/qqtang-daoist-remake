"""Gate and register generated Mountain Guardian north and south walk cells."""
from importlib import util
from pathlib import Path
import argparse
import json

from PIL import Image, ImageDraw

MOTION = Path(__file__).resolve().parent.parent
ROOT = MOTION.parents[2]
spec = util.spec_from_file_location('walk_export', MOTION / 'daoist-child-west/export-diagnostics.py')
walk = util.module_from_spec(spec)
spec.loader.exec_module(walk)
record, read_json, save_json = walk.record, walk.read_json, walk.save_json
DIRECTIONS = {'north': (1, 'N'), 'south': (3, 'S')}


def preview(base, name, frames):
    board = Image.new('RGBA', (1280, 440), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 220, 1279, 439), fill='#173e36')
    draw.text((16, 12), f'Mountain Guardian / {name} walk / visual review pending', fill='#26463c')
    draw.text((16, 232), 'Same source order / dark background / no timing inferred', fill='#f6f0df')
    for i, frame in enumerate(frames):
        x = 16+i*210
        label = f"f{frame['sourceFrameIndex']}  112 / 64 / 48 / 32px"
        if frame.get('rasterImageShared'):
            label = f"f{frame['sourceFrameIndex']} (= f{frame['rasterAliasOfSourceFrameIndex']})  112 / 64 / 48 / 32px"
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
    parser = argparse.ArgumentParser()
    parser.add_argument('direction', choices=DIRECTIONS)
    name = parser.parse_args().direction
    group, direction = DIRECTIONS[name]
    expected = list(range(group*6, group*6+6))
    base = MOTION / f'mountain-guardian-{name}'
    walk.BASE = walk.helpers.BASE = base
    source_path = base / f'source-{name}-evidence.json'
    source = read_json(source_path)
    for key in ('directionEvidence', 'phaseBoard', 'lowerBodyBoard'):
        info = source[key]
        if record(ROOT / info['file']) != info:
            raise ValueError(f'Source board digest changed: {key}')
    positions = {p['frameIndex']: p for p in source['positions']}
    if list(positions) != expected or source['declaredCanvas'] != [100, 100]:
        raise ValueError('Unexpected source phase order or declared canvas')
    if source['sourceDirectionGroupIndex'] != group or any(len(p['layers']) != 7 for p in positions.values()):
        raise ValueError('Unexpected group or declared layer count')
    pairs = source['encodedLayerPairComparisons']['pairs']
    source_aliases = {b: a for a, b in (p['sourceFrameIndices'] for p in pairs if p['eightDeclaredLayersEqual'])}
    if len(pairs) != 15 or source_aliases != ({9: 6} if direction == 'N' else {21: 18}):
        raise ValueError('Eight-layer equivalence changed')

    layout_path = base / 'diagnostic-layout.json'
    layout = read_json(layout_path)
    (base / 'frames').mkdir(exist_ok=True)
    by_frame, generations = {}, []
    for mother in layout['mothers']:
        version = mother['version']
        path = base / f'mother-{version}.png'
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
                if frame in by_frame or frame in source_aliases:
                    raise ValueError(f'Invalid repeated frame selection {frame}')
                bounds = cells[pick['slot']]
                by_frame[frame] = walk.export_frame(image.crop(bounds), bounds, positions[frame], path, generation,
                                                    pick['hipX'])
    if len({f['sha256'] for f in by_frame.values()}) != len(expected)-len(source_aliases):
        raise ValueError('Missing or duplicate original diagnostic rasters')
    for frame, original in source_aliases.items():
        by_frame[frame] = {**by_frame[original], 'sourceFrameIndex': frame, 'sourceLayers': positions[frame]['layers'],
                           'sourceHeadLayer': positions[frame]['headLayer'], 'rasterImageShared': True,
                           'rasterAliasOfSourceFrameIndex': original,
                           'aliasEvidence': 'All eight declared source layers match encoded and geometry fields'}
    frames = [by_frame[i] for i in expected]
    save_json(base / 'manifest.json', {
        'schemaVersion': 1, 'characterId': 'mountain-guardian', 'sourceRoleId': 1, 'direction': direction,
        'sourceDirectionGroupIndex': group, 'sourceFrameOrder': expected, 'sourceDeclaredCanvas': [100, 100],
        'sourceEvidence': record(source_path), 'diagnosticLayout': record(layout_path),
        'sourceFrameDurationMs': None, 'originalLoop': None, 'nativeActorAnchor': None, 'frames': frames,
        'exportCanvas': [walk.OUT, walk.OUT], 'generatedMothers': generations, 'preview': preview(base, name, frames),
        'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False, 'motionContinuityConfirmed': False,
        'userReviewStatus': 'pending',
    })
    print(json.dumps({'direction': direction, 'sourcePositions': len(frames),
                      'uniqueCandidateRasters': len(expected)-len(source_aliases),
                      'nativeMothers': len(generations), 'alphaThreshold': 8, 'humanReview': 'pending'}))


if __name__ == '__main__':
    main()
