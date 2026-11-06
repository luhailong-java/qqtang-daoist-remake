"""Make only3 visible source representatives for4 preserved original indices."""
from pathlib import Path
from PIL import Image
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'))
assert context['sourceFrames'][2]['exactVisibleAliasOfFrameIndex']==0
indices=[0,1,3];board=Image.new('RGBA',(1536,1024));records=[]
for col,index in enumerate(indices):
    source=next(f for f in context['sourceFrames']if f['frameIndex']==index)
    im=Image.open(ROOT/source['file']).convert('RGBA');scale=360/126
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    x=col*512+(512-im.width)//2;y=850-im.height;board.alpha_composite(im,(x,y))
    records.append({'sourceFrameIndex':index,'file':source['file'],'sha256':source['sha256'],'referenceRect':[x,y,x+im.width,y+im.height],'scale':scale})
path=OUT/'source-representatives-0-1-3.png';assert not path.exists();board.save(path)
(OUT/'source-representatives-0-1-3.source.json').write_text(json.dumps({'elementId':14107,'file':path.relative_to(ROOT).as_posix(),
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'referenceOnly':True,'runtimeArt':False,'newModelGeneration':False,
    'operation':'already decoded source frames0,1,3 nearest-neighbor inspection placement only; source offsets not applied',
    'sourceFrame2Equals0':True,'originalIndicesStillPreserved':[0,1,2,3],'sourceFrames':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records))
