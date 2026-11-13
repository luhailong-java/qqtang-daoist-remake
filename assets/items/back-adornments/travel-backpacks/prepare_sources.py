"""Static reference inputs for all six literal-name 背包 IDs; no game execution."""
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
IDS = [1169, 1329, 1330, 1331, 1553, 3027]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ZIP_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('backpack_source_reader', ROOT / 'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


catalog = json.loads((ROOT / 'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
family = [i for i in catalog['items'] if i['category'] == 'npack' and '背包' in i['name']]
if [i['item_id'] for i in family] != IDS:
    raise ValueError('Exact literal-name family changed; investigate instead of guessing')
lookup = {i['item_id']: i for i in family}
parser = argparse.ArgumentParser()
parser.add_argument('--kind', choices=['inventory', 'world-static'], required=True)
parser.add_argument('--ids', type=int, nargs='+', required=True)
args = parser.parse_args()
if not 1 <= len(args.ids) <= 6 or len(set(args.ids)) != len(args.ids) or any(i not in IDS for i in args.ids):
    raise ValueError('Select 1–6 explicit known source IDs')
digest = hashlib.sha256()
with ARCHIVE.open('rb') as stream:
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
if digest.hexdigest() != ZIP_SHA:
    raise ValueError('Fixed archive SHA mismatch')
archive_record = {'file': relative(ARCHIVE), 'sha256': ZIP_SHA,
                  'sourceUrl': 'https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip',
                  'authenticity': 'Community modified sample, original target authenticity/version unverified'}


def member_data(archive, entry, ending):
    matches = [p for p in entry['installed_files'] if p.startswith('res/uiRes/icon/')]
    if ending != 'inventory':
        matches = [p for p in entry['installed_files'] if p.endswith('_' + ending + '.img')]
    if len(matches) != 1:
        raise ValueError('Expected one exact installed resource, never infer resource index from name')
    member = 'QQTang-Local/runtime/client-patched/' + matches[0]
    raw = archive.read(member)
    meta, _ = reader.inspect_dimg(raw, metadata_only=True)
    return {'member': member, 'sha256': sha(raw), 'byteLength': len(raw), 'dimg': meta}, raw


def decode(entry, record, raw, target, index):
    f = record['dimg']['frames'][index]
    encoded = raw[f['pixelDataOffset']:f['pixelDataOffset'] + f['pixelByteLength']]
    if sha(encoded) != f['encodedPixelSha256']:
        raise ValueError('Encoded pixel SHA mismatch')
    pixels = reader.decode_frame_pixels(encoded, f['pixelMode'], f['width'], f['height'])
    picture = Image.frombytes('RGBA', (f['width'], f['height']), pixels)
    target.parent.mkdir(parents=True, exist_ok=True)
    picture.save(target)
    result = {'itemId': entry['item_id'], 'category': 'npack', 'sourceName': entry['name'],
              'file': relative(target), 'sha256': sha(target.read_bytes()), 'sourceArchive': archive_record,
              'sourceMember': record['member'], 'sourceSha256': record['sha256'], 'sourceFrameIndex': index,
              'sourceNativeFrameRecord': f, 'nativeFrameSize': list(picture.size), 'frameOffsetRaw': f['frameOffset'],
              'sourceAlphaBBoxAt16': list(picture.getchannel('A').point(lambda a: 255 if a >= 16 else 0).getbbox()),
              'decodedRgbaSha256': sha(pixels), 'referenceOnly': True, 'notRuntimeArt': True,
              'directionSemantic': None, 'frameDurationMs': None, 'loop': None, 'nativeAttachment': None}
    save(Path(str(target) + '.source.json'), result)
    return result


board = Image.new('RGBA', (1536, 1024), (64, 72, 80, 255))
draw = ImageDraw.Draw(board)
board_refs = []
with zipfile.ZipFile(ARCHIVE) as archive:
    for slot, ident in enumerate(args.ids):
        entry = lookup[ident]
        folder = HERE / f'references/{ident}'
        if args.kind == 'inventory':
            record, raw = member_data(archive, entry, 'inventory')
            if record['dimg']['frameCount'] != 1:
                raise ValueError('Inventory has multiple source frames; do not choose blindly')
            result = decode(entry, record, raw, folder / 'inventory-source.png', 0)
            save(folder / 'inventory-source-contract.json', {**entry, 'sourceArchive': archive_record, 'sourceResource': record,
                'decodedReference': result, 'referenceOnly': True, 'notRuntimeArt': True})
        else:
            stand, raw = member_data(archive, entry, 'stand')
            walk, walk_raw = member_data(archive, entry, 'walk')
            result = decode(entry, stand, raw, folder / 'world-source-frame000.png', 0)
            groups = defaultdict(list)
            for f in stand['dimg']['frames']:
                groups[(f['width'], f['height'], f['pixelMode'], f['encodedPixelSha256'])].append(f['index'])
            save(folder / 'world-source-contract.json', {**entry, 'sourceArchive': archive_record,
                'sourceStates': {'stand': stand, 'walk': walk}, 'standWalkByteIdentical': raw == walk_raw,
                'sourceFrameOrder': list(range(stand['dimg']['frameCount'])), 'encodedRasterGroups': list(groups.values()),
                'decodedSourcePositions': [0], 'decodedStaticReference': result, 'pixelReferenceCoverageComplete': False,
                'worldCandidatePositions': [], 'worldCandidateCoverageComplete': False,
                'directionSemantic': None, 'frameDurationMs': None, 'loop': None, 'nativeAttachment': None,
                'referenceOnly': True, 'notRuntimeArt': True, 'completeAnimationAccepted': False})
        picture = Image.open(ROOT / result['file']).convert('RGBA')
        scale = min(10, 430 // picture.width, 390 // picture.height)
        enlarged = picture.resize((picture.width * scale, picture.height * scale), Image.Resampling.NEAREST)
        board.alpha_composite(enlarged, (slot % 3 * 512 + (512 - enlarged.width) // 2,
                                         slot // 3 * 512 + (512 - enlarged.height) // 2))
        draw.text((slot % 3 * 512 + 18, slot // 3 * 512 + 18),
                  f'SOURCE ID{ident} / {args.kind} / native{picture.size} / resource{entry["resource_id"]}', fill='white')
        board_refs.append({'file': result['file'], 'sha256': result['sha256'], 'itemId': ident, 'nearestScale': scale})
board_key = 'six' if args.ids == IDS else '-'.join(map(str, args.ids))
target = HERE / f'references/source-{args.kind}-{board_key}.png'
board.save(target)
save(Path(str(target) + '.source.json'), {'file': relative(target), 'sha256': sha(target.read_bytes()),
    'operation': 'Six explicit reference-only native source rasters, nearest-neighbour enlargement',
    'sourceArchive': archive_record, 'sources': board_refs, 'referenceOnly': True, 'notRuntimeArt': True})
print(json.dumps({'kind': args.kind, 'sourceIds': args.ids, 'decodedSourceRasters': len(args.ids), 'worldCandidatePositions': 0}))
