"""Merge four completed worker JSON records only; no image scan or mutation."""
from pathlib import Path
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'creatures';SUB=OUT/'boss-extension'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=read(OUT/'art.json');m=read(OUT/'identity-mapping.json');suba=read(SUB/'art.json');subm=read(SUB/'identity-mapping.json')
assert m['source']['sha256']==subm['source']['sha256']
assert {p['entityId']for p in suba['masters']}=={30006,30009,30012,30014}
for p in suba['masters']:
 assert p['accepted']is False and p['staticMasterOnly']is True and p['entityClass']=='boss'
 assert (ROOT/p['file']).is_file()and(ROOT/p['generationRecord']).is_file()
 old=next((x for x in a['masters']if x['entityId']==p['entityId']),None)
 if old:assert old==p
 else:a['masters'].append(p)
for p in subm['mappedIdentities']:
 assert p['entityClass']=='boss'and all(g['sourceGroupUnmodified']['combat_profiles'][0]['is_boss']is True for g in p['sourceMapGroups'])
 old=next((x for x in m['mappedIdentities']if x['entityId']==p['entityId']),None)
 if old:assert old==p
 else:m['mappedIdentities'].append(p)
save(OUT/'art.json',a);save(OUT/'identity-mapping.json',m)
save(SUB/'merge-receipt.json',{'mergedAtUTC':datetime.now(timezone.utc).isoformat(),'mergedEntityIds':[30006,30009,30012,30014],'masterCountAfterMerge':len(a['masters']),'identityCountAfterMerge':len(m['mappedIdentities']),'sourceFilesRemainInWorkerDirectory':True,'newImageScanPerformed':False,'accepted':False})
print(json.dumps({'mergedBossMasters':4,'masterCount':len(a['masters']),'mappedIdentityCount':len(m['mappedIdentities']),'accepted':False}))
