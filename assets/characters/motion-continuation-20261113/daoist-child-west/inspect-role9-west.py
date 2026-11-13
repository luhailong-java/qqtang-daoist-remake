"""Render diagnostic views of role 9's six stored west-walk phases."""
from itertools import combinations
from pathlib import Path
from importlib import util
import json

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
OLD = ROOT / 'assets/characters/motion-continuation-20261112/daoist-child-north'
spec = util.spec_from_file_location('role9_source', OLD / 'inspect-role9-north.py')
role9 = util.module_from_spec(spec)
spec.loader.exec_module(role9)
helpers, reader = role9.helpers, role9.reader
POSITIONS = tuple(range(12, 18))
FIELDS = ('width', 'height', 'frameOffset', 'pixelMode', 'empty', 'encodedPixelSha256')


def main():
    inputs, ids, entries, package = role9.inspect_sources()
    resources = {layer: helpers.load_layer(reader, entries, package, layer, ids[layer])
                 for layer in role9.LAYERS}
    _, head_frames, head_resource = helpers.load_layer(reader, entries, package, 'head', ids['head'])
    sheet = Image.new('RGB', (1500, 1100), '#f6f0de')
    lower = Image.new('RGB', (1050, 630), '#f6f0de')
    draw, lower_draw = ImageDraw.Draw(sheet), ImageDraw.Draw(lower)
    positions = []
    for phase, index in enumerate(POSITIONS):
        panel, frame_layers = helpers.card(), []
        for layer in role9.LAYERS:
            image, evidence = helpers.decode(reader, resources[layer], index)
            if image:
                panel.alpha_composite(image, tuple(evidence['frameOffset']))
            frame_layers.append({'layer': layer, **evidence})
        col, row = phase % 3, phase // 3
        helpers.paste_scaled(sheet, panel, col*500, row*550+50, 5)
        draw.text((col*500+15, row*550+12), f'Role 9 / group 2 / frame {index}', fill='#26463c')
        helpers.paste_scaled(lower, panel.crop((25, 54, 75, 94)), col*350, row*315+29, 7)
        lower_draw.text((col*350+12, row*315+9), f'f{index} / phase {phase} lower body', fill='#26463c')
        positions.append({'frameIndex': index, 'phaseIndex': phase, 'layers': frame_layers,
                          'headLayer': {'layer': 'head', **head_frames[index]}})

    equivalences = []
    for a, b in combinations(positions, 2):
        layers_a, layers_b = [*a['layers'], a['headLayer']], [*b['layers'], b['headLayer']]
        same = {first['layer']: all(first.get(field) == second.get(field) for field in FIELDS)
                for first, second in zip(layers_a, layers_b, strict=True)}
        equivalences.append({'sourceFrameIndices': [a['frameIndex'], b['frameIndex']],
                             'sameByLayer': same, 'sevenDeclaredLayersEqual': all(same.values())})

    board, details = BASE / 'source-west-six-phases.png', BASE / 'source-west-lower-body.png'
    sheet.save(board)
    lower.save(details)
    group2 = ROOT / 'assets/characters/motion-generated/daoist-child/native-role9-evidence/group2-direction-probe-5x.png'
    role9.save_json(BASE / 'source-west-evidence.json', {
        **inputs, 'sourceRoleId': 9, 'identityId': 'daoist-child', 'sourceDirectionGroupIndex': 2,
        'direction': 'W', 'declaredCanvas': [100, 100], 'frameCount': 24, 'directions': 4,
        'diagnosticLayerOrder': list(role9.LAYERS), 'nativeCompositeOrderConfirmed': False,
        'headLayerMetadata': {**head_resource, 'pixelDecodePerformed': False},
        'sourceFrameDurationMs': None, 'nativeActorAnchor': None, 'positions': positions,
        'phaseBoard': role9.ref(board), 'lowerBodyBoard': role9.ref(details),
        'directionEvidence': role9.ref(group2), 'allDirectionsEvidence': role9.ref(OLD / 'source-face-groups.png'),
        'encodedLayerPairComparisons': {'comparedFields': list(FIELDS), 'pairs': equivalences,
                                        'sourcePlaybackReuseConfirmed': False},
        'referenceOnly': True,
    })
    print(json.dumps({'positions': POSITIONS, 'layerDecodes': len(POSITIONS) * len(resources),
                      'matchingDeclaredLayerPairs': [p['sourceFrameIndices'] for p in equivalences
                                                     if p['sevenDeclaredLayersEqual']]}))


if __name__ == '__main__':
    main()
