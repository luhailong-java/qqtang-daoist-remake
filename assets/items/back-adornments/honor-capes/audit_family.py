"""Independent file/contract audit for the five new capes; no visual acceptance."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDS = {148, 149, 150, 151, 152}
parser = argparse.ArgumentParser()
parser.add_argument('--write-report', action='store_true', help='Explicitly replace the frozen audit report; refresh selected-index audit SHA afterwards')
args = parser.parse_args()
errors = []
checked = {}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, reason):
    if not condition:
        errors.append(reason)


def file_hash(path, expected):
    path = Path(path)
    path = path if path.is_absolute() else ROOT / path
    require(path.is_file(), f'Missing {path}')
    if path.is_file():
        key = path.relative_to(ROOT).as_posix()
        actual = checked.get(key) or sha(path)
        require(actual == expected, f'SHA mismatch {path}')
        checked[key] = actual


for path in sorted((HERE / 'mothers').glob('*.png.generation.json')):
    g = read(path)
    file_hash(g['file'], g['sha256'])
    exact = g['exactPrompt']
    require(exact == g['prompt'], f'Prompt text mismatch {path.name}')
    require(hashlib.sha256(exact.encode('utf-8')).hexdigest() == g['submittedPromptSha256'],
            f'Actual prompt SHA mismatch {path.name}')
    require(g['actualModel'] is None and g['actualQuality'] is None,
            f'Unproven actual model/quality {path.name}')
    require(g['submittedParameters']['transparent_background'] is True, f'Transparency not requested {path.name}')
    file_hash(g['promptFile'], g['promptFileSha256'])
    file_hash(g['evidence']['actualSubmissionRecord'], g['evidence']['actualSubmissionRecordSha256'])
    submission = read(ROOT / g['evidence']['actualSubmissionRecord'])
    require(submission['prompt'] == exact, f'Pre-call evidence differs {path.name}')
    require(submission['submittedParameters'] == {k: g['submittedParameters'][k]
            for k in ['referenced_image_paths', 'transparent_background']}, f'Actual parameters differ {path.name}')
    for ref in g['references']:
        file_hash(ref['path'], ref['sha256'])
    if 'editOf' in g:
        file_hash(g['editOf']['file'], g['editOf']['sha256'])
        if 'sourceRecord' in g['editOf']:
            file_hash(g['editOf']['sourceRecord'], g['editOf']['sourceRecordSha256'])
    with Image.open(ROOT / g['file']) as pic:
        require(pic.mode == 'RGBA' and pic.size == (g['width'], g['height']), f'Native PNG mismatch {path.name}')

for path in sorted((HERE / 'references').rglob('*.source.json')):
    ref = read(path)
    if ref.get('file') and ref.get('sha256'):
        file_hash(ref['file'], ref['sha256'])
    source = ref.get('source', {})
    if isinstance(source, dict) and source.get('generationRecord'):
        file_hash(source['file'], source['sha256'])
        file_hash(source['generationRecord'], source['generationRecordSha256'])

position_count = 0
icon_count = 0
for kind, name in [('inventory', 'art.json'), ('world', 'world-art.json')]:
    path = HERE / name
    if not path.exists():
        errors.append(f'Missing selected {name}')
        continue
    document = read(path)
    require({i['itemId'] for i in document['items']} == IDS, f'{kind} must select exactly five source IDs')
    require(document['accepted'] is False and document['runtimeAdopted'] is False, f'{kind} overall flag')
    for entry in document['items']:
        ident = entry['itemId']
        contract = read(HERE / f'references/{ident}/source-contract.json')
        require(contract['sourceFrameOrder'] == list(range(12)), f'{ident} source order')
        require(contract['standWalkByteIdentical'] is True, f'{ident} source states no longer identical')
        for source in contract['frames']:
            file_hash(source['file'], source['sha256'])
        frames = [entry] if kind == 'inventory' else entry['frames']
        if kind == 'world':
            require({f['sourceFrameIndex'] for f in frames} == set(range(12)) and len(frames) == 12,
                    f'{ident} world source-position coverage incomplete')
            require(entry['sourceFrameOrder'] == list(range(12)), f'{ident} selected order')
            for key in ['directionSemantic', 'frameDurationsMs', 'loop', 'nativeAttachment']:
                require(entry[key] is None, f'{ident} unproven {key}')
        for frame in frames:
            icon_count += kind == 'inventory'
            position_count += kind == 'world'
            file_hash(frame['file'], frame['sha256'])
            sidecar = read(ROOT / frame['provenanceRecord'])
            require(sidecar == frame, f'Sidecar differs {frame["file"]}')
            for key in ['accepted', 'runtimeAdopted', 'visualAccepted', 'geometryAccepted', 'completeAnimationAccepted']:
                require(frame[key] is False, f'Unreviewed {key} true {frame["file"]}')
            require(frame['userReviewStatus'] == 'pending', f'Unreviewed status {frame["file"]}')
            require(frame['qa']['relativeAspectDeviation'] <= 0.1, f'Envelope failed {frame["file"]}')
            derived = frame['derivedFrom']
            file_hash(derived['file'], derived['sha256'])
            file_hash(derived['generationRecord'], derived['generationRecordSha256'])
            with Image.open(ROOT / frame['file']) as picture:
                require(picture.mode == 'RGBA' and picture.getchannel('A').getextrema()[0] == 0,
                        f'Output lacks actual transparency {frame["file"]}')
                require(picture.size == (frame['width'], frame['height']), f'Output dimensions {frame["file"]}')
            if kind == 'world':
                source = contract['frames'][frame['sourceFrameIndex']]
                require(frame['logicalFrameSize'] == source['nativeFrameSize'], f'Logical size changed {frame["file"]}')
                require(frame['frameOffsetRaw'] == source['frameOffsetRaw'], f'Raw offset changed {frame["file"]}')
                require([frame['width'], frame['height']] == [v * 4 for v in source['nativeFrameSize']],
                        f'Density4 mismatch {frame["file"]}')
                require(frame['sourceNativeFrameRecord'] == source['sourceNativeFrameRecord'],
                        f'Source record changed {frame["file"]}')
            elif frame.get('nativeInventoryVariant'):
                native = frame['nativeInventoryVariant']
                file_hash(native['file'], native['sha256'])
                native_record = read(ROOT / native['provenanceRecord'])
                file_hash(native_record['file'], native_record['sha256'])
                original = read(HERE / f'references/{ident}/inventory-source.png.source.json')
                require(native_record['logicalFrameSize'] == original['nativeFrameSize'], f'Inventory native size {ident}')
                require(native_record['frameOffsetRaw'] == original['frameOffsetRaw'], f'Inventory raw offset {ident}')
                with Image.open(ROOT / native['file']) as pic:
                    require(list(pic.size) == [v * 4 for v in original['nativeFrameSize']], f'Inventory density4 {ident}')

preview_provenance = HERE / 'previews/provenance.json'
if preview_provenance.exists():
    for preview in read(preview_provenance)['files']:
        file_hash(preview['file'], preview['sha256'])
        for asset in preview['inputs']:
            file_hash(asset['file'], asset['sha256'])

report = {'schemaVersion': 1, 'auditedAtUTC': datetime.now(timezone.utc).isoformat(),
          'scope': 'Only IDs148–152 static file/hash/source geometry checks; no visual, timing, attachment or runtime acceptance',
          'sourceIds': sorted(IDS), 'selectedInventoryIcons': icon_count,
          'selectedWorldPositions': position_count, 'errors': errors, 'checkedFiles': checked,
          'technicalFileChecksPassed': not errors, 'visualAccepted': False,
          'completeAnimationAccepted': False, 'runtimeAdopted': False}
if args.write_report:
    target = HERE / 'validation/final-source-chain-audit.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'checkedFiles'}, ensure_ascii=False))
raise SystemExit(bool(errors))
