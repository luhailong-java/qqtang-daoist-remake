"""Bounded static reads of the five explicitly selected source capes; no client code."""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.dont_write_bytecode = True  # Trusted reader import must not write to shared scripts/.
IDS = [148, 149, 150, 151, 152]
STAND_SHA = {
    148: 'e562e20d8c02215094bc7cfdf6bde2ebe3969c4e523dd73af6e788fc9e7b5067',
    149: 'ded3e91912ccfa5586a8f486a5ccd3c05e0326e82b34a82b56e1ee9c6915fab6',
    150: '55eeb1d0067a19428610691732fde305a0915a4c075d32e8bc9a96a603e86a83',
    151: '502ddbab1dedf00102d3da75928f72463097203c4bb8c897840678d42ac8b11e',
    152: '72f3e094384029a93896cb2c3217fcb434a95e470f054078dd93743e7e7c2da9',
}
ICON_SHA = {
    148: '059cfd3569be66161fef482ee2a1aa576df3a920c947c13dc2af235e50c63cfe',
    149: 'f08227c39f47ec98c9756b11a8d7b365d96df27cbfb3b8373205f755cb86da86',
    150: '016fc8f94dc5c5b9cc9fb5ae0d7d73cae670fd5f38a2f5c7e0d0fb87d375158c',
    151: 'ac6acea978891c1087059e5ebef359ae57c7e85fd38e3205490e05006edb7b33',
    152: '445341704d19b31ba83dd1c9236478556f9a26cbea0ab4562f59886e7428eee3',
}
ARCHIVE = {
    'file': '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip',
    'sha256': 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
    'sourceUrl': 'https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip',
    'authenticity': 'community modified sample; Tencent original target version unverified',
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


reader_spec = importlib.util.spec_from_file_location('honor_cape_source_reader', ROOT / 'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(reader_spec)
reader_spec.loader.exec_module(reader)
catalog = json.loads((ROOT / 'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
selected = {entry['item_id']: entry for entry in catalog['items'] if entry['item_id'] in IDS}


def member_data(archive, ident, kind):
    entry = selected[ident]
    if kind == 'inventory':
        installed = next(path for path in entry['installed_files'] if path.startswith('res/uiRes/icon/'))
        expected = ICON_SHA[ident]
    else:
        installed = next(path for path in entry['installed_files'] if path.endswith('_' + kind + '.img'))
        expected = STAND_SHA[ident]
    member = 'QQTang-Local/runtime/client-patched/' + installed
    raw = archive.read(member)
    if sha(raw) != expected:
        raise ValueError('Explicit selected member SHA mismatch')
    metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
    return member, raw, metadata


def decode_one(ident, kind, member, raw, frame):
    encoded = raw[frame['pixelDataOffset']:frame['pixelDataOffset'] + frame['pixelByteLength']]
    if sha(encoded) != frame['encodedPixelSha256']:
        raise ValueError('Encoded frame SHA mismatch')
    pixels = reader.decode_frame_pixels(encoded, frame['pixelMode'], frame['width'], frame['height'])
    picture = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
    filename = 'inventory-source.png' if kind == 'inventory' else f'frame-{frame["index"]:03d}.png'
    target = HERE / f'references/{ident}/{filename}'
    target.parent.mkdir(parents=True, exist_ok=True)
    picture.save(target)
    record = {
        'itemId': ident, 'category': 'npack', 'sourceFrameIndex': frame['index'], 'resourceKind': kind,
        'file': relative(target), 'sha256': sha(target.read_bytes()), 'sourceArchive': ARCHIVE,
        'sourceMember': member, 'sourceSha256': sha(raw), 'sourceFrameRecord': frame,
        'nativeFrameSize': list(picture.size), 'frameOffsetRaw': frame['frameOffset'],
        'sourceAlphaBBoxAt16': list(picture.getchannel('A').point(lambda a: 255 if a >= 16 else 0).getbbox()),
        'decodedRgbaSha256': sha(pixels), 'referenceOnly': True, 'notRuntimeArt': True,
        'directionSemantic': None, 'frameDurationMs': None, 'loop': None,
    }
    save(Path(str(target) + '.source.json'), record)
    return record


def source_contract(archive, ident):
    member, raw, meta = member_data(archive, ident, 'stand')
    walk_member, walk, walk_meta = member_data(archive, ident, 'walk')
    if raw != walk or meta['frameCount'] != 12 or meta['directions'] != 4:
        raise ValueError('Selected cape source differs from fixed bounded contract')
    groups = defaultdict(list)
    frames = []
    for frame in meta['frames']:
        groups[(frame['width'], frame['height'], frame['pixelMode'], frame['encodedPixelSha256'])].append(frame['index'])
        reference = HERE / f'references/{ident}/frame-{frame["index"]:03d}.png.source.json'
        value = json.loads(reference.read_text(encoding='utf-8')) if reference.exists() else {}
        frames.append({'sourceFrameIndex': frame['index'], 'sourceNativeFrameRecord': frame,
                       'nativeFrameSize': [frame['width'], frame['height']], 'frameOffsetRaw': frame['frameOffset'],
                       'sourceAlphaBBoxAt16': value.get('sourceAlphaBBoxAt16'), 'file': value.get('file'),
                       'sha256': value.get('sha256'), 'directionSemantic': None, 'frameDurationMs': None,
                       'referenceOnly': True, 'notRuntimeArt': True})
    value = {'itemId': ident, 'sourceName': selected[ident]['name'], 'sourceDescription': selected[ident]['description'],
             'category': 'npack', 'resourceId': selected[ident]['resource_id'], 'sourceArchive': ARCHIVE,
             'sourceMembers': {'stand': member, 'walk': walk_member}, 'sourceSha256': sha(raw),
             'sourceDimg': meta, 'walkDimg': walk_meta, 'standWalkByteIdentical': True,
             'sourceFrameOrder': list(range(12)), 'sourceFrameCount': 12, 'directions': 4,
             'directionSemantic': None, 'directionBlockOrderKnown': False, 'frameDurationMs': None,
             'loop': None, 'nativeAttachment': None, 'encodedRasterGroups': list(groups.values()),
             'frames': frames, 'pixelReferenceCoverageComplete': all(frame['file'] for frame in frames),
             'referenceOnly': True, 'notRuntimeArt': True, 'runtimeUsable': False}
    save(HERE / f'references/{ident}/source-contract.json', value)
    return value


def board(ident, indices, key):
    picture = Image.new('RGBA', (1536, 1024), (64, 72, 80, 255))
    draw = ImageDraw.Draw(picture)
    sources = []
    for slot, index in enumerate(indices):
        path = HERE / f'references/{ident}/frame-{index:03d}.png'
        record = json.loads(Path(str(path) + '.source.json').read_text(encoding='utf-8'))
        image = Image.open(path).convert('RGBA')
        scale = min(10, 430 // image.width, 360 // image.height)
        size = (image.width * scale, image.height * scale)
        pos = (slot % 3 * 512 + (512 - size[0]) // 2, slot // 3 * 512 + (512 - size[1]) // 2)
        picture.alpha_composite(image.resize(size, Image.Resampling.NEAREST), pos)
        draw.text((slot % 3 * 512 + 18, slot // 3 * 512 + 20),
                  f'SOURCE {ident} PHASE {index} | {image.width}x{image.height} | raw {record["frameOffsetRaw"]}', fill='white')
        sources.append({'file': relative(path), 'sha256': sha(path.read_bytes()), 'sourceFrameIndex': index, 'uniformNearestScale': scale})
    target = HERE / f'references/{ident}/source-phases-{key}.png'
    picture.save(target)
    save(Path(str(target) + '.source.json'), {'operation': 'source-reference nearest-neighbour board only',
        'file': relative(target), 'sha256': sha(target.read_bytes()), 'sources': sources, 'referenceOnly': True, 'runtimeUsable': False})


parser = argparse.ArgumentParser()
parser.add_argument('--icons', action='store_true')
parser.add_argument('--item', type=int, choices=IDS)
parser.add_argument('--indices', nargs='+', type=int)
args = parser.parse_args()
with zipfile.ZipFile(ROOT / ARCHIVE['file']) as archive:
    if args.icons:
        records = []
        for ident in IDS:
            member, raw, meta = member_data(archive, ident, 'inventory')
            if meta['frameCount'] != 1:
                raise ValueError('Expected one explicit inventory icon')
            records.append(decode_one(ident, 'inventory', member, raw, meta['frames'][0]))
        target = HERE / 'references/source-inventory-five.png'
        picture = Image.new('RGBA', (1536, 1024), (64, 72, 80, 255))
        draw = ImageDraw.Draw(picture)
        for slot, record in enumerate(records):
            image = Image.open(ROOT / record['file']).convert('RGBA')
            scale = min(10, 430 // image.width, 360 // image.height)
            size = (image.width * scale, image.height * scale)
            pos = (slot % 3 * 512 + (512 - size[0]) // 2, slot // 3 * 512 + (512 - size[1]) // 2)
            picture.alpha_composite(image.resize(size, Image.Resampling.NEAREST), pos)
            draw.text((slot % 3 * 512 + 18, slot // 3 * 512 + 20), f'SOURCE ID {record["itemId"]} INVENTORY', fill='white')
        picture.save(target)
        save(Path(str(target) + '.source.json'), {'operation': 'five explicitly decoded source icons, reference-only', 'sources': records, 'runtimeUsable': False})
        print(json.dumps({'explicitSourceIds': IDS, 'decodedInventoryIcons': 5, 'referenceOnly': True}))
    else:
        if args.item is None or not args.indices or not 1 <= len(args.indices) <= 6 or len(set(args.indices)) != len(args.indices):
            raise ValueError('Select one known item and at most six distinct source frames')
        if any(index < 0 or index >= 12 for index in args.indices):
            raise ValueError('Source phase outside fixed 12-position contract')
        member, raw, meta = member_data(archive, args.item, 'stand')
        records = [decode_one(args.item, 'world', member, raw, meta['frames'][index]) for index in args.indices]
        value = source_contract(archive, args.item)
        key = 'a' if args.indices == list(range(6)) else 'b' if args.indices == list(range(6, 12)) else '-'.join(map(str, args.indices))
        board(args.item, args.indices, key)
        print(json.dumps({'itemId': args.item, 'decodedIndices': args.indices, 'sourcePixelCoverageComplete': value['pixelReferenceCoverageComplete'], 'sourceIndependentRasters': len(value['encodedRasterGroups']), 'referenceOnly': True}))
