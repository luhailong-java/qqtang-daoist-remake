from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
by={e['elementId']:e for e in json.loads((ROOT/'assets/maps/production-index.json').read_text(encoding='utf-8'))['elements']};ids=[14001,14101,14102,14127]
board=Image.new('RGBA',(1024,1024));items=[]
for n,ident in enumerate(ids):
    e=by[ident];source=ROOT/e['referencePng']['file'];im=Image.open(source).convert('RGBA').resize((480,480),Image.Resampling.NEAREST);pos=(n%2*512+16,n//2*512+16);board.alpha_composite(im,pos);items.append({'elementId':ident,'source':e['referencePng'],'rect':[pos[0],pos[1],pos[0]+480,pos[1]+480]})
target=OUT/'references/structure-e.png';board.save(target);target.with_suffix('.png.source.json').write_text(json.dumps({'referenceOnly':True,'notRuntimeArt':True,'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'operation':'source-only nearest inspection contact','items':items},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(target),'items':items}))
