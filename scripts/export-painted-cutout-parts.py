"""Export one explicitly measured painted atlas without inventing a bind pose.

Ownership is a human-authored rectangle or polygon, never a nominal grid.
Every source pixel with alpha>=8 must belong to exactly one part before writing.
This is deterministic cropping, not image generation or animation acceptance.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json,hashlib,sys
import numpy as np

root=Path(__file__).resolve().parents[1]
spec=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
source=(root/spec['source']).resolve();folder=(root/spec['assetDirectory']).resolve()
if not source.is_relative_to(root/'assets/characters/motion-generated/experimental-parts') or not folder.is_relative_to(source.parent):
    raise ValueError('This exporter is restricted to the owned experimental atlas')
im=Image.open(source).convert('RGBA')
if list(im.size)!=spec['actualNativeSize']:raise ValueError('Measured source dimensions changed')
parts=spec['parts']
if len(parts)!=16 or len({p['id']for p in parts})!=16:raise ValueError('Expected16 distinct painted component identities')
alpha=np.asarray(im.getchannel('A'));visible=alpha>=8;coverage=np.zeros(alpha.shape,dtype=np.uint8);masks=[];boundary_failures=[]
for part in parts:
    mask=Image.new('L',im.size)
    if 'polygon'in part:ImageDraw.Draw(mask).polygon([tuple(p)for p in part['polygon']],fill=255)
    else:
        l,t,r,b=part['rect'];ImageDraw.Draw(mask).rectangle((l,t,r-1,b-1),fill=255)
    bits=np.asarray(mask)>0;coverage+=bits;masks.append(mask)
    interior=np.asarray(mask.filter(ImageFilter.MinFilter(3)))>0
    crossing=int(np.count_nonzero(visible&bits&~interior))
    if crossing:boundary_failures.append({'part':part['id'],'visiblePixelsOnOwnershipCut':crossing})
unassigned=int(np.count_nonzero(visible&(coverage==0)));ambiguous=int(np.count_nonzero(visible&(coverage>1)))
if unassigned or ambiguous or boundary_failures:raise ValueError(f'Unresolved visible ownership: missing={unassigned}, multiple={ambiguous}, boundaries={boundary_failures}; no parts written')
sha=hashlib.sha256(source.read_bytes()).hexdigest();records=[];folder.mkdir(parents=True,exist_ok=True)
for part,mask in zip(parts,masks):
    region=im.copy();region.putalpha(Image.fromarray(np.where(np.asarray(mask)>0,alpha,0).astype(np.uint8)))
    bounds=region.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
    if not bounds:raise ValueError('Empty component')
    # Keep8 source pixels outside the measured visible contour. No resize or rotation.
    rect=[max(0,bounds[0]-8),max(0,bounds[1]-8),min(im.width,bounds[2]+8),min(im.height,bounds[3]+8)]
    output=region.crop(rect);target=folder/(part['id']+'.png');output.save(target)
    record={'partId':part['id'],'anatomicalSide':part.get('anatomicalSide'),'file':target.relative_to(root).as_posix(),
        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'nativeCropSize':list(output.size),
        'source':spec['source'],'sourceSha256':sha,'generationRecord':spec['source']+'.generation.json',
        'operation':'explicit measured ownership crop; no resizing, rotation, pixel repaint or new model generation',
        'sourceCropRect':rect,'ownership':{k:v for k,v in part.items()if k in ['rect','polygon']},
        'alphaSource':'unchanged source alpha inside the assigned component; other component ownership excluded',
        'sourceVisibleBounds':list(bounds),'pivot':None,'bindPosition':None,'imageScale':None,
        'bindApproved':False,'visualAccepted':False,'runtimeAdopted':False}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');records.append(record)
manifest={'schemaVersion':1,'source':spec['source'],'sourceSha256':sha,'sourceNativeSize':list(im.size),
    'measuredOwnership':'manual irregular partitions; nominal4x4 rejected','visibleAlphaThreshold':8,
    'unassignedVisiblePixels':unassigned,'multiplyAssignedVisiblePixels':ambiguous,'parts':records,
    'commonPhysicalScaleApproved':False,'bindApproved':False,'animationSource':None,'runtimeAdopted':False}
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'parts':len(records),'unassignedVisiblePixels':unassigned,'multiplyAssignedVisiblePixels':ambiguous,'bindApproved':False}))
