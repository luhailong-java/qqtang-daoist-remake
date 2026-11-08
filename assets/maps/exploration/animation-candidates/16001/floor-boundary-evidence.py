"""Only3 actual source reps and their3 current x1 exports; no family scan."""
from pathlib import Path
from PIL import Image
import json,argparse
ROOT=Path(__file__).resolve().parents[5]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--element',type=int,default=16001);p.add_argument('--family',default='exploration');a=p.parse_args()
OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}'
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'));sequence=json.loads((OUT/'sequence.json').read_text(encoding='utf-8'))
def evidence(path):
    im=Image.open(path).convert('RGBA');a=im.getchannel('A');b=a.point(lambda v:255 if v>8 else 0).getbbox()
    n=sum(a.getpixel((x,0))>8 or a.getpixel((x,im.height-1))>8 for x in range(im.width))+sum(a.getpixel((0,y))>8 or a.getpixel((im.width-1,y))>8 for y in range(1,im.height-1))
    return {'size':list(im.size),'alphaExtrema':list(a.getextrema()),'alpha8BBox':list(b),'alpha8EdgeCount':n}
rows=[]
indices=[f['frameIndex']for f in context['sourceFrames']if not f['structuralEmpty']and not f['fullyTransparentPixels']and f['exactVisibleAliasOfFrameIndex']is None]
assert 1<=len(indices)<=6
for index in indices:
    source=next(f for f in context['sourceFrames']if f['frameIndex']==index)
    own=next(f for f in sequence['frames']if f['sourceFrameIndex']==index)
    rows.append({'frameIndex':index,'source':evidence(ROOT/source['file']),'candidateX1':evidence(ROOT/own['exports']['1']['file'])})
(OUT/'floor-boundary-evidence.json').write_text(json.dumps({'elementId':a.element,'selectedRepresentatives':indices,
    'sourceKindObservation':'flat rounded lava appearance with full-frame alpha8 bounds; no gameplay meaning inferred',
    'exportGuardNativePixels':0,'why':'Do not add the standing-object4-native-pixel clear guard to an edge-reaching floor image; actual surface alpha remains unnormalized.',
    'sourceAndCurrentCandidateOnly':True,'rows':rows,'accepted':False,'geometryAccepted':False,
    'limitation':'Boundary pixel counts are factual evidence, not acceptance. Per-axis margins/contour differences, if present, frame stability and native source edge registration remain pending.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))
