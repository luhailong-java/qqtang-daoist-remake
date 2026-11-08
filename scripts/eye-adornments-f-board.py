from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
ids=[3017,3020,3767,3768,3874,3875]
board=Image.new('RGBA',(1536,1024));records=[]
for index,ident in enumerate(ids):
 suffix='-stand-frame-000' if ident==3767 else '-inventory-icon'
 path=ROOT/f'references/qqtang-item-data/icons/item-{ident}{suffix}.png'
 source=json.loads(path.with_suffix('.png.source.json').read_text(encoding='utf-8'))
 im=Image.open(path).convert('RGBA');scale=min(380/im.width,400/im.height)
 size=(round(im.width*scale),round(im.height*scale));x=index%3*512+(512-size[0])//2;y=index//3*512+460-size[1]
 board.alpha_composite(im.resize(size,Image.Resampling.NEAREST),(x,y))
 records.append({'itemId':ident,'source':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nativeFrameSize':list(im.size),'inspectionScale':scale,'rect':[x,y,x+size[0],y+size[1]],'sourceMember':source['sourceMember'],'resourceKind':source['resourceKind'],'inventoryMappingVerified':False if ident==3767 else None})
 im.close()
out=ROOT/'assets/items/eye-adornments/references/eye-adornments-f-structure.png';out.parent.mkdir(parents=True,exist_ok=True);board.save(out)
out.with_suffix('.png.source.json').write_text(json.dumps({'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'referenceOnly':True,'notRuntimeArt':True,'operation':'Nearest inspection enlargement of five actual inventory icons plus item3767 explicitly declared stand frame0. No inventory alias created.','items':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'items':ids,'standReferenceException':3767}))
