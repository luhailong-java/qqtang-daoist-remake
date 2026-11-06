"""Arrange enlarged source reference frames as inspection input, never game art."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
arguments=sys.argv[2:];extra=[value[8:]for value in arguments if value.startswith('--extra=')]
if len(extra)>1:raise ValueError('Use at most one supplemental inventory')
ids=[int(value)for value in arguments if not value.startswith('--extra=')];destination=root/sys.argv[1]
if not 1<=len(ids)<=6:raise ValueError('Use one to six source reference frames')
inventory=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))
elements={item['elementId']:item for item in inventory['elements']}
if extra:
    for item in json.loads((root/extra[0]).read_text(encoding='utf-8'))['elements']:
        if item['elementId']in elements:raise ValueError('Supplement cannot replace a baseline definition')
        elements[item['elementId']]=item
board=Image.new('RGBA',(1536,1024));items=[]
for index,ident in enumerate(ids):
    entry=elements[ident];source=root/entry['referencePng']['file'];im=Image.open(source).convert('RGBA')
    scale=min(380/im.width,410/im.height)
    resized=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    cell_x=(index%3)*512;cell_y=(index//3)*512
    x=cell_x+(512-resized.width)//2;y=cell_y+460-resized.height
    board.alpha_composite(resized,(x,y))
    items.append({'elementId':ident,'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'referenceFrameSize':list(im.size),'inspectionScale':scale,'rect':[x,y,x+resized.width,y+resized.height]})
destination.parent.mkdir(parents=True,exist_ok=True);board.save(destination)
destination.with_suffix('.png.source.json').write_text(json.dumps({'file':destination.relative_to(root).as_posix(),
    'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'referenceOnly':True,'notRuntimeArt':True,
    'operation':'nearest-neighbour enlarged source-frame inspection board','items':items},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(destination),'referenceOnly':True,'items':items}))
