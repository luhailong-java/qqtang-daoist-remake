"""Crop or verify the four transparent UI action icons."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ICONS = (
    ('play', 'Start the game'),
    ('pause', 'Pause the game'),
    ('close', 'Close the dialog'),
    ('next', 'Continue or enter'),
)
ICON_SIZE = 128
CONTENT_SIZE = 112


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def read_json(path):
    return json.loads(path.read_bytes())


def save_json(path, data):
    path.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode())


def visible_box(alpha, threshold):
    return alpha.point(lambda value: 255 if value >= threshold else 0).getbbox()


def resize(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def validate_generation(generation_path):
    generation = read_json(generation_path)
    if generation['actualModel'] is not None or generation['actualQuality'] is not None:
        raise ValueError('The built-in tool did not disclose the actual model or quality')
    source = ROOT / generation['file']
    if source.parent != HERE or sha(source) != generation['sha256']:
        raise ValueError('Native atlas hash mismatch')
    for entry in (generation['exactSubmittedArgs'], generation['exactPromptUtf8'],
                  generation['returnedToolEvidence'], *generation['references']):
        if sha(ROOT / entry['file']) != entry['sha256']:
            raise ValueError(f'Generation provenance differs: {entry["file"]}')
    args = read_json(ROOT / generation['exactSubmittedArgs']['file'])
    if args['transparent_background'] is not True:
        raise ValueError('Missing native alpha request')
    if (ROOT / generation['exactPromptUtf8']['file']).read_bytes() != args['prompt'].encode():
        raise ValueError('Exact prompt differs from submitted arguments')
    return generation, source


def derive(atlas, source, generation_path, generation):
    if atlas.mode != 'RGBA' or atlas.size != tuple(generation['actualNativeSize']):
        raise ValueError('Native dimensions or mode differ from the generation record')
    if atlas.width % 2 or atlas.height % 2 or atlas.width != atlas.height:
        raise ValueError('Expected an even square 2×2 native atlas')
    size = atlas.width // 2
    output_items = []
    for index, (name, meaning) in enumerate(ICONS):
        x, y = (index % 2) * size, (index // 2) * size
        rect = (x, y, x + size, y + size)
        cell = atlas.crop(rect)
        alpha = cell.getchannel('A')
        edges = ((0, 0, 1, size), (0, 0, size, 1),
                 (size - 1, 0, size, size), (0, size - 1, size, size))
        max_alpha = [alpha.crop(edge).getextrema()[1] for edge in edges]
        box = visible_box(alpha, 8)
        if box is None or max(max_alpha) >= 8:
            raise ValueError(f'{name}: empty or connected to cell boundary, alpha {max_alpha}')
        left, top, right, bottom = box
        native_inset = min(left, top, size - right, size - bottom)
        if native_inset < 8:
            raise ValueError(f'{name}: insufficient clean atlas space')
        content = cell.crop(box)
        scale = CONTENT_SIZE / max(content.size)
        scaled = tuple(round(v * scale) for v in content.size)
        placement = tuple((ICON_SIZE - v) // 2 for v in scaled)
        output = Image.new('RGBA', (ICON_SIZE, ICON_SIZE))
        output.alpha_composite(resize(content, scaled), placement)
        output_box = visible_box(output.getchannel('A'), 8)
        inset = min(output_box[0], output_box[1], ICON_SIZE - output_box[2], ICON_SIZE - output_box[3])
        if inset < 8:
            raise ValueError(f'{name}: the export has insufficient transparent padding')
        path = HERE / (name + '.png')
        record = {
            'id': name,
            'meaning': meaning,
            'file': rel(path),
            'width': ICON_SIZE,
            'height': ICON_SIZE,
            'mode': 'RGBA',
            'derivedFrom': {
                'file': rel(source),
                'sha256': generation['sha256'],
                'generationRecord': rel(generation_path),
            },
            'operation': {
                'type': 'alpha-content crop and uniform centred fit',
                'sourceRectLTRB': list(rect),
                'sourceAlpha8BoxWithinCell': list(box),
                'sourceCellEdgeAlphaMax': max_alpha,
                'sourceAlpha8InsetPx': native_inset,
                'uniformScale': scale,
                'placementPx': list(placement),
                'resampler': 'premultiplied-alpha LANCZOS',
                'newModelGeneration': False,
            },
            'alpha8BBox': list(output_box),
            'alpha8InsetPx': inset,
            'alphaExtrema': list(output.getchannel('A').getextrema()),
            'provenanceRecord': rel(path) + '.provenance.json',
            'visualAccepted': False,
            'userReviewStatus': 'pending',
        }
        output_items.append((path, output, record))
    return output_items


def diagnostics(items):
    sizes = [16, 20, 24, 32, 128]
    row_height = 140
    label_width = 90
    cell_width = 70
    side_width = (len(sizes) - 1) * cell_width + 152
    light, dark = '#f6f0df', '#183e37'
    board = Image.new('RGB', (label_width + side_width * 2, 45 + row_height * len(items)), light)
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=16)
    draw.rectangle((label_width + side_width, 0, board.width - 1, board.height - 1), fill=dark)
    for side, ink in enumerate(('#214a3d', '#f4ead3')):
        for col, size in enumerate(sizes):
            x = label_width + side_width * side + cell_width * col
            width = 152 if size == ICON_SIZE else cell_width
            draw.text((x + 10, 13), f'{size}px', font=font, fill=ink)
            for row, (_, output, record) in enumerate(items):
                y = 45 + row_height * row
                icon = output if size == ICON_SIZE else resize(output, (size, size))
                board.paste(icon, (x + (width - size) // 2, y + (row_height - size) // 2), icon)
                if side == 0 and col == 0:
                    draw.text((14, y + 60), record['id'], font=font, fill=ink)
    return board


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generation_path = HERE / 'actions-v1.png.generation.json'
    generation, source = validate_generation(generation_path)
    with Image.open(source) as atlas:
        items = derive(atlas, source, generation_path, generation)
    preview_path = HERE / 'contact-16-20-24-32-128.png'
    preview = diagnostics(items)
    for path, output, record in items:
        if args.check:
            with Image.open(path) as actual:
                if actual.mode != output.mode or actual.size != output.size or actual.tobytes() != output.tobytes():
                    raise ValueError(f'Export replay mismatch: {path}')
        else:
            output.save(path, optimize=True)
        record['sha256'] = sha(path)
        if args.check:
            if read_json(ROOT / record['provenanceRecord']) != record:
                raise ValueError(f'Provenance mismatch: {path}')
        else:
            save_json(ROOT / record['provenanceRecord'], record)
    if args.check:
        with Image.open(preview_path) as actual:
            if actual.size != preview.size or actual.tobytes() != preview.tobytes():
                raise ValueError('Preview replay mismatch')
    else:
        preview.save(preview_path, optimize=True)
    preview_record = {
        'file': rel(preview_path), 'sha256': sha(preview_path),
        'sizesPx': [16, 20, 24, 32, 128],
        'backgrounds': ['#f6f0df', '#183e37'],
        'inputs': [{'file': r['file'], 'sha256': r['sha256']} for _, _, r in items],
        'operation': 'Diagnostic composites on two solid background colors',
        'newModelGeneration': False, 'runtimeScreenshot': False,
    }
    manifest = {
        'schemaVersion': 1, 'scope': 'Four in-game UI action icon assets',
        'items': [entry for _, _, entry in items], 'preview': preview_record,
        'visualAccepted': False, 'userReviewStatus': 'pending',
    }
    if args.check:
        if read_json(HERE / 'manifest.json') != manifest:
            raise ValueError('Manifest differs from replay')
    else:
        save_json(HERE / 'manifest.json', manifest)
    print(json.dumps({
        'icons': [icon[0] for icon in ICONS], 'count': len(items),
        'maximumSourceCropEdgeAlpha': max(max(r['operation']['sourceCellEdgeAlphaMax']) for _, _, r in items),
        'minimumOutputAlpha8InsetPx': min(r['alpha8InsetPx'] for _, _, r in items),
        'manifestSha256': sha(HERE / 'manifest.json'),
        'pixelsVerifiedByReplay': args.check, 'errors': [],
    }))


if __name__ == '__main__':
    main()
