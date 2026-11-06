"""1–6 real source crops, integer uniform nearest-neighbour reference enlargement only."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ident=int(sys.argv[1]);key=sys.argv[2];indices=[int(a)for a in sys.argv[3:]]
assert 1<=len(indices)<=6 and len(set(indices))==len(indices)
board=Image.new('RGBA',(1536,1024),(64,72,80,255));draw=ImageDraw.Draw(board);records=[]
for pos,index in enumerate(indices):
    path=OUT/f'references/world/{ident}/frame-{index:03d}.png'
    source=json.loads(Path(str(path)+'.source.json').read_text(encoding='utf-8'))
    image=Image.open(path).convert('RGBA');scale=max(1,min(8,430//image.width,360//image.height));size=(image.width*scale,image.height*scale)
    x=pos%3*512+(512-size[0])//2;y=pos//3*512+(512-size[1])//2
    board.alpha_composite(image.resize(size,Image.Resampling.NEAREST),(x,y))
    draw.text((pos%3*512+20,pos//3*512+24),f'SOURCE PHASE {index} | {image.width}x{image.height} | offset {source["frameOffsetRaw"]}',fill='white')
    records.append({'sourceFrameIndex':index,'sourceFile':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'uniformNearestScale':scale,'source':source})
target=OUT/f'references/world/{ident}/source-phases-{key}.png';board.save(target)
Path(str(target)+'.source.json').write_text(json.dumps({'operation':'source-reference board only, no new generated art','frames':records,'runtimeUsable':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(target.relative_to(ROOT).as_posix())
