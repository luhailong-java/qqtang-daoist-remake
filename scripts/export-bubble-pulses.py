"""Bounded export of eight painted breathing frames, without runtime approval."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[1];source=root/'assets/effects/bubble-pulses-a-v1.png'
sheet=Image.open(source).convert('RGBA');source_sha=hashlib.sha256(source.read_bytes()).hexdigest();clips=[]
if sheet.size!=(1536,1024):raise ValueError('Unexpected native sheet dimensions; update measured cell contract explicitly')
for row,bomb in enumerate([1,4]):
    native_record=json.loads((root/f'references/qqtang-packed-art/object--bomb--bomb{bomb}_stand-first-visible.png.source.json').read_text(encoding='utf-8'))
    frames=[]
    for index,original in enumerate(native_record['dimg']['frames']):
        # Source bomb1 repeats frame0 exactly at frame2. Preserve that verified
        # source repeat rather than substituting a slightly different new pose.
        if bomb==1 and index==2:
            if original['encodedPixelSha256']!=native_record['dimg']['frames'][0]['encodedPixelSha256']:raise ValueError('Source alias no longer exact')
            previous=frames[0];frames.append({**previous,'frameIndex':2,'sourceFrame':original,'reuseOfFrameIndex':0,
                'reuseEvidence':'source encoded-pixel SHA256 and native frame/offset are equal to frame0'});continue
        rect=[index*384,row*512,(index+1)*384,(row+1)*512];cell=sheet.crop(rect)
        box=cell.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
        if box is None:raise ValueError('Empty painted cell')
        crop=cell.crop(box);width=original['width']*4;height=original['height']*4
        scale=min(width/crop.width,height/crop.height);size=(round(crop.width*scale),round(crop.height*scale))
        fit=crop.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA');out=Image.new('RGBA',(width,height))
        place=((width-size[0])//2,height-size[1]);out.alpha_composite(fit,place)
        target=root/f'assets/effects/bubbles/bomb-{bomb}/{index:02d}.png';target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
        record={'frameIndex':index,'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'width':width,'height':height,'exportDensity':4,'sourceFrame':original,
            'sourcePackagePath':native_record['packagePath'],'sourceReferenceRecord':f'references/qqtang-packed-art/object--bomb--bomb{bomb}_stand-first-visible.png.source.json',
            'derivedFrom':{'file':source.relative_to(root).as_posix(),'sha256':source_sha,'generationRecord':source.relative_to(root).as_posix()+'.generation.json'},
            'operation':{'type':'cell-crop-uniform-fit-bottom-align','sourceCellRect':rect,'contentBoxWithinCell':list(box),
                'placementPx':list(place),'uniformScale':scale,'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False},
            'alphaExtrema':list(out.getchannel('A').getextrema()),'visualAccepted':False,'runtimeAdopted':False,
            'limitations':['alpha halo and source-relative scale not accepted','source frame offsets retained verbatim; renderer origin/sign not verified','breathing loop requires real playback and target-background review']}
        target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');frames.append(record)
    clips.append({'sourceResource':f'bomb{bomb}_stand','frameCount':len(frames),'loop':True,'frames':frames,
        'sourceFrameTimingMs':None,'timingEvidence':'not exposed by DIMG; original timing not verified','status':'painted-animation-candidate-not-runtime-adopted'})
manifest={'schemaVersion':1,'artSource':'builtin-generated-and-recorded-uniform-resampling','clips':clips,'accepted':False,'runtimeAdopted':False}
(root/'assets/effects/bubbles/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'clipCandidates':len(clips),'frameEntries':sum(len(c['frames'])for c in clips),'uniquePaintedFramePngs':7,'accepted':False}))
