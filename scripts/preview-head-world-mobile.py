"""One explicitly selected world item: 32/48/64px diagnostics, awaiting human review."""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZES = (32, 48, 64)
BACKGROUNDS = (('light', '#f6f0df', '#214a3d'), ('dark', '#183e37', '#f4ead3'))


def project_path(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('All inputs and outputs must remain inside this project')
    return path


def relative(path):
    return path.relative_to(ROOT).as_posix()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def alpha_box(image):
    box = image.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
    return list(box) if box else None


def font(size):
    for name in ('C:/Windows/Fonts/msyh.ttc',
                 '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'):
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    raise ValueError('A Chinese font is required for the diagnostic labels')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--item', type=int, required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    manifest_path = project_path(args.manifest)
    output = project_path(args.output)
    provenance = Path(str(output) + '.source.json')
    if output.suffix.lower() != '.png':
        raise ValueError('--output must be a PNG path')
    if output.exists() or provenance.exists():
        raise ValueError('Output already exists; choose a new versioned output path')
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    matches = [item for item in manifest['items'] if item['itemId'] == args.item]
    if len(matches) != 1:
        raise ValueError('The selected item must occur exactly once in this manifest')
    frames = matches[0]['frames']
    if not frames:
        raise ValueError('The selected item has no source positions')

    # Only the selected item's files are decoded. Exact raster hashes share a row.
    rasters, files, source_positions, seen_indices = {}, {}, [], set()
    for frame in frames:
        index = frame['sourceFrameIndex']
        if not isinstance(index, int) or index in seen_indices:
            raise ValueError('Invalid or duplicate source frame index')
        seen_indices.add(index)
        reference = {key: frame.get(key) for key in (
            'sourceFrameIndex', 'logicalFrameSize', 'rawOffset', 'frameOffsetRaw',
            'exportDensity', 'width', 'height')}
        if frame.get('empty') is True:
            reference['empty'] = True
            source_positions.append(reference)
            continue
        path = project_path(frame['file'])
        if path.suffix.lower() != '.png':
            raise ValueError('Selected world rasters must be PNG files')
        name = relative(path)
        if name not in files:
            raw = path.read_bytes()
            sha = digest(raw)
            with Image.open(io.BytesIO(raw)) as opened:
                if opened.format != 'PNG' or opened.mode != 'RGBA':
                    raise ValueError(f'Expected an RGBA PNG: {name}')
                image = opened.copy()
            files[name] = {'file': name, 'sha256': sha, 'sourceCanvas': list(image.size)}
            if sha not in rasters:
                rasters[sha] = {'image': image, 'files': [], 'sourceFrames': []}
            rasters[sha]['files'].append(files[name])
        sha = files[name]['sha256']
        if sha != frame['sha256']:
            raise ValueError(f'PNG hash differs from manifest: {name}')
        reference.update(file=name, sha256=sha)
        source_positions.append(reference)
        rasters[sha]['sourceFrames'].append(reference)
    if not rasters:
        raise ValueError('The selected item has no nonempty PNG candidates')

    label_w, cell_w, row_h, header_h = 190, 104, 110, 122
    width = label_w + 6 * cell_w
    board = Image.new('RGB', (width, header_h + len(rasters) * row_h), '#f6f0df')
    draw = ImageDraw.Draw(board)
    text_font, title_font = font(14), font(21)
    draw.text((16, 12), f'物品 {args.item} · 诊断预览 · 人审待定', font=title_font, fill='#214a3d')
    draw.text((16, 45), '32 / 48 / 64px 最大边 · 非手游尺寸/挂点验收', font=text_font, fill='#214a3d')
    draw.text((16, 68), '等比缩小，不放大；原逻辑画布与 rawOffset 只记录，不修改。', font=text_font, fill='#214a3d')
    records = []
    for side, (background_name, color, foreground) in enumerate(BACKGROUNDS):
        left = label_w + side * 3 * cell_w
        draw.rectangle((left, 92, left + 3 * cell_w - 1, board.height - 1), fill=color)
        for column, size in enumerate(SIZES):
            draw.text((left + column * cell_w + 17, 96),
                      f'{background_name} {size}px', font=text_font, fill=foreground)
    for row, (sha, raster) in enumerate(rasters.items()):
        image = raster['image']
        y = header_h + row * row_h
        indices = ','.join(str(frame['sourceFrameIndex']) for frame in raster['sourceFrames'])
        draw.text((12, y + 10), f'PNG {row + 1} / frame', font=text_font, fill='#214a3d')
        draw.text((12, y + 32), indices if len(indices) <= 21 else indices[:18] + '...',
                  font=text_font, fill='#214a3d')
        draw.text((12, y + 55), f'{image.width} x {image.height}px', font=text_font, fill='#214a3d')
        thumbnails = []
        for column, limit in enumerate(SIZES):
            scale = min(1.0, limit / max(image.size))
            extent = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
            thumb = image.convert('RGBa').resize(extent, Image.Resampling.LANCZOS).convert('RGBA')
            placements = []
            for side, (background_name, _, foreground) in enumerate(BACKGROUNDS):
                x = label_w + (side * 3 + column) * cell_w + (cell_w - thumb.width) // 2
                top = y + (70 - thumb.height) // 2
                board.paste(thumb, (x, top), thumb)
                draw.text((label_w + (side * 3 + column) * cell_w + 15, y + 76),
                          f'{thumb.width} x {thumb.height}', font=text_font, fill=foreground)
                placements.append({'background': background_name, 'rectLTRB':
                                   [x, top, x + thumb.width, top + thumb.height]})
            thumbnails.append({'requestedMaxEdgePx': limit, 'actualExtentPx': list(extent),
                               'nominalUniformScale': scale, 'sourceCanvasAspect': image.width / image.height,
                               'thumbnailCanvasAspect': thumb.width / thumb.height,
                               'roundingRelativeAspectDeviation': abs((thumb.width / thumb.height) /
                                                                      (image.width / image.height) - 1),
                               'alpha8BBoxLTRB': alpha_box(thumb), 'sheetPlacements': placements})
        records.append({'sha256': sha, 'originalPngs': raster['files'],
                        'sourceFramesUnchanged': raster['sourceFrames'],
                        'sourceAlpha8BBoxLTRB': alpha_box(image), 'thumbnails': thumbnails})
    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output, optimize=True)
    record = {'schemaVersion': 1, 'createdAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'itemId': args.item, 'manifest': relative(manifest_path), 'manifestSha256': digest(manifest_bytes),
              'file': relative(output), 'sha256': digest(output.read_bytes()), 'sheetExtentPx': list(board.size),
              'diagnosticOnly': True, 'userReviewStatus': 'pending', 'newModelGeneration': False,
              'runtimeScreenshot': False, 'sizesPx': list(SIZES), 'sourcePositionCount': len(frames),
              'uniquePngFileCount': len(files), 'uniqueRasterCount': len(rasters),
              'operation': 'SHA256-deduplicated selected item; premultiplied-alpha LANCZOS uniform downscale '
                           'without upscaling; integer extent rounding; standard light/dark alpha composite. '
                           'Source logical canvas, offsets and adoption/acceptance flags are not modified. '
                           'Not mobile sizing or attachment acceptance.',
              'sourcePositionsUnchanged': source_positions, 'rasters': records}
    provenance.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'item': args.item, 'output': relative(output), 'sourceRecord': relative(provenance),
                      'sourcePositions': len(frames), 'uniqueRasters': len(rasters),
                      'userReviewStatus': 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
