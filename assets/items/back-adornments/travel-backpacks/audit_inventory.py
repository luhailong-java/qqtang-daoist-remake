"""Read-only audit of this six-ID inventory scope and exact builtin evidence."""
from pathlib import Path
import hashlib
import json

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDS = {1169, 1329, 1330, 1331, 1553, 3027}
errors = []
checked = {}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def require(condition, message):
    if not condition:
        errors.append(message)


def check_file(path, expected):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    require(path.is_file(), f'Missing {path}')
    if path.is_file():
        key = path.relative_to(ROOT).as_posix()
        checked.setdefault(key, hashlib.sha256(path.read_bytes()).hexdigest())
        require(checked[key] == expected, f'SHA mismatch {key}')


for path in sorted((HERE / 'mothers').glob('*.generation.json')):
    g = read(path)
    check_file(g['file'], g['sha256'])
    require(g['exactPrompt'] == g['prompt'], f'Exact prompt mismatch {path.name}')
    require(hashlib.sha256(g['exactPrompt'].encode('utf-8')).hexdigest() == g['submittedPromptSha256'],
            f'CRLF actual prompt SHA mismatch {path.name}')
    require(g['actualModel'] is None and g['actualQuality'] is None, f'Unproven actual selectors {path.name}')
    require(g['submittedParameters']['transparent_background'] is True, f'Transparency not requested {path.name}')
    check_file(g['promptFile'], g['promptFileSha256'])
    check_file(g['evidence']['actualSubmissionRecord'], g['evidence']['actualSubmissionRecordSha256'])
    sub = read(ROOT / g['evidence']['actualSubmissionRecord'])
    require(sub['prompt'] == g['exactPrompt'], f'Actual pre-call submission differs {path.name}')
    require(sub['submittedParameters']['referenced_image_paths'] == g['submittedParameters']['referenced_image_paths'],
            f'Actual reference order differs {path.name}')
    for ref in g['references']:
        check_file(ref['path'], ref['sha256'])
    if 'editOf' in g:
        check_file(g['editOf']['file'], g['editOf']['sha256'])
        if 'generationRecord' in g['editOf']:
            check_file(g['editOf']['generationRecord'], g['editOf']['generationRecordSha256'])
        if 'sourceRecord' in g['editOf']:
            check_file(g['editOf']['sourceRecord'], g['editOf']['sourceRecordSha256'])
    with Image.open(ROOT / g['file']) as picture:
        require(picture.mode == 'RGBA' and list(picture.size) == [g['width'], g['height']], f'Native metadata {path.name}')

for path in sorted((HERE / 'references').rglob('*.source.json')):
    source = read(path)
    if source.get('file') and source.get('sha256'):
        check_file(source['file'], source['sha256'])
    parent = source.get('source')
    if isinstance(parent, dict) and parent.get('generationRecord'):
        check_file(parent['file'], parent['sha256'])
        check_file(parent['generationRecord'], parent['generationRecordSha256'])

selected = []
path = HERE / 'art.json'
if not path.exists():
    errors.append('Missing selected inventory manifest')
else:
    document = read(path)
    require({e['itemId'] for e in document['items']} == IDS and len(document['items']) == 6, 'Incomplete six-ID inventory family')
    for flag in ['accepted', 'visualAccepted', 'geometryAccepted', 'runtimeAdopted', 'completeAnimationAccepted']:
        require(document[flag] is False, f'Unreviewed overall flag {flag}')
    require(document['worldCandidatePositions'] == 0 and document['worldCandidateCoverageComplete'] is False,
            'Inventory work cannot claim world coverage')
    for item in document['items']:
        ident = item['itemId']
        require({v['width'] for v in item['mobileVariants']} == {64, 96}, f'Mobile variants missing {ident}')
        rows = [item] + [read(ROOT / v['provenanceRecord']) for v in item['mobileVariants']]
        source = read(HERE / f'references/{ident}/inventory-source-contract.json')['decodedReference']
        physical = read(HERE / f'references/{ident}/inventory-physical-reference.png.source.json')
        world = read(HERE / f'references/{ident}/world-source-contract.json')
        require(world['decodedSourcePositions'] == [0] and world['pixelReferenceCoverageComplete'] is False,
                f'Static-only world input overstated {ident}')
        require(world['worldCandidatePositions'] == [] and world['worldCandidateCoverageComplete'] is False,
                f'Unmade world phases overstated {ident}')
        for frame in rows:
            selected.append(frame)
            check_file(frame['file'], frame['sha256'])
            require(read(ROOT / frame['provenanceRecord']) == frame, f'Sidecar differs {frame["file"]}')
            require(frame['sourceNativeInventoryFrameSize'] == source['nativeFrameSize'], f'Source size changed {ident}')
            require(frame['sourceInventoryFrameOffsetRaw'] == source['frameOffsetRaw'], f'Source offset changed {ident}')
            require(frame['sourceNativeFrameRecord'] == source['sourceNativeFrameRecord'], f'Source native record changed {ident}')
            for flag in ['accepted', 'visualAccepted', 'geometryAccepted', 'runtimeAdopted', 'completeAnimationAccepted']:
                require(frame[flag] is False, f'Unreviewed flag {flag} {ident}')
            require(frame['userReviewStatus'] == 'pending', f'Unreviewed status {ident}')
            require(all(frame[k] is None for k in ['directionSemantic', 'frameDurationMs', 'loop', 'nativeAttachment']),
                    f'Invented native semantics {ident}')
            require(frame['qa']['relativeAspectDeviation'] <= 0.1, f'Mother physical envelope failed {ident}')
            derived = frame['derivedFrom']
            for key in ['sourceReference', 'sourcePhysicalEnvelopeRecord', 'sourceWorldStaticInput']:
                check_file(frame[key]['file'], frame[key]['sha256'])
            check_file(derived['file'], derived['sha256'])
            check_file(derived['generationRecord'], derived['generationRecordSha256'])
            with Image.open(ROOT / frame['file']) as picture:
                require(picture.mode == 'RGBA' and picture.size == (frame['width'], frame['height']), f'RGBA/dimensions {ident}')
                require(picture.getchannel('A').getextrema()[0] == 0, f'Actual empty alpha missing {ident}')
                box = picture.getchannel('A').point(lambda a: 255 if a >= 16 else 0).getbbox()
                sw, sh = physical['sourcePhysicalEnvelopeSize']
                deviation = abs(((box[2] - box[0]) / (box[3] - box[1])) / (sw / sh) - 1)
                require(deviation <= 0.1, f'Export physical envelope failed {ident} size{picture.width}: {deviation}')
                require(abs(frame['qa']['exportedAspectDeviation'] - deviation) < 1e-12, f'Export QA differs {ident}')
provenance = HERE / 'previews/provenance.json'
if provenance.exists():
    for preview in read(provenance)['files']:
        check_file(preview['file'], preview['sha256'])
        for source in preview['inputs']:
            check_file(source['file'], source['sha256'])
report = {'scope': 'six literal-name backpack inventory IDs only; world unmade and user review pending',
          'sourceIds': sorted(IDS), 'selectedInventoryItems': len(selected) // 3,
          'selected256AndMobilePngs': len(selected), 'worldCandidatePositions': 0,
          'errors': errors, 'checkedFiles': checked, 'technicalFileChecksPassed': not errors,
          'visualAccepted': False, 'geometryAccepted': False, 'runtimeAdopted': False, 'completeAnimationAccepted': False}
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(bool(errors))
