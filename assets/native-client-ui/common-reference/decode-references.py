"""Decode the complete packed common UI group as static source references."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
source = ROOT / '.artifacts/reference-inputs'
spec = importlib.util.spec_from_file_location('common_dimg', ROOT / 'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    package_path, index_path = source / 'object.pkg', source / 'object.idx'
    package, index = package_path.read_bytes(), index_path.read_bytes()
    items = [entry for entry in reader.parse_index(index, len(package))['entries']
             if entry['path'].replace('\\', '/').lower().startswith('object/ui/common/')]
    if len(items) != 28:
        raise ValueError('Expected all 28 common resources')
    inventory_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    resources = []
    icon_rows, glyph_rows = [], []
    for entry in items:
        raw, compressed_sha = reader.unpack_resource(package, entry)
        metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
        name = entry['path'].replace('\\', '/')
        source_record = next(r for r in inventory['resources'] if r['canonicalPath'] == name.lower())
        if hashlib.sha256(raw).hexdigest() != source_record['sourceSha256']:
            raise ValueError('Native inventory source SHA differs')
        frames = []
        for frame in metadata['frames']:
            if frame['empty']:
                continue
            start = frame['pixelDataOffset']
            encoded = raw[start:start + frame['pixelByteLength']]
            pixels = reader.decode_frame_pixels(encoded, frame['pixelMode'], frame['width'], frame['height'])
            image = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
            png = HERE / 'source' / f'{Path(name).stem}-{frame["index"]:02}.png'
            png.parent.mkdir(exist_ok=True)
            image.save(png)
            frames.append({**record(png), 'sourceFrame': frame, 'rgbaSha256': hashlib.sha256(pixels).hexdigest()})
            target = glyph_rows if Path(name).stem.lower().startswith('number') else icon_rows
            target.append((name, frame, image))
        resources.append({'nativePath': name, 'sourceSha256': hashlib.sha256(raw).hexdigest(),
                          'compressedSha256': compressed_sha, 'packageEntry': entry,
                          'metadata': metadata, 'frames': frames,
                          'sourceBindings': [inventory['bindings'][i] for i in source_record.get('exactBindingIds', [])]})
    preview_records = []
    for rows, name, width, cell_height in ((icon_rows, 'source-controls-all-frames.png', 1060, 134),
                                           (glyph_rows, 'source-numbers.png', 1620, 180)):
        board = Image.new('RGB', (width, cell_height * len(rows)), '#ede7d4')
        draw = ImageDraw.Draw(board)
        font = ImageFont.load_default(size=16)
        for i, (native, frame, image) in enumerate(rows):
            y = i * cell_height
            label = f'{Path(native).name}  raw {frame["index"]}  {image.width}x{image.height}  offset {frame["frameOffset"]}'
            draw.text((8, y + 5), label, font=font, fill='#244d3c')
            scale = min(2, (width - 20) / image.width, (cell_height - 35) / image.height)
            thumb = image.resize(tuple(max(1, round(v * scale)) for v in image.size), Image.Resampling.NEAREST)
            board.paste(thumb, (8, y + 32), thumb)
        path = HERE / name
        board.save(path)
        preview_records.append({**record(path), 'role': 'source reference only'})
    controls = [r for r in resources if not Path(r['nativePath']).stem.lower().startswith('number')]
    board = Image.new('RGB', (1200, len(controls) * 124), '#ede7d4')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=17)
    for i, item in enumerate(controls):
        y = i * 124
        draw.text((8, y + 4), Path(item['nativePath']).name, font=font, fill='#244d3c')
        for j, frame in enumerate(item['frames']):
            with Image.open(ROOT / frame['file']) as art:
                thumb = art.copy()
            scale = min(2, 260 / thumb.width, 87 / thumb.height)
            thumb = thumb.resize(tuple(max(1, round(v * scale)) for v in thumb.size), Image.Resampling.NEAREST)
            x = j * 295 + 10
            draw.text((x, y + 26), f'raw {j}', font=font, fill='#244d3c')
            board.paste(thumb, (x + 35, y + 28), thumb)
    path = HERE / 'source-controls-compact.png'
    board.save(path)
    preview_records.append({**record(path), 'role': 'all common control frames, source reference only'})
    board = Image.new('RGB', (1500, len(glyph_rows) * 125), '#264d42')
    draw = ImageDraw.Draw(board)
    for row, (name, frame, picture) in enumerate(glyph_rows):
        metadata = next(r['metadata'] for r in resources if r['nativePath'] == name)
        canvas = Image.new('RGBA', tuple(metadata['declaredCanvas']))
        canvas.alpha_composite(picture, tuple(frame['frameOffset']))
        cw = canvas.width // 15
        draw.text((8, row * 125 + 3), Path(name).name, font=font, fill='#f7efd8')
        for column in range(15):
            glyph = canvas.crop((column * cw, 0, (column + 1) * cw, canvas.height))
            scale = min(76 / glyph.width, 85 / glyph.height)
            glyph = glyph.resize(tuple(max(1, round(v * scale)) for v in glyph.size), Image.Resampling.NEAREST)
            x, y = column * 100 + 10, row * 125 + 30
            draw.text((x, y), str(column), font=font, fill='#f7efd8')
            board.paste(glyph, (x + 20, y + 2), glyph)
    path = HERE / 'source-number-cells-observed.png'
    board.save(path)
    preview_records.append({**record(path), 'role': 'visually observed 15-cell partition candidate; runtime cell evidence recorded separately'})
    result = {'schemaVersion': 1, 'scope': 'All 28 packed native common resources',
              'package': record(package_path), 'index': record(index_path),
              'inventory': record(inventory_path), 'decodeScript': record(Path(__file__)),
              'resources': resources, 'previews': preview_records,
              'originalClientExecuted': False}
    (HERE / 'manifest.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'resources': len(resources), 'frames': sum(len(r['frames']) for r in resources)}))


if __name__ == '__main__':
    main()
