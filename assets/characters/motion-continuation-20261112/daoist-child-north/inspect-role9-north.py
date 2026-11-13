"""Build the verified six north-walk source panels for Daoist Child / source role 9."""
from configparser import ConfigParser
from hashlib import sha256
from pathlib import Path
from importlib import util
import argparse
import json
import zipfile

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_DIGEST = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
INI_DIGEST = '54e609aec636603ad02e9449dff0baf011ad3c614659796c8446549f895e5c44'
ROLE_MAP = ROOT / 'assets/characters/motion-generated/roster-skin-mapping-20261028.json'
MEMBER_ROOT = 'QQTang-Local/runtime/client-patched/'
LAYERS = ('body', 'foot', 'leg', 'cloth', 'face', 'hair')


def import_local(file, name):
    spec = util.spec_from_file_location(name, file)
    result = util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


# Reuse the already-frozen strict reader helpers and their frame-offset checks.
helpers = import_local(BASE.parent / 'moon-shadow-east/inspect-role22-east.py', 'source_frame_helpers')
reader = helpers.load_reader()
ref, save_json = helpers.ref, helpers.save_json


def inspect_sources():
    fingerprint = sha256()
    with ARCHIVE.open('rb') as stream:
        while data := stream.read(1024 * 1024):
            fingerprint.update(data)
    if fingerprint.hexdigest() != ARCHIVE_DIGEST:
        raise ValueError('Pinned archive digest changed')
    with zipfile.ZipFile(ARCHIVE) as archive:
        member = MEMBER_ROOT + 'object/player/player9.ini'
        ini = archive.read(member)
        if sha256(ini).hexdigest() != INI_DIGEST:
            raise ValueError('Role-9 INI digest changed')
        config = ConfigParser(interpolation=None)
        config.read_string(ini.decode('utf-8-sig'))
        ids = dict(config['walk'])
        source = next(row for row in json.loads(ROLE_MAP.read_bytes())['slots'] if row['sourceRoleId'] == 9)
        if source['appearance']['identityId'] != 'daoist-child' or source['sourcePlayerIni']['sections']['walk'] != ids:
            raise ValueError('Role-9 project mapping or walk layers changed')
        index = archive.read(MEMBER_ROOT + 'data/object.idx')
        package = archive.read(MEMBER_ROOT + 'data/object.pkg')
    entries = {row['path'].replace(chr(92), '/'): row for row in reader.parse_index(index, len(package))['entries']}
    metadata = {
        'archive': {'file': ARCHIVE.relative_to(ROOT).as_posix(), 'sha256': ARCHIVE_DIGEST},
        'playerIni': {'member': member, 'sha256': INI_DIGEST, 'walk': ids},
        'sourceRoleMapping': ref(ROLE_MAP),
        'objectIdx': {'member': MEMBER_ROOT + 'data/object.idx', 'sha256': sha256(index).hexdigest()},
        'objectPkg': {'member': MEMBER_ROOT + 'data/object.pkg', 'sha256': sha256(package).hexdigest()},
    }
    return metadata, ids, entries, package


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--north-group', type=int, choices=range(4))
    args = parser.parse_args()
    inputs, ids, entries, package = inspect_sources()
    layers = LAYERS if args.north_group is not None else ('face',)
    resources = {layer: helpers.load_layer(reader, entries, package, layer, ids[layer]) for layer in layers}
    probes = args.north_group is None
    positions = [0, 6, 12, 18] if probes else list(range(args.north_group * 6, args.north_group * 6 + 6))
    sheet = Image.new('RGB', (1600, 440) if probes else (1500, 1100), '#f6f0de')
    draw = ImageDraw.Draw(sheet)
    lower = Image.new('RGB', (1050, 630), '#f6f0de')
    lower_draw = ImageDraw.Draw(lower)
    records = []
    for i, index in enumerate(positions):
        panel = helpers.card()
        frame_layers = []
        for layer in layers:
            image, evidence = helpers.decode(reader, resources[layer], index)
            if image:
                panel.alpha_composite(image, tuple(evidence['frameOffset']))
            frame_layers.append({'layer': layer, **evidence})
        if probes:
            helpers.paste_scaled(sheet, panel, i * 400, 40, 4)
            draw.text((i * 400 + 16, 12), f'Face group {i}, native frame {index}', fill='#26463c')
        else:
            x, y = i % 3 * 500, i // 3 * 550
            helpers.paste_scaled(sheet, panel, x, y + 50, 5)
            draw.text((x+15, y+12), f'Role 9 / group {args.north_group} / frame {index}', fill='#26463c')
            x, y = i % 3 * 350, i // 3 * 315
            helpers.paste_scaled(lower, panel.crop((25, 54, 75, 94)), x, y + 29, 7)
            lower_draw.text((x+12, y+9), f'f{index} / phase {i} lower body', fill='#26463c')
        records.append({'frameIndex': index, 'phaseIndex': index % 6, 'layers': frame_layers})
    board = BASE / ('source-face-groups.png' if probes else 'source-north-six-phases.png')
    sheet.save(board)
    metadata = {
        **inputs, 'sourceRoleId': 9, 'identityId': 'daoist-child',
        'declaredCanvas': [100, 100], 'frameCount': 24, 'directions': 4,
        'diagnosticLayerOrder': list(layers), 'nativeCompositeOrderConfirmed': False,
        'headLayerIncluded': False, 'sourceFrameDurationMs': None, 'nativeActorAnchor': None,
        'positions': records, 'phaseBoard': ref(board), 'referenceOnly': True,
    }
    if not probes:
        lower_path = BASE / 'source-north-lower-body.png'
        lower.save(lower_path)
        _, head_frames, head_resource = helpers.load_layer(reader, entries, package, 'head', ids['head'])
        # The diagnostic boards omit this layer. Its encoded metadata still participates in the reuse check.
        signatures = ('width', 'height', 'frameOffset', 'pixelMode', 'empty', 'encodedPixelSha256')
        original_a, original_b = positions[0], positions[3]
        phase_a = [*records[0]['layers'], {'layer': 'head', **head_frames[original_a]}]
        phase_b = [*records[3]['layers'], {'layer': 'head', **head_frames[original_b]}]
        same = {a['layer']: all(a.get(field) == b.get(field) for field in signatures)
                for a, b in zip(phase_a, phase_b, strict=True)}
        metadata.update({'sourceDirectionGroupIndex': args.north_group, 'direction': 'N',
                         'directionEvidence': ref(BASE / 'source-face-groups.png'),
                         'lowerBodyBoard': ref(lower_path),
                         'headLayerMetadata': {**head_resource, 'frames': [head_frames[i] for i in positions],
                                               'pixelDecodePerformed': False},
                         'encodedLayerPairComparison': {'sourceFrameIndices': [original_a, original_b],
                                                        'comparedFields': list(signatures), 'sameByLayer': same,
                                                        'sevenDeclaredLayersEqual': all(same.values()),
                                                        'sourcePlaybackReuseConfirmed': False}})
    save_json(BASE / ('source-face-groups.json' if probes else 'source-north-evidence.json'), metadata)
    print(json.dumps({'positions': positions, 'layerDecodes': len(positions) * len(layers),
                      'sourceDirectionGroupIndex': args.north_group}))


if __name__ == '__main__':
    main()
