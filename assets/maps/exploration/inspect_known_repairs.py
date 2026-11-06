"""Inspect only two current repairs (four small PNGs), never a full scan."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
art=json.loads((OUT/'art.json').read_text(encoding='utf-8'));byid={p['elementId']:p for p in art['pieces']};rows=[]
for ident in [16111,16114]:
 p=byid[ident];row={'elementId':ident,'file':p['file']}
 for key,path in [('source',p['sourceReference']['file']),('paint',p['file'])]:
  im=Image.open(ROOT/path).convert('RGBA');b=im.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox();w,h=b[2]-b[0],b[3]-b[1]
  row[key]={'frame':list(im.size),'alphaAtLeast8BBox':list(b),'visibleWidthHeightRatio':w/h}
 row['visibleRatioRelativeError']=row['paint']['visibleWidthHeightRatio']/row['source']['visibleWidthHeightRatio']-1
 row['accepted']=False;row['notes']='local ratio evidence only, opening geometry/identity/anchors and actual gameplay still pending'
 rows.append(row)
data={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'decodedFiles':4,'scope':'two known repair targets only; full-family QA remains paused','rows':rows,'accepted':False}
record_parent=(ROOT/byid[16111]['derivedFrom']['generationRecord']).parent
(record_parent/'local-ratio-check.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print(json.dumps(data))
