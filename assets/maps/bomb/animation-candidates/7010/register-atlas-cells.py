"""Register the four whole v3 poses across actual transparent atlas gaps."""
from pathlib import Path
from PIL import Image
import json
OUT=Path(__file__).resolve().parent
path=OUT/'native-check-v3.json'
check=json.loads(path.read_text(encoding='utf-8'))
im=Image.open(OUT/'sequence-v3.png').convert('RGBA')
regions=[[0,0,520,765],[520,0,987,765],[987,0,1476,765],[1476,0,2056,765]]
assert im.size==(2056,765)
if 'nominalEqualCellFrames' not in check:
    check['nominalEqualCellFrames']=check['frames']
check['actualExtractionRegionEvidence']='Actual alpha>8 continuous x groups are [97,482), [557,953), [1022,1431), [1522,1924). Boundaries placed only in transparent gaps; unequal generated spacing, no pixel or component moved.'
check['frames']=[]
for index,rect in enumerate(regions):
    alpha=im.getchannel('A').crop(rect).point(lambda v:255 if v>8 else 0)
    b=list(alpha.getbbox());w=rect[2]-rect[0]
    check['frames'].append({'sourceFrameIndex':index,'cellRect':rect,'localAlpha8BBox':b,
        'sourceFrameSize':[33,49],'sourceFrameOffset':[6,0],
        'visibleAspectRatioRelativeError':abs((b[2]-b[0])/(b[3]-b[1])/(33/49)-1),
        'touchesNominalCellAlpha8':b[0]==0 or b[1]==0 or b[2]==w or b[3]==im.height,
        'regionType':'manual whole-pose extraction interval in native atlas, not logical registration'})
check['nativeAtlasUnmodified']=True
path.write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(check['frames']))
