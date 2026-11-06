"""Slice one measured sprite sheet into original-frame-size painted candidates."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
root=Path(__file__).resolve().parents[1];spec=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
source=root/spec['source'];sheet=Image.open(source).convert('RGBA');source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
if list(sheet.size)!=spec['actualNativeSheetSize']:raise ValueError('Native dimensions differ from measured cell contract')
original=json.loads((root/spec['sourceRecord']).read_text(encoding='utf-8'));columns=spec['columns'];rows=spec['rows'];frames=[];by_key={}
output_folder=(root/spec.get('assetDirectory','assets/effects/flames')).resolve()
if not any(output_folder.is_relative_to(root/p)for p in ['assets/effects','assets/items/namecard-borders/animation','assets/items/battlefield/animation']):raise ValueError('Sequence output must remain in an explicitly owned animation asset folder')
if len(spec['frameOrder'])>9 or len(spec['frameOrder'])!=len(original['dimg']['frames']):raise ValueError('Expected a bounded complete frame mapping')
if sorted(spec['frameOrder'])!=list(range(len(original['dimg']['frames']))):raise ValueError('Every declared frame index must appear exactly once')
cell_slots=spec.get('cellSlots',list(range(len(spec['frameOrder']))))
if len(cell_slots)!=len(spec['frameOrder']) or any(type(i)is not int or i<0 or i>=columns*rows for i in cell_slots):raise ValueError('Invalid explicitly selected source cells')
cell_keys={};prepared={}
for slot,index in enumerate(spec['frameOrder']):
    frame=original['dimg']['frames'][index];source_slot=cell_slots[slot]
    if frame.get('empty'):raise ValueError('Do not paint an originally empty frame')
    key=(frame['encodedPixelSha256'],frame['width'],frame['height'],*frame['frameOffset'])
    if source_slot in cell_keys and cell_keys[source_slot]!=key:raise ValueError('One painted cell cannot represent different original visible frames')
    cell_keys[source_slot]=key
    if source_slot not in prepared:
        rect=[source_slot%columns*sheet.width//columns,source_slot//columns*sheet.height//rows,(source_slot%columns+1)*sheet.width//columns,(source_slot//columns+1)*sheet.height//rows]
        cell=sheet.crop(rect);box=cell.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
        if box is None or box[0]<=0 or box[1]<=0 or box[2]>=cell.width or box[3]>=cell.height:raise ValueError('Empty or crossing cell; no frame files written')
        prepared[source_slot]=(rect,cell,box)
for slot,index in enumerate(spec['frameOrder']):
    source_slot=cell_slots[slot]
    frame=original['dimg']['frames'][index]
    if frame.get('empty'):raise ValueError('Do not paint an originally empty frame')
    key=(frame['encodedPixelSha256'],frame['width'],frame['height'],*frame['frameOffset'])
    if key in by_key:
        previous=by_key[key];selection={'generatedCellReused':source_slot}if source_slot==previous['operation']['sourceCellIndex']else{'unusedGeneratedCellIndex':source_slot}
        frames.append({**previous,'frameIndex':index,'sourceFrame':frame,'reuseOfFrameIndex':previous['frameIndex'],
            'reuseEvidence':'identical source encoded-pixel SHA256, frame dimensions and raw offset',**selection});continue
    rect,cell,box=prepared[source_slot]
    crop=cell.crop(box);size=(frame['width']*4,frame['height']*4);scale=min(size[0]/crop.width,size[1]/crop.height)
    fit_size=(round(crop.width*scale),round(crop.height*scale));fit=crop.convert('RGBa').resize(fit_size,Image.Resampling.LANCZOS).convert('RGBA')
    out=Image.new('RGBA',size);place=((size[0]-fit_size[0])//2,(size[1]-fit_size[1])//2);out.alpha_composite(fit,place)
    target=output_folder/spec['name']/f'{index:02d}.png';target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
    record={'frameIndex':index,'empty':False,'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'width':size[0],'height':size[1],'exportDensity':4,'sourceFrame':frame,'sourceReferenceRecord':spec['sourceRecord'],
        'derivedFrom':{'file':spec['source'],'sha256':source_sha,'generationRecord':spec['source']+'.generation.json'},
        'operation':{'type':'measured-cell-crop-uniform-fit-centred','sourceCellIndex':source_slot,'sourceCellRect':rect,'contentBoxWithinCell':list(box),
            'placementPx':list(place),'uniformScale':scale,'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False},
        'alphaSource':'new painted sprite; original alpha is reference only, not copied','alphaExtrema':list(out.getchannel('A').getextrema()),
        'visualAccepted':False,'runtimeAdopted':False,'limitations':['shared-root projection, effect usage and timing unverified','actual background, decay readability and neighboring-cell overlap need playback review']}
    ratio_error=abs((crop.width/crop.height)/(frame['width']/frame['height'])-1)
    record['visibleAspectRatioRelativeError']=ratio_error
    record['geometryAccepted']=False
    record['warnings']=['visible-proportions-differ-more-than-10-percent']if ratio_error>.1 else[]
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');frames.append(record);by_key[key]=record
manifest_path=output_folder/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))if manifest_path.exists()else{'schemaVersion':1,'resources':[],'accepted':False,'runtimeAdopted':False}
entry={'sourceResource':spec.get('sourceResource',spec['name']+'_stand'),'projectEffectName':spec.get('displayName'),'sourcePackagePath':original.get('packagePath',original.get('sourceMember')),'sourceRecord':spec['sourceRecord'],
    'frameCount':len(frames),'frames':frames,'sourceFrameTimingMs':None,'timingEvidence':'not verified from original client',
    'sourceFrameCoverage':sorted(f['frameIndex']for f in frames),'allDeclaredFramesHaveCandidates':True,'fullStateAnimationAccepted':False,
    'status':'original-painted-sprite-sequence-candidate','mappingNotes':spec.get('mappingNotes'),'accepted':False,'runtimeAdopted':False}
if spec.get('sourceItemId')is not None:entry['sourceItemId']=spec['sourceItemId']
manifest['resources']=[r for r in manifest['resources']if r['sourceResource']!=entry['sourceResource']];manifest['resources'].append(entry)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceResource':entry['sourceResource'],'sourceFrameEntries':len(frames),'uniquePaintedPngs':len({f['file']for f in frames}),'resourceCandidates':len(manifest['resources']),'accepted':False}))
