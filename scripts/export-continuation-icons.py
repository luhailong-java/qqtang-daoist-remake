"""Export or replay the Nov 13 direction and profile-medal sprite sheets."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TOUCH = (('up', '向上'), ('left', '向左'), ('down', '向下'), ('right', '向右'))
MEDALS = (
    ('2398-frost-seal', '霜花蓝玉章'), ('2399-lantern', '赤灯金穗章'),
    ('2400-four-leaf-jade', '四叶青玉章'), ('2401-ice-sword', '寒锋玉剑章'),
    ('2402-dragon-boat', '金龙彩舟章'), ('2403-cloud-shield', '云纹银盾章'),
)


def rel(path):
    return path.relative_to(ROOT).as_posix()


def read(path):
    return json.loads(path.read_bytes())


def entry(path):
    return {'file': rel(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verify(record):
    if entry(ROOT / record['file'])['sha256'] != record['sha256']:
        raise ValueError(f"Changed source: {record['file']}")


def save_json(path, data, check):
    if check:
        if read(path) != data:
            raise ValueError(f'JSON replay mismatch: {path}')
    else:
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def save_image(path, image, check):
    if check:
        with Image.open(path) as previous:
            if (previous.size, previous.mode, previous.tobytes()) != (image.size, image.mode, image.tobytes()):
                raise ValueError(f'Image replay mismatch: {path}')
    else:
        image.save(path, optimize=True)


def scaled(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def bbox(alpha):
    return alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()


def preview(items, sizes):
    row_height = max(sizes) + 24
    col_widths = [max(60, size + 18) for size in sizes]
    half_width = sum(col_widths)
    label_width = 75
    board = Image.new('RGB', (label_width + 2 * half_width, 32 + row_height * len(items)), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((label_width + half_width, 0, board.width - 1, board.height - 1), fill='#183e37')
    font = ImageFont.load_default(size=13)
    for side, ink in enumerate(('#214a3d', '#f4ead3')):
        x = label_width + half_width * side
        for size, width in zip(sizes, col_widths, strict=True):
            draw.text((x + 8, 8), f'{size}px', fill=ink, font=font)
            for row, (image, label) in enumerate(items):
                y = 32 + row * row_height
                thumb = image if image.width == size else scaled(image, (size, size))
                board.paste(thumb, (x + (width - size) // 2, y + (row_height - size) // 2), thumb)
                if x == label_width:
                    draw.text((10, y + 5), label, fill=ink, font=font)
            x += width
    return board


def run(group, check):
    medals = group == 'medals'
    directory, base, items, columns, size, fill, scales = (
        ('assets/items/profile-frames/elemental-medals', 'elemental-medals-v1', MEDALS, 3, 256, 224, [32, 48, 64, 256]) if medals else
        ('assets/ui/touch-icons-20261113', 'jade-touch-v1', TOUCH, 2, 128, 112, [20, 24, 32, 128])
    )
    here = ROOT / directory
    generation_path = here / f'{base}.png.generation.json'
    generation = read(generation_path)
    for rec in (generation, generation['exactSubmittedArgs'], generation['exactPromptUtf8'],
                generation['returnedToolEvidence'], *generation['references']):
        verify(rec)
    args = read(ROOT / generation['exactSubmittedArgs']['file'])
    submitted_paths = [path.replace('\\', '/') for path in args['referenced_image_paths']]
    if (set(args) != {'transparent_background', 'prompt', 'referenced_image_paths'} or not args['transparent_background']
            or (ROOT / generation['exactPromptUtf8']['file']).read_bytes() != args['prompt'].encode()
            or generation['actualModel'] is not None or generation['actualQuality'] is not None
            or len(submitted_paths) != len(generation['references'])
            or not all(path.endswith('/' + record['file'])
                       for path, record in zip(submitted_paths, generation['references'], strict=True))):
        raise ValueError('Generation record differs from the submitted inputs or disclosed settings')
    sources = {}
    if medals:
        contract = read(here / 'source-contract.json')
        catalog = read(ROOT / 'references/qqtang-item-data/catalog.json')
        by_id = {i['item_id']: i for i in catalog['items']}
        sources = {r['itemId']: r for r in contract['items']}
        for item_id, source in sources.items():
            verify(source)
            verify({'file': source['catalog'], 'sha256': source['catalogSha256']})
            i = by_id[item_id]
            if (i['category'] != 'frame' or i['resource_id'] != source['resourceId']
                    or source['catalogInstalledFile'] not in i['installed_files']
                    or source['relatedDisplayPath'] not in i['installed_files']
                    or source['sourceMember'] != 'QQTang-Local/runtime/client-patched/' + source['catalogInstalledFile']):
                raise ValueError(f'Profile border source mismatch: {item_id}')
    outputs, previews = [], []
    with Image.open(ROOT / generation['file']) as atlas:
        if (atlas.mode != 'RGBA' or list(atlas.size) != generation['actualNativeSize']
                or atlas.width % columns or atlas.height % 2 or atlas.width // columns != atlas.height // 2):
            raise ValueError('Atlas must have exactly equal RGBA square cells')
        cell = atlas.width // columns
        for index, (slug, name) in enumerate(items):
            x, y = index % columns * cell, index // columns * cell
            rect = (x, y, x + cell, y + cell)
            image = atlas.crop(rect)
            alpha = image.getchannel('A')
            edges = [(0, 0, 1, cell), (0, 0, cell, 1), (cell - 1, 0, cell, cell), (0, cell - 1, cell, cell)]
            max_edge = max(alpha.crop(e).getextrema()[1] for e in edges)
            visible = bbox(alpha)
            if visible is None or max_edge >= 8 or min(visible[0], visible[1], cell-visible[2], cell-visible[3]) < 8:
                raise ValueError(f'Atlas isolation failed: {slug}')
            content = image.crop(visible)
            scale = fill / max(content.size)
            fitted = tuple(round(axis * scale) for axis in content.size)
            origin = tuple((size - axis) // 2 for axis in fitted)
            output = Image.new('RGBA', (size, size))
            output.alpha_composite(scaled(content, fitted), origin)
            l, t, r, b = bbox(output.getchannel('A'))
            if min(l, t, size-r, size-b) < (size-fill)//2:
                raise ValueError(f'Export padding failed: {slug}')
            path = here / f'{slug}.png'
            save_image(path, output, check)
            record = {
                **entry(path), 'width': size, 'height': size, 'mode': 'RGBA',
                'projectDisplayName': name, 'visualAccepted': False, 'userReviewStatus': 'pending',
                'runtimeAdopted': not medals,
                'derivedFrom': {**entry(ROOT / generation['file']), 'generationRecord': rel(generation_path)},
                'operation': {'type': 'alpha crop and uniform centered fit', 'newModelGeneration': False,
                              'sourceRectLTRB': list(rect), 'sourceAlpha8Box': list(visible), 'maximumSourceCropEdgeAlpha': max_edge,
                              'uniformScale': scale, 'placementPx': list(origin), 'resampler': 'premultiplied-alpha LANCZOS'},
                'alpha8BBox': [l, t, r, b], 'alphaExtrema': list(output.getchannel('A').getextrema()),
                'provenanceRecord': rel(path) + '.provenance.json',
            }
            if medals:
                source = sources[int(slug.split('-')[0])]
                record.update({k: source[k] for k in ('itemId', 'category', 'resourceId', 'sourceName')})
                record.update(sourceReference=source['file'], sourceReferenceSha256=source['sha256'],
                              sourceReferenceRecord=source['file'] + '.source.json',
                              sourceInventoryNativeFrameSize=source['nativeFrameSize'],
                              sourceInventoryFrameOffsetRaw=source['frameOffsetRaw'],
                              relatedDisplayPath=source['relatedDisplayPath'], worldMapped=False,
                              accepted=False, representation='inventory-icon-only')
            else:
                record['id'] = slug
            save_json(ROOT / record['provenanceRecord'], record, check)
            outputs.append(record)
            previews.append((output, str(record.get('itemId', slug))))
    contact = here / ('contact-' + '-'.join(map(str, scales)) + '.png')
    save_image(contact, preview(previews, scales), check)
    save_json(here / ('art.json' if medals else 'manifest.json'), {
        'schemaVersion': 1, 'category': 'frame' if medals else 'touch-direction-icons',
        'scope': 'inventory-only-static-candidates' if medals else 'runtime touch-control art',
        'items': outputs, 'preview': {**entry(contact), 'sizesPx': scales, 'newModelGeneration': False,
                                    'runtimeScreenshot': False, 'inputs': [{k: o[k] for k in ('file', 'sha256')} for o in outputs]},
        'visualAccepted': False, 'runtimeAdopted': not medals,
    }, check)
    print(f'{group}: {len(outputs)} exact RGBA exports; max crop edge alpha {max(o["operation"]["maximumSourceCropEdgeAlpha"] for o in outputs)}; replay={check}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    options = parser.parse_args()
    for name in ('touch', 'medals'):
        run(name, options.check)
