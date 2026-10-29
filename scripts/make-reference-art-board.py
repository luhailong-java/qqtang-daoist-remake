"""Nearest-neighbour inspection board, not game art or model generation."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
root=Path(__file__).resolve().parents[1];destination=root/sys.argv[1];sources=sys.argv[2:]
columns=4 if '--columns=4'in sources else 2 if '--columns=2'in sources else 1 if '--columns=1'in sources else 3
rows=3 if '--rows=3'in sources else 2
sources=[s for s in sources if s not in ['--columns=4','--columns=2','--columns=1','--rows=3']];cell_width=1536//columns
if not 1<=len(sources)<=columns*rows:raise ValueError('Reference count exceeds selected bounded grid')
board=Image.new('RGBA',(1536,512*rows));records=[]
for index,relative in enumerate(sources):
    path=(root/relative).resolve()
    if not path.is_relative_to(root/'references'):raise ValueError('Reference board sources must be in references/')
    im=Image.open(path).convert('RGBA');scale=min((cell_width-100)/im.width,400/im.height);size=(round(im.width*scale),round(im.height*scale))
    x=index%columns*cell_width+(cell_width-size[0])//2;y=index//columns*512+(512-size[1])//2
    board.alpha_composite(im.resize(size,Image.Resampling.NEAREST),(x,y))
    records.append({'source':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nativeFrameSize':list(im.size),'inspectionScale':scale,'rect':[x,y,x+size[0],y+size[1]]})
destination.parent.mkdir(parents=True,exist_ok=True);board.save(destination)
destination.with_suffix('.png.source.json').write_text(json.dumps({'file':destination.relative_to(root).as_posix(),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'operation':'nearest-neighbour inspection enlargement and board placement','referenceOnly':True,'notRuntimeArt':True,'sources':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(destination),'references':len(sources),'referenceOnly':True}))
