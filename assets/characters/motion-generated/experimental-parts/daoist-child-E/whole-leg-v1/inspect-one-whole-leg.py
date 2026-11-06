"""One necessary source inspection only; no slicing, fitting, or assembly."""
from pathlib import Path
from PIL import Image
import numpy as np, hashlib, json
from datetime import datetime, timezone

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[6]
src=OUT/'whole-leg-v1.png'
raw=src.read_bytes()
im=Image.open(src).convert('RGBA')
a=np.asarray(im.getchannel('A'))
mask=a>=8
ys,xs=np.nonzero(mask)
W,H=im.size
alpha={'alphaMin':int(a.min()),'alphaMax':int(a.max()),'threshold':8,
       'visiblePixelCount':int(mask.sum()),'alpha8BboxExclusive':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
       'alpha8OuterEdges':{'top':int(mask[0].sum()),'right':int(mask[:,-1].sum()),'bottom':int(mask[-1].sum()),'left':int(mask[:,0].sum())},
       'centerLineVisiblePixels':{'xHalfMinus1':int(mask[:,W//2-1].sum()),'xHalf':int(mask[:,W//2].sum()),'yHalfMinus1':int(mask[H//2-1].sum()),'yHalf':int(mask[H//2].sum())},
       'notASlicingApproval':True,'hiddenRgbNotAnAlphaFailure':True}
bg=Image.new('RGBA',im.size,(248,242,225,255))
bg.alpha_composite(im)
preview=OUT/'whole-leg-v1-ivory.png'
bg.convert('RGB').save(preview)
record={'schemaVersion':1,'file':src.name,'sha256':hashlib.sha256(raw).hexdigest(),
        'actualNativeSize':[W,H],'inspectedAt':datetime.now(timezone.utc).isoformat(),
        'operation':'one necessary source alpha inspection and full-canvas ivory composite only',
        'alpha':alpha,'noSlicing':True,'noAssembly':True,'runtimeAdopted':False}
(OUT/'whole-leg-v1.alpha-review.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(OUT/'whole-leg-v1-ivory.png.source.json').write_text(json.dumps({
    'file':preview.name,'sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),
    'derivedFrom':{'file':src.name,'sha256':record['sha256'],'generationRecord':'whole-leg-v1.png.generation.json'},
    'operation':'full native canvas alpha composite on opaque RGB248,242,225; no scaling or geometry edits',
    'newModelGeneration':False,'size':[W,H]},indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
