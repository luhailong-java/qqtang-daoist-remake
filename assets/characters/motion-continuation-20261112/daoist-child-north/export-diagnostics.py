"""Export a review-only north walk. Use the verified seven-layer f6/f9 alias."""
from importlib import util
from pathlib import Path
from hashlib import sha256
import json
import sys

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from painted_crop_gate import validate_visible_boundaries

helper_file = BASE.parent / 'moon-shadow-east/export-diagnostics.py'
spec = util.spec_from_file_location('pose_export_helpers', helper_file)
helpers = util.module_from_spec(spec)
spec.loader.exec_module(helpers)
record, read_json, save_json = helpers.record, helpers.read_json, helpers.save_json
alpha_box, resize = helpers.alpha_box, helpers.uniform_resize

WORK = 804
OUT = 256
ROOT_POINT = (128, 232)
SOURCE_BASELINE = 678
# Estimated centers at the belt from the actual illustrations.
PICKS = [('a-v1', 0, 6, 370), ('a-v1', 1, 7, 376), ('a-v1', 2, 8, 370),
         ('b-v1', 1, 10, 380), ('b-v1', 2, 11, 382)]


def main():
    source_path = BASE / 'source-north-evidence.json'
    source = read_json(source_path)
    for key in ('directionEvidence', 'phaseBoard', 'lowerBodyBoard'):
        info = source[key]
        if record(ROOT / info['file']) != info:
            raise ValueError('Source board digest changed')
    positions = source['positions']
    if [phase['frameIndex'] for phase in positions] != list(range(6, 12)) or source['declaredCanvas'] != [100, 100]:
        raise ValueError('Unexpected source frame layout')
    pair = source['encodedLayerPairComparison']
    if pair['sourceFrameIndices'] != [6, 9] or len(pair['sameByLayer']) != 7 or not all(pair['sameByLayer'].values()):
        raise ValueError('Native f6/f9 encoded-layer equivalence changed')
    destination = BASE / 'frames'
    destination.mkdir(exist_ok=True)
    by_frame, generations = {}, {}
    for batch in ('a-v1', 'b-v1'):
        path = BASE / f'mother-{batch}.png'
        with Image.open(path) as image:
            if image.size != (2172, 724) or image.mode != 'RGBA' or image.getchannel('A').getextrema() != (0, 255):
                raise ValueError('Unexpected native mother PNG geometry or alpha')
            cells = [(i*724, 0, (i+1)*724, 724) for i in range(3)]
            validate_visible_boundaries(image, cells, threshold=8)
            # Shared recorder reads BASE to resolve exact inputs and native-output metadata.
            helpers.BASE = BASE
            generation = helpers.generation_record(batch, path, image)
            generations[batch] = generation
            for version, slot, frame, hip in PICKS:
                if version != batch:
                    continue
                rect = cells[slot]
                cell = image.crop(rect)
                box = alpha_box(cell)
                placement = (WORK//2-hip, round(ROOT_POINT[1]*WORK/OUT)-SOURCE_BASELINE)
                if box is None or not (0 <= box[0]+placement[0] < box[2]+placement[0] <= WORK and
                                       0 <= box[1]+placement[1] < box[3]+placement[1] <= WORK):
                    raise ValueError(f'Unsafe diagnostic crop for native position {frame}')
                work = Image.new('RGBA', (WORK, WORK))
                work.paste(cell, placement)
                sample = resize(work, (OUT, OUT))
                validate_visible_boundaries(sample, [(0, 0, OUT, OUT)], threshold=8)
                target = destination / f'phase-{frame:02d}.png'
                sample.save(target)
                meta = {**record(target), 'derivedFrom': record(path), 'generationRecord': generation,
                        'sourceFrameIndex': frame, 'sourceDeclaredCanvas': [100, 100],
                        'sourceLayers': positions[frame-6]['layers'],
                        'sourceHeadLayer': source['headLayerMetadata']['frames'][frame-6],
                        'sourceFrameDurationMs': None, 'nativeActorAnchor': None,
                        'width': OUT, 'height': OUT, 'alpha8BBox': list(alpha_box(sample)),
                        'alphaExtrema': list(sample.getchannel('A').getextrema()),
                        'operation': {'sourceRectLTRB': list(rect), 'sourceCellAlpha8BBox': list(box),
                                      'placement': list(placement), 'diagnosticHipX': hip,
                                      'diagnosticSourceBaseline': SOURCE_BASELINE, 'workingCanvas': [WORK, WORK],
                                      'sharedScale': OUT/WORK, 'diagnosticAnchor': list(ROOT_POINT),
                                      'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False},
                        'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
                        'userReviewStatus': 'pending'}
                sidecar = target.with_suffix('.png.provenance.json')
                save_json(sidecar, meta)
                by_frame[frame] = {**meta, 'provenance': record(sidecar)}

    # Keep both source positions in order; a single exact source-equivalent diagnostic raster serves them.
    by_frame[9] = {**by_frame[6], 'sourceFrameIndex': 9, 'sourceLayers': positions[3]['layers'],
                   'sourceHeadLayer': source['headLayerMetadata']['frames'][3],
                   'rasterAliasOfSourceFrameIndex': 6, 'rasterImageShared': True,
                   'aliasEvidence': 'All seven declared layers match encoded bytes, frame offsets and sizes'}
    frames = [by_frame[i] for i in range(6, 12)]
    if len({frame['sha256'] for frame in frames}) != 5:
        raise ValueError('Expected five different diagnostic rasters across six source positions')

    board = Image.new('RGBA', (1280, 440), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 220, 1279, 439), fill='#173e36')
    draw.text((16, 12), 'Daoist child / north walk / visual review pending', fill='#26463c')
    draw.text((16, 232), 'Same source order / dark background / f9 shares f6', fill='#f6f0df')
    for offset, meta in enumerate(frames):
        x = 16 + offset * 210
        with Image.open(ROOT / meta['file']) as sample:
            for y, ink in ((0, '#26463c'), (220, '#f6f0df')):
                label = f"f{meta['sourceFrameIndex']}  112px / 64px"
                if offset == 3:
                    label = 'f9 (= f6)  112px / 64px'
                draw.text((x, y+35), label, fill=ink)
                board.alpha_composite(resize(sample, (112, 112)), (x, y+60))
                board.alpha_composite(resize(sample, (64, 64)), (x+112, y+108))
    preview = BASE / 'review-light-dark.png'
    board.convert('RGB').save(preview)
    save_json(preview.with_suffix('.png.source.json'), {
        **record(preview), 'sourcePositions': [{k: f[k] for k in ('sourceFrameIndex', 'file', 'sha256')} for f in frames],
        'operation': 'Dual-background 112px and 64px composites', 'newModelGeneration': False,
        'userReviewStatus': 'pending',
    })
    save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'characterId': 'daoist-child', 'sourceRoleId': 9, 'direction': 'N',
        'sourceDirectionGroupIndex': 1, 'sourceFrameOrder': list(range(6, 12)),
        'sourceDeclaredCanvas': [100, 100], 'sourceEvidence': record(source_path),
        'sourceLayerReuseEvidence': pair, 'sourceFrameDurationMs': None, 'originalLoop': None,
        'nativeActorAnchor': None, 'frames': frames, 'exportCanvas': [OUT, OUT],
        'generatedMothers': generations, 'preview': record(preview), 'visualAccepted': False,
        'runtimeAdopted': False, 'accepted': False, 'motionContinuityConfirmed': False, 'userReviewStatus': 'pending',
    })
    print(json.dumps({'sourcePositions': len(frames), 'uniqueCandidateRasters': 5, 'f9SharesF6': True,
                      'nativeMothers': len(generations), 'alphaThreshold': 8, 'humanReview': 'pending'}))


if __name__ == '__main__':
    main()
