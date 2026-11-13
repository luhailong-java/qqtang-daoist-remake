"""Export and verify six static, full-bleed scenic inventory thumbnails."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ITEMS = [
    (3, 'spring-willow-bank', '春柳汀'),
    (4, 'summer-tide', '夏潮湾'),
    (1, 'autumn-gold-trail', '秋金径'),
    (2, 'snow-shelter', '雪檐小筑'),
    (7, 'mist-cloud-sea', '云海观'),
    (55, 'moss-stone-trail', '苔石幽径'),
]
TOTAL = 395
GENERATED = 'four-seasons-a-v1.png.generation.json'


def read(path):
    return json.loads(path.read_bytes())


def save(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fingerprint(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}


def check_file(record):
    path = ROOT / record['file']
    if fingerprint(path)['sha256'] != record['sha256']:
        raise ValueError(f'SHA mismatch: {path}')
    return path


def reproduce_thumbnail(atlas, rect):
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= atlas.width and 0 <= y1 < y2 <= atlas.height
            and x2 - x1 == y2 - y1 >= 256):
        raise ValueError(f'Invalid uniform square crop: {rect}')
    art = atlas.crop(rect).convert('RGBA')
    if art.getchannel('A').getextrema() != (255, 255):
        raise ValueError(f'Thumbnail contains unexpected transparent pixels: {rect}')
    return art.resize((256, 256), Image.Resampling.LANCZOS)


def check_panel_crops(atlas, crops):
    if atlas.size != (1536, 1024):
        raise ValueError('Expected a 3 by 2 atlas of 512 px squares')
    for index, crop in enumerate(crops):
        x, y = index % 3 * 512, index // 3 * 512
        if crop['xyxy'] != [x + 8, y + 8, x + 504, y + 504]:
            raise ValueError(f"{crop['itemId']}: crop does not preserve the 8 px seam guard")


def review_board(pictures, sizes):
    cell = max(sizes) + 22
    board = Image.new('RGB', (65 + cell * len(sizes), 37 + cell * len(pictures)), '#f6f0df')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=13)
    for column, size in enumerate(sizes):
        draw.text((76 + column * cell, 12), f'{size} px', font=font, fill='#214a3d')
    for row, ((item_id, _, _), picture) in enumerate(zip(ITEMS, pictures, strict=True)):
        y = 37 + row * cell
        draw.text((12, y + cell // 2), str(item_id), font=font, fill='#214a3d')
        for column, size in enumerate(sizes):
            thumb = picture if size == 256 else picture.resize((size, size), Image.Resampling.LANCZOS)
            board.paste(thumb.convert('RGB'), (76 + column * cell, y + (cell - size) // 2))
    return board


def export(atlas, generated, contract):
    records, pictures = [], []
    for (item_id, slug, label), source, crop in zip(
            ITEMS, contract['items'], generated['selectedSourceRects'], strict=True):
        if item_id != source['itemId'] or item_id != crop['itemId']:
            raise ValueError('Source, crop and export orders must agree')
        check_file(source)
        rect = crop['xyxy']
        picture = reproduce_thumbnail(atlas, rect)
        path = HERE / f'{item_id}-{slug}.png'
        picture.save(path, optimize=True)
        provenance = path.with_name(path.name + '.provenance.json')
        record = {
            'itemId': item_id, 'category': 'bg', 'resourceId': source['resourceId'],
            'sourceName': source['sourceName'], 'projectDisplayName': label,
            **fingerprint(path), 'provenanceRecord': provenance.relative_to(ROOT).as_posix(),
            'width': 256, 'height': 256, 'alphaExtrema': [255, 255],
            'sourceReference': source['file'], 'sourceReferenceSha256': source['sha256'],
            'sourceReferenceRecord': source['file'] + '.source.json',
            'sourceInventoryNativeFrameSize': source['nativeFrameSize'],
            'sourceInventoryFrameOffsetRaw': source['frameOffsetRaw'],
            'derivedFrom': {key: generated[key] for key in ('file', 'sha256', 'generationRecord')},
            'operation': {'type': 'protected-square-panel-crop-uniform-scale', 'sourceCellRect': rect,
                          'resampler': 'LANCZOS', 'newModelGeneration': False},
            'representation': 'inventory-icon-only', 'worldMapped': False,
            'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
            'userReviewStatus': 'pending',
        }
        save(provenance, record)
        records.append(record)
        pictures.append(picture)
    previews = []
    for sizes, name in (([256], 'contact-native-256.png'), ([32, 48, 64], 'contact-mobile-32-48-64.png')):
        path = HERE / name
        review_board(pictures, sizes).save(path, optimize=True)
        preview = {
            **fingerprint(path), 'sizesPx': sizes,
            'inputs': [{k: item[k] for k in ('itemId', 'file', 'sha256')} for item in records],
            'operation': 'Composite thumbnails on neutral parchment for review',
            'runtimeScreenshot': False, 'userReviewStatus': 'pending',
        }
        save(path.with_name(path.name + '.source.json'), preview)
        previews.append(preview)
    save(HERE / 'art.json', {
        'schemaVersion': 1, 'category': 'bg', 'scope': 'inventory-only-static-candidates',
        'sourceCategoryTotal': TOTAL, 'items': records, 'previews': previews,
        'visualAccepted': False, 'accepted': False, 'runtimeAdopted': False,
    })


def verify(atlas, generated, contract):
    manifest_path = HERE / 'art.json'
    manifest = read(manifest_path)
    expected_ids = [item_id for item_id, _, _ in ITEMS]
    if (manifest['category'] != 'bg' or manifest['sourceCategoryTotal'] != TOTAL
            or [item['itemId'] for item in manifest['items']] != expected_ids
            or any(manifest[key] for key in ('accepted', 'visualAccepted', 'runtimeAdopted'))):
        raise ValueError('Unexpected manifest scope, IDs or approval')
    args = read(check_file(generated['exactSubmittedArgs']))
    if (args['route'] != 'builtin' or args['input']['transparent_background'] is not False
            or check_file(generated['exactPromptUtf8']).read_bytes() != args['input']['prompt'].encode()
            or generated['actualModel'] is not None or generated['actualQuality'] is not None):
        raise ValueError('Unexpected generation provenance')
    check_file(read(HERE / 'references/source-six-board.png.source.json'))
    for entry in generated['references']:
        check_file(entry)
    archive_path = ROOT / contract['items'][0]['sourceArchive']['file']
    with archive_path.open('rb') as stream:
        archive_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    catalog_bytes = (ROOT / contract['items'][0]['catalog']).read_bytes()
    category = {item['item_id']: item for item in json.loads(catalog_bytes)['items']
                if item['category'] == 'bg'}
    if len(category) != TOTAL:
        raise ValueError('Catalog category total differs')
    reader_spec = importlib.util.spec_from_file_location('inventory_bg_decoder', ROOT / 'scripts/inspect-reference-dimg.py')
    reader = importlib.util.module_from_spec(reader_spec)
    reader_spec.loader.exec_module(reader)
    pictures = []
    with ZipFile(archive_path) as archive:
        for item, source, crop in zip(manifest['items'], contract['items'], generated['selectedSourceRects'], strict=True):
            item_id = item['itemId']
            if (source['itemId'] != item_id or crop['itemId'] != item_id
                    or source['resourceId'] != category[item_id]['resource_id']
                    or source['catalogInstalledFile'] not in category[item_id]['installed_files']
                    or source['sourceMember'] != 'QQTang-Local/runtime/client-patched/' + source['catalogInstalledFile']
                    or source['sourceArchive']['sha256'] != archive_sha
                    or source['catalogSha256'] != digest(catalog_bytes)
                    or read(ROOT / item['sourceReferenceRecord']) != source):
                raise ValueError(f'{item_id}: source identity or evidence differs')
            raw = archive.read(source['sourceMember'])
            metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
            frame = next(entry for entry in metadata['frames'] if not entry['empty'])
            offset = frame['pixelDataOffset']
            pixels = reader.decode_frame_pixels(raw[offset:offset + frame['pixelByteLength']],
                                                frame['pixelMode'], frame['width'], frame['height'])
            with Image.open(check_file(source)) as thumbnail:
                if (digest(raw) != source['sourceMemberSha256'] or frame != source['sourceFrameRecord']
                        or frame['frameOffset'] != item['sourceInventoryFrameOffsetRaw']
                        or thumbnail.size != tuple(item['sourceInventoryNativeFrameSize'])
                        or thumbnail.tobytes() != pixels):
                    raise ValueError(f'{item_id}: source decoding differs')
            expected = reproduce_thumbnail(atlas, crop['xyxy'])
            with Image.open(check_file(item)) as actual:
                if actual.mode != 'RGBA' or actual.size != (256, 256) or actual.tobytes() != expected.tobytes():
                    raise ValueError(f'{item_id}: output differs from exact crop replay')
            if (item['operation']['sourceCellRect'] != crop['xyxy']
                    or any(item[k] for k in ('accepted', 'visualAccepted', 'runtimeAdopted', 'worldMapped'))
                    or item != read(ROOT / item['provenanceRecord'])):
                raise ValueError(f'{item_id}: provenance or approval differs')
            pictures.append(expected)
    for entry in manifest['previews']:
        preview = check_file(entry)
        with Image.open(preview) as actual:
            expected = review_board(pictures, entry['sizesPx'])
            if actual.mode != 'RGB' or actual.size != expected.size or actual.tobytes() != expected.tobytes():
                raise ValueError('Preview differs from exact replay')
        if read(preview.with_name(preview.name + '.source.json')) != entry:
            raise ValueError('Preview provenance differs')
    return {
        'itemIds': expected_ids, 'sourceCategoryCount': len(category), 'checkedSourceMembers': len(pictures),
        'checkedExports': len(pictures), 'pixelReplayExact': True, 'checkedPreviews': len(manifest['previews']),
        'generationSha256': generated['sha256'], 'manifestSha256': fingerprint(manifest_path)['sha256'],
        'worldCandidatePositions': 0, 'technicalFileChecksPassed': True,
        'visualAccepted': False, 'runtimeAdopted': False, 'errors': [],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='write thumbnails and previews, then verify')
    args = parser.parse_args()
    generated = read(HERE / GENERATED)
    contract = read(HERE / 'source-contract.json')
    with Image.open(check_file(generated)) as atlas:
        if (atlas.format != 'PNG' or atlas.mode != generated['mode']
                or atlas.size != (generated['width'], generated['height'])):
            raise ValueError('Native atlas metadata differs')
        check_panel_crops(atlas, generated['selectedSourceRects'])
        if args.export:
            export(atlas, generated, contract)
        print(json.dumps(verify(atlas, generated, contract), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
