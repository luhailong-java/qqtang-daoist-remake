"""List explicit bounded batches for the already identified45 multi-frame IDs."""
from pathlib import Path
from datetime import datetime,timezone
import json
OUT=Path(__file__).resolve().parent
source=json.loads((OUT/'multi-frame-gap-list.json').read_text(encoding='utf-8'))
rows=sorted(source['elements'],key=lambda row:row['elementId'])
assert len(rows)==45 and all(row['declaredFrameCount']>1 for row in rows)
batches=[]
for start in range(0,len(rows),6):
    selected=rows[start:start+6]
    batches.append({'batch':'batch-'+str(start//6+1).zfill(2),'elementIds':[row['elementId']for row in selected],
                    'resourcePaths':[row['sourceCandidatePath']for row in selected],
                    'expectedRawSHA256':[row['sourceDimgSHA256']for row in selected],
                    'maxResources':6,'pixelDecodeAllowed':False})
(OUT/'sequential-read-plan.json').write_text(json.dumps({'createdAtUTC':datetime.now(timezone.utc).isoformat(),
    'scope':'exact45 previously identified multi-frame definitions, not a package scan','sourceContract':'multi-frame-gap-list.json',
    'resourceCount':45,'batches':batches,'pixelDecodeAllowed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'resourceCount':45,'batchCount':len(batches),'next':batches[1]},ensure_ascii=True))
