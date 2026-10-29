"""One to six explicitly decoded inventory PNGs, source-only structure board."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
key,*tokens=sys.argv[1:]
ids=list(map(int,tokens))
assert 1<=len(ids)<=6
board=Image.new('RGBA',(1536,1024));rows=[]
for n,ident in enumerate(ids):
    path=ROOT/f'references/qqtang-item-data/icons/item-{ident}-inventory-icon.png'
    record=json.loads(Path(str(path)+'.source.json').read_text(encoding='utf-8'))
    assert record['resourceKind']=='explicit inventory icon' and record['category']=='thadorn'
    im=Image.open(path).convert('RGBA');scale=min(380/im.width,400/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    x=n%3*512+(512-im.width)//2;y=n//3*512+460-im.height
    board.alpha_composite(im,(x,y));rows.append({'itemId':ident,'source':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                               'nativeFrameSize':record['nativeFrameSize'],'resourceKind':record['resourceKind'],'rect':[x,y,x+im.width,y+im.height],
                                               'inspectionScale':scale,'completeContainerFormatVerified':record.get('completeContainerFormatVerified',True)})
target=OUT/f'references/structure-{key}.png';target.parent.mkdir(exist_ok=True)
board.save(target);Path(str(target)+'.source.json').write_text(json.dumps({'referenceOnly':True,'notRuntimeArt':True,'operation':'nearest-neighbour inspection enlargement only','items':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'items':ids,'file':str(target),'referenceOnly':True}))
