"""Crop/resample existing generated artwork without inventing pixels or geometry."""
from pathlib import Path
from PIL import Image
import json,sys,hashlib,math
root=Path(__file__).resolve().parents[1]
spec_file=root/sys.argv[1];spec=json.loads(spec_file.read_text(encoding='utf-8'))
source=root/spec['source'];im=Image.open(source).convert('RGBA')
inventory=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))
elements={item['elementId']:item for item in inventory['elements']}
folder=root/'assets/maps'/spec['family'];manifest=folder/'art.json'
art=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {'schemaVersion':1,'tilePixels':40,'status':'production-candidates','pieces':[]}
results=[]
for item in spec['items']:
    ident=item['elementId'];entry=elements[ident];rect=item['rect'];cropped=im.crop(rect)
    # Alpha threshold locates content only; original RGBA edges are retained.
    opaque_texture=item.get('opaqueSquareTexture',False)
    if opaque_texture:
        reference=Image.open(root/entry['referencePng']['file']).convert('RGBA')
        if cropped.width!=cropped.height or entry['selectedFrameSize'][0]!=entry['selectedFrameSize'][1] or reference.getchannel('A').getextrema()!=(255,255):
            raise ValueError(f'Opaque texture mode requires square source and an opaque square reference: {ident}')
        if cropped.getchannel('A').getextrema()[0]<250:raise ValueError(f'Opaque texture crop crosses the painted edge: {ident}')
        cropped.putalpha(255)
    bounds=(0,0,cropped.width,cropped.height) if opaque_texture else cropped.getchannel('A').point(lambda value:255 if value>8 else 0).getbbox()
    if not bounds:raise ValueError(f'Empty sprite {ident}')
    crop=cropped.crop(bounds);actual=[rect[0]+bounds[0],rect[1]+bounds[1],rect[0]+bounds[2],rect[1]+bounds[3]]
    fw,fh=entry['selectedFrameSize'];target_size=(fw*4,fh*4)
    scale=min(target_size[0]/crop.width,target_size[1]/crop.height)
    resized=crop.convert('RGBa').resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.LANCZOS).convert('RGBA')
    result=Image.new('RGBA',target_size,(0,0,0,0));placement=((target_size[0]-resized.width)//2,target_size[1]-resized.height);result.alpha_composite(resized,placement)
    target=folder/'pieces'/f'{ident}-{item["name"]}.png';target.parent.mkdir(parents=True,exist_ok=True);result.save(target)
    error=abs(crop.width/crop.height/(fw/fh)-1)
    record={'elementId':ident,'idMapping':'candidate-filename-inference','file':target.relative_to(root).as_posix(),
        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':target_size[0],'height':target_size[1],
        'worldFrameWidth':fw,'worldFrameHeight':fh,'exportDensity':4,
        'sourceFootprintCells':entry['footprintCells'],'sourceMapElemOffset':entry['mapElemOffsetRaw'],
        'derivedFrom':{'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'generationRecord':source.relative_to(root).as_posix()+'.generation.json'},
        'operation':{'type':'crop-opaque-square-texture-uniform-resize' if opaque_texture else 'crop-uniform-fit-bottom-align','sourceRectLTRB':actual,'uniformScale':scale,'placementPx':list(placement),
            'resampled':True,'newModelGeneration':False,'resizeAlpha':'premultiplied'},
        'alphaExtrema':list(result.getchannel('A').getextrema()),'visibleAspectRatioRelativeError':error,
        'geometryAccepted':False,'seamlessVerified':False if item.get('floor') else None,
        'status':'painted-candidate-awaiting-geometry-and-in-game-validation',
        'warnings':(['visible-proportions-differ-more-than-10-percent'] if error>.1 else [])}
    if opaque_texture:record['operation']['alphaNormalization']='interior alpha>=250 normalized to255; no transparent-edge pixels used'
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    art['pieces']=[p for p in art['pieces'] if p['elementId']!=ident];art['pieces'].append(record)
    results.append({'id':ident,'crop':actual,'target':list(target_size),'ratioError':round(error,3)})
manifest.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'family':spec['family'],'total':len(art['pieces']),'exports':results}))
