"""Read ZIP directory and existing item JSON only; do not decode artwork."""
from pathlib import Path
from collections import Counter,defaultdict
import json,zipfile,datetime

root=Path(__file__).resolve().parents[1]
archive=root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
prefix='QQTang-Local/runtime/client-patched/'
with zipfile.ZipFile(archive)as z:
    rows=[]
    for info in z.infolist():
        if info.is_dir()or not info.filename.startswith(prefix):continue
        relative=info.filename[len(prefix):]
        if not(relative.startswith('res/uiRes/')or relative.startswith('ui/')):continue
        parts=relative.split('/')
        group='/'.join(parts[:3])if relative.startswith('res/')else'/'.join(parts[:2])
        rows.append({'path':relative,'archiveMember':info.filename,'uncompressedBytes':info.file_size,
            'zipCrc32':f'{info.CRC:08x}','group':group,'extension':Path(relative).suffix.lower()})
groups=Counter(r['group']for r in rows)
catalog=json.loads((root/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
same_paths=defaultdict(list)
for item in catalog['items']:
    paths=tuple(sorted(item['installed_files']))
    if paths:same_paths[(item['category'],paths)].append(item['item_id'])
aliases=[{'category':key[0],'installedPaths':list(key[1]),'itemIds':ids}for key,ids in same_paths.items()if len(ids)>1]
record={'schemaVersion':1,'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'operation':'ZIP central-directory metadata and existing item JSON only; no image decode, client execution, build or test',
    'sourceArchive':'QQTang-Local-v1.3.4.zip',
    'previouslyVerifiedArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
    'archiveRehashedInThisRead':False,'officialOriginalAuthenticity':'unverified',
    'uiDirectoryFileCount':sum(r['path'].startswith('ui/')for r in rows),
    'resUiDirectoryFileCount':sum(r['path'].startswith('res/uiRes/')for r in rows),
    'groups':dict(sorted(groups.items())),'files':rows,
    'itemSourceRecordCount':len(catalog['items']),
    'uniqueCategoryAndInstalledPathSets':len(same_paths),'identicalInstalledPathGroups':aliases,
    'interpretation':'File counts are source inventory, not page counts or accepted new artwork. Same installed paths are an explicit source-file alias, not permission to merge unlike items or claim new visual approval.',
    'runtimeImported':False,'visualAccepted':False}
folder=root/'references/qqtang-ui-data';folder.mkdir(exist_ok=True)
(folder/'resource-inventory.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k]for k in ['uiDirectoryFileCount','resUiDirectoryFileCount','groups','itemSourceRecordCount','uniqueCategoryAndInstalledPathSets']}))
