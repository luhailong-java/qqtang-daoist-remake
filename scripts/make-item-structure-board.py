"""Enlarge item references for model structure input, never runtime artwork."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
root=Path(__file__).resolve().parents[1];destination=root/sys.argv[1]
inventory='--inventory-icon' in sys.argv[2:]
ids=[int(value) for value in sys.argv[2:] if value!='--inventory-icon']
if not 1<=len(ids)<=6:raise ValueError('Select one to six items')
board=Image.new('RGBA',(1536,1024));records=[]
for index,ident in enumerate(ids):
    path=root/'references/qqtang-item-data/icons'/f'item-{ident}{"-inventory-icon" if inventory else ""}.png';im=Image.open(path).convert('RGBA')
    box=im.getchannel('A').getbbox()
    if not box:raise ValueError('Empty icon')
    # Inspection enlargement keeps full native frame and ratio, including padding.
    scale=min(380/im.width,400/im.height);size=(round(im.width*scale),round(im.height*scale))
    resized=im.resize(size,Image.Resampling.NEAREST);x=index%3*512+(512-size[0])//2;y=index//3*512+460-size[1]
    board.alpha_composite(resized,(x,y));records.append({'itemId':ident,'source':path.relative_to(root).as_posix(),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nativeFrameSize':list(im.size),'inspectionScale':scale,'rect':[x,y,x+size[0],y+size[1]]})
destination.parent.mkdir(parents=True,exist_ok=True);board.save(destination)
destination.with_suffix('.png.source.json').write_text(json.dumps({'file':destination.relative_to(root).as_posix(),
    'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'referenceOnly':True,'notRuntimeArt':True,'operation':'nearest-inspection-enlargement','items':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(destination),'items':ids,'referenceOnly':True}))
