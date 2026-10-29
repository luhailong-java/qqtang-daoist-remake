"""At most6 real source-reference crops, uniform nearest-neighbour enlargement only."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
key=sys.argv[1];indices=[int(a)for a in sys.argv[2:]]
assert 1<=len(indices)<=6 and len(set(indices))==len(indices)
board=Image.new('RGBA',(1536,1024),(64,72,80,255));draw=ImageDraw.Draw(board)
records=[]
for pos,index in enumerate(indices):
    path=OUT/f'references/world/138/frame-{index:03d}.png'
    source=json.loads(Path(str(path)+'.source.json').read_text(encoding='utf-8'))
    image=Image.open(path).convert('RGBA');size=(image.width*8,image.height*8)
    x=(pos%3)*512+(512-size[0])//2;y=(pos//3)*512+(512-size[1])//2
    board.alpha_composite(image.resize(size,Image.Resampling.NEAREST),(x,y))
    draw.text(((pos%3)*512+20,(pos//3)*512+24),f'SOURCE PHASE {index} | {image.width}x{image.height} | offset {source["frameOffsetRaw"]}',fill='white')
    records.append({'sourceFrameIndex':index,'sourceFile':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'uniformNearestScale':8,'source':source})
target=OUT/f'references/world/138/source-phases-{key}.png';board.save(target)
Path(str(target)+'.source.json').write_text(json.dumps({'operation':'reference board of source PNGs, no new generated art','frames':records,'runtimeUsable':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(target.relative_to(ROOT).as_posix())
