"""Export or replay the source-registered 147 candidate rasters and previews."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from prepare_sources import HERE, ROOT, fingerprint, inspect, save

DENSITY = 4
SLOT_INDICES = [0, 1, 2, 4, 5, 6, 8, 9, 10]
THRESHOLD = 16


def read(path):
    return json.loads(path.read_bytes())


def checked(record):
    path = ROOT / record['file']
    if fingerprint(path) != record:
        raise ValueError(f'File hash differs: {path}')
    return path


def bbox(alpha):
    return alpha.point(lambda v: 255 if v >= THRESHOLD else 0).getbbox()


def resize(picture, size):
    return picture.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def center_alpha(picture):
    alpha = picture.getchannel('A')
    left, top, right, bottom = bbox(alpha)
    x = (left + right) // 2
    span = bottom - top
    return {
        'openingMiddleAlpha': alpha.getpixel((x, top + span // 2)),
        'lowerCenterMaxAlpha': alpha.crop((x, top + span * 3 // 4, x + 1, bottom)).getextrema()[1],
    }


def export_raster(atlas, rect, source):
    left, top, right, bottom = rect
    if not (0 <= left < right <= atlas.width and 0 <= top < bottom <= atlas.height):
        raise ValueError(f'Invalid atlas crop {rect}')
    cell = atlas.crop(rect)
    alpha = cell.getchannel('A')
    w, h = alpha.size
    edges = [(0, 0, 1, h), (0, 0, w, 1), (w - 1, 0, w, h), (0, h - 1, w, h)]
    edge_max = [alpha.crop(edge).getextrema()[1] for edge in edges]
    bounds = bbox(alpha)
    if bounds is None or max(edge_max) >= 8:
        raise ValueError(f"{source['index']}: empty or cut atlas crop, alpha edges {edge_max}")
    logical_size = source['sourceSize']
    original_box = source['alpha16Box']
    target = tuple(v * DENSITY for v in logical_size)
    target_box = tuple(v * DENSITY for v in original_box)
    target_w, target_h = target_box[2] - target_box[0], target_box[3] - target_box[1]
    sprite = cell.crop(bounds)
    delta = 100 * (sprite.width / sprite.height / (target_w / target_h) - 1)
    scale = min(target_w / sprite.width, target_h / sprite.height)
    size = tuple(round(v * scale) for v in sprite.size)
    x = target_box[0] + (target_w - size[0]) // 2
    y = target_box[3] - size[1]
    candidate = Image.new('RGBA', target)
    candidate.alpha_composite(resize(sprite, size), (x, y))
    return candidate, {
        'sourceCellRect': rect, 'sourceCellEdgeAlphaMax': edge_max, 'contentBoxWithinCell': list(bounds),
        'uniformScale': scale, 'placementPx': [x, y], 'density': DENSITY,
        'resampler': 'premultiplied-alpha LANCZOS', 'registration': 'center x and align to lower source alpha bound',
        'alpha16Box': list(bbox(candidate.getchannel('A'))),
        'signedAspectDeltaPercent': round(delta, 4), 'withinTenPercentAspect': abs(delta) <= 10,
        'newModelGeneration': False,
    }


def load_atlases(selection):
    loaded = {}
    for name in dict.fromkeys(pose['generationRecord'] for pose in selection['poses']):
        generation_path = ROOT / name
        generation = read(generation_path)
        if generation['generationRecord'] != name:
            raise ValueError('Generation sidecar path differs')
        args = read(checked(generation['exactSubmittedArgs']))
        if (args['route'] != 'builtin' or args['input']['transparent_background'] is not True
                or checked(generation['exactPromptUtf8']).read_bytes() != args['input']['prompt'].encode()
                or generation['actualModel'] is not None or generation['actualQuality'] is not None):
            raise ValueError('Generation provenance differs')
        for reference in generation['references']:
            checked({k: reference[k] for k in ('file', 'sha256')})
        path = checked({k: generation[k] for k in ('file', 'sha256')})
        with Image.open(path) as atlas:
            if (atlas.format != 'PNG' or atlas.mode != 'RGBA'
                    or atlas.size != (generation['width'], generation['height'])):
                raise ValueError('Native atlas metadata differs')
            loaded[name] = (atlas.copy(), generation)
    return loaded


def board(entries, source_images, pictures, background):
    columns, rows, cell_w, cell_h = 4, 4, 438, 250
    output = Image.new('RGB', (columns * cell_w, rows * cell_h), background)
    ink = '#203e37' if background == '#f6f0df' else '#f6f0df'
    draw = ImageDraw.Draw(output)
    font = ImageFont.load_default(size=18)
    for entry in entries:
        slot, raster = entry['index'], entry['uniqueRasterIndex']
        x, y = slot % columns * cell_w, slot // columns * cell_h
        draw.text((x + 22, y + 6), f"raw {slot:02}  /  raster {raster:02}  /  offset {entry['sourceRawOffset']}", font=font, fill=ink)
        for j, (name, picture) in enumerate((('source', source_images[raster]), ('candidate', pictures[raster]))):
            # The largest frame cannot be shown side by side at native 4x in this tile.
            zoom = (2 * picture.width, 2 * picture.height) if j == 0 else (picture.width // 2, picture.height // 2)
            art = picture.resize(zoom, Image.Resampling.NEAREST) if j == 0 else resize(picture, zoom)
            pane_x = x + j * (cell_w // 2)
            output.paste(art, (pane_x + (cell_w // 2 - art.width) // 2, y + 30), art)
            draw.text((pane_x + 14, y + 181), name, font=font, fill=ink)
        draw.text((x + 20, y + 220), f"{entry['sourceSize'][0]}x{entry['sourceSize'][1]} logical", font=font, fill=ink)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='write current selections, then verify')
    args = parser.parse_args()
    source_contract = read(HERE / 'source-contract.json')
    decoded, source_images = inspect()
    checked({k: source_contract['sourceBoard'][k] for k in ('file', 'sha256')})
    for key, value in decoded.items():
        if key != 'positions' and value != source_contract[key]:
            raise ValueError(f'Source contract differs at {key}')
    for actual, original in zip(source_contract['positions'], decoded['positions'], strict=True):
        if {key: actual[key] for key in original} != original:
            raise ValueError('Source position differs')
        if actual['index'] in SLOT_INDICES:
            with Image.open(checked(actual['sourceReference'])) as picture:
                image = source_images[actual['index']]
                if image.tobytes() != picture.tobytes() or list(bbox(image.getchannel('A'))) != actual['alpha16Box']:
                    raise ValueError('Source raster differs from actual locked archive decode')

    selection = read(HERE / 'selection.json')
    if [pose['sourceIndex'] for pose in selection['poses']] != SLOT_INDICES:
        raise ValueError('Selection must cover each unique source raster in raw order')
    atlases = load_atlases(selection)
    pictures, exports = {}, {}
    for pose in selection['poses']:
        index = pose['sourceIndex']
        source = source_contract['positions'][index]
        atlas, generation = atlases[pose['generationRecord']]
        picture, operation = export_raster(atlas, pose['xyxy'], source)
        path = HERE / 'sprites' / f'{index:02}-candidate.png'
        if args.export:
            path.parent.mkdir(exist_ok=True)
            picture.save(path, optimize=True)
        with Image.open(path) as actual:
            if actual.mode != 'RGBA' or actual.size != picture.size or actual.tobytes() != picture.tobytes():
                raise ValueError(f'{index}: candidate differs from exact crop replay')
        sidecar = path.with_name(path.name + '.provenance.json')
        record = {
            'sourceIndex': index, **fingerprint(path), 'density4Size': list(picture.size),
            'sourceSize': source['sourceSize'], 'sourceRawOffset': source['sourceRawOffset'],
            'sourceReference': source['sourceReference'],
            'derivedFrom': {k: generation[k] for k in ('file', 'sha256', 'generationRecord')},
            'operation': operation, 'geometryAccepted': False, 'visualAccepted': False,
            'accepted': False, 'runtimeAdopted': False,
        }
        if args.export:
            save(sidecar, record)
        if record != read(sidecar):
            raise ValueError(f'{index}: sidecar differs')
        exports[index] = {**record, 'provenance': fingerprint(sidecar)}
        pictures[index] = picture

    positions = [{
        'index': pos['index'], 'uniqueRasterIndex': pos['uniqueRasterIndex'], 'sourceSize': pos['sourceSize'],
        'sourceRawOffset': pos['sourceRawOffset'], 'sourceRgbaSha256': pos['rgbaSha256'],
        'candidate': {k: exports[pos['uniqueRasterIndex']][k] for k in ('file', 'sha256')},
    } for pos in source_contract['positions']]
    previews = []
    for name, background in (('light', '#f6f0df'), ('jade', '#193c35')):
        path = HERE / f'contact-{name}.png'
        image = board(positions, source_images, pictures, background)
        if args.export:
            image.save(path, optimize=True)
        with Image.open(path) as actual:
            if actual.mode != 'RGB' or actual.size != image.size or actual.tobytes() != image.tobytes():
                raise ValueError(f'{name}: review image differs')
        preview = {**fingerprint(path), 'role': 'source nearest2 and candidate half-size; no placement preview',
                   'sourceContract': fingerprint(HERE / 'source-contract.json'),
                   'inputs': [{k: entry[k] for k in ('sourceIndex', 'file', 'sha256')} for entry in exports.values()],
                   'newModelGeneration': False, 'runtimeScreenshot': False}
        sidecar = path.with_name(path.name + '.source.json')
        if args.export:
            save(sidecar, preview)
        if preview != read(sidecar):
            raise ValueError(f'{name}: review image provenance differs')
        previews.append({**preview, 'provenance': fingerprint(sidecar)})
    manifest_path = HERE / 'world-art.json'
    manifest = {
        'schemaVersion': 1, 'category': 'fpack', 'itemId': 147, 'resourceId': 18,
        'projectDisplayName': '丹羽凤翼', 'density': DENSITY, 'sourceDeclaredCanvas': [96, 65],
        'sourceContract': fingerprint(HERE / 'source-contract.json'),
        'sourceMembers': source_contract['members'], 'byteIdenticalStandWalk': True,
        'memberPositions': {'stand': positions, 'walk': positions}, 'uniqueRasters': list(exports.values()),
        'previews': previews, 'geometryAccepted': False, 'visualAccepted': False,
        'accepted': False, 'runtimeAdopted': False, 'worldAnchorConfirmed': False,
        'directionSemanticsConfirmed': False, 'timingConfirmed': False, 'completeAnimationAccepted': False,
    }
    if args.export:
        save(manifest_path, manifest)
    if manifest != read(manifest_path):
        raise ValueError('World manifest differs from replay')
    failures = [index for index, entry in exports.items() if not entry['operation']['withinTenPercentAspect']]
    bilateral_review = [{
        'rawIndex': index,
        'source': center_alpha(source_images[index]),
        'candidate': center_alpha(pictures[index]),
    } for index in (4, 5, 6)]
    if failures:
        raise ValueError(f'Silhouette ratio exceeds 10 percent at source slots {failures}')
    for row in bilateral_review:
        if row['candidate']['openingMiddleAlpha'] >= 8 or row['candidate']['lowerCenterMaxAlpha'] < 240:
            raise ValueError(f"{row['rawIndex']}: expected a clear opening and opaque lower contact")
    print(json.dumps({
        'sourceMembers': 2, 'distinctSourcePositions': len(positions), 'memberPositions': 2 * len(positions),
        'distinctCandidateRasters': len(exports), 'previews': len(previews), 'pixelReplayExact': True,
        'aspectTolerancePercent': 10, 'aspectToleranceExceedingRawIndices': failures,
        'signedAspectDeltaPercentByRawIndex': {i: e['operation']['signedAspectDeltaPercent'] for i, e in exports.items()},
        'bilateralCenterAlphaReview': bilateral_review,
        'maximumCropEdgeAlpha': max(max(e['operation']['sourceCellEdgeAlphaMax']) for e in exports.values()),
        'manifest': fingerprint(manifest_path), 'accepted': False, 'runtimeAdopted': False, 'errors': [],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
