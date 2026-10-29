"""Bounded static property-table inspection; never executes client code."""
from pathlib import Path
import json,struct,hashlib,zipfile
root=Path(__file__).resolve().parents[1]
source=root/'.artifacts/reference-inputs/extracted/QQTang-Local/runtime/client-patched/object/mapElem/mapElem.prop'
data=source.read_bytes()
if hashlib.sha256(data).hexdigest()!='9b27eb66494c74770e9242ba4df34d7c03db7dd44b130a02440abff95a284a64':raise ValueError('Property input differs from inspected source')
with zipfile.ZipFile(root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as package:
    archive_data=package.read('QQTang-Local/runtime/client-patched/object/mapElem/mapElem.prop')
if archive_data!=data:raise ValueError('Extracted property file differs from fixed archive member')
version,count=struct.unpack_from('<II',data)
if version!=2 or count>4096:raise ValueError('Unsupported property header')
cursor=8;records=[];seen=set()
for ordinal in range(count):
    start=cursor
    if cursor+24>len(data):raise ValueError('Property record truncated')
    ident,width,height,ox,oy,lifetime,word20,word24=struct.unpack_from('<IHHhhiII',data,cursor);cursor+=24
    if ident in seen or not 1<=width<=64 or not 1<=height<=64:raise ValueError(f'Invalid property identity/size at {ordinal}')
    cells=width*height
    if cursor+cells*4>len(data):raise ValueError('Property grid truncated')
    attrs=list(struct.unpack_from('<'+'I'*cells,data,cursor));cursor+=cells*4;seen.add(ident)
    records.append({'id':ident,'recordOffset':start,'recordBytes':cursor-start,'widthCells':width,'heightCells':height,
        'offsetRaw':[ox,oy],'lifeTimeRaw':lifetime,'wordAtRecord16':word20,'wordAtRecord20':word24,'gridAttrRaw':attrs})
if cursor!=len(data):raise ValueError(f'Unparsed property bytes: {len(data)-cursor}')
python_elements=json.loads((root/'references/qqtang-map-data/elements.json').read_text(encoding='utf-8'))['elements'];by_id={e['id']:e for e in python_elements}
comparisons=[]
for record in records:
    if record['id']not in by_id:continue
    p=by_id[record['id']];pairs={'widthCells':(record['widthCells'],p['widthCells']),'heightCells':(record['heightCells'],p['heightCells']),
        'offset':(record['offsetRaw'],p['imageOffset']),'lifeTime':(record['lifeTimeRaw'],p['properties']['LifeTime']),
        'gridAttr':(record['gridAttrRaw'],p['gridAttr']),'word16_vs_Level':(record['wordAtRecord16'],p['properties']['Level']),
        'word20_vs_canMove':(record['wordAtRecord20'],p['properties']['canMove'])}
    differences={key:{'binary':a,'python':b}for key,(a,b)in pairs.items()if a!=b}
    comparisons.append({'id':record['id'],'differences':differences,'binaryWord20':record['wordAtRecord20'],
        'pythonFlags':{key:p['properties'].get(key)for key in['canMove','canDoSpecial','canHide']}})
production=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'));unknown={e['elementId']for e in production['unknownSourceElementIds']}
result={'schemaVersion':1,'sourceFile':source.relative_to(root).as_posix(),'sourceSha256':hashlib.sha256(data).hexdigest(),
    'sourceArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
    'sourceType':'fixed community client property file; official original identity unverified','archiveMemberBytesEqual':True,
    'operation':'read-only independent binary structure inspection and comparison with static Python literals; no input execution',
    'formatHypothesis':'version2/count header; 24-byte fixed record plus width*height little-endian uint32 grid attributes',
    'version':version,'recordCount':count,'parsedBytes':cursor,'trailingBytes':0,'records':records,
    'sharedPythonDefinitionCount':len(comparisons),'comparedFields':['width','height','offset','LifeTime','GridAttr','word16 vs Level','word20 vs canMove'],
    'fieldDifferenceCount':sum(bool(c['differences'])for c in comparisons),'differences':[c for c in comparisons if c['differences']],
    'flagComparisons':[c for c in comparisons if c['binaryWord20']or any(c['pythonFlags'].values())],
    'additionalIds':[r['id']for r in records if r['id']not in by_id],
    'previouslyMissingIdsFound':sorted(unknown&seen),'previouslyMissingIdsStillAbsent':sorted(unknown-seen),
    'pythonIdsAbsentFromBinary':sorted(set(by_id)-seen),'runtimeChanged':False,'accepted':False,
    'limitations':['word16/word20 interpreted as Level/canMove from exact721-row correlation; native reader function not independently traced',
        'canDoSpecial and canHide are not serialized in this format and remain unknown for extra rows',
        'new records are not imported into runtime or art inventory','image lookup and source target-version identity remain separately unverified']}
out=root/'references/qqtang-map-data/binary-properties-inspection.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k]for k in['recordCount','parsedBytes','trailingBytes','sharedPythonDefinitionCount','fieldDifferenceCount','additionalIds','previouslyMissingIdsFound','previouslyMissingIdsStillAbsent','pythonIdsAbsentFromBinary']}))
