"""Combine exactly six decoded source frames, uniform nearest display only."""
from pathlib import Path
from PIL import Image
import json,hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
frames=[]
for ident in [42,54]:
    frames.extend(json.loads((OUT/f'references/world/{ident}/source-contract.json').read_text(encoding='utf-8'))['frames'])
assert len(frames)==6
board=Image.new('RGBA',(1536,1024));rows=[]
for n,f in enumerate(frames):
    im=Image.open(ROOT/f['file']).convert('RGBA');scale=min(380/im.width,400/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    x=n%3*512+(512-im.width)//2;y=n//3*512+460-im.height
    board.alpha_composite(im,(x,y));rows.append({**f,'inspectionScale':scale,'boardRectLTRB':[x,y,x+im.width,y+im.height]})
target=OUT/'references/world-action-42-54.png';board.save(target)
Path(str(target)+'.source.json').write_text(json.dumps({'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'referenceOnly':True,'notRuntimeArt':True,'operation':'uniform nearest source display; no new paint','frames':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(target),'frames':len(frames),'referenceOnly':True}))
