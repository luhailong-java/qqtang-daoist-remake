"""Decode only the catalog-identified enter32 stand and inventory members."""
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
import hashlib
import importlib.util
import json

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
CATALOG = ROOT / 'references/qqtang-item-data/catalog.json'
MEMBERS = {'stand': 'object/enter/enter32_stand.img', 'inventory': 'res/uiRes/icon/enter/enter32.img'}
PREFIX = 'QQTang-Local/runtime/client-patched/'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fingerprint(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}


def save(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def inspect():
    with ARCHIVE.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Fixed source archive SHA mismatch')
    item = next(item for item in json.loads(CATALOG.read_bytes())['items'] if item['item_id'] == 1658)
    if item['category'] != 'enter' or item['resource_id'] != 32 or any(
            path not in item['installed_files'] for path in MEMBERS.values()):
        raise ValueError('Catalog does not explicitly identify both requested resources')
    spec = importlib.util.spec_from_file_location('enter_1658_dimg', ROOT / 'scripts/inspect-reference-dimg.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    with ZipFile(ARCHIVE) as archive:
        raw_by_action = {action: archive.read(PREFIX + path) for action, path in MEMBERS.items()}
    raw = raw_by_action['stand']
    metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
    if metadata['declaredCanvas'] != [100, 100] or metadata['frameCount'] != 6 or metadata['directions'] != 1:
        raise ValueError('Unexpected fixed source layout')
    positions, rasters, aliases = [], {}, defaultdict(list)
    for frame in metadata['frames']:
        if frame['empty']:
            raise ValueError('An unexpected source slot is empty')
        offset = frame['pixelDataOffset']
        encoded = raw[offset:offset + frame['pixelByteLength']]
        if digest(encoded) != frame['encodedPixelSha256']:
            raise ValueError('Encoded source payload differs')
        size = (frame['width'], frame['height'])
        pixels = reader.decode_frame_pixels(encoded, frame['pixelMode'], *size)
        sha = digest(pixels)
        key = (*size, sha)
        positions.append({
            'index': frame['index'], 'sourceFrame': frame, 'sourceSize': list(size),
            'sourceRawOffset': frame['frameOffset'], 'rgbaSha256': sha,
        })
        aliases[key].append(frame['index'])
        rasters.setdefault(aliases[key][0], Image.frombytes('RGBA', size, pixels))
    if len(rasters) != 6:
        raise ValueError('Expected six distinct source rasters')
    for indices in aliases.values():
        for index in indices:
            positions[index]['uniqueRasterIndex'] = indices[0]
    icon_meta, icon = reader.inspect_dimg(raw_by_action['inventory'])
    icon_picture = Image.frombytes('RGBA', (icon['width'], icon['height']), icon['pixels'])
    return {
        'inventory': {'nativeSize': list(icon_picture.size), 'frame': icon_meta['frames'][icon['index']],
                      'rgbaSha256': digest(icon['pixels'])},
        'schemaVersion': 1, 'itemId': 1658, 'resourceId': 32, 'category': 'enter',
        'sourceArchive': {
            'file': ARCHIVE.relative_to(ROOT).as_posix(), 'sha256': ARCHIVE_SHA,
            'authenticity': 'community modified sample; Tencent original target version unverified',
            'url': reader.ARCHIVE_URL,
        },
        'catalog': fingerprint(CATALOG),
        'members': {action: {'path': PREFIX + path, 'catalogInstalledFile': path,
                             'sha256': digest(raw_by_action[action])} for action, path in MEMBERS.items()},
        'containerMetadata': metadata, 'positions': positions,
        'aliases': list(aliases.values()),
        'directionSemanticsConfirmed': False, 'timingConfirmed': False, 'worldAnchorConfirmed': False,
    }, rasters, icon_picture


def main():
    source, rasters, icon = inspect()
    refs = HERE / 'references'
    refs.mkdir(exist_ok=True)
    icon_path = refs / 'inventory-source.png'
    icon.save(icon_path)
    source['inventory']['reference'] = fingerprint(icon_path)
    board = Image.new('RGB', (1536, 1024), '#263b37')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=23)
    for i, (index, picture) in enumerate(rasters.items()):
        path = refs / f'{index:02}-source.png'
        picture.save(path)
        entry = source['positions'][index]
        bbox = picture.getchannel('A').point(lambda v: 255 if v >= 16 else 0).getbbox()
        entry.update(sourceReference=fingerprint(path), alpha16Box=list(bbox))
        scale = min(386 / picture.width, 352 / picture.height)
        thumb = picture.resize(tuple(round(v * scale) for v in picture.size), Image.Resampling.NEAREST)
        x, y = i % 3 * 512, i // 3 * 512
        board.paste(thumb, (x + (512 - thumb.width) // 2, y + 40 + (352 - thumb.height) // 2), thumb)
        draw.text((x + 28, y + 431), f'1658 · raw slot {index:02} · {picture.width}x{picture.height}',
                  fill='#f7ead5', font=font)
        draw.text((x + 28, y + 467), 'source only · relative sizing enlarged', fill='#f7ead5', font=font)
    board_path = refs / 'source-six-board.png'
    board.save(board_path)
    source['sourceBoard'] = {**fingerprint(board_path), 'referenceOnly': True,
                             'operation': 'Nearest-neighbor enlargement of unaltered source rasters'}
    save(HERE / 'source-contract.json', source)
    print(json.dumps({'aliasGroups': source['aliases'], 'frames': [
        [index, entry['sourceSize'], entry['sourceRawOffset'], entry['alpha16Box']]
        for index in rasters for entry in [source['positions'][index]]]}))


if __name__ == '__main__':
    main()
