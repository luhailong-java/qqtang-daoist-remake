"""Bounded own-family inventory export; world metadata remains reference-only."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
from painted_crop_gate import validate_visible_boundaries

NAMES = {1169: '蹴云圆囊', 1329: '月兔行囊', 1330: '云栖考拉囊', 1331: '山灵小熊囊', 1553: '福豚锦囊', 3027: '灵酪甜筒囊'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def normalized(content, size):
    padding = size // 16
    scale = min((size - 2 * padding) / content.width, (size - 2 * padding) / content.height)
    extent = [round(content.width * scale), round(content.height * scale)]
    paint = content.convert('RGBa').resize(tuple(extent), Image.Resampling.LANCZOS).convert('RGBA')
    placement = [(size - extent[0]) // 2, (size - extent[1]) // 2]
    output = Image.new('RGBA', (size, size))
    output.alpha_composite(paint, tuple(placement))
    return output, scale, placement


version = sys.argv[1]
if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in version):
    raise ValueError('Unsafe take name')
spec_path = HERE / f'specs/{version}.json'
spec = read(spec_path)
if spec.get('doNotExport') or not 1 <= len(spec['frames']) <= 6:
    raise ValueError('Rejected or unbounded inventory batch')
source = ROOT / spec['source']
generation_path = Path(str(source) + '.generation.json')
generation = read(generation_path)
if sha(source) != generation['sha256']:
    raise ValueError('Native source bytes changed')
picture = Image.open(source).convert('RGBA')
cols, rows = spec['grid']
rects = []
for n, frame in enumerate(spec['frames']):
    cell = frame.get('cellIndex', n)
    rects.append(frame.get('manualRect', [round(cell % cols * picture.width / cols), round(cell // cols * picture.height / rows),
        round((cell % cols + 1) * picture.width / cols), round((cell // cols + 1) * picture.height / rows)]))
validate_visible_boundaries(picture, rects, threshold=16)
manifest_path = HERE / 'art.json'
document = read(manifest_path) if manifest_path.exists() else {'schemaVersion': 1, 'category': 'npack',
    'status': 'inventory-candidate-pending-user-review', 'familyRule': "catalog category=npack AND literal name contains 背包",
    'sourceIds': sorted(NAMES), 'worldCandidatePositions': 0, 'worldCandidateCoverageComplete': False,
    'accepted': False, 'visualAccepted': False, 'geometryAccepted': False, 'runtimeAdopted': False,
    'completeAnimationAccepted': False, 'items': []}
observations = []
for frame, rect in zip(spec['frames'], rects):
    ident = frame['itemId']
    if ident not in NAMES or frame['sourceFrameIndex'] != 0:
        raise ValueError('Inventory batch escapes explicit IDs or singleton source index')
    native = read(HERE / f'references/{ident}/inventory-source-contract.json')
    physical_path = HERE / f'references/{ident}/inventory-physical-reference.png.source.json'
    physical = read(physical_path)
    sw, sh = physical['sourcePhysicalEnvelopeSize']
    crop = picture.crop(rect)
    alpha = crop.getchannel('A')
    bbox = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
    if bbox is None or alpha.getextrema()[0] != 0:
        raise ValueError('No real empty alpha or no visible object in crop')
    content = crop.crop(bbox)
    deviation = abs((content.width / content.height) / (sw / sh) - 1)
    observation = {'itemId': ident, 'sourceFrameIndex': 0, 'actualNativeMotherSize': list(picture.size),
        'actualCellRectLTRB': rect, 'generatedAlphaBBoxAt16': list(bbox),
        'sourcePhysicalEnvelopeSize': [sw, sh], 'sourcePhysicalAspect': sw / sh,
        'generatedAspect': content.width / content.height, 'relativeAspectDeviation': deviation,
        'sourcePhysicalEnvelopeIsNotNativeAlpha': True, 'exported': deviation <= 0.1}
    observations.append(observation)
    if deviation > 0.1:
        continue
    original = native['decodedReference']
    world_contract = HERE / f'references/{ident}/world-source-contract.json'
    common = {'itemId': ident, 'category': 'npack', 'sourceName': native['name'], 'projectDisplayName': NAMES[ident],
        'sourceDescription': native['description'], 'scope': 'normalized static inventory only; no world phases created',
        'sourceReference': {'file': original['file'], 'sha256': original['sha256']},
        'sourceNativeInventoryFrameSize': original['nativeFrameSize'], 'sourceInventoryFrameOffsetRaw': original['frameOffsetRaw'],
        'sourceNativeFrameRecord': original['sourceNativeFrameRecord'],
        'sourcePhysicalEnvelopeRecord': {'file': rel(physical_path), 'sha256': sha(physical_path),
            'physicalRectLTRB': physical['sourcePhysicalRectLTRB'], 'size': [sw, sh],
            'method': physical['physicalEnvelopeMethod'], 'notNativeAlphaBBox': True},
        'nonPhysicalSourceUiOmitted': True, 'sourceUiOmission': physical['excludedUi'],
        'sourceWorldStaticInput': {'file': rel(world_contract), 'sha256': sha(world_contract),
                                  'decodedSourcePositions': [0], 'worldCandidatePositions': 0},
        'derivedFrom': {'file': spec['source'], 'sha256': sha(source), 'generationRecord': rel(generation_path),
                        'generationRecordSha256': sha(generation_path)},
        'qa': {k: observation[k] for k in ['relativeAspectDeviation', 'generatedAspect', 'sourcePhysicalAspect']},
        'visualAccepted': False, 'geometryAccepted': False, 'accepted': False, 'runtimeAdopted': False,
        'completeAnimationAccepted': False, 'userReviewStatus': 'pending', 'directionSemantic': None,
        'frameDurationMs': None, 'loop': None, 'nativeAttachment': None}
    variants = []
    for size in [64, 96, 256]:
        output, scale, placement = normalized(content, size)
        folder = 'icons' if size == 256 else f'mobile/{size}'
        target = HERE / f'{folder}/{ident}-{version}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        output.save(target)
        record = {**deepcopy(common), 'file': rel(target), 'sha256': sha(target), 'width': size, 'height': size,
            'anchor': [size // 2, size // 2], 'alphaExtrema': list(output.getchannel('A').getextrema()),
            'provenanceRecord': rel(target) + '.provenance.json',
            'operation': {'type': 'crop-uniform-fit-normalized-inventory', 'sourceCellRectLTRB': rect,
                          'generatedAlphaBBoxAt16': list(bbox), 'uniformScale': scale, 'placementPx': placement,
                          'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False,
                          'notWorldRegistration': True}}
        final_bbox = output.getchannel('A').point(lambda a: 255 if a >= 16 else 0).getbbox()
        final_aspect = (final_bbox[2] - final_bbox[0]) / (final_bbox[3] - final_bbox[1])
        record['qa'].update({'exportedAlphaBBoxAt16': list(final_bbox), 'exportedVisibleAspect': final_aspect,
                             'exportedAspectDeviation': abs(final_aspect / (sw / sh) - 1)})
        if size == 256:
            record['mobileVariants'] = variants
            document['items'] = [e for e in document['items'] if e['itemId'] != ident] + [record]
        else:
            variants.append({'file': record['file'], 'sha256': record['sha256'], 'width': size, 'height': size,
                             'provenanceRecord': record['provenanceRecord']})
        save(Path(str(target) + '.provenance.json'), record)
    observation['selected256'] = record['file']
document['items'].sort(key=lambda e: e['itemId'])
document['inventoryCandidateCoverageComplete'] = len(document['items']) == 6
save(manifest_path, document)
save(HERE / f'validation/{version}-export.json', {'source': spec['source'], 'frames': observations,
    'scope': 'physical envelope ratio/transparent crop checks only; no visual acceptance', 'visualAccepted': False})
for frame, rect in zip(spec['frames'], rects):
    frame['manualRect'] = rect
save(spec_path, spec)
print(json.dumps({'version': version, 'selectedInventoryIds': [e['itemId'] for e in document['items']],
                  'observations': observations, 'worldCandidatePositions': 0, 'visualAccepted': False}))
