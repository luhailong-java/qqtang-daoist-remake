"""Read only selected data from a hash-pinned community archive. Never run it."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
OUT = ROOT / '.artifacts/reference-inputs/extracted'
EXPECTED = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
actual = hashlib.file_digest(ARCHIVE.open('rb'), 'sha256').hexdigest()
if actual != EXPECTED:
    raise ValueError('Archive SHA-256 mismatch')

prefix = 'QQTang-Local/runtime/client-patched/'
extra = {
    'QQTang-Local/README.md',
    'QQTang-Local/release-manifest.json',
    'QQTang-Local/data/qqt_competitive_map_rules.json',
    prefix + 'map/mapDesc.py',
    prefix + 'object/mapElem/mapElem.py',
    prefix + 'object/mapElem/mapElem.prop',
    prefix + 'config/LocalVersionFile.xml',
    prefix + 'config/UpdateVersionFile.xml',
    prefix + 'config/DLVersion.ini',
}
records = []
with zipfile.ZipFile(ARCHIVE) as archive:
    for entry in archive.infolist():
        if not (entry.filename in extra or
                entry.filename.startswith(prefix + 'map/') and
                entry.filename.endswith('.map')):
            continue
        name = PurePosixPath(entry.filename)
        if name.is_absolute() or '..' in name.parts or '\\' in entry.filename:
            raise ValueError('Unsafe entry path')
        target = (OUT / Path(*name.parts)).resolve()
        if not target.is_relative_to(OUT.resolve()):
            raise ValueError('Entry escapes output directory')
        if entry.file_size > 10_000_000:
            raise ValueError('Unexpectedly large reference data')
        data = archive.read(entry)  # zipfile checks the entry CRC.
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records.append({'archiveEntry': entry.filename,
                        'localPath': target.relative_to(ROOT).as_posix(),
                        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})

report = {'retrievedOn': '2026-10-26', 'sourceType': 'community-patched-client-data',
          'url': 'https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip',
          'archiveSha256': actual, 'executedExternalCode': False,
          'officialOriginalAuthenticity': 'unverified', 'files': records}
(OUT.parent / 'extracted-data-manifest.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'files': len(records), 'maps': sum(r['archiveEntry'].endswith('.map') for r in records),
                  'output': str(OUT), 'sha256': actual}))
