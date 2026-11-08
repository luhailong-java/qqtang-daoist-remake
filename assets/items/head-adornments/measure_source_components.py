"""Measure at most six explicit tiny source frames; no pixel mutations or art drawing."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
from collections import deque
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
ident=int(sys.argv[1]);key=sys.argv[2];indices=[int(x)for x in sys.argv[3:]]
assert 1<=len(indices)<=6 and len(indices)==len(set(indices))
rows=[]
for index in indices:
 p=OUT/f'references/world/{ident}/frame-{index:03}.png';im=Image.open(p).convert('RGBA');w,h=im.size;a=im.getchannel('A');mask=a.point(lambda v:255 if v>=16 else 0);px=mask.load();seen=set();parts=[]
 for y in range(h):
  for x in range(w):
   if not px[x,y] or (x,y)in seen:continue
   q=deque([(x,y)]);seen.add((x,y));points=[]
   while q:
    xx,yy=q.popleft();points.append((xx,yy))
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
     nx,ny=xx+dx,yy+dy
     if 0<=nx<w and 0<=ny<h and px[nx,ny] and (nx,ny)not in seen:seen.add((nx,ny));q.append((nx,ny))
   xs,ys=zip(*points);parts.append({'areaAt16':len(points),'bboxLTRB':[min(xs),min(ys),max(xs)+1,max(ys)+1],'centroidNormalized':[round(sum(xs)/len(xs)/w,4),round(sum(ys)/len(ys)/h,4)]})
 rows.append({'sourceFrameIndex':index,'sourcePNG':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[w,h],'componentCountAt16':len(parts),'components':sorted(parts,key=lambda z:z['centroidNormalized'][0])})
r={'scope':'bounded source measurement only, no new art/no runtime/QA acceptance','threshold':16,'connectivity':8,'itemId':ident,'frames':rows};p=OUT/f'references/world/{ident}/source-components-{key}.json';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'index':r['sourceFrameIndex'],'count':r['componentCountAt16'],'centres':[c['centroidNormalized']for c in r['components']]}for r in rows]))
