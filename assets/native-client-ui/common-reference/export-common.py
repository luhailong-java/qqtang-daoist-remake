"""Encode and replay the common renderer without editing the install/build entrypoint."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def own_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ART = own_module('common_native_art', 'scripts/native-ui-common-art.py')
CODEC = own_module('common_native_codec', 'scripts/native-ui-format.py')
ROOT_PAINTS = {
    'panel': 'assets/ui/window-frame.png', 'normal': 'assets/ui/primary-normal.png',
    'hover': 'assets/ui/primary-hover.png', 'pressed': 'assets/ui/primary-pressed.png',
    **ART.PAINT_INPUTS,
}
FONT = Path('C:/Windows/Fonts/msyh.ttc')


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def read(path):
    return json.loads(path.read_bytes())


def write_json(path, data, check):
    if check:
        if read(path) != data:
            raise ValueError(f'Record replay differs at {path}')
    else:
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def png(path, image, check):
    if check:
        with Image.open(path) as actual:
            if image.size != actual.size or image.mode != actual.mode or image.tobytes() != actual.tobytes():
                raise ValueError(f'PNG pixels differ at {path}')
    else:
        path.parent.mkdir(exist_ok=True, parents=True)
        image.save(path, optimize=True)


def scaled(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def nine_slice(image, size, inset):
    width, height = size
    edge = min(inset, width // 3, height // 3)
    sx, sy = (0, inset, image.width - inset, image.width), (0, inset, image.height - inset, image.height)
    dx, dy = (0, edge, width - edge, width), (0, edge, height - edge, height)
    out = Image.new('RGBA', size)
    for y in range(3):
        for x in range(3):
            tile = scaled(image.crop((sx[x], sy[y], sx[x + 1], sy[y + 1])),
                          (dx[x + 1] - dx[x], dy[y + 1] - dy[y]))
            out.alpha_composite(tile, (dx[x], dy[y]))
    return out


def logical_frame(frame, image, size):
    output = Image.new('RGBA', size)
    output.alpha_composite(image, tuple(frame['frameOffset']))
    return output


def glyph_contract(source_items, candidates):
    constants = ROOT / 'references/qqtang-ui-data/constants'
    by_path = {entry['nativePath']: entry for entry in source_items}
    records = []
    for name, (canvas, crop, cell_width, characters) in ART.NUMBER_LAYOUTS.items():
        path = f'object/ui/common/{name}.img'
        item = by_path[path]
        frame = item['frames'][0]['sourceFrame']
        if (item['metadata']['declaredCanvas'] != list(canvas)
                or frame['frameOffset'] != list(crop[:2])
                or [frame['width'], frame['height']] != [crop[2] - crop[0], crop[3] - crop[1]]
                or canvas[0] != 15 * cell_width):
            raise ValueError(f'{name}: source glyph geometry differs')
        with Image.open(ROOT / item['frames'][0]['file']) as native:
            original = logical_frame(frame, native, canvas)
        candidate = logical_frame(frame, candidates[path][0][1], canvas)
        cells = []
        for index, char in enumerate(characters):
            rect = (index * cell_width, 0, (index + 1) * cell_width, canvas[1])
            before, after = original.crop(rect), candidate.crop(rect)
            bbox = after.getchannel('A').point(lambda value: 255 if value >= 16 else 0).getbbox()
            if bbox is None:
                raise ValueError(f'{name}: glyph {index}/{char} has no candidate pixels')
            cells.append({'index': index, 'observedCharacter': char, 'logicalCellXYXY': list(rect),
                          'sourceAlpha8BoxInCell': list(before.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()),
                          'candidateAlpha16BoxInCell': list(bbox)})
        declarations = []
        for module_path in constants.glob('*.json'):
            module = read(module_path)
            for scope in module['scopes']:
                stores = {a['name']: a['literalValue'] for a in scope['literalAssignments']}
                if stores.get('bkimage', {}).get('text', '').lower() != path.lower():
                    continue
                declarations.append({'module': module['module'], 'scope': scope['scope'],
                                     'type': stores.get('type'), 'textwidth': stores.get('textwidth'),
                                     'textheight': stores.get('textheight')})
        records.append({'nativePath': path, 'sourceCanvas': list(canvas), 'sourceRasterCropXYXY': list(crop),
                        'cellWidth': cell_width, 'cellHeight': canvas[1], 'characters': characters,
                        'cells': cells, 'exactPycNumberDeclarations': declarations,
                        'runtimeUsageConfirmed': False, 'observedGridAndCharactersReviewed': True})
    return {'schemaVersion': 1, 'glyphsPerStrip': 15, 'strips': records,
            'observationBoard': record(HERE / 'source-number-cells-observed.png'),
            'sourceAndCandidateUseSameNativeCanvasCrop': True}


def previews(source_items, candidates):
    controls = [item for item in source_items if item['nativePath'] in candidates
                and not Path(item['nativePath']).stem.lower().startswith('number')]
    font = ImageFont.load_default(size=15)
    board = Image.new('RGB', (1100, 133 * len(controls)), '#f3ecd8')
    draw = ImageDraw.Draw(board)
    for row, item in enumerate(controls):
        y = row * 133
        draw.text((8, y + 4), Path(item['nativePath']).name, font=font, fill='#24513f')
        for index, (frame, image) in enumerate(candidates[item['nativePath']]):
            scale = min(2, 258 / image.width, 99 / image.height)
            art = scaled(image, tuple(max(1, round(v * scale)) for v in image.size))
            x = index * 275 + 8
            draw.text((x, y + 28), f'raw {index}', font=font, fill='#24513f')
            board.paste(art, (x + 36, y + 29), art)
    numbers = [item for item in source_items if item['nativePath'] in candidates
               and Path(item['nativePath']).stem.lower().startswith('number')]
    numeric = Image.new('RGB', (1500, 132 * len(numbers)), '#264d42')
    draw = ImageDraw.Draw(numeric)
    for row, item in enumerate(numbers):
        name = Path(item['nativePath']).stem
        canvas, _, cell_width, _ = ART.NUMBER_LAYOUTS[name]
        frame, image = candidates[item['nativePath']][0]
        registered = logical_frame(frame, image, canvas)
        draw.text((8, row * 132 + 4), f'{name} / native {cell_width}px cells', font=font, fill='#f9edc7')
        for column in range(15):
            rect = (column * cell_width, 0, (column + 1) * cell_width, canvas[1])
            cell = registered.crop(rect)
            scale = min(74 / cell.width, 85 / cell.height)
            cell = scaled(cell, tuple(max(1, round(v * scale)) for v in cell.size))
            x, y = column * 100 + 8, row * 132 + 32
            draw.text((x, y), str(column), font=font, fill='#f9edc7')
            numeric.paste(cell, (x + 20, y + 3), cell)
    return {'candidate-controls.png': board, 'candidate-number-cells.png': numeric}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    package_path = ROOT / '.artifacts/reference-inputs/object.pkg'
    package = package_path.read_bytes()
    source_manifest = read(HERE / 'manifest.json')
    paints = {name: Image.open(ROOT / path).convert('RGBA') for name, path in ROOT_PAINTS.items()}
    source_items = source_manifest['resources']
    by_path = {item['nativePath'].lower(): item for item in source_items}
    candidates, exports = {}, []
    for path, (kind, label) in ART.PATHS.items():
        source = by_path[path.lower()]
        original, _ = CODEC.reader.unpack_resource(package, source['packageEntry'])
        if hashlib.sha256(original).hexdigest() != source['sourceSha256']:
            raise ValueError('Source bytes differ')
        pictures = {frame['index']: ART.render(kind, label, frame['index'],
                    (frame['width'], frame['height']), paints, FONT, nine_slice, scaled)
                    for frame in source['metadata']['frames'] if not frame['empty']}
        output, _, decoded = CODEC.replace_frames(original, pictures)
        target = HERE / 'patch' / path
        if args.check:
            if target.read_bytes() != output:
                raise ValueError(f'Native bytes differ: {path}')
        else:
            target.parent.mkdir(exist_ok=True, parents=True)
            target.write_bytes(output)
        permitted = bytearray(len(original))
        decoded_items = []
        for frame, image in decoded:
            start, length = frame['pixelDataOffset'], frame['pixelByteLength']
            permitted[start:start + length] = b'\x01' * length
            png_path = HERE / 'decoded' / f'{Path(path).stem}-{frame["index"]:02}.png'
            png(png_path, image, args.check)
            decoded_items.append({**record(png_path), 'index': frame['index'],
                                  'sourceFrameOffset': frame['frameOffset'], 'width': image.width,
                                  'height': image.height, 'pixelMode': frame['pixelMode'],
                                  'rgbaSha256': hashlib.sha256(image.tobytes()).hexdigest()})
        if any(before != after and not allowed for before, after, allowed in zip(original, output, permitted, strict=True)):
            raise ValueError('A non-pixel source byte changed')
        candidates[source['nativePath']] = decoded
        exports.append({**record(target), 'nativePath': path, 'sourceSha256': source['sourceSha256'],
                        'rendererKind': kind, 'caption': label, 'frames': decoded_items,
                        'allNonPixelBytesIdenticalToSource': True, 'visualAccepted': False,
                        'nativeRuntimeVerified': False})
    glyphs = glyph_contract(source_items, candidates)
    write_json(HERE / 'numeric-contract.json', glyphs, args.check)
    preview_records = []
    for name, image in previews(source_items, candidates).items():
        path = HERE / name
        png(path, image, args.check)
        preview_records.append({**record(path), 'operation': 'Composite of actual native-mode decoded candidate pixels',
                                'runtimeScreenshot': False})
    write_json(HERE / 'candidate-manifest.json', {
        'schemaVersion': 1, 'scope': '24 new native common resources; four common resources owned by the root batch',
        'sourceReferences': record(HERE / 'manifest.json'), 'items': exports,
        'numericContract': record(HERE / 'numeric-contract.json'), 'previews': preview_records,
        'renderer': record(ROOT / 'scripts/native-ui-common-art.py'),
        'exporter': record(Path(__file__)), 'nativeCodec': record(ROOT / 'scripts/native-ui-format.py'),
        'paintInputs': [record(ROOT / path) for path in ROOT_PAINTS.values()],
        'font': {'family': 'Microsoft YaHei', 'sha256': hashlib.sha256(FONT.read_bytes()).hexdigest()},
        'symbolFont': {'family': 'Segoe UI Symbol', 'sha256': hashlib.sha256(ART.SYMBOL_FONT.read_bytes()).hexdigest()},
        'newModelGeneration': False, 'visualAccepted': False, 'nativeRuntimeVerified': False,
    }, args.check)
    print(json.dumps({'nativeResources': len(exports), 'sourcePositions': sum(len(item['frames']) for item in exports),
                      'glyphStrips': len(glyphs['strips']), 'glyphCells': 15 * len(glyphs['strips']),
                      'nativeReplayChecked': args.check, 'allNativeHeadersAndOffsetsRetained': True}))


if __name__ == '__main__':
    main()
