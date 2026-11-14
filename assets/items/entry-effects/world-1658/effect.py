"""Export and verify the six source-mapped Auspicious Jade Dragon entry frames."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from prepare_sources import HERE, ROOT, fingerprint, inspect, save

SIZE = 400
PHASES = (
    ('星空', None, None),
    ('窄光柱', 'beamNarrow', None),
    ('宽光柱与金白龙影', 'beamWide', 'silhouette'),
    ('窄光柱与暖色显形', 'beamNarrow', 'warmDragon'),
    ('宽光柱与青玉龙', 'beamWide', 'jadeDragon'),
    ('窄光柱与青玉亮边', 'beamNarrow', 'litDragon'),
)
TARGET_RECT = {
    'beamNarrow': (158, 0, 242, 400),
    'beamWide': (134, 0, 266, 400),
    'silhouette': (16, 58, 384, 274),
    'warmDragon': (16, 58, 384, 274),
    'jadeDragon': (16, 58, 384, 274),
    'litDragon': (16, 58, 384, 274),
}
OPENING_SAMPLES = ((111, 187), (300, 174))


def read(path):
    return json.loads(path.read_bytes())


def check(record):
    path = ROOT / record['file']
    if fingerprint(path)['sha256'] != record['sha256']:
        raise ValueError(f'Hash mismatch: {path}')
    return path


def resize(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def extent(mask, threshold=16):
    return mask.point(lambda a: 255 if a >= threshold else 0).getbbox()


def load_generation(name, transparent):
    metadata = read(ROOT / name)
    if metadata['generationRecord'] != name:
        raise ValueError('Generation path differs')
    args = read(check(metadata['exactSubmittedArgs']))
    if (args['route'] != 'builtin' or args['input']['transparent_background'] is not transparent
            or check(metadata['exactPromptUtf8']).read_bytes() != args['input']['prompt'].encode()
            or metadata['actualModel'] is not None or metadata['actualQuality'] is not None):
        raise ValueError('Generation evidence differs')
    for reference in metadata['references']:
        check(reference)
    with Image.open(check(metadata)) as image:
        if (image.format != 'PNG' or image.mode != metadata['mode']
                or image.size != (metadata['width'], metadata['height'])):
            raise ValueError('Generation metadata differs')
        if transparent and image.mode != 'RGBA':
            raise ValueError('The transparent layer must have original alpha')
        return image.convert('RGBA'), {key: metadata[key] for key in ('file', 'sha256', 'generationRecord')}


def render_layer(atlas, name, rect):
    x0, y0, x1, y1 = rect
    if not (0 <= x0 < x1 <= atlas.width and 0 <= y0 < y1 <= atlas.height):
        raise ValueError(f'Invalid source crop for {name}')
    image = atlas.crop(rect)
    alpha = image.getchannel('A')
    w, h = image.size
    edge_max = [alpha.crop(p).getextrema()[1] for p in ((0, 0, w, 1), (0, h - 1, w, h),
                                                       (0, 0, 1, h), (w - 1, 0, w, h))]
    bbox = extent(alpha)
    if not bbox or max(edge_max) >= 8:
        raise ValueError(f'{name}: atlas crop contains clipped content or is empty: {edge_max}')
    content = image.crop(bbox)
    x0, y0, x1, y1 = TARGET_RECT[name]
    if name.startswith('beam'):
        # Stretch only the vertical light layer to the authored full-height slot.
        size = (x1 - x0, y1 - y0)
        offset = (x0, y0)
        method = 'fit axis-aligned light shaft to full-height target'
    else:
        scale = min((x1 - x0) / content.width, (y1 - y0) / content.height)
        size = tuple(round(v * scale) for v in content.size)
        offset = (x0 + (x1 - x0 - size[0]) // 2, y0 + (y1 - y0 - size[1]) // 2)
        method = 'uniformly fit dragon alpha crop into authored target area'
    result = Image.new('RGBA', (SIZE, SIZE))
    result.alpha_composite(resize(content, size), offset)
    return result, {
        'cropXYXY': rect, 'cropEdgeAlphaMax': edge_max, 'alpha16BoundsInCrop': list(bbox),
        'destinationXYXY': list(TARGET_RECT[name]), 'actualPaintedSize': list(size), 'placement': list(offset),
        'resampler': 'premultiplied-alpha LANCZOS', 'method': method,
    }


def board(source, world, icon):
    board = Image.new('RGB', (1010, 622), '#f6f0df')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=17)
    draw.text((12, 10), 'Source (top) / candidate (bottom), raw slot order', font=font, fill='#26473d')
    for index in range(6):
        x = 10 + index * 165
        before = source[index].resize((156, 156), Image.Resampling.NEAREST)
        after = resize(world[index], (156, 156))
        board.paste(before.convert('RGB'), (x, 44))
        board.paste(after.convert('RGB'), (x, 208))
        draw.text((x, 369), f'{index:02} / 100 px logical', font=font, fill='#26473d')
        for dx, size in ((0, 32), (43, 48), (100, 64)):
            board.paste(resize(world[index], (size, size)).convert('RGB'), (x + dx, 410))
    draw.text((12, 493), 'Inventory candidate at 32 / 48 / 64 px', font=font, fill='#26473d')
    for x, size in ((12, 32), (59, 48), (124, 64)):
        art = resize(icon, (size, size))
        board.paste(art, (x, 521), art)
    return board


def ensure_image(path, expected, write):
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        expected.save(path, optimize=True)
    with Image.open(path) as actual:
        if actual.size != expected.size or actual.mode != expected.mode or actual.tobytes() != expected.tobytes():
            raise ValueError(f'PNG differs from exact replay: {path}')


def ensure_json(path, record, write):
    if write:
        save(path, record)
    if read(path) != record:
        raise ValueError(f'Record differs from replay: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='write candidates and previews, then verify')
    args = parser.parse_args()
    source_contract_path = HERE / 'source-contract.json'
    source = read(source_contract_path)
    decoded, source_images, source_icon = inspect()
    for key, value in decoded.items():
        if key not in ('positions', 'inventory') and value != source[key]:
            raise ValueError(f'Source metadata differs at {key}')
    for entry, original in zip(source['positions'], decoded['positions'], strict=True):
        if {key: entry[key] for key in original} != original:
            raise ValueError('Source position metadata differs')
        with Image.open(check(entry['sourceReference'])) as picture:
            if picture.tobytes() != source_images[entry['index']].tobytes():
                raise ValueError('Source world raster differs')
    if {k: source['inventory'][k] for k in decoded['inventory']} != decoded['inventory']:
        raise ValueError('Source inventory metadata differs')
    with Image.open(check(source['inventory']['reference'])) as picture:
        if picture.tobytes() != source_icon.tobytes():
            raise ValueError('Source inventory pixels differ')
    check(source['sourceBoard'])

    selection = read(HERE / 'selection.json')
    bg, bg_record = load_generation(selection['background'], False)
    if bg.width != bg.height or bg.getchannel('A').getextrema() != (255, 255):
        raise ValueError('Background must be a square opaque plate')
    sky = resize(bg, (SIZE, SIZE))
    atlases = {name: load_generation(name, True)
               for name in dict.fromkeys(v['generationRecord'] for v in selection['layers'].values())}
    rendered, operations = {}, {}
    if set(selection['layers']) != set(TARGET_RECT):
        raise ValueError('Layer set differs')
    for name, selected in selection['layers'].items():
        atlas, generator = atlases[selected['generationRecord']]
        rendered[name], op = render_layer(atlas, name, selected['xyxy'])
        operations[name] = {'derivedFrom': generator, **op}
    open_loop_alpha = {
        name: [layer.getchannel('A').getpixel(point) for point in OPENING_SAMPLES]
        for name, layer in rendered.items() if not name.startswith('beam')
    }
    if any(max(values) >= 8 for values in open_loop_alpha.values()):
        raise ValueError('One or both dragon loop openings are obstructed')
    beam_tip_alpha = {
        name: [layer.getchannel('A').getpixel((SIZE // 2, y)) for y in (0, SIZE - 1)]
        for name, layer in rendered.items() if name.startswith('beam')
    }
    if any(min(values) < 128 for values in beam_tip_alpha.values()):
        raise ValueError('Light shafts do not reach both tile edges')

    world, positions = [], []
    for index, (label, beam, dragon) in enumerate(PHASES):
        image = sky.copy()
        names = [name for name in (beam, dragon) if name]
        for name in names:
            image.alpha_composite(rendered[name])
        if image.getchannel('A').getextrema() != (255, 255):
            raise ValueError('World tile must remain opaque like the source')
        path = HERE / 'sprites' / f'{index:02}-entry.png'
        ensure_image(path, image, args.export)
        world.append(image)
        source_pos = source['positions'][index]
        positions.append({
            'index': index, 'phaseDescription': label, 'sourceSize': source_pos['sourceSize'],
            'sourceRawOffset': source_pos['sourceRawOffset'], 'sourceReference': source_pos['sourceReference'],
            'density4Size': [SIZE, SIZE], 'alphaExtrema': [255, 255], **fingerprint(path),
            'derivedFrom': [bg_record, *[operations[name]['derivedFrom'] for name in names]],
            'operation': {'commonBackground': bg_record, 'layersInCompositeOrder': [
                {'name': name, **operations[name]} for name in names],
                'composite': 'RGBA source-over', 'newModelGeneration': False},
            'visualAccepted': False, 'runtimeAdopted': False,
        })
        sidecar = path.with_name(path.name + '.provenance.json')
        ensure_json(sidecar, positions[-1], args.export)
        positions[-1]['provenance'] = fingerprint(sidecar)
    if len({record['sha256'] for record in positions}) != len(PHASES):
        raise ValueError('The source has six distinct positions, so no candidate position may alias another')

    icon = resize(world[4], (256, 256))
    icon_path = HERE / '1658-auspicious-jade-dragon.png'
    ensure_image(icon_path, icon, args.export)
    icon_record = {
        **fingerprint(icon_path), 'itemId': 1658, 'resourceId': 32, 'category': 'enter',
        'projectDisplayName': '玉龙迎云', 'width': 256, 'height': 256, 'alphaExtrema': [255, 255],
        'sourceReference': source['inventory']['reference']['file'],
        'sourceReferenceSha256': source['inventory']['reference']['sha256'],
        'sourceInventoryNativeFrameSize': source['inventory']['nativeSize'],
        'sourceInventoryFrameOffsetRaw': source['inventory']['frame']['frameOffset'],
        'derivedFrom': {key: positions[4][key] for key in ('file', 'sha256', 'provenance')},
        'operation': 'Full-bleed selected world frame uniformly resampled to inventory tile',
        'representation': 'inventory-icon-only', 'worldMapped': False,
        'accepted': False, 'visualAccepted': False, 'runtimeAdopted': False,
    }
    icon_sidecar = icon_path.with_name(icon_path.name + '.provenance.json')
    ensure_json(icon_sidecar, icon_record, args.export)
    icon_record['provenanceRecord'] = fingerprint(icon_sidecar)['file']
    preview_path = HERE / 'contact-source-candidate-mobile.png'
    ensure_image(preview_path, board(source_images, world, icon), args.export)
    preview = {**fingerprint(preview_path), 'inputWorldFrames': [p['file'] for p in positions],
               'inputInventory': fingerprint(icon_path), 'sourceContract': fingerprint(source_contract_path),
               'runtimeScreenshot': False}
    ensure_json(preview_path.with_name(preview_path.name + '.source.json'), preview, args.export)

    world_path = HERE / 'world-art.json'
    inventory_path = HERE / 'art.json'
    ensure_json(world_path, {
        'schemaVersion': 1, 'category': 'enter', 'itemId': 1658, 'resourceId': 32,
        'projectDisplayName': '玉龙迎云', 'density': 4, 'sourceDeclaredCanvas': [100, 100],
        'sourceContract': fingerprint(source_contract_path), 'sourceMember': source['members']['stand'],
        'positions': positions, 'previews': [preview],
        'accepted': False, 'visualAccepted': False, 'geometryAccepted': False,
        'runtimeAdopted': False, 'directionSemanticsConfirmed': False,
        'timingConfirmed': False, 'worldAnchorConfirmed': False, 'completeAnimationAccepted': False,
    }, args.export)
    ensure_json(inventory_path, {
        'schemaVersion': 1, 'category': 'enter', 'scope': 'inventory-only-static-candidates',
        'sourceCategoryTotal': 71, 'items': [icon_record], 'previews': [preview],
        'accepted': False, 'visualAccepted': False, 'runtimeAdopted': False,
    }, args.export)
    print(json.dumps({
        'itemId': 1658, 'worldSlots': 6, 'worldDistinctRasters': 6, 'inventoryCandidates': 1,
        'worldManifest': fingerprint(world_path), 'inventoryManifest': fingerprint(inventory_path),
        'pixelReplayExact': True, 'maxCropEdgeAlpha': max(max(op['cropEdgeAlphaMax']) for op in operations.values()),
        'dragonOpeningAlphaAtPoints': {'pointsXY': OPENING_SAMPLES, 'layerAlpha': open_loop_alpha},
        'beamTopBottomCenterAlpha': beam_tip_alpha,
        'worldFrameAlphaExtrema': [255, 255], 'errors': [], 'runtimeAdopted': False,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
