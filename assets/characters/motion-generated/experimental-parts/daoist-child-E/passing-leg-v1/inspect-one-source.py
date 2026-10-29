"""One generated atlas alpha/ivory inspection only; no slice or binding exports."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
src=BASE/'passing-leg-v1.png';raw=src.read_bytes();digest=hashlib.sha256(raw).hexdigest()
im=Image.open(src).convert('RGBA');W,H=im.size;a=np.asarray(im.getchannel('A'));m=a>=8
y,x=np.nonzero(m);cells=[]
for i,ident in enumerate(['near_R_planted','near_R_raised','far_L_planted','far_L_raised']):
    l=(i%2)*(W//2);t=(i//2)*(H//2);r=(i%2+1)*(W//2);b=(i//2+1)*(H//2)
    yy,xx=np.nonzero(m[t:b,l:r])
    cells.append({'id':ident,'inspectionCell':[l,t,r,b],
      'alpha8BBoxInCellExclusive':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
      'alpha8Count':int(len(xx)),
      'scope':'Nominal cell alpha observation only, not an asset crop, ownership approval, anatomical landmark or sourceRoot.'})
lift_proxy={'nearR':cells[0]['alpha8BBoxInCellExclusive'][3]-cells[1]['alpha8BBoxInCellExclusive'][3],
            'farL':cells[2]['alpha8BBoxInCellExclusive'][3]-cells[3]['alpha8BBoxInCellExclusive'][3]}
record={'file':src.name,'sha256':digest,'actualNativeSize':[W,H],'inspectedAtUTC':datetime.now(timezone.utc).isoformat(),
 'alphaMin':int(a.min()),'alphaMax':int(a.max()),'threshold':8,'alpha8Count':int(m.sum()),
 'alpha8BBoxExclusive':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],
 'alpha8OuterEdges':{'top':int(m[0].sum()),'right':int(m[:,-1].sum()),'bottom':int(m[-1].sum()),'left':int(m[:,0].sum())},
 'nominalCenterLines':{'xHalfMinus1':int(m[:,W//2-1].sum()),'xHalf':int(m[:,W//2].sum()),'yHalfMinus1':int(m[H//2-1].sum()),'yHalf':int(m[H//2].sum())},
 'cellObservations':cells,'nominalCellLowestVisiblePixelLiftProxy':lift_proxy,
 'proxyWarning':'Lower alpha bbox edges are a visible-height proxy before any shared hip registration, not measured sole/ankle coordinates or accepted lift. Do not treat as native timing/ground.',
 'operation':'Decode this one new atlas only, alpha observation and native full-canvas ivory composite; no crop/fit/binding/animation.',
 'hiddenRgbIsNotAlphaFailure':True,'runtimeAdopted':False}
(BASE/'passing-leg-v1.alpha-review.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
bg=Image.new('RGBA',im.size,(248,242,225,255));bg.alpha_composite(im)
iv=BASE/'passing-leg-v1-ivory.png';bg.convert('RGB').save(iv)
iv.with_suffix('.png.source.json').write_text(json.dumps({'file':iv.name,'sha256':hashlib.sha256(iv.read_bytes()).hexdigest(),'size':[W,H],
 'derivedFrom':{'file':src.name,'sha256':digest,'generationRecord':'passing-leg-v1.png.generation.json'},
 'operation':'Full native canvas alpha composite on opaque RGB248,242,225, no crop/scale/mirror/pixel repaint.',
 'newModelGeneration':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
