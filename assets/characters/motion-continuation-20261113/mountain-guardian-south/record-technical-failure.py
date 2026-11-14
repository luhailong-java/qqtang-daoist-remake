"""Preserve native outputs and their alpha failure without exporting sprites."""
from importlib import util
from pathlib import Path
import json

from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
spec = util.spec_from_file_location('generation_records', ROOT / 'assets/characters/motion-continuation-20261112/moon-shadow-east/export-diagnostics.py')
records = util.module_from_spec(spec)
spec.loader.exec_module(records)
records.BASE = BASE


def main():
    source_path = BASE / 'source-south-evidence.json'
    source = records.read_json(source_path)
    if [f['frameIndex'] for f in source['positions']] != list(range(18, 24)):
        raise ValueError('Unexpected source positions')
    mothers = []
    for version, limits in (('a-v1', (163, 251)), ('b-v1', (166, 251))):
        path = BASE / f'mother-{version}.png'
        with Image.open(path) as image:
            if image.size != (2172, 724) or image.mode != 'RGBA':
                raise ValueError('Unexpected returned native geometry')
            alpha = image.getchannel('A')
            if alpha.getextrema() != limits:
                raise ValueError('Native alpha evidence changed')
            mothers.append({
                **records.record(path), 'generationRecord': records.generation_record(version, path, image),
                'width': image.width, 'height': image.height, 'alphaExtrema': list(limits),
                'alpha8BBox': list(records.alpha_box(image)), 'technicalAccepted': False,
                'technicalFailure': 'Nontransparent white background with alpha above 8 over the entire native canvas',
                'spriteFramesExported': 0,
            })
    records.save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'characterId': 'mountain-guardian', 'sourceRoleId': 1, 'direction': 'S',
        'sourceDirectionGroupIndex': 3, 'sourceFrameOrder': list(range(18, 24)),
        'sourceDeclaredCanvas': [100, 100], 'sourceEvidence': records.record(source_path),
        'sourceFrameDurationMs': None, 'originalLoop': None, 'nativeActorAnchor': None,
        'frames': [], 'generatedMothers': mothers, 'technicalStatus': 'failed_alpha_background',
        'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
        'motionContinuityConfirmed': False, 'userReviewStatus': 'pending',
        'reasonNoExport': 'Native outputs lack transparent pixels. Both backgrounds cover every crop boundary.',
    })
    print(json.dumps({'direction': 'S', 'nativeMothers': len(mothers), 'sourcePositions': 6,
                      'uniqueCandidateRasters': 0, 'technicalStatus': 'failed_alpha_background'}))


if __name__ == '__main__':
    main()
