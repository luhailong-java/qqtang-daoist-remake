"""Six explicit mouth inventory references from a SHA-locked archive; no client execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDS = [1230, 1232, 1233, 1234, 1306, 1307]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


with ARCHIVE.open('rb') as stream:
    actual_archive_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
if actual_archive_sha != ARCHIVE_SHA:
    raise ValueError('Fixed source archive SHA mismatch')
catalog_path = ROOT / 'references/qqtang-item-data/catalog.json'
catalog_bytes = catalog_path.read_bytes()
catalog = json.loads(catalog_bytes)
entries = {item['item_id']: item for item in catalog['items'] if item['item_id'] in IDS}
reader_spec = importlib.util.spec_from_file_location('mouth_inventory_reader', ROOT / 'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(reader_spec)
reader_spec.loader.exec_module(reader)
records = []
board = Image.new('RGB', (1536, 1024), '#66736b')
draw = ImageDraw.Draw(board)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
with zipfile.ZipFile(ARCHIVE) as archive:
    for ordinal, item_id in enumerate(IDS):
        item = entries[item_id]
        if item['category'] != 'mouth':
            raise ValueError('Wrong inventory category')
        icons = [name for name in item['installed_files'] if name.startswith('res/uiRes/icon/mouth/')]
        if len(icons) != 1:
            raise ValueError('Inventory resource must be explicitly installed exactly once')
        member = 'QQTang-Local/runtime/client-patched/' + icons[0]
        raw = archive.read(member)
        metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
        frame = next(frame for frame in metadata['frames'] if not frame['empty'])
        encoded = raw[frame['pixelDataOffset']:frame['pixelDataOffset'] + frame['pixelByteLength']]
        if sha(encoded) != frame['encodedPixelSha256']:
            raise ValueError('Encoded frame SHA mismatch')
        pixels = reader.decode_frame_pixels(encoded, frame['pixelMode'], frame['width'], frame['height'])
        picture = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
        target = HERE / f'references/{item_id}-inventory.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        picture.save(target)
        record = {'itemId': item_id, 'resourceId': item['resource_id'], 'category': 'mouth',
                  'sourceName': item['name'], 'sourceDescription': item['description'],
                  'sourceArchive': {'file': rel(ARCHIVE), 'sha256': ARCHIVE_SHA,
                    'url': 'https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip',
                    'authenticity': 'community modified sample; Tencent original target version unverified'},
                  'catalog': rel(catalog_path), 'catalogSha256': sha(catalog_bytes),
                  'catalogInstalledFile': icons[0], 'sourceMember': member, 'sourceMemberSha256': sha(raw),
                  'inventoryContainerMetadata': metadata, 'sourceFrameRecord': frame,
                  'file': rel(target), 'sha256': sha(target.read_bytes()), 'nativeFrameSize': list(picture.size),
                  'decodedRgbaSha256': sha(pixels), 'frameOffsetRaw': frame['frameOffset'],
                  'sourceAlphaBBoxAt16': list(picture.getchannel('A').point(lambda a: 255 if a >= 16 else 0).getbbox()),
                  'resourceKind': 'explicit inventory icon', 'referenceOnly': True, 'notRuntimeArt': True}
        save(Path(str(target) + '.source.json'), record)
        records.append(record)
        scale = min(390 / picture.width, 350 / picture.height)
        enlarged = picture.resize((round(picture.width * scale), round(picture.height * scale)), Image.Resampling.NEAREST)
        x, y = ordinal % 3 * 512, ordinal // 3 * 512
        board.paste(enlarged, (x + (512 - enlarged.width) // 2, y + 40 + (350 - enlarged.height) // 2), enlarged)
        draw.text((x + 22, y + 414), f'item {item_id} / resource {item["resource_id"]} · {item["name"]}', font=font, fill='#fff4da')
        draw.text((x + 22, y + 454), f'{picture.width}x{picture.height}px · source reference only', font=font, fill='#fff4da')
board_path = HERE / 'references/source-six-board.png'
board.save(board_path)
save(Path(str(board_path) + '.source.json'), {'file': rel(board_path), 'sha256': sha(board_path.read_bytes()),
     'referenceOnly': True, 'notRuntimeArt': True, 'operation': 'Nearest-neighbor source inspection enlargement only',
     'items': records})
save(HERE / 'source-contract.json', {'schemaVersion': 1, 'category': 'mouth', 'itemIds': IDS, 'items': records,
     'scope': 'six inventory icons only; no world frames, mounting or source timing inferred'})
print(json.dumps({'items': IDS, 'archiveSha256': actual_archive_sha, 'board': rel(board_path),
                  'nativeSizes': [record['nativeFrameSize'] for record in records]}, ensure_ascii=False))
