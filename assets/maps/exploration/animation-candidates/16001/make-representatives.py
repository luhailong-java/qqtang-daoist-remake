"""Create an explicit resource's <=6 distinct source-frame geometry board only."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[5]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--element',type=int,required=True);p.add_argument('--family',required=True);p.add_argument('--layout',choices=['horizontal','vertical'],default='horizontal');p.add_argument('--canvas-width',type=int,default=1536);p.add_argument('--canvas-height',type=int,default=1024);p.add_argument('--output-name',default='source-distinct-representatives');a=p.parse_args()
OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}'
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'))
representatives=[f for f in context['sourceFrames']if not f['structuralEmpty']and not f['fullyTransparentPixels']and f['exactVisibleAliasOfFrameIndex']is None]
assert 1<=len(representatives)<=6
assert 256<=a.canvas_width<=2048 and 256<=a.canvas_height<=2048 and '/'not in a.output_name and '\\'not in a.output_name
board=Image.new('RGBA',(a.canvas_width,a.canvas_height));cell_width=a.canvas_width/len(representatives)
scale=min(cell_width*.72/max(f['sourceFrameSize'][0]for f in representatives),a.canvas_height*.72/max(f['sourceFrameSize'][1]for f in representatives))if a.layout=='horizontal'else min(a.canvas_width*.72/max(f['sourceFrameSize'][0]for f in representatives),(a.canvas_height/len(representatives))*.72/max(f['sourceFrameSize'][1]for f in representatives))
records=[]
for col,source in enumerate(representatives):
    im=Image.open(ROOT/source['file']).convert('RGBA');im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    if a.layout=='horizontal':x=round(col*cell_width+(cell_width-im.width)/2);y=round(a.canvas_height*.83)-im.height
    else:x=(a.canvas_width-im.width)//2;y=round(col*(a.canvas_height/len(representatives))+((a.canvas_height/len(representatives))-im.height)/2)
    board.alpha_composite(im,(x,y))
    records.append({'sourceFrameIndex':source['frameIndex'],'file':source['file'],'sha256':source['sha256'],'referenceRect':[x,y,x+im.width,y+im.height],'scale':scale})
path=OUT/(a.output_name+'.png');assert not path.exists();board.save(path)
(OUT/(a.output_name+'.source.json')).write_text(json.dumps({'elementId':a.element,'file':path.relative_to(ROOT).as_posix(),
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'referenceOnly':True,'runtimeArt':False,'newModelGeneration':False,
    'operation':'explicit already-decoded source representatives nearest-neighbor inspection placement; offsets not applied',
    'layout':a.layout,'canvas':[a.canvas_width,a.canvas_height],'originalIndicesStillPreserved':[f['frameIndex']for f in context['sourceFrames']],'sourceFrames':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records))
