"""Export only this five-cape family, fitting actual AI paint to fixed source geometry."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.dont_write_bytecode = True  # Keep imported shared helper read-only.
sys.path.insert(0, str(ROOT / 'scripts'))
from painted_crop_gate import validate_visible_boundaries

NAMES = {148: '青岚羽林披', 149: '紫雾骁风披', 150: '玄霜夜行披', 151: '金霞影羽披', 152: '朱金太御披'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def fit(content, canvas, target_box, bottom=True):
    left, top, right, low = target_box
    scale = min((right - left) / content.width, (low - top) / content.height)
    size = (round(content.width * scale), round(content.height * scale))
    painted = content.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
    pos = (left + (right - left - size[0]) // 2,
           low - size[1] if bottom else top + (low - top - size[1]) // 2)
    result = Image.new('RGBA', canvas)
    result.alpha_composite(painted, pos)
    return result, scale, pos


version = sys.argv[1]
spec_path = HERE / f'specs/{version}.json'
spec = read(spec_path)
if spec.get('doNotExport'):
    raise ValueError('Rejected take cannot be exported')
if not 1 <= len(spec['frames']) <= 6:
    raise ValueError('Bounded batch must select 1–6 explicit frames')
source = ROOT / spec['source']
generation_path = Path(str(source) + '.generation.json')
generation = read(generation_path)
if sha(source) != generation['sha256']:
    raise ValueError('Native generated source SHA changed')
mother = Image.open(source).convert('RGBA')
cols, rows = spec['grid']
rects = []
for n, item in enumerate(spec['frames']):
    cell = item.get('cellIndex', n)
    rects.append(item.get('manualRect', [round(cell % cols * mother.width / cols), round(cell // cols * mother.height / rows),
        round((cell % cols + 1) * mother.width / cols), round((cell // cols + 1) * mother.height / rows)]))
validate_visible_boundaries(mother, rects, threshold=16)
manifest_path = HERE / ('art.json' if spec['kind'] == 'inventory' else 'world-art.json')
document = read(manifest_path) if manifest_path.exists() else {
    'schemaVersion': 1, 'status': 'candidate-pending-user-review', 'items': [], 'accepted': False, 'runtimeAdopted': False}
observations = []
for item, rect in zip(spec['frames'], rects):
    ident, index = item['itemId'], item['sourceFrameIndex']
    if ident not in NAMES:
        raise ValueError('Attempt to export outside the assigned five source IDs')
    crop = mother.crop(rect)
    alpha = crop.getchannel('A')
    bbox = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
    if bbox is None or alpha.getextrema()[0] != 0:
        raise ValueError('Crop lacks visible paint or actual empty alpha')
    content = crop.crop(bbox)
    source_contract = read(HERE / f'references/{ident}/source-contract.json')
    if spec['kind'] == 'inventory':
        original = read(HERE / f'references/{ident}/inventory-source.png.source.json')
        physical = read(HERE / f'references/{ident}/inventory-physical-source.png.source.json')
        source_box = physical['physicalCapeRectLTRB']
    else:
        if index < 0 or index >= 12:
            raise ValueError('Cape source index outside explicit source contract')
        original = source_contract['frames'][index]
        source_box = original['sourceAlphaBBoxAt16']
    source_aspect = (source_box[2] - source_box[0]) / (source_box[3] - source_box[1])
    error = abs((content.width / content.height) / source_aspect - 1)
    observation = {'itemId': ident, 'sourceFrameIndex': index, 'actualMotherSize': list(mother.size),
                   'actualCellRectLTRB': rect, 'generatedAlphaBBoxAt16': list(bbox),
                   'sourcePhysicalAlphaBBoxAt16': source_box, 'relativeAspectDeviation': error,
                   'sourceVisibleAspect': source_aspect, 'generatedVisibleAspect': content.width / content.height,
                   'exported': error <= 0.1}
    observations.append(observation)
    if error > 0.1:
        continue
    derived = {'file': spec['source'], 'sha256': sha(source), 'generationRecord': relative(generation_path),
               'generationRecordSha256': sha(generation_path)}
    common = {'itemId': ident, 'category': 'npack', 'sourceName': source_contract['sourceName'],
              'projectDisplayName': NAMES[ident], 'sourceDescription': source_contract['sourceDescription'],
              'derivedFrom': derived, 'geometryAccepted': False, 'visualAccepted': False,
              'accepted': False, 'runtimeAdopted': False, 'userReviewStatus': 'pending',
              'completeAnimationAccepted': False,
              'directionSemantic': None, 'frameDurationMs': None, 'loop': None,
              'qa': {'relativeAspectDeviation': error, 'sourceVisibleAspect': source_aspect,
                     'generatedVisibleAspect': content.width / content.height}}
    if spec['kind'] == 'inventory':
        output, scale, placement = fit(content, (256, 256), [16, 16, 240, 240], bottom=False)
        target = HERE / f'icons/{ident}-honor-cape-{version}.png'
        operation = {'type': 'crop-uniform-fit-normalized-ui-icon', 'sourceCellRectLTRB': rect,
                     'generatedContentBBoxAt16': list(bbox), 'uniformScale': scale, 'placementPx': list(placement),
                     'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False}
        record = {**common, 'file': relative(target), 'width': 256, 'height': 256, 'anchor': [128, 128],
                  'sourceReference': original['file'], 'sourceReferenceSha256': original['sha256'],
                  'sourceNativeInventoryFrameSize': original['nativeFrameSize'],
                  'sourceInventoryFrameOffsetRaw': original['frameOffsetRaw'], 'operation': operation,
                  'sourcePhysicalCapeRectLTRB': source_box, 'nonPhysicalSourceBlueUiBaseOmitted': True,
                  'scope': 'static normalized inventory garment icon; world source geometry is separately preserved'}
        native_size = [value * 4 for value in original['nativeFrameSize']]
        native, native_scale, native_pos = fit(content, tuple(native_size), [value * 4 for value in source_box])
        native_target = HERE / f'icons-native/{ident}-inventory-density4-{version}.png'
        native_target.parent.mkdir(parents=True, exist_ok=True)
        native.save(native_target)
        native_record = {**deepcopy(common), 'file': relative(native_target), 'sha256': sha(native_target),
            'width': native.width, 'height': native.height, 'logicalFrameSize': original['nativeFrameSize'],
            'frameOffsetRaw': original['frameOffsetRaw'], 'exportDensity': 4,
            'sourceReference': {'file': original['file'], 'sha256': original['sha256']},
            'nonPhysicalSourceBlueUiBaseOmitted': True,
            'operation': {**operation, 'type': 'uniform-fit-physical-cape-to-original-inventory-canvas-density4',
                          'sourcePhysicalCapeRectLTRB': source_box, 'uniformScale': native_scale, 'placementPx': list(native_pos)}}
        save(Path(str(native_target) + '.provenance.json'), native_record)
        record['nativeInventoryVariant'] = {'file': relative(native_target), 'sha256': sha(native_target),
                                            'provenanceRecord': relative(native_target) + '.provenance.json'}
    else:
        native_size = [value * 4 for value in original['nativeFrameSize']]
        output, scale, placement = fit(content, tuple(native_size), [value * 4 for value in source_box])
        target = HERE / f'world/{ident}/frame-{index:03d}-{version}.png'
        operation = {'type': 'crop-uniform-fit-original-world-alpha-envelope', 'sourceCellRectLTRB': rect,
                     'generatedContentBBoxAt16': list(bbox), 'sourceLogicalAlphaBBoxAt16': source_box,
                     'uniformScale': scale, 'placementPx': list(placement), 'resampler': 'premultiplied-alpha LANCZOS',
                     'newModelGeneration': False, 'registration': 'source alpha envelope X-centred/Y-bottom; rawOffset unchanged'}
        record = {**common, 'sourceFrameIndex': index, 'sourcePhaseIndex': index, 'file': relative(target),
                  'width': native_size[0], 'height': native_size[1], 'logicalFrameSize': original['nativeFrameSize'],
                  'exportDensity': 4, 'frameOffsetRaw': original['frameOffsetRaw'],
                  'frameOffsetPxAtDensity4': [value * 4 for value in original['frameOffsetRaw']],
                  'sourceNativeFrameRecord': original['sourceNativeFrameRecord'],
                  'sourceReference': {'file': original['file'], 'sha256': original['sha256']},
                  'operation': operation, 'imagePhaseRepresentativeIndex': index,
                  'rasterAliasOfSourceFrameIndex': None, 'rasterImageShared': False,
                  'completeAnimationAccepted': False}
    target.parent.mkdir(parents=True, exist_ok=True)
    output.save(target)
    record.update({'sha256': sha(target), 'alphaExtrema': list(output.getchannel('A').getextrema()),
                   'provenanceRecord': relative(target) + '.provenance.json'})
    save(Path(str(target) + '.provenance.json'), record)
    if spec['kind'] == 'inventory':
        document['items'] = [entry for entry in document['items'] if entry['itemId'] != ident] + [record]
    else:
        entry = next((entry for entry in document['items'] if entry['itemId'] == ident), None)
        if entry is None:
            entry = {'itemId': ident, 'category': 'npack', 'sourceName': source_contract['sourceName'],
                     'projectDisplayName': NAMES[ident], 'sourceContract': relative(HERE / f'references/{ident}/source-contract.json'),
                     'sourceSha256': source_contract['sourceSha256'], 'sourceFrameOrder': list(range(12)),
                     'sourceFrameCount': 12, 'directions': 4, 'directionSemantic': None, 'frameDurationsMs': None,
                     'loop': None, 'nativeAttachment': None, 'standWalkByteIdentical': True,
                     'sourceStates': ['stand', 'walk'], 'sourceStateTimingShared': None, 'frames': [],
                     'accepted': False, 'visualAccepted': False, 'runtimeAdopted': False, 'completeAnimationAccepted': False}
            document['items'].append(entry)
        entry['frames'] = [frame for frame in entry['frames'] if frame['sourceFrameIndex'] != index] + [record]
        entry['frames'].sort(key=lambda frame: frame['sourceFrameIndex'])
        entry['candidateFrameCoverage'] = len(entry['frames'])
        entry['sourceDeclaredFrameCoverageComplete'] = len(entry['frames']) == 12
        entry['animationTimingKnown'] = False
    observation['outputFile'] = record['file']
document['items'].sort(key=lambda entry: entry['itemId'])
save(manifest_path, document)
save(HERE / f'validation/{version}-export.json', {'scope': 'bounded technical export only, user review pending',
    'source': spec['source'], 'frames': observations, 'visualAccepted': False, 'runtimeAdopted': False})
for item, rect in zip(spec['frames'], rects):
    item['manualRect'] = rect
save(spec_path, spec)
print(json.dumps({'version': version, 'frames': observations, 'manifest': relative(manifest_path), 'accepted': 0}))
