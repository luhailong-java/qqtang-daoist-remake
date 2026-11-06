"""First-visible battlefield pickup master export; scene IDs are not inventory IDs."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
root=Path(__file__).resolve().parents[1];spec=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
source=root/spec['source'];sheet=Image.open(source).convert('RGBA');source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
folder=root/'assets/items/battlefield';manifest_path=folder/'art.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))if manifest_path.exists()else{'schemaVersion':1,'namespace':'battlefield-scene-factory-ID; not account-inventory-item-ID','pieces':[],'accepted':False,'runtimeAdopted':False}
for item in spec['pieces']:
    ident=item['sceneId'];reference_record=item.get('sourceRecord')or f'references/qqtang-packed-art/object--item--item{ident}_stand-first-visible.png.source.json'
    reference=json.loads((root/reference_record).read_text(encoding='utf-8'));original=next(f for f in reference['dimg']['frames']if not f.get('empty'))
    rect=item['rect'];cell=sheet.crop(rect);box=cell.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
    if not box:raise ValueError('Empty pickup master')
    crop=cell.crop(box);size=(original['width']*4,original['height']*4);scale=min(size[0]/crop.width,size[1]/crop.height)
    fit_size=(round(crop.width*scale),round(crop.height*scale));fit=crop.convert('RGBa').resize(fit_size,Image.Resampling.LANCZOS).convert('RGBA')
    out=Image.new('RGBA',size);placement=((size[0]-fit_size[0])//2,size[1]-fit_size[1]);out.alpha_composite(fit,placement)
    target=folder/'masters'/f'{ident}-{item["name"]}.png';target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
    record={'sceneId':ident,'displayName':item['displayName'],'projectNameOriginal':True,'semanticCandidate':item['semantic'],
        'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':size[0],'height':size[1],
        'sourceFirstFrame':original,'sourceAnimationFrameCount':reference['dimg']['frameCount'],'sourceRecord':reference_record,
        'semanticsSource':{'url':'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/pickup.go',
            'gitBlobSha':'c5a613e311dbbf841271ce99d08ac7499532d023','scope':'community reconstruction constants and handling; native usage not independently verified'},
        'imageMapping':'numeric filename association with scene-factory ID; original client lookup not independently verified',
        'derivedFrom':{'file':spec['source'],'sha256':source_sha,'generationRecord':spec['source']+'.generation.json'},
        'operation':{'type':'crop-uniform-fit-bottom-align','sourceCellRect':rect,'contentBoxWithinCell':list(box),'uniformScale':scale,
            'placementPx':list(placement),'exportDensity':4,'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False},
        'alphaExtrema':list(out.getchannel('A').getextrema()),'masterOnly':True,'fullIdleAnimationComplete':False,'visualAccepted':False,'runtimeAdopted':False}
    ratio_error=abs((crop.width/crop.height)/(original['width']/original['height'])-1)
    record['visibleAspectRatioRelativeError']=ratio_error
    record['geometryAccepted']=False
    record['warnings']=['visible-proportions-differ-more-than-10-percent']if ratio_error>.1 else[]
    if ident in [21,23,24,25,27,28]:
        action_id,count={21:(41,1),23:(42,1),24:(63,1),25:(43,3),27:(44,2),28:(64,1)}[ident]
        record['communitySceneToAction']={'sceneId':ident,'actionId':action_id,'count':count,
            'sourceUrl':'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/clientdata/sceneelement/catalog.go',
            'gitBlobSha':'83ef5a6fc73dfd51aa4d881b10c9a32eb4bb6db5','nativeFunctionIndependentlyVerified':False}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest['pieces']=[p for p in manifest['pieces']if p['sceneId']!=ident];manifest['pieces'].append(record)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'battlefieldMasterCandidates':len(manifest['pieces']),'fullAnimationsComplete':False,'accepted':False}))
