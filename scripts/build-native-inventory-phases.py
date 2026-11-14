"""Convert original level drawings and material variations into five native inventory IMGs."""
from datetime import datetime, timezone
from importlib import util
from pathlib import Path
import argparse
import json
import struct
import zipfile

from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'assets/native-client-ui/inventory-phases-v1'
spec = util.spec_from_file_location('native_inventory_base', ROOT / 'scripts/build-native-inventory-art.py')
base = util.module_from_spec(spec)
spec.loader.exec_module(base)
gate_spec = util.spec_from_file_location('painted_crop_gate', ROOT / 'scripts/painted_crop_gate.py')
gate = util.module_from_spec(gate_spec)
gate_spec.loader.exec_module(gate)
GENERATIONS = {27061: ('courage-levels-v1', (1254, 1254), 3, 3),
               27073: ('affinity-levels-v1', (1774, 887), 4, 2)}
LEVELS = {27061: tuple(range(1, 11)), 27073: tuple(range(3, 11))}


def checked_record(record):
    path = ROOT / record['file']
    if base.ref(path)['sha256'] != record['sha256']:
        raise ValueError(f"Recorded input changed: {record['file']}")
    return path


def generation_record(name, path, image, check):
    submission = HERE / f'submission-{name}.json'
    returned = HERE / f'result-{name}.json'
    sent = json.loads(submission.read_bytes())['input']
    result = json.loads(returned.read_bytes())
    references = []
    for filename, role in zip(sent['referenced_image_paths'],
                              ('own skill identity', 'source level order only', 'Daoist Q finish', 'Daoist Q finish'),
                              strict=True):
        references.append({**base.ref(Path(filename)), 'role': role})
    config = ROOT / 'config/image-generation.json'
    sidecar = path.with_suffix('.png.generation.json')
    base.save_json(sidecar, {
        'schemaVersion': 1, **base.ref(path), 'nativeSize': list(image.size), 'mode': image.mode,
        'art_source': 'host_image', 'tool': 'image_gen.imagegen', 'route': 'builtin',
        'configSource': base.ref(config), 'configSnapshot': json.loads(config.read_bytes()),
        'exactPrompt': sent['prompt'], 'submittedPromptSha256': base.sha(sent['prompt'].encode()),
        'submittedParameters': {k: v for k, v in sent.items() if k != 'prompt'},
        'actualModel': None, 'actualQuality': None,
        'actualParametersEvidence': 'Builtin tool exposes no model or quality selector and disclosed neither.',
        'references': references, 'submission': base.ref(submission), 'returnedMetadata': base.ref(returned),
        'hostSource': result['hostSource'], 'returnedFields': result['returnedFields'],
        'hostFileModifiedTimeUtc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        'timeEvidence': 'Native file modification time; model-side timestamp undisclosed',
        'visualAccepted': False, 'nativeRuntimeVerified': False,
    }, check)
    return base.ref(sidecar)


def generated_cells(item_id, check):
    name, extent, cols, rows = GENERATIONS[item_id]
    mother = HERE / f'mother-{name}.png'
    result = {}
    with Image.open(mother) as image:
        if image.size != extent or image.mode != 'RGBA' or image.getchannel('A').getextrema() != (0, 255):
            raise ValueError('Unexpected generated skill mother geometry or alpha')
        cells = [(image.width*x//cols, image.height*y//rows,
                  image.width*(x+1)//cols, image.height*(y+1)//rows)
                 for y in range(rows) for x in range(cols)]
        gate.validate_visible_boundaries(image, cells, threshold=8)
        generated = generation_record(name, mother, image, check)
        for index in range(1, len(LEVELS[item_id])):
            slot = index-1 if item_id == 27061 else index
            rect = cells[slot]
            picture = image.crop(rect)
            target = HERE / 'painted-frames' / str(item_id) / f'{index:02}.png'
            base.save_image(target, picture, check)
            operation = {'type': 'native mother cell crop', 'sourceRectLTRB': list(rect),
                         'alpha8BBox': list(picture.getchannel('A').point(lambda v: 255 if v >= 8 else 0).getbbox()),
                         'newModelGeneration': False}
            sidecar = target.with_suffix('.png.provenance.json')
            meta = {**base.ref(target), 'itemId': item_id, 'sourceFrameIndex': index,
                    'displayedLevel': LEVELS[item_id][index], 'derivedFrom': base.ref(mother),
                    'generationRecord': generated, 'operation': operation, 'visualAccepted': False}
            base.save_json(sidecar, meta, check)
            result[index] = (picture, {**base.ref(target), 'provenance': base.ref(sidecar),
                                      'generationRecord': generated, 'displayedLevel': LEVELS[item_id][index]})
    return result


def material_evidence(source):
    a, b = [Image.open(checked_record(f)).convert('RGBA') for f in source['frames']]
    if a.size != b.size or a.getchannel('A').tobytes() != b.getchannel('A').tobytes():
        raise ValueError('Hammer source silhouette changes between states')
    rgb_a, rgb_b = [], []
    for first, second in zip(struct.iter_unpack('4B', a.tobytes()),
                             struct.iter_unpack('4B', b.tobytes()), strict=True):
        if first[3] > 128 and second[3] > 128:
            rgb_a.append(sum(first[:3]))
            rgb_b.append(sum(second[:3]))
    if not rgb_a or any(second < first for first, second in zip(rgb_a, rgb_b, strict=True)):
        raise ValueError('Hammer source state is more than a uniform bright material variation')
    return {'sourceAlphaPlanesEqual': True, 'sourceOpaquePixelsCompared': len(rgb_a),
            'sourceOpaqueChannelSumRatio': sum(rgb_b)/sum(rgb_a),
            'sourceAllComparedPixelRgbSumsNonDecreasing': True,
            'interpretation': 'Same silhouette and pose; second stored state uses brighter material',
            'runtimeTriggerConfirmed': False}


def make_preview(items, sources, check):
    sheet = Image.new('RGB', (1000, len(items)*290), '#ede6d4')
    draw = ImageDraw.Draw(sheet)
    for row, item in enumerate(items):
        y = row*290
        draw.text((10, y+6), f"{item['itemId']} / native stored slots / review pending", fill='#244e40')
        draw.rectangle((0, y+145, 999, y+289), fill='#173e36')
        source = sources[item['itemId']]
        for frame in item['frames']:
            index = frame['index']
            image = Image.open(ROOT / frame['file']).convert('RGBA')
            canvas = Image.new('RGBA', tuple(source['metadata']['declaredCanvas']))
            canvas.alpha_composite(image, tuple(frame['frameOffset']))
            for top, ink in ((y+29, '#244e40'), (y+164, '#f6f0dd')):
                sheet.paste(canvas, (10+index*98, top), canvas)
                caption = f"f{index}"
                if 'displayedLevel' in frame:
                    caption += f" level{frame['displayedLevel']}"
                draw.text((10+index*98, top+70), caption, fill=ink)
    path = HERE / 'contact-native-light-dark.png'
    base.save_image(path, sheet, check)
    return base.ref(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    contract_path = HERE / 'source-contract.json'
    contract = json.loads(contract_path.read_bytes())
    source_items = {i['itemId']: i for i in contract['items']}
    if set(source_items) != {27061, 27073, 9011, 9012, 9013}:
        raise ValueError('Unexpected item set')
    resources = []
    with base.ARCHIVE.open('rb') as stream:
        if base.hashlib.file_digest(stream, 'sha256').hexdigest() != base.ARCHIVE_SHA:
            raise ValueError('Pinned native source archive changed')
    with zipfile.ZipFile(base.ARCHIVE) as archive:
        for item_id, source in source_items.items():
            raw = archive.read(source['sourceArchiveMember'])
            if base.sha(raw) != source['sourceSha256']:
                raise ValueError('Source native IMG changed')
            own_path = checked_record({k: source['ownCandidate'][k] for k in ('file', 'sha256')})
            provenance = checked_record(source['ownCandidate']['sourceProvenanceRecord'])
            original_provenance = json.loads(provenance.read_bytes())
            original_generation = base.ref(ROOT / original_provenance['derivedFrom']['generationRecord'])
            own = Image.open(own_path).convert('RGBA')
            generated = generated_cells(item_id, check) if item_id in LEVELS else {}
            material = material_evidence(source) if item_id not in LEVELS else None
            pictures, phase_records = {}, {}
            for frame in source['metadata']['frames']:
                index = frame['index']
                picture, origin = generated.get(index, (own.copy(), {
                    **base.ref(own_path), 'provenance': base.ref(provenance), 'generationRecord': original_generation}))
                variation = None
                if material is not None and index == 1:
                    factor = material['sourceOpaqueChannelSumRatio']
                    picture = ImageEnhance.Brightness(picture).enhance(factor)
                    variation = {'type': 'own painted material brightness variation', 'brightnessFactor': factor,
                                 'sourceEvidence': material, 'alphaPreserved': True, 'newModelGeneration': False}
                fitted, transform = base.candidate_fit(picture, (frame['width'], frame['height']))
                pictures[index] = fitted
                phase_records[index] = {'derivedFrom': origin, 'operation': transform}
                if item_id in LEVELS:
                    phase_records[index]['displayedLevel'] = LEVELS[item_id][index]
                if variation:
                    phase_records[index]['materialVariation'] = variation
            output, _, decoded = base.codec.replace_frames(raw, pictures)
            target = HERE / 'patch' / source['nativePath']
            base.save_bytes(target, output, check)
            frames = []
            for native, image in decoded:
                index = native['index']
                if image.getchannel('A').getextrema()[1] < 8:
                    raise ValueError('Native phase lost its visible art')
                path = HERE / 'decoded' / str(item_id) / f'{index:02}.png'
                base.save_image(path, image, check)
                record = {**base.ref(path), 'index': index, 'width': image.width, 'height': image.height,
                          'pixelMode': native['pixelMode'], 'frameOffset': native['frameOffset'],
                          'sourceFrameIndex': index, 'sourceOriginalFrame': source['frames'][index],
                          'alphaExtrema': list(image.getchannel('A').getextrema()), **phase_records[index]}
                frames.append(record)
            if len({f['sha256'] for f in frames}) != len(frames):
                raise ValueError('Distinct original slots need distinct replacement rasters')
            resources.append({**base.ref(target), 'nativePath': source['nativePath'], 'itemId': item_id,
                              'category': source['category'], 'resourceId': source['resourceId'],
                              'sourceSha256': source['sourceSha256'], 'sourceLoose': True, 'sourcePacked': False,
                              'stateInterpretation': 'displayed skill levels' if item_id in LEVELS else 'material brightness variants',
                              'frames': frames, 'sourceFrameDurationMs': None, 'nativeRuntimeVerified': False,
                              'visualAccepted': False})
    result = {'schemaVersion': 1, 'scope': 'Five native inventory level and material state resources',
              'sourceContract': base.ref(contract_path), 'items': resources,
              'convertedItemCount': len(resources), 'sourcePositions': sum(len(i['frames']) for i in resources),
              'converterSources': [base.ref(Path(__file__).resolve()), base.ref(ROOT / 'scripts/native-ui-format.py'),
                                   base.ref(ROOT / 'scripts/build-native-inventory-art.py')],
              'paintedLevelGenerationCalls': 2, 'newModelGeneration': False,
              'sourceFrameDurationMs': None, 'visualAccepted': False, 'nativeRuntimeVerified': False,
              'preview': make_preview(resources, source_items, check)}
    base.save_json(HERE / 'manifest.json', result, check)
    print(json.dumps({'convertedNativeIcons': len(resources), 'sourcePositions': result['sourcePositions'],
                      'nativeGeometryRetained': True, 'pixelReplay': check}))


if __name__ == '__main__':
    main()
