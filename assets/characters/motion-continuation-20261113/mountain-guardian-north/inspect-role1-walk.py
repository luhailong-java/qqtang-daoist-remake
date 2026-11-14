"""Build source-only evidence for Mountain Guardian's north and south walk."""
from importlib import util
from itertools import combinations
from pathlib import Path
import argparse
import json

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
MOTION = Path(__file__).resolve().parent.parent
WEST = MOTION / 'mountain-guardian-west'
spec = util.spec_from_file_location('role1_source', WEST / 'inspect-role1-west.py')
role1 = util.module_from_spec(spec)
spec.loader.exec_module(role1)
source, LAYERS, FIELDS = role1.source, role1.LAYERS, role1.FIELDS
DIRECTIONS = {'north': (1, 'N'), 'south': (3, 'S')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('direction', choices=DIRECTIONS)
    name = parser.parse_args().direction
    group, direction = DIRECTIONS[name]
    base = MOTION / f'mountain-guardian-{name}'
    base.mkdir(exist_ok=True)
    reader = source.load_reader()
    inputs, entries, package, ids = role1.role1_inputs(reader)
    inputs.pop('daoistChildTriggerLookup')
    layers = {layer: source.load_layer(reader, entries, package, layer, ids[layer]) for layer in LAYERS}
    _, head_frames, head_meta = source.load_layer(reader, entries, package, 'head', ids['head'])
    probe = source.ref(WEST / 'source-face-groups.png')
    full = Image.new('RGB', (1500, 1100), source.PALE)
    lower = Image.new('RGB', (1050, 630), source.PALE)
    full_draw, lower_draw = ImageDraw.Draw(full), ImageDraw.Draw(lower)
    positions = []
    for phase in range(6):
        index = group*6+phase
        panel, decoded = source.card(), []
        for layer in LAYERS:
            image, data = source.decode(reader, layers[layer], index)
            if image:
                panel.alpha_composite(image, tuple(data['frameOffset']))
            decoded.append({'layer': layer, **data})
        col, row = phase % 3, phase // 3
        source.paste_scaled(full, panel, col*500, row*550+50, 5)
        full_draw.text((col*500+15, row*550+12), f'Role 1 / group {group} / frame {index}', fill='#26463c')
        source.paste_scaled(lower, panel.crop((25, 54, 75, 94)), col*350, row*315+29, 7)
        lower_draw.text((col*350+12, row*315+9), f'f{index} / phase {phase} lower body', fill='#26463c')
        positions.append({'frameIndex': index, 'phaseIndex': phase, 'layers': decoded,
                          'headLayer': {'layer': 'head', **head_frames[index]}})
    pairs = []
    for a, b in combinations(positions, 2):
        layers_a, layers_b = [*a['layers'], a['headLayer']], [*b['layers'], b['headLayer']]
        same = {first['layer']: all(first.get(field) == second.get(field) for field in FIELDS)
                for first, second in zip(layers_a, layers_b, strict=True)}
        pairs.append({'sourceFrameIndices': [a['frameIndex'], b['frameIndex']],
                      'sameByLayer': same, 'eightDeclaredLayersEqual': all(same.values())})
    board, details = base / f'source-{name}-six-phases.png', base / f'source-{name}-lower-body.png'
    full.save(board)
    lower.save(details)
    source.save_json(base / f'source-{name}-evidence.json', {
        **inputs, 'sourceRoleId': 1, 'identityId': 'mountain-guardian', 'sourceDirectionGroupIndex': group,
        'direction': direction, 'declaredCanvas': [100, 100], 'frameCount': 24, 'directions': 4,
        'diagnosticLayerOrder': list(LAYERS), 'nativeCompositeOrderConfirmed': False,
        'headLayerMetadata': {**head_meta, 'pixelDecodePerformed': False},
        'sourceFrameDurationMs': None, 'nativeActorAnchor': None, 'positions': positions,
        'phaseBoard': source.ref(board), 'lowerBodyBoard': source.ref(details),
        'directionEvidence': probe,
        'encodedLayerPairComparisons': {'comparedFields': list(FIELDS), 'pairs': pairs,
                                        'sourcePlaybackReuseConfirmed': False},
        'referenceOnly': True,
    })
    print(json.dumps({'direction': direction, 'positions': [p['frameIndex'] for p in positions],
                      'layerDecodes': len(positions) * len(layers),
                      'matchingDeclaredLayerPairs': [p['sourceFrameIndices'] for p in pairs
                                                     if p['eightDeclaredLayersEqual']]}))


if __name__ == '__main__':
    main()
