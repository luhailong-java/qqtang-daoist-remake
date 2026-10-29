"""Index completed candidate sequence records only; never decode images or alter runtime art."""
from pathlib import Path
import datetime
import hashlib
import json

root = Path(__file__).resolve().parents[1]
records = []
for path in sorted((root / 'assets/maps').glob('*/animation-candidates/*/sequence.json')):
    raw = path.read_bytes()
    data = json.loads(raw)
    frames = data['frames']
    density4 = [f.get('exports', {}).get('4', {}) for f in frames]
    files = {f['file'] for f in density4 if f.get('file')}
    missing = sorted(f for f in files if not (root / f).is_file())
    records.append({
        'elementId': data['elementId'], 'family': data.get('family', path.parents[2].name),
        'manifest': path.relative_to(root).as_posix(),
        'manifestSha256': hashlib.sha256(raw).hexdigest(),
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
    'entries': records,
}
target = root / 'assets/maps/animation-candidates-index.json'
target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: out[k] for k in ['sequenceCount', 'sourceFramePositionsRecorded', 'acceptedCount']}))
