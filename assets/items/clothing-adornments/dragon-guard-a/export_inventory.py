"""Export six inventory PNGs from a reviewed transparent atlas."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ITEMS = [
    (1194, 'cloud-court-coat', '云庭法袍'),
    (1195, 'azure-dragon-armor', '青龙护法铠'),
    (1196, 'wind-arena-vest', '迎风武衣'),
    (1197, 'golden-cloud-armor', '金云仪卫甲'),
    (1453, 'sun-talisman-mail', '曜日符鳞甲'),
    (1460, 'ink-thunder-mail', '玄雷护身甲'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def save_json(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def alpha_bbox(alpha, threshold):
    return alpha.point(lambda value: 255 if value >= threshold else 0).getbbox()


def resize(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def export(atlas, generation, references):
    if atlas.mode != 'RGBA' or atlas.size != (1536, 1024):
        raise ValueError(f'Expected native RGBA atlas 1536×1024, got {atlas.mode} {atlas.size}')
    prepared = []
    for ordinal, (item_id, slug, name) in enumerate(ITEMS):
        left, top = ordinal % 3 * 512, ordinal // 3 * 512
        rect = (left, top, left + 512, top + 512)
        alpha = atlas.crop(rect).getchannel('A')
        edge_rects = ((0, 0, 1, 512), (0, 0, 512, 1), (511, 0, 512, 512), (0, 511, 512, 512))
        edge_max = [alpha.crop(edge).getextrema()[1] for edge in edge_rects]
        bbox = alpha_bbox(alpha, 16)
        if bbox is None or max(edge_max) >= 8:
            raise ValueError(f'{item_id}: empty or non-isolated atlas crop, edge maxima {edge_max}')
        source = references[item_id]
        if sha((ROOT / source['file']).read_bytes()) != source['sha256']:
            raise ValueError(f'{item_id}: source reference hash mismatch')
        content = atlas.crop(rect).crop(bbox)
        scale = 224 / max(content.size)
        size = tuple(round(v * scale) for v in content.size)
        placement = tuple((256 - v) // 2 for v in size)
        output = Image.new('RGBA', (256, 256))
        output.alpha_composite(resize(content, size), placement)
        visible = alpha_bbox(output.getchannel('A'), 8)
        inset = min(visible[0], visible[1], 256 - visible[2], 256 - visible[3])
        if inset < 16:
            raise ValueError(f'{item_id}: alpha inset {inset}px')
        prepared.append((output, HERE / f'{item_id}-{slug}.png', {
            'itemId': item_id,
            'category': 'cladorn',
            'resourceId': source['resourceId'],
            'sourceName': source['sourceName'],
            'projectDisplayName': name,
            'width': 256,
            'height': 256,
            'sourceReference': source['file'],
            'sourceReferenceSha256': source['sha256'],
            'sourceReferenceRecord': source['file'] + '.source.json',
            'sourceInventoryNativeFrameSize': source['nativeFrameSize'],
            'sourceInventoryFrameOffsetRaw': source['frameOffsetRaw'],
            'derivedFrom': {
                'file': generation['file'],
                'sha256': generation['sha256'],
                'generationRecord': generation['generationRecord'],
            },
            'operation': {
                'type': 'alpha-bbox-crop-uniform-fit-centred',
                'sourceCellRect': list(rect),
                'sourceCellEdgeAlphaMax': edge_max,
                'contentBoxWithinCell': list(bbox),
                'uniformScale': scale,
                'placementPx': list(placement),
                'resampler': 'premultiplied-alpha LANCZOS',
                'newModelGeneration': False,
            },
            'alphaExtrema': list(output.getchannel('A').getextrema()),
            'alpha8BBox': list(visible),
            'alpha8InsetPx': inset,
            'representation': 'inventory-icon-only',
            'worldMapped': False,
            'visualAccepted': False,
            'runtimeAdopted': False,
            'accepted': False,
            'userReviewStatus': 'pending',
        }))
    for output, path, record in prepared:
        output.save(path, optimize=True)
        record.update(file=rel(path), sha256=sha(path.read_bytes()), provenanceRecord=rel(path) + '.provenance.json')
        save_json(Path(str(path) + '.provenance.json'), record)
    return prepared


def preview(prepared, sizes, name):
    font_path = Path('C:/Windows/Fonts/msyh.ttc')
    font = ImageFont.truetype(str(font_path), 16) if font_path.exists() else ImageFont.load_default()
    cell_width = max(sizes) + 24
    side_width = cell_width * len(sizes)
    row_height = max(sizes) + 20
    label_width = 90
    board = Image.new('RGB', (label_width + side_width * 2, 45 + row_height * len(prepared)), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((label_width + side_width, 0, board.width - 1, board.height - 1), fill='#183e37')
    for side, ink in enumerate(('#214a3d', '#f4ead3')):
        for index, size in enumerate(sizes):
            x = label_width + side_width * side + cell_width * index
            draw.text((x + 12, 12), f'{size} px', font=font, fill=ink)
            for row, (output, _, record) in enumerate(prepared):
                y = 45 + row_height * row
                thumbnail = output if size == 256 else resize(output, (size, size))
                board.paste(thumbnail, (x + 12, y + (max(sizes) - size) // 2), thumbnail)
                if side == 0 and index == 0:
                    draw.text((12, y + 12), str(record['itemId']), font=font, fill=ink)
    path = HERE / name
    board.save(path, optimize=True)
    record = {
        'file': rel(path), 'sha256': sha(path.read_bytes()), 'sizesPx': sizes,
        'inputs': [{'file': r['file'], 'sha256': r['sha256'], 'itemId': r['itemId']} for _, _, r in prepared],
        'operation': 'Alpha composite on two solid colors, with premultiplied LANCZOS for smaller sizes',
        'newModelGeneration': False, 'runtimeScreenshot': False, 'userReviewStatus': 'pending',
    }
    save_json(Path(str(path) + '.source.json'), record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generation_record', type=Path)
    args = parser.parse_args()
    generation = json.loads(args.generation_record.read_bytes())
    source = ROOT / generation['file']
    if source.parent != HERE or sha(source.read_bytes()) != generation['sha256']:
        raise ValueError('Unexpected or changed generation file')
    contract = json.loads((HERE / 'source-contract.json').read_bytes())
    references = {record['itemId']: record for record in contract['items']}
    with Image.open(source) as atlas:
        prepared = export(atlas, generation, references)
    previews = [
        preview(prepared, [256], 'contact-native-256.png'),
        preview(prepared, [32, 48, 64], 'contact-mobile-32-48-64.png'),
    ]
    records = [record for _, _, record in prepared]
    save_json(HERE / 'art.json', {
        'schemaVersion': 1, 'category': 'cladorn', 'scope': 'inventory-only-static-candidates',
        'sourceCategoryTotal': 365, 'items': records, 'previews': previews,
        'visualAccepted': False, 'accepted': False, 'runtimeAdopted': False,
    })
    print(json.dumps({'itemIds': list(references), 'outputCount': len(records), 'errors': []}))


if __name__ == '__main__':
    main()
