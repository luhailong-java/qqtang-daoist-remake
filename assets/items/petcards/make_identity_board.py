"""Compose only existing portrait references into a six-slot identity input board."""
from pathlib import Path
from PIL import Image
import json,sys,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];key=sys.argv[1];spec=json.loads((OUT/f'exports/batch-{key}.json').read_text(encoding='utf-8'));board=Image.new('RGBA',(1536,1024));records=[]
for n,e in enumerate(spec['items']):
    source=e.get('identityReference')
    if not source:continue
    p=ROOT/source;im=Image.open(p).convert('RGBA');scale=min(1,400/im.width,400/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);x=n%3*512+(512-im.width)//2;y=n//3*512+60;board.alpha_composite(im,(x,y));records.append({'itemId':e['itemId'],'projectIdentity':e.get('projectIdentity'),'file':source,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rect':[x,y,x+im.width,y+im.height],'uniformScale':scale})
target=OUT/f'references/identity-{key}.png';board.save(target);target.with_suffix('.png.source.json').write_text(json.dumps({'referenceOnly':True,'notRuntimeArt':True,'operation':'uniform resize and composition of existing original identity references only; no new paint','file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'items':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'identityBoard':str(target),'references':len(records)}))
