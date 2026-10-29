"""Source-only long-piece image arrangement, no generated pixels or map editing."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
by={e['elementId']:e for e in json.loads((ROOT/'assets/maps/production-index.json').read_text(encoding='utf-8'))['elements']}
kind=sys.argv[1];ids=[13020,13021]if kind=='k'else[13054,13055,13079]
canvas=Image.new('RGBA',(1536,1024));items=[]
for n,ident in enumerate(ids):
    e=by[ident];source=ROOT/e['referencePng']['file'];im=Image.open(source).convert('RGBA')
    scale=900/im.height if kind=='k' else 1400/im.width
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    if kind=='k':position=(n*768+(768-im.width)//2,62)
    else:position=((1536-im.width)//2,120+n*320)
    canvas.alpha_composite(im,position);items.append({'elementId':ident,'source':e['referencePng'],'position':position,'size':im.size,'inspectionScale':scale})
target=OUT/'references'/f'structure-{kind}.png';canvas.save(target)
target.with_suffix('.png.source.json').write_text(json.dumps({'referenceOnly':True,'notRuntimeArt':True,'operation':'nearest-neighbour source frame inspection layout','file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'items':items},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(target),'items':items}))
