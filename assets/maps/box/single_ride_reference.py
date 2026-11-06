from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[3]
entry=next(e for e in json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))['elements']if e['elementId']==14107)
source=root/entry['referencePng']['file'];im=Image.open(source).convert('RGBA');scale=768/im.height
im=im.resize((round(im.width*scale),768),Image.Resampling.NEAREST)
board=Image.new('RGBA',(1024,1024));pos=((1024-im.width)//2,128);board.alpha_composite(im,pos)
out=Path(__file__).parent/'references/structure-f.png';board.save(out)
out.with_suffix('.png.source.json').write_text(json.dumps({'referenceOnly':True,'notRuntimeArt':True,'operation':'source frame uniformly nearest-neighbour enlarged on inspection canvas','elementId':14107,'source':entry['referencePng'],'inspectionScale':scale,'rect':[pos[0],pos[1],pos[0]+im.width,pos[1]+im.height],'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
