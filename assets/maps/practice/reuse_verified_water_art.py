"""Reuse only exact source-visible aliases; keep every practice definition separate.

Reads JSON plus file existence during the reserved heavy-job window. Full byte
and image QC is deliberately left pending for the coordinator's later pass.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,copy
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=read(ROOT/'assets/maps/production-index.json');by_id={p['elementId']:p for p in inventory['elements']}
water=read(ROOT/'assets/maps/water/art.json');painted={p['elementId']:p for p in water['pieces']}
definitions=sorted([p for p in inventory['elements']if p['family']=='practice'],key=lambda p:p['elementId'])
assert len(definitions)==22
pieces=[];relationships=[];(OUT/'records').mkdir(exist_ok=True)
for e in definitions:
 representative=e['referencePng']['representativeElementId'];original=by_id[representative]
 assert original['family']=='water' and e['visualGroupId']==original['visualGroupId']
 assert e['selectedFrameSize']==original['selectedFrameSize'] and e['referencePng']['sha256']==original['referencePng']['sha256']
 base=painted[representative];assert (ROOT/base['file']).is_file()
 assert [base['worldFrameWidth'],base['worldFrameHeight']]==e['selectedFrameSize']
 p=copy.deepcopy(base);p.update({'elementId':e['elementId'],'idMapping':e['familyMappingStatus'],
  'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourceReference':e['referencePng'],
  'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'seamlessVerified':False,
  'status':'painted-exact-source-visible-alias-reuse-awaiting-rule-anchor-and-in-game-validation'})
 origins=p['derivedFrom'];origins=origins if isinstance(origins,list)else[origins]
 source_record=base.get('provenanceRecord')
 if not source_record:
  source_record=next((base['file']+suffix for suffix in ['.source.json','.provenance.json']if (ROOT/(base['file']+suffix)).is_file()),None)
 assert source_record
 p['derivedFrom']=origins+[{'file':base['file'],'sha256':base['sha256'],'sourceRecord':source_record,'purpose':'existing own painted water sprite; exact source-visible alias, no new pixels'}]
 p['operation']={'type':'reuse-original-painted-png-by-verified-source-visible-alias','newModelGeneration':False,'resampled':False,'pixelBytesCopied':False,
  'sourceElementId':representative,'sameSourceVisualGroupId':e['visualGroupId'],'sourceReferencePngSha256':e['referencePng']['sha256'],'sourceNativeFrameSizeEqual':True,
  'newDefinitionRulesRetained':True,'imageByteVerification':'deferred during another task reserved heavy-job window; recorded existing source SHA retained'}
 p['provenanceRecord']=f'assets/maps/practice/records/{e["elementId"]}.source.json'
 save(ROOT/p['provenanceRecord'],p);pieces.append(p)
 relationships.append({'practiceElementId':e['elementId'],'waterElementId':representative,'sourceVisualGroupId':e['visualGroupId'],'sourceFrame':e['selectedFrameSize'],'paintedFile':base['file'],'paintedSha256':base['sha256']})
save(OUT/'art.json',{'schemaVersion':1,'tilePixels':40,'status':'production-candidates','pieces':pieces})
save(OUT/'source-alias-relationships.json',{'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'relationshipCount':len(relationships),'method':'exact source visual-group identity plus native frame and reference PNG hash equality; not directory-name inference','newModelGenerations':0,'byteAndImageQA':'pending coordinator time slot','accepted':False,'relationships':relationships})
print(json.dumps({'family':'practice','candidates':len(pieces),'newGenerations':0,'exactSourceVisibleAliases':len(relationships),'accepted':False}))
