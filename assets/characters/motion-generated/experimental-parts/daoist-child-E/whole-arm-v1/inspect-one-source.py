"""One necessary alpha and full-canvas ivory inspection, never slicing/binding."""
from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
src=OUT/'whole-arm-v1.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(src).convert('RGBA');a=np.asarray(im.getchannel('A'));m=a>=8
ys,xs=np.nonzero(m);W,H=im.size
record={'file':src.name,'sha256':sha(src),'actualNativeSize':[W,H],'inspectedAtUTC':datetime.now(timezone.utc).isoformat(),
 'operation':'Single source alpha inspection only; no component slicing, fit, registration, binding or animation.',
 'alphaMin':int(a.min()),'alphaMax':int(a.max()),'threshold':8,'visiblePixelCount':int(m.sum()),
 'alpha8BboxExclusive':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
 'alpha8OuterEdges':{'top':int(m[0].sum()),'right':int(m[:,-1].sum()),'bottom':int(m[-1].sum()),'left':int(m[:,0].sum())},
 'centerColumnVisiblePixels':{'xHalfMinus1':int(m[:,W//2-1].sum()),'xHalf':int(m[:,W//2].sum())},
 'hiddenRgbNotAnAlphaFailure':True,'equalSlicingApproved':False,'runtimeAdopted':False}
bg=Image.new('RGBA',im.size,(248,242,225,255));bg.alpha_composite(im)
preview=OUT/'whole-arm-v1-ivory.png';bg.convert('RGB').save(preview)
(OUT/'whole-arm-v1.alpha-review.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(OUT/'whole-arm-v1-ivory.png.source.json').write_text(json.dumps({'file':preview.name,'sha256':sha(preview),'size':[W,H],
 'derivedFrom':{'file':src.name,'sha256':sha(src),'generationRecord':'whole-arm-v1.png.generation.json'},
 'operation':'Native full-canvas alpha composite on opaque RGB248,242,225; no resizing, crop, source repaint or geometry change.',
 'newModelGeneration':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
