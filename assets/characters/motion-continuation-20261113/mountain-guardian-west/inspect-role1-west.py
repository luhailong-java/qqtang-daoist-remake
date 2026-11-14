"""Build source-only evidence for Mountain Guardian's west walk."""
from importlib import util
from itertools import combinations
from pathlib import Path
from configparser import ConfigParser
from hashlib import sha256
from zipfile import ZipFile
import json

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
EAST = ROOT / 'assets/characters/motion-continuation-20261112/moon-shadow-east'
spec = util.spec_from_file_location('role22_source', EAST / 'inspect-role22-east.py')
source = util.module_from_spec(spec)
spec.loader.exec_module(source)
BASE = Path(__file__).resolve().parent
LAYERS = ('body', 'foot', 'leg', 'cloth', 'face', 'hair', 'npack')
FIELDS = ('width', 'height', 'frameOffset', 'pixelMode', 'empty', 'encodedPixelSha256')


def role1_inputs(reader):
    fingerprint = sha256()
    with source.INPUT.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            fingerprint.update(chunk)
    if fingerprint.hexdigest() != source.ARCHIVE_SHA:
        raise ValueError('Pinned archive digest changed')
    with ZipFile(source.INPUT) as archive:
        prefix = source.MEMBER_ROOT
        member = prefix + 'object/player/player1.ini'
        ini = archive.read(member)
        if source.digest(ini) != 'cc8a4fdccebe3ef6b84a4eec10343c68f6ad31aad55a8ff209d8f4445932956d':
            raise ValueError('Unexpected role 1 INI')
        config = ConfigParser(interpolation=None)
        config.read_string(ini.decode('utf-8-sig'))
        ids = dict(config['walk'])
        mapping = next(r for r in json.loads(source.ROLE_MAP.read_bytes())['slots'] if r['sourceRoleId'] == 1)
        if mapping['appearance']['identityId'] != 'mountain-guardian' or ids != mapping['sourcePlayerIni']['sections']['walk']:
            raise ValueError('Unexpected walk or project identity mapping')
        index = archive.read(prefix + 'data/object.idx')
        package = archive.read(prefix + 'data/object.pkg')
        role9_ini = archive.read(prefix + 'object/player/player9.ini')
        named_matches = [name for name in archive.namelist() if '10902' in name.casefold()]
    entries = {e['path'].replace(chr(92), '/'): e for e in reader.parse_index(index, len(package))['entries']}
    role9 = ConfigParser(interpolation=None)
    role9.read_string(role9_ini.decode('utf-8-sig'))
    inputs = {'archive': {'file': source.INPUT.relative_to(ROOT).as_posix(), 'sha256': source.ARCHIVE_SHA},
              'playerIni': {'member': member, 'sha256': source.digest(ini), 'walk': ids},
              'sourceRoleMapping': source.ref(source.ROLE_MAP),
              'objectIdx': {'member': prefix + 'data/object.idx', 'sha256': source.digest(index)},
              'objectPkg': {'member': prefix + 'data/object.pkg', 'sha256': source.digest(package)},
              'daoistChildTriggerLookup': {'member': prefix + 'object/player/player9.ini',
                                           'sha256': source.digest(role9_ini), 'trigger': dict(role9['trigger']),
                                           'nameMatchesInZip': named_matches,
                                           'nameMatchesInObjectIndex': [n for n in entries if '10902' in n.casefold()],
                                           'placementActionMappingConfirmed': False}}
    return inputs, entries, package, ids


def direction_probe(reader, face):
    board = Image.new('RGB', (1600, 445), source.PALE)
    draw = ImageDraw.Draw(board)
    phases = []
    for group in range(4):
        image, frame = source.decode(reader, face, group*6)
        panel = source.card()
        if image:
            panel.alpha_composite(image, tuple(frame['frameOffset']))
        source.paste_scaled(board, panel, group*400, 45, 4)
        draw.text((group*400+15, 12), f'Face group {group}, native frame {group*6}', fill='#26463c')
        phases.append(frame)
    path = BASE / 'source-face-groups.png'
    board.save(path)
    return source.ref(path), phases


def main():
    name, group, direction = 'west', 2, 'W'
    base = BASE
    reader = source.load_reader()
    inputs, entries, package, ids = role1_inputs(reader)
    layers = {layer: source.load_layer(reader, entries, package, layer, ids[layer]) for layer in LAYERS}
    _, head_frames, head_meta = source.load_layer(reader, entries, package, 'head', ids['head'])
    probe, probes = direction_probe(reader, layers['face'])
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
        'directionEvidence': probe, 'directionProbeFrames': probes,
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
