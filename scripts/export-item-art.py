"""Crop and uniformly scale original painted inventory icons; no new generation."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
root=Path(__file__).resolve().parents[1];spec=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
source=root/spec['source'];sheet=Image.open(source).convert('RGBA');folder=(root/spec.get('assetDirectory','assets/items')).resolve()
if not folder.is_relative_to(root/'assets/items'):raise ValueError('Icon outputs must remain under assets/items/')
folder.mkdir(parents=True,exist_ok=True)
catalog=json.loads((root/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
items={item['item_id']:item for item in catalog['items']}
manifest_path=folder/'art.json';art=json.loads(manifest_path.read_text(encoding='utf-8'))if manifest_path.exists()else{'schemaVersion':1,'status':'original-painted-candidates','items':[]}
for item in spec['items']:
    ident=item['itemId'];entry=items[ident];rect=item['rect'];crop=sheet.crop(rect)
    box=crop.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
    if not box:raise ValueError(f'No visible content for item {ident}')
    visible=crop.crop(box);scale=min(224/visible.width,224/visible.height)
    size=(round(visible.width*scale),round(visible.height*scale));fit=visible.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
    output=Image.new('RGBA',(256,256));placement=((256-size[0])//2,(256-size[1])//2);output.alpha_composite(fit,placement)
    target=folder/'icons'/f'{ident}-{item["name"]}.png';target.parent.mkdir(parents=True,exist_ok=True);output.save(target)
    record={'itemId':ident,'category':entry['category'],'sourceName':entry['name'],'sourceDescription':entry['description'],
        'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':256,'height':256,
        'anchor':[128,128],'derivedFrom':{'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'generationRecord':source.relative_to(root).as_posix()+'.generation.json'},
        'operation':{'type':'crop-uniform-fit-centred','sourceCellRect':rect,'contentBoxWithinCell':list(box),
            'sourceContentRect':[rect[0]+box[0],rect[1]+box[1],rect[0]+box[2],rect[1]+box[3]],'uniformScale':scale,
            'placementPx':list(placement),'resampled':True,'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False},
        'alphaExtrema':list(output.getchannel('A').getextrema()),'sourceReference':item.get('sourceReference')or f'references/qqtang-item-data/icons/item-{ident}.png',
        'runtimeAdopted':False,'visualAccepted':False,'status':'painted-candidate-awaiting-alpha-background-and-runtime-review'}
    if item.get('displayName'):record['projectDisplayName']=item['displayName']
    if item.get('relatedFrameCandidate'):record['relatedFrameCandidate']=item['relatedFrameCandidate']
    touching=[name for name,touches in [('left',box[0]==0),('top',box[1]==0),('right',box[2]==crop.width),('bottom',box[3]==crop.height)]if touches]
    record['sourceCellAlphaTouchEdges']=touching
    record['warnings']=['source-cell-alpha-touches-boundary-review-ownership']if touching else[]
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    art['items']=[old for old in art['items']if old['itemId']!=ident];art['items'].append(record)
manifest_path.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'paintedItems':len(art['items']),'newModelGeneration':False,'visualAccepted':False}))
