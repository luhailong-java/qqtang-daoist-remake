"""Index completed candidate sequence records only; never decode images or alter runtime art."""
from pathlib import Path
import datetime
import hashlib
import json

root = Path(__file__).resolve().parents[1]
maps = root / 'assets/maps'
continuation_paths = set(maps.glob('animation-continuation-*/*/sequence.json'))
paths = set(maps.glob('*/animation-candidates/*/sequence.json')) | continuation_paths
records = []
continuation_dates = []
element_ids = set()
for path in sorted(paths):
    raw = path.read_bytes()
    data = json.loads(raw)
    element_id = data['elementId']
    if element_id in element_ids:
        raise ValueError(f'Duplicate candidate sequence for element {element_id}')
    element_ids.add(element_id)
    manifest_hash = hashlib.sha256(raw).hexdigest()
    if path in continuation_paths:
        audit_path = path.with_name('source-chain-file-audit.json')
        audit = json.loads(audit_path.read_bytes())
        if audit['elementId'] != element_id or audit['sequenceSha256'] != manifest_hash or audit['errors']:
            raise ValueError(f'Source chain audit does not verify {path.relative_to(root)}')
        continuation_dates.append(datetime.datetime.fromisoformat(data['createdAtUTC']).date())
    frames = data['frames']
    density4 = [f.get('exports', {}).get('4', {}) for f in frames]
    files = {f['file'] for f in density4 if f.get('file')}
    missing = sorted(f for f in files if not (root / f).is_file())
    records.append({
        'elementId': element_id, 'family': data.get('family', path.parents[2].name),
        'manifest': path.relative_to(root).as_posix(),
        'manifestSha256': manifest_hash,
        'sourceDeclaredFrameCount': data['sourceDeclaredFrameCount'],
        'framePositionsRecorded': len(frames),
        'referencedDensity4PngFiles': len(files), 'missingFiles': missing,
        'allResourceFramePositionsPresent': (len(frames) == data['sourceDeclaredFrameCount']
            and {f['sourceFrameIndex'] for f in frames} == set(range(data['sourceDeclaredFrameCount']))
            and not missing and all(f.get('exports', {}).get('4', {}).get('file')
                or f.get('structuralEmpty') or f.get('sourceFullyTransparentPixels') for f in frames)),
        'accepted': False, 'runtimeIntegrated': False,
    })
out = {
    'schemaVersion': 1,
    'capturedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Production-only JSON membership and file existence; no PNG, geometry, state or runtime acceptance.',
    'sequenceCount': len(records),
    'sourceFramePositionsRecorded': sum(r['framePositionsRecorded'] for r in records),
    'referencedDensity4PngFiles': sum(r['referencedDensity4PngFiles'] for r in records),
    'acceptedCount': 0, 'runtimeIntegrated': False,
    'nativeTimingKnown': False, 'nativeCombinedOriginKnown': False,
    'entries': sorted(records, key=lambda record: record['elementId']),
}
if continuation_dates:
    out['continuationDate'] = max(continuation_dates).isoformat()
target = root / 'assets/maps/animation-candidates-index.json'
target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: out[k] for k in ['sequenceCount', 'sourceFramePositionsRecorded', 'acceptedCount']}))
