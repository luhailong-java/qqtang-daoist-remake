"""Crop new narrow UI frames; keep original frame extent and pending geometry."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
root=Path(__file__).resolve().parents[1];spec=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
source=root/spec['source'];sheet=Image.open(source).convert('RGBA');sha=hashlib.sha256(source.read_bytes()).hexdigest()
folder=(root/spec.get('assetDirectory','assets/items/namecard-borders')).resolve()
if not folder.is_relative_to(root/'assets/items/namecard-borders'):raise ValueError('Nameplate output must stay inside the owned asset folder')
folder.mkdir(parents=True,exist_ok=True);resource_state=spec.get('resourceState','stand')
catalog=json.loads((root/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'));source_items={i['item_id']:i for i in catalog['items']}
manifest_path=folder/'art.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))if manifest_path.exists()else{'schemaVersion':1,'items':[],'accepted':False,'runtimeAdopted':False}
for item in spec['items']:
    ident=item['itemId'];entry=source_items[ident]
    if entry['category']!='namecardbound':raise ValueError('Wrong source category')
    ref_path=item.get('sourceRecord')or f'references/qqtang-item-data/icons/item-{ident}.png.source.json';ref=json.loads((root/ref_path).read_text(encoding='utf-8'))
    rect=item['rect'];cell=sheet.crop(rect);box=cell.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
    if not box or box[0]==0 or box[1]==0 or box[2]==cell.width or box[3]==cell.height:raise ValueError('Empty or unresolved cell ownership')
    crop=cell.crop(box);fw,fh=ref['nativeFrameSize'];size=(fw*4,fh*4);scale=min(size[0]/crop.width,size[1]/crop.height)
    fit_size=(round(crop.width*scale),round(crop.height*scale));fit=crop.convert('RGBa').resize(fit_size,Image.Resampling.LANCZOS).convert('RGBA')
    out=Image.new('RGBA',size);placement=((size[0]-fit_size[0])//2,(size[1]-fit_size[1])//2);out.alpha_composite(fit,placement)
    target=folder/'frames'/f'{ident}-{item["name"]}.png';target.parent.mkdir(exist_ok=True);out.save(target)
    error=abs(crop.width/crop.height/(fw/fh)-1)
    record={'itemId':ident,'category':entry['category'],'sourceName':entry['name'],'sourceDescription':entry['description'],
        'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':size[0],'height':size[1],
        'sourceFrameSize':[fw,fh],'sourceRawOffset':ref.get('selectedFrameOffset'),'sourceStateFrameCount':ref['sourceFrameCount'],'resourceState':resource_state,
        'sourceReferenceRecord':ref_path,'sourceInstalledResources':entry['installed_files'],'exportDensity':4,
        'derivedFrom':{'file':spec['source'],'sha256':sha,'generationRecord':spec['source']+'.generation.json'},
        'operation':{'type':'crop-uniform-fit-centred','sourceCellRect':rect,'contentBoxWithinCell':list(box),
            'uniformScale':scale,'placementPx':list(placement),'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False},
        'visibleAspectRatioRelativeError':error,'alphaExtrema':list(out.getchannel('A').getextrema()),
        'centreAlpha':out.getpixel((size[0]//2,size[1]//2))[3],
        'warnings':(['visible-proportions-differ-more-than-10-percent']if error>.1 else[])+(['resampling-upscale-not-native-detail']if scale>1 else[]),
        'masterOnly':True,'sourceFrameCoverage':[ref['sourceFrameIndex']],
        'allDeclaredFramePositionsHaveCandidates':ref['sourceFrameCount']==1,
        'fullSourceStateAnimationComplete':False,'otherStateAnimationsComplete':False,'animationTimingVerified':False,'nineSlice':None,
        'geometryAccepted':False,'visualAccepted':False,'runtimeAdopted':False}
    if resource_state=='stand':record['sourceStandFrameCount']=ref['sourceFrameCount'];record['fullStandAnimationComplete']=False
    if resource_state=='walk':record['fullWalkAnimationComplete']=False
    if ref.get('completeContainerFormatVerified')is False:
        record['sourceCompleteContainerFormatVerified']=False
        record['sourceReferenceScope']=ref['referenceScope']
        record['sourceOpaqueSuffixEvidence']={key:ref['dimg'].get(key)for key in ['trailingByteLength','trailingBytesSha256','referenceOnlyOpaqueVersionedSuffix']}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest['items']=[i for i in manifest['items']if i['itemId']!=ident];manifest['items'].append(record)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'firstStateBorderCandidates':len(manifest['items']),'accepted':False,'fullAnimationsComplete':False}))
