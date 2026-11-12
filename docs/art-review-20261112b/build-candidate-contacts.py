"""One selected 407/2000 candidate: original density-4 PNGs on two backgrounds."""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ROWS_407 = [[0, 1, 2, 4, 5], [6, 7, 8], [12, 13, 14, 16, 17], [18, 19, 20, 22, 23]]
BACKGROUNDS = [('ivory', '#f6f0df', '#214a3d'), ('deep-teal', '#183e37', '#f4ead3')]


def project_path(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('All inputs and outputs must remain in this project')
    return path


def rel(path):
    return path.relative_to(ROOT).as_posix()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def font(size):
    for path in ('C:/Windows/Fonts/msyh.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'):
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise ValueError('A Chinese font is required for the review labels')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--item', type=int, choices=[407, 2000], required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    manifest_path, output = project_path(args.manifest), project_path(args.output)
    record_path = Path(str(output) + '.source.json')
    if output.suffix.lower() != '.png' or output.exists() or record_path.exists():
        raise ValueError('Choose a new PNG output path; existing outputs are preserved')
    manifest_bytes = manifest_path.read_bytes()
    matches = [item for item in json.loads(manifest_bytes)['items'] if item['itemId'] == args.item]
    if len(matches) != 1:
        raise ValueError('The item must occur exactly once in the selected manifest')
    frames = sorted(matches[0]['frames'], key=lambda frame: frame['sourceFrameIndex'])
    if [frame['sourceFrameIndex'] for frame in frames] != list(range(24)):
        raise ValueError('This review requires all 24 ordered source positions')

    rasters, files = {}, {}
    for frame in frames:
        if frame.get('exportDensity') != 4:
            raise ValueError('Only existing density-4 exports are accepted')
        path = project_path(frame['file'])
        name = rel(path)
        if name not in files:
            raw = path.read_bytes()
            digest = sha(raw)
            with Image.open(io.BytesIO(raw)) as opened:
                if opened.format != 'PNG' or opened.mode != 'RGBA':
                    raise ValueError(f'Expected an RGBA PNG: {name}')
                image = opened.copy()
            files[name] = digest
            if digest not in rasters:
                rasters[digest] = {'image': image, 'files': [], 'frames': [], 'provenanceRecords': []}
            rasters[digest]['files'].append({'file': name, 'sha256': digest})
        digest = files[name]
        raster = rasters[digest]
        image = raster['image']
        if digest != frame['sha256'] or list(image.size) != [frame['width'], frame['height']]:
            raise ValueError(f'PNG bytes or dimensions differ from the manifest: {name}')
        if list(image.size) != [value * 4 for value in frame['logicalFrameSize']]:
            raise ValueError(f'PNG dimensions do not match density 4: {name}')
        provenance = project_path(frame['provenanceRecord'])
        provenance_record = {'file': rel(provenance), 'sha256': sha(provenance.read_bytes())}
        if provenance_record not in raster['provenanceRecords']:
            raster['provenanceRecords'].append(provenance_record)
        raster['frames'].append({key: frame.get(key) for key in (
            'sourceFrameIndex', 'logicalFrameSize', 'frameOffsetRaw', 'file', 'sha256', 'provenanceRecord')})

    by_index = {raster['frames'][0]['sourceFrameIndex']: (digest, raster)
                for digest, raster in rasters.items()}
    rows = ROWS_407 if args.item == 407 else [list(range(row * 6, row * 6 + 6)) for row in range(4)]
    if sorted(index for row in rows for index in row) != sorted(by_index):
        raise ValueError('Unique raster representatives differ from this item review layout')
    columns = max(map(len, rows))
    max_width = max(raster['image'].width for raster in rasters.values())
    max_height = max(raster['image'].height for raster in rasters.values())
    cell_width = max(128, max_width + 20)
    row_height = max(144, max_height + 40)
    margin, gutter, header = 16, 24, 96
    side_width = columns * cell_width
    width, height = margin * 2 + gutter + side_width * 2, header + 4 * row_height
    if (args.item == 407 and not 1300 <= width <= 1800) or (args.item == 2000 and width > 3300):
        raise ValueError('Native pixels require a wider sheet than this item layout permits')
    board = Image.new('RGB', (width, height), '#f6f0df')
    draw = ImageDraw.Draw(board)
    small, title = font(12), font(20)
    draw.text((margin, 10), f'{args.item} · 待用户审核候选 · 原 PNG density4', font=title, fill='#214a3d')
    draw.text((margin, 40), '米白/深青同图同像素 · 未缩放、未镜像 · 非实机或实速验收',
              font=font(14), fill='#214a3d')
    placements = {digest: [] for digest in rasters}
    for side, (background, color, foreground) in enumerate(BACKGROUNDS):
        left = margin + side * (side_width + gutter)
        draw.rectangle((left, 66, left + side_width - 1, height - 1), fill=color)
        draw.text((left + 8, 70), '米白 · 原 PNG 1:1' if side == 0 else '深青 · 原 PNG 1:1',
                  font=font(14), fill=foreground)
        for row_index, indices in enumerate(rows):
            row_left = left + (columns - len(indices)) * cell_width // 2
            top = header + row_index * row_height
            for column, index in enumerate(indices):
                digest, raster = by_index[index]
                image = raster['image']
                cell_left = row_left + column * cell_width
                alias = [frame['sourceFrameIndex'] for frame in raster['frames'] if frame['sourceFrameIndex'] != index]
                lines = [f'idx {index} · {image.width}x{image.height}px',
                         'alias ' + (','.join(map(str, alias)) if alias else '-')]
                for line, text in enumerate(lines):
                    if draw.textlength(text, font=small) > cell_width - 12:
                        raise ValueError('A review label exceeds its cell width')
                    draw.text((cell_left + 6, top + line * 16), text, font=small, fill=foreground)
                x, y = cell_left + (cell_width - image.width) // 2, top + 36
                board.paste(image, (x, y), image)
                placements[digest].append({'background': background, 'row': row_index,
                                           'representativeSourceIndex': index,
                                           'rectLTRB': [x, y, x + image.width, y + image.height]})
    derived = []
    for index in sorted(by_index):
        digest, raster = by_index[index]
        derived.append({'representativeSourceIndex': index, 'sha256': digest,
                        'derivedPngs': raster['files'], 'pixelSize': list(raster['image'].size),
                        'aliasPositions': [frame['sourceFrameIndex'] for frame in raster['frames']],
                        'provenanceRecord': raster['provenanceRecords'][0]['file'],
                        'provenanceRecords': raster['provenanceRecords'],
                        'sourceFramesUnchanged': raster['frames'], 'placedRects': placements[digest]})
    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output, optimize=True)
    record = {'schemaVersion': 1, 'createdAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'itemId': args.item, 'file': rel(output), 'previewSha256': sha(output.read_bytes()),
              'manifest': rel(manifest_path), 'manifestSha256': sha(manifest_bytes),
              'sheetExtentPx': list(board.size), 'sourcePositionCount': len(frames),
              'uniqueRasterCount': len(rasters), 'rowRepresentativeIndices': rows,
              'newModelGeneration': False, 'userReviewStatus': 'pending', 'noGUI': True,
              'runtimeScreenshot': False, 'notRuntimeArt': True,
              'operation': 'SHA256-deduplicated selected item; standard alpha composite of exact density-4 '
                           'PNG bytes onto ivory and deep teal. No scaling, mirroring, gameplay rendering '
                           'or visual acceptance; source metadata and adoption flags remain unchanged.',
              'derivedFrom': derived}
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'item': args.item, 'preview': rel(output), 'sourceRecord': rel(record_path),
                      'sheetExtentPx': list(board.size), 'uniqueRasters': len(rasters),
                      'userReviewStatus': 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
