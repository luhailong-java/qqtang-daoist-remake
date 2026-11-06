"""One current atlas only: alpha/blank cuts and ivory preview, never item slicing."""
from pathlib import Path
from PIL import Image
import numpy as np,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];batch=sys.argv[1]
if batch not in 'abcdefghijkl' or len(batch)!=1:raise ValueError('Batch a-l only')
base=ROOT/'assets/items/eye-adornments';src=base/f'eye-adornments-{batch}-v1.png'
im=Image.open(src).convert('RGBA');a=np.asarray(im.getchannel('A'));m=a>=8;H,W=a.shape
def runs(values):
 out=[];start=None
 for i,v in enumerate(values):
  if v and start is None:start=i
  if not v and start is not None:out.append([start,i]);start=None
 if start is not None:out.append([start,len(values)])
 return out
def nearby_blank_columns(t,b):
 zero=(m[t:b].sum(axis=0)==0);return [r for r in runs(zero)if r[1]>W*.22 and r[0]<W*.78]
y,x=np.nonzero(m)
record={'file':src.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'nativeSize':[W,H],
 'alphaExtrema':[int(a.min()),int(a.max())],'alpha8Count':int(m.sum()),'alpha8BBox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],
 'outerAlpha8':{'top':int(m[0].sum()),'right':int(m[:,-1].sum()),'bottom':int(m[-1].sum()),'left':int(m[:,0].sum())},
 'blankHorizontalRuns':[r for r in runs(m.sum(axis=1)==0)if r[1]>H*.35 and r[0]<H*.65],
 'blankTopColumns':nearby_blank_columns(0,H//2),'blankBottomColumns':nearby_blank_columns(H//2,H),
 'scope':'Current atlas only; candidate blank intervals need actual visual ownership review, not automatic equal cuts.',
 'newModelGeneration':False}
(base/'qa').mkdir(exist_ok=True);out=base/'qa'/f'eye-adornments-{batch}-native-ivory.png'
bg=Image.new('RGBA',im.size,(248,242,225,255));bg.alpha_composite(im);bg.convert('RGB').save(out)
out.with_suffix('.png.source.json').write_text(json.dumps({'file':out.relative_to(ROOT).as_posix(),
 'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'derivedFrom':record['file'],'sourceSha256':record['sha256'],
 'operation':'Native full-canvas ivory composite, no resize/crop/repaint/new imagegen'},indent=2)+'\n',encoding='utf-8')
(ROOT/f'docs/eye-adornments-{batch}-alpha.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
