"""Read alpha span of exactly two already-rendered627 PNGs. No render/resize."""
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
STATIC=BASE.parent/'whole-arm-v1'/'bind-static-v2'
proposal=json.loads((STATIC/'proposal.json').read_text(encoding='utf-8'))
records=[]
for pose in proposal['twoContacts']:
    p=ROOT/pose['output'];raw=p.read_bytes();actual=hashlib.sha256(raw).hexdigest()
    if actual!=pose['sha256']:raise ValueError('Current static source differs from proposal')
    im=Image.open(p)
    if im.mode!='RGBA' or im.size!=(627,627):raise ValueError('Unexpected current static source')
    a=im.getchannel('A');mask=a.point(lambda v:255 if v>=8 else 0)
    bbox=list(mask.getbbox());full=list(a.getbbox())
    records.append({'contact':pose['contact'],'file':p.relative_to(ROOT).as_posix(),'sha256':actual,
        'canvasSize':list(im.size),'alphaThreshold':8,'alpha8BBoxExclusive':bbox,
        'alpha8Span':[bbox[2]-bbox[0],bbox[3]-bbox[1]],'nonzeroAlphaBBoxExclusive':full,
        'operation':'Decode only this current627 PNG alpha, compute span; no generated image, export, registration, resize, full-art-family scan or runtime.'})
    im.close()
union=[min(r['alpha8BBoxExclusive'][0]for r in records),min(r['alpha8BBoxExclusive'][1]for r in records),
       max(r['alpha8BBoxExclusive'][2]for r in records),max(r['alpha8BBoxExclusive'][3]for r in records)]
span=[union[2]-union[0],union[3]-union[1]]
fallback=90*40/64
scale=fallback/span[1]
out={'schemaVersion':1,'projectDisplayName':'灵葫大作战','measuredAtUTC':datetime.now(timezone.utc).isoformat(),
 'existingPngDecodesThisScript':2,'existingPngViewedElsewhereThisTask':4,'totalUniqueExistingPngBudgetThisTask':6,
 'records':records,'fixedReferenceUnionAlpha8BBoxExclusive':union,'fixedReferenceSpan':span,
 'targetFallbackLogicalVisibleHeight':fallback,
 'recommendedOneSharedDesignPixelToLogicalPixelScale':scale,
 'recommendedFull627DesignCanvasLogicalSize':627*scale,
 'recommendedFull627CanvasSizeInExisting64DrawSpace':627*scale/(40/64),
 'logicalReferenceUnionWidth':span[0]*scale,'unchangedSourceMapCellLogicalPx':40,
 'heightIn40pxCells':fallback/40,'scope':'One fixed reference union over currentA/B only; use this same chosen scale for all future poses, never recompute it from each pose bbox. New motion envelopes may exceed this reference; record separately rather than auto-shrinking poses.',
 'nativeScaleOneToOneClaim':False,'worldRoot':None,'nativeTimingMs':None,
 'newPngOutputs':0,'newImagegenCalls':0,'rendererExecutions':0,'runtimeAdopted':False}
(BASE/'current-static-alpha-scale.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
