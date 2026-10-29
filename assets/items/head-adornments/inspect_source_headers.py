"""Inspect at most six stand/walk headers. No pixel decode or runtime loading."""
from pathlib import Path
import zipfile, json, hashlib, struct, sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ids=list(map(int,sys.argv[1:]))
assert 1<=len(ids)<=3
catalog=json.loads((ROOT/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
entries={e['item_id']:e for e in catalog['items']}
target=OUT/'source-state-inventory.json'
doc=json.loads(target.read_text(encoding='utf-8')) if target.exists() else {'schemaVersion':1,'scope':'bounded source headers only, not animation production','items':[]}
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as package:
    for ident in ids:
        e=entries[ident]
        assert e['category']=='thadorn'
        row={'itemId':ident,'category':e['category'],'sourceName':e['name'],'sourceDescription':e['description'],
             'installedFiles':e['installed_files'],'inventoryIconCandidate':next(p for p in e['installed_files'] if p.lower().startswith('res/uires/icon/')),
             'worldStaticMasterProduced':False,'completeAnimationProduced':False,'worldStates':[]}
        for state in ['stand','walk']:
            member=next(p for p in e['installed_files'] if p.lower().endswith('_'+state+'.img'))
            source='QQTang-Local/runtime/client-patched/'+member
            data=package.read(source)
            record={'state':state,'sourceMember':source,'sourceSha256':hashlib.sha256(data).hexdigest(),'byteLength':len(data),'referenceOnly':True,
                    'pixelDataDecoded':False,'completeContainerVerified':False,'opaqueSuffixMeaning':'not inspected by header-only reader'}
            if len(data)>=40 and data[:8]==b'QQF\x1aDIMG':
                words=struct.unpack_from('<8I',data,8)
                record.update({'signature':'QQF1aDIMG','version':words[0],'frameInfoSize':words[1],'frameCount':words[2],
                               'directions':words[3],'unknownHeaderWords24And28':list(words[4:6]),'declaredCanvas':list(words[6:8])})
                if len(data)>=56:
                    marker,x,y,mode=struct.unpack_from('<IiiI',data,40)
                    record['firstDeclaredFrame']={'index':0,'marker':marker,'offsetRaw':[x,y],'pixelMode':mode,'empty':mode==0}
                    if mode and len(data)>=68:
                        w,h,u=struct.unpack_from('<3I',data,56)
                        record['firstDeclaredFrame'].update({'size':[w,h],'unknownImageHeaderWord':u})
            else:
                record['formatStatus']='non-DIMG or truncated; do not decode by assumed layout'
            row['worldStates'].append(record)
        doc['items']=[p for p in doc['items'] if p['itemId']!=ident]+[row]
        print(json.dumps(row,ensure_ascii=False))
doc['items'].sort(key=lambda e:e['itemId'])
target.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
