"""Register exact source-visible aliases without copying pixels or rules.

Only JSON and file existence are read during another task's heavy-job reservation.
Byte and image QA is intentionally deferred.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,copy
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=read(ROOT/'assets/maps/production-index.json');definitions={p['elementId']:p for p in inventory['elements']}
art=read(OUT/'art.json');painted={p['elementId']:p for p in art['pieces']}
pairs={16016:16002,16017:16003,16018:16004,16019:16001,16020:16005,16115:16101}
relationships=[];(OUT/'records').mkdir(exist_ok=True)
for target,representative in pairs.items():
 e=definitions[target];original=definitions[representative]
 assert e['family']==original['family']=='exploration'
 assert e['visualGroupId']==original['visualGroupId'] and e['selectedFrameSize']==original['selectedFrameSize']
 assert e['referencePng']['sha256']==original['referencePng']['sha256']
 base=painted[representative];assert (ROOT/base['file']).is_file()
 assert [base['worldFrameWidth'],base['worldFrameHeight']]==e['selectedFrameSize']
 p=copy.deepcopy(base);p.update({'elementId':target,'idMapping':e['familyMappingStatus'],'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourceReference':e['referencePng'],'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'seamlessVerified':False,'status':'painted-exact-source-visible-alias-reuse-awaiting-rule-anchor-and-in-game-validation'})
 origins=p['derivedFrom'];origins=origins if isinstance(origins,list)else[origins]
 record=base.get('provenanceRecord',base['file']+'.source.json');assert (ROOT/record).is_file()
 p['derivedFrom']=origins+[{'file':base['file'],'sha256':base['sha256'],'sourceRecord':record,'purpose':'existing own painted exploration sprite; verified exact source-visible alias, no new pixels'}]
 p['operation']={'type':'reuse-original-painted-png-by-verified-source-visible-alias','newModelGeneration':False,'resampled':False,'pixelBytesCopied':False,'sourceElementId':representative,'sameSourceVisualGroupId':e['visualGroupId'],'sourceReferencePngSha256':e['referencePng']['sha256'],'sourceNativeFrameSizeEqual':True,'newDefinitionRulesRetained':True,'imageByteVerification':'deferred during reserved heavy-job window; source SHA retained'}
 p['provenanceRecord']=f'assets/maps/exploration/records/{target}.source.json';save(ROOT/p['provenanceRecord'],p)
 if target in painted:art['pieces']=[x for x in art['pieces']if x['elementId']!=target]
 art['pieces'].append(p)
 relationships.append({'elementId':target,'sourceElementId':representative,'sourceVisualGroupId':e['visualGroupId'],'sourceFrame':e['selectedFrameSize'],'paintedFile':base['file'],'paintedSha256':base['sha256']})
save(OUT/'art.json',art)
save(OUT/'source-alias-relationships.json',{'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'relationshipCount':len(relationships),'method':'exact source visual-group identity, native frame size and reference PNG hash equality','newModelGenerations':0,'byteAndImageQA':'deferred during reserved heavy-job window','accepted':False,'relationships':relationships})
print(json.dumps({'family':'exploration','candidates':len(art['pieces']),'aliases':len(relationships),'newGenerations':0,'accepted':False}))
