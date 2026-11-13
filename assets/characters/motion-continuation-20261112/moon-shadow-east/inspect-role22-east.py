"""Read just the exact walk resources named by role 22 and build motion references."""
from configparser import ConfigParser
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
INPUT = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
MEMBER_ROOT = 'QQTang-Local/runtime/client-patched/'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
ROLE_INI_SHA = 'a1827a93658408e3a4ff1b8e640d1ce4865786854f2a9763e56287360e80d931'
ROLE_MAP = ROOT / 'assets/characters/motion-generated/roster-skin-mapping-20261028.json'
LAYERS = ('body', 'foot', 'leg', 'cloth', 'face', 'hair')
PALE = '#f6f0de'


def digest(data):
    return sha256(data).hexdigest()


def ref(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}


def save_json(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def load_reader():
    spec = importlib.util.spec_from_file_location('dimg', ROOT / 'scripts/inspect-reference-dimg.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    return reader


def source_inputs(reader):
    digest_value = sha256()
    with INPUT.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest_value.update(block)
    if digest_value.hexdigest() != ARCHIVE_SHA:
        raise ValueError('Pinned archive digest changed')
    with zipfile.ZipFile(INPUT) as archive:
        player_member = MEMBER_ROOT + 'object/player/player22.ini'
        ini = archive.read(player_member)
        if digest(ini) != ROLE_INI_SHA:
            raise ValueError('Role 22 INI does not match the project reference')
        config = ConfigParser(interpolation=None)
        config.read_string(ini.decode('utf-8-sig'))
        ids = dict(config['walk'])
        mapping = next(row for row in json.loads(ROLE_MAP.read_bytes())['slots'] if row['sourceRoleId'] == 22)
        if mapping['appearance']['identityId'] != 'moon-shadow' or ids != mapping['sourcePlayerIni']['sections']['walk']:
            raise ValueError('Role 22 identity or walk member mapping changed')
        index = archive.read(MEMBER_ROOT + 'data/object.idx')
        package = archive.read(MEMBER_ROOT + 'data/object.pkg')
    entries = {row['path'].replace(chr(92), '/'): row
               for row in reader.parse_index(index, len(package))['entries']}
    base = {
        'archive': {'file': INPUT.relative_to(ROOT).as_posix(), 'sha256': ARCHIVE_SHA},
        'playerIni': {'member': player_member, 'sha256': digest(ini), 'bytes': len(ini), 'walk': ids},
        'sourceRoleMapping': ref(ROLE_MAP),
        'objectIdx': {'member': MEMBER_ROOT + 'data/object.idx', 'sha256': digest(index)},
        'objectPkg': {'member': MEMBER_ROOT + 'data/object.pkg', 'sha256': digest(package)},
    }
    return base, entries, package, ids


def load_layer(reader, entries, package, layer, ident):
    if not ident.isdecimal():
        raise ValueError('Invalid layer identifier')
    member = f'object/{layer}/{layer}{ident}_walk.img'
    entry = entries[member]
    if entry['rawByteLength'] > 500_000 or entry['compressedByteLength'] > 100_000:
        raise ValueError('Unexpected source resource size')
    raw, compressed_digest = reader.unpack_resource(package, entry)
    metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
    if (metadata['version'], metadata['frameCount'], metadata['directions'], metadata['declaredCanvas']) != (65536, 24, 4, [100, 100]):
        raise ValueError('Inconsistent source role-22 walk dimensions')
    evidence = {'member': member, 'packageIndexEntry': entry, 'compressedSha256': compressed_digest,
                'sourceDimgSha256': digest(raw), 'version': metadata['version']}
    return raw, metadata['frames'], evidence


def decode(reader, layer, index):
    raw, frames, evidence = layer
    frame = frames[index]
    if frame['empty']:
        return None, {**evidence, **frame}
    w, h = frame['width'], frame['height']
    x, y = frame['frameOffset']
    if not (0 <= x < x+w <= 100 and 0 <= y < y+h <= 100):
        raise ValueError('Source layer exceeds its declared diagnostic canvas')
    start = frame['pixelDataOffset']
    pixels = reader.decode_frame_pixels(raw[start:start+frame['pixelByteLength']], frame['pixelMode'], w, h)
    return Image.frombytes('RGBA', (w, h), pixels), {**evidence, **frame, 'decodedRgbaSha256': digest(pixels)}


def card(size=(100, 100)):
    return Image.new('RGBA', size, PALE)


def paste_scaled(dst, image, x, y, ratio):
    dst.paste(image.resize((image.width*ratio, image.height*ratio), Image.Resampling.NEAREST).convert('RGB'), (x, y))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--east-group', type=int, choices=range(4))
    args = parser.parse_args()
    reader = load_reader()
    input_evidence, entries, package, ids = source_inputs(reader)
    wanted = ('face',) if args.east_group is None else LAYERS
    layers = {name: load_layer(reader, entries, package, name, ids[name]) for name in wanted}
    if args.east_group is None:
        board = Image.new('RGB', (1600, 445), PALE)
        draw = ImageDraw.Draw(board)
        data = []
        for group in range(4):
            image, frame = decode(reader, layers['face'], group * 6)
            panel = card()
            if image:
                panel.alpha_composite(image, tuple(frame['frameOffset']))
            paste_scaled(board, panel, group*400, 45, 4)
            draw.text((group*400+15, 12), f'Face group {group}, native frame {group*6}', fill='#26463c')
            data.append(frame)
        target = BASE / 'source-face-groups.png'
        board.save(target)
        save_json(BASE / 'source-face-groups.json', {
            **input_evidence, 'sourceRoleId': 22, 'identityId': 'moon-shadow',
            'images': data, 'board': ref(target), 'directionSemanticsAssigned': False,
        })
        print(json.dumps({'sourceRoleId': 22, 'faceProbeFrames': 4}))
        return

    full = Image.new('RGB', (1500, 1100), PALE)
    lower = Image.new('RGB', (1050, 630), PALE)
    full_draw = ImageDraw.Draw(full)
    lower_draw = ImageDraw.Draw(lower)
    records = []
    for phase in range(6):
        frame_index = args.east_group*6 + phase
        panel = card()
        phase_layers = []
        for name in LAYERS:
            image, source = decode(reader, layers[name], frame_index)
            if image:
                panel.alpha_composite(image, tuple(source['frameOffset']))
            phase_layers.append({'layer': name, **source})
        x, y = phase%3*500, phase//3*550
        paste_scaled(full, panel, x, y+50, 5)
        full_draw.text((x+15, y+12), f'Role 22 / east group {args.east_group} / frame {frame_index}', fill='#26463c')
        x, y = phase%3*350, phase//3*315
        paste_scaled(lower, panel.crop((25, 54, 75, 94)), x, y+29, 7)
        lower_draw.text((x+12, y+9), f'f{frame_index} lower body', fill='#26463c')
        records.append({'frameIndex': frame_index, 'phaseIndex': phase, 'layers': phase_layers})
    full_target = BASE / 'source-east-six-phases.png'
    lower_target = BASE / 'source-east-lower-body.png'
    full.save(full_target)
    lower.save(lower_target)
    save_json(BASE / 'source-east-evidence.json', {
        **input_evidence, 'sourceRoleId': 22, 'identityId': 'moon-shadow',
        'sourceDirectionGroupIndex': args.east_group, 'direction': 'E',
        'directionEvidence': ref(BASE / 'source-face-groups.png'),
        'declaredCanvas': [100, 100], 'frameCount': 24, 'directions': 4, 'positions': records,
        'diagnosticLayerOrder': list(LAYERS), 'nativeCompositeOrderConfirmed': False,
        'headLayerIncluded': False, 'sourceFrameDurationMs': None, 'nativeActorAnchor': None,
        'phaseBoard': ref(full_target), 'lowerBodyBoard': ref(lower_target), 'referenceOnly': True,
    })
    print(json.dumps({'sourceRoleId': 22, 'decodedPhaseLayers': 36, 'eastGroup': args.east_group,
                      'nativeFrames': [record['frameIndex'] for record in records]}))


if __name__ == '__main__':
    main()
