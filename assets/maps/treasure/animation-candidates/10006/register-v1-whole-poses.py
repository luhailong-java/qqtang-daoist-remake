"""Record actual complete v1 extraction gaps, not nominal equal cell divisions."""
from pathlib import Path
from PIL import Image
import json
OUT=Path(__file__).resolve().parent;path=OUT/'native-check-v1.json'
check=json.loads(path.read_text(encoding='utf-8'));context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'))
im=Image.open(OUT/'sequence-v1.png').convert('RGBA');assert im.size==(1983,793)
regions=[[0,0,413,793],[413,0,806,793],[806,0,1196,793],[1196,0,1584,793],[1584,0,1983,793]]
if 'nominalEqualCellFrames' not in check:check['nominalEqualCellFrames']=check['frames']
check['actualExtractionRegionEvidence']='Alpha>8 continuous x groups [25,405), [420,799), [813,1189), [1204,1578), [1591,1960); boundaries placed only in native transparent gaps. Generated spacing unequal; native pixels unchanged.'
check['frames']=[]
for source,rect in zip(context['sourceFrames'],regions):
    b=list(im.getchannel('A').crop(rect).point(lambda v:255 if v>8 else 0).getbbox());w,h=source['sourceFrameSize']
    check['frames'].append({'sourceFrameIndex':source['frameIndex'],'cellRect':rect,'localAlpha8BBox':b,
        'sourceFrameSize':[w,h],'sourceFrameOffset':source['sourceFrameOffset'],
        'visibleAspectRatioRelativeError':abs((b[2]-b[0])/(b[3]-b[1])/(w/h)-1),
        'touchesNominalCellAlpha8':b[0]==0 or b[1]==0 or b[2]==rect[2]-rect[0] or b[3]==im.height,
        'regionType':'whole-pose native extraction interval; not source render placement'})
check['nativeAtlasUnmodified']=True
path.write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(check['frames']))
