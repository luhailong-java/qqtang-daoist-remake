"""Enlarge up to six narrow source nameplates for inspection only."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
root=Path(__file__).resolve().parents[1];destination=root/sys.argv[1];ids=list(map(int,sys.argv[2:]))
if not 1<=len(ids)<=6:raise ValueError('Select one to six explicit narrow source frames')
board=Image.new('RGBA',(1536,1024));rows=[]
for index,ident in enumerate(ids):
    file=root/f'references/qqtang-item-data/icons/item-{ident}.png';im=Image.open(file).convert('RGBA')
    scale=min(1400/im.width,110/im.height);size=(round(im.width*scale),round(im.height*scale))
    x=(1536-size[0])//2;y=round(index*1024/6+(1024/6-size[1])/2)
    board.alpha_composite(im.resize(size,Image.Resampling.NEAREST),(x,y))
    rows.append({'itemId':ident,'file':file.relative_to(root).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
        'nativeSize':list(im.size),'inspectionScale':scale,'rect':[x,y,x+size[0],y+size[1]]})
destination.parent.mkdir(parents=True,exist_ok=True);board.save(destination)
destination.with_suffix('.png.source.json').write_text(json.dumps({'file':destination.relative_to(root).as_posix(),
    'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'referenceOnly':True,'notRuntimeArt':True,
    'operation':'nearest-neighbour narrow-frame inspection enlargement; no new art','rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(destination),'sourceFrames':len(rows),'referenceOnly':True}))
