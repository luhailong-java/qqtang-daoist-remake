"""New painted RGB + original alpha/frame structure; no new generation here."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
root=Path(__file__).resolve().parents[1];spec=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
source=root/spec['source'];sheet=Image.open(source).convert('RGBA');source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
source_cache={spec['source']:(sheet,source_sha)}
manifest_path=root/'assets/effects/flames/manifest.json';manifest={'schemaVersion':1,'resources':[],'accepted':False,'runtimeAdopted':False}
if manifest_path.exists():manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
for resource in spec['resources']:
    original=json.loads((root/resource['sourceRecord']).read_text(encoding='utf-8'));frames=[];by_key={}
    phases={p['sourceFrameIndex']:p for p in resource['phases']}
    for frame in original['dimg']['frames']:
        index=frame['index']
        if frame.get('empty'):
            frames.append({'frameIndex':index,'empty':True,'file':None,'sourceFrame':frame,'operation':'original empty frame preserved; no pixels generated or substituted'});continue
        key=(frame['encodedPixelSha256'],frame['width'],frame['height'],*frame['frameOffset'])
        if key in by_key:
            previous=by_key[key];frames.append({**previous,'frameIndex':index,'sourceFrame':frame,'reuseOfFrameIndex':previous['frameIndex'],
                'reuseEvidence':'identical source encoded-pixel SHA256, native dimensions and raw offset'});continue
        phase=phases[index];reference_path=root/phase['reference'];reference=Image.open(reference_path).convert('RGBA')
        if reference.size!=(frame['width'],frame['height']):raise ValueError('Geometry-mask reference size mismatch')
        paint_source=phase.get('source',spec['source'])
        if paint_source not in source_cache:
            paint_path=root/paint_source;source_cache[paint_source]=(Image.open(paint_path).convert('RGBA'),hashlib.sha256(paint_path.read_bytes()).hexdigest())
        paint_sheet,paint_sha=source_cache[paint_source]
        material=paint_sheet.crop(phase['textureRect']);material_alpha=material.getchannel('A').getextrema()
        if material_alpha[0]<245:raise ValueError('Material crop includes transparent gutter; choose an actual filled interior')
        size=(frame['width']*4,frame['height']*4)
        rgb=material.convert('RGB').resize(size,Image.Resampling.LANCZOS)
        alpha=reference.getchannel('A').resize(size,Image.Resampling.NEAREST);out=rgb.convert('RGBA');out.putalpha(alpha)
        target=root/f'assets/effects/flames/{resource["name"]}/{index:02d}.png';target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
        record={'frameIndex':index,'empty':False,'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'width':size[0],'height':size[1],'exportDensity':4,'sourceFrame':frame,
            'derivedFrom':{'file':paint_source,'sha256':paint_sha,'generationRecord':paint_source+'.generation.json'},
            'geometryMaskSource':{'file':phase['reference'],'sha256':hashlib.sha256(reference_path.read_bytes()).hexdigest(),
                'sourceRecord':resource['sourceRecord'],'use':'original alpha only; no original RGB in final'},
            'operation':{'type':'generated-material-interior-RGB-resample-plus-original-frame-alpha','materialRect':phase['textureRect'],
                'materialAlphaBeforeReplacement':list(material_alpha),'rgbResampler':'LANCZOS','alphaResampler':'NEAREST 4x',
                'outputAlpha':'original frame alpha, not generated-material alpha','newModelGeneration':False},
            'materialReuse':spec.get('materialReuse',False),'materialReuseReason':spec.get('reuseReason'),
            'alphaExtrema':list(alpha.getextrema()),'visualAccepted':False,'runtimeAdopted':False,
            'limitations':['texture edges and neighboring-cell seams unverified','original low-resolution alpha enlarged; not native HD contour','actual client layer, timing, blend mode and end-state not yet verified']}
        target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        by_key[key]=record;frames.append(record)
    entry={'sourceResource':resource['name']+'_stand','sourcePackagePath':original['packagePath'],'sourceRecord':resource['sourceRecord'],
        'frameCount':len(frames),'sourceFrameTimingMs':None,'timingEvidence':'DIMG has no verified playback timing','frames':frames,
        'status':'original-painted-candidate-with-source-alpha-and-frame-sequence','accepted':False,'runtimeAdopted':False}
    manifest['resources']=[r for r in manifest['resources']if r['sourceResource']!=entry['sourceResource']];manifest['resources'].append(entry)
manifest_path.parent.mkdir(parents=True,exist_ok=True);manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'resourceCandidates':len(manifest['resources']),'sourceFrameEntries':sum(r['frameCount']for r in manifest['resources']),'accepted':False}))
