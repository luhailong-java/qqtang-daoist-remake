"""Lossless crop and state-group padding of the generated UI atlas."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).resolve().parents[1];source=root/'assets/ui/qdao-ui-controls-v3.png'
im=Image.open(source).convert('RGBA');out=root/'assets/ui/controls';out.mkdir(exist_ok=True)
names=[['tab-normal','tab-active','secondary-normal','secondary-hover'],['input-normal','input-focus','input-error','input-disabled'],['checkbox-off','checkbox-on','radio-off','radio-on']]
xs=[0,315,628,942,1254];ys=[(100,300),(355,555),(615,840)];items=[]
for row in range(3):
    for col in range(4):items.append((names[row][col],[xs[col],ys[row][0],xs[col+1],ys[row][1]],'row'+str(row)))
items += [('scroll-track',[110,835,225,1215],'scroll-track'),('scroll-thumb',[397,900,519,1160],'scroll-thumb'),('slider-track',[590,960,1018,1090],'slider-track'),('slider-knob',[1024,928,1230,1130],'slider-knob')]
prepared=[]
for name,rect,group in items:
    tile=im.crop(rect);box=tile.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
    if not box:raise ValueError(name)
    actual=[rect[0]+box[0],rect[1]+box[1],rect[0]+box[2],rect[1]+box[3]]
    prepared.append((name,im.crop(actual),actual,group))
group_sizes={}
for name,tile,rect,group in prepared:
    old=group_sizes.get(group,(0,0));group_sizes[group]=(max(old[0],tile.width),max(old[1],tile.height))
manifest={'schemaVersion':1,'source':source.relative_to(root).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'items':[]}
review=Image.new('RGB',(1000,780),(242,235,215));draw=ImageDraw.Draw(review)
for index,(name,tile,rect,group) in enumerate(prepared):
    size=group_sizes[group];canvas=Image.new('RGBA',size);placement=((size[0]-tile.width)//2,(size[1]-tile.height)//2);canvas.alpha_composite(tile,placement)
    target=out/f'{name}.png';canvas.save(target)
    record={'name':name,'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'width':canvas.width,'height':canvas.height,'source':manifest['source'],'sourceSha256':manifest['sourceSha256'],
        'generationRecord':manifest['source']+'.generation.json','sourceRectLTRB':rect,'paddingPlacement':list(placement),
        'operation':'lossless-crop-and-state-group-padding','resampled':False,'newModelGeneration':False,
        'alphaExtrema':list(canvas.getchannel('A').getextrema()),'status':'candidate-awaiting-browser-state-validation'}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');manifest['items'].append(record)
    thumb=canvas.copy();thumb.thumbnail((224,150),Image.Resampling.LANCZOS);x=(index%4)*250;y=(index//4)*195;review.paste(thumb,(x+(250-thumb.width)//2,y+15+(150-thumb.height)//2),thumb);draw.text((x+10,y+171),name,fill='#1b4c3e')
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');review.save(root/'.artifacts/ui-controls-review.png')
print(json.dumps({'controls':len(manifest['items']),'stateGroups':group_sizes,'resampled':False}))
