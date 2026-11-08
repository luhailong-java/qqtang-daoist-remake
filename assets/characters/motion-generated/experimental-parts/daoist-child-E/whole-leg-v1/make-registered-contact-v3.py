"""One coordinator-authorized two-contact artistic registration; not animation."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
OUT=BASE/'registered-contact-v3'
OUT.mkdir(exist_ok=True)
source_path=BASE/'root-contact-diagnostic'/'proposal.json'
source_raw=source_path.read_bytes()
source=json.loads(source_raw)
sha=lambda b:hashlib.sha256(b).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
save_json=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if any(OUT.glob('*.png')):
    raise RuntimeError('One-time registered v3 already rendered; do not iterate automatically')
if source['wholeLegUniformScale']!=.24 or source['nearHipPosition']!=[307,439] or source['farHipPosition']!=[319,438]:
    raise ValueError('Coordinator source proposal changed')
poses=[]
contact_images=[]
for pose in source['twoContacts']:
    label=pose['contact']
    canvas=Image.new('RGBA',(627,627),(246,240,222,255))
    nodes=[]
    sole_points={}
    for old in pose['nodes']:
        n=dict(old)
        n['originalPosition']=list(old['position'])
        n['originalImageMatrix']=list(old['imageMatrix'])
        if old['id'] in ('head','torso_pelvis'):
            n['artisticRegistrationTranslation']=[0,3]
        elif label=='B':
            n['artisticRegistrationTranslation']=[0,2.4]
        else:
            n['artisticRegistrationTranslation']=[0,0]
        dx,dy=n['artisticRegistrationTranslation']
        n['position']=[old['position'][0]+dx,old['position'][1]+dy]
        n['imageMatrix']=list(old['imageMatrix'])
        n['imageMatrix'][4]+=dx
        n['imageMatrix'][5]+=dy
        p=ROOT/n['file']
        image_bytes=p.read_bytes()
        if sha(image_bytes)!=n['sha256']:
            raise ValueError('Source changed: '+n['id'])
        im=Image.open(p).convert('RGBA')
        n['sourceCropSize']=list(im.size)
        n['paintedSourceGenerationRecord']=(
            rel(BASE/'whole-leg-v1.png.generation.json')
            if n['id'] in source['parts'] else
            rel(BASE.parent/'parts-master-v1.png.generation.json'))
        if n['id'] in source['parts']:
            n['originalNativeCrop']=source['parts'][n['id']]
        a,b,c,d,e,f=n['imageMatrix']
        if b!=0 or c!=0 or a!=d or a<=0:
            raise ValueError('Unexpected warp, mirror or rotation')
        rendered=im.convert('RGBa').transform((627,627),Image.Transform.AFFINE,
            (1/a,0,-e/a,0,1/d,-f/d),resample=Image.Resampling.BICUBIC).convert('RGBA')
        canvas.alpha_composite(rendered)
        if n['id'] in source['parts']:
            sx,sy=source['parts'][n['id']]['soleCandidate']
            sole_points[n['id']]=[a*sx+e,d*sy+f]
        nodes.append(n)
        im.close()
        rendered.close()
    clean=OUT/f'contact-{label}-ivory.png'
    canvas.convert('RGB').save(clean)
    common={'operation':'Deterministic fixed-isotropic PMA affine artistic attachment/image registration, existing own painted parts only; not a new model frame or animation.',
            'sourceProposal':rel(source_path),'sourceProposalSha256':sha(source_raw),
            'newModelGeneration':False,'nativeFrameOffsetModified':False,'mirroring':False,'perPoseAlphaBboxFit':False,
            'sourceNativeTimingMs':None,'gameCallerRootModified':False,'worldRoot':None,'runtimeAdopted':False}
    save_json(clean.with_suffix('.png.source.json'),{
        'file':rel(clean),'sha256':sha(clean.read_bytes()),'size':[627,627],
        'contact':label,'nodes':nodes,'transformedUnapprovedManualSolePoints':sole_points,**common})
    diag=canvas.convert('RGB')
    draw=ImageDraw.Draw(diag)
    for x in range(80,550,12):
        draw.line((x,529,min(x+6,550),529),fill='#b86a59',width=1)
    draw.text((18,16),f'CONTACT {label} | artistic registration v3 | UNAPPROVED',fill='#214a3d')
    draw.text((18,556),'Head+torso +3px both; B legs +2.4px. Arms still missing.',fill='#214a3d')
    draw.text((18,574),'Art-ground528.5; raster line529. Not gameplay root or source offset.',fill='#214a3d')
    contact_images.append(diag)
    poses.append({'contact':label,'nearPart':pose['nearPart'],'farPart':pose['farPart'],
                  'nodes':nodes,'transformedUnapprovedManualSolePoints':sole_points,
                  'output':rel(clean),'outputSha256':sha(clean.read_bytes())})
    canvas.close()
board=Image.new('RGB',(1254,627),(246,240,222))
for index,image in enumerate(contact_images):
    board.paste(image,(627*index,0))
board_path=OUT/'two-contacts-ivory.png'
board.save(board_path)
record={
    'schemaVersion':1,'projectDisplayName':'灵葫大作战','createdAtUTC':datetime.now(timezone.utc).isoformat(),
    'sourceProposal':rel(source_path),'sourceProposalSha256':sha(source_raw),
    'sourceWholeLeg':source['source'],'sourceWholeLegSha256':source['sourceSHA256'],
    'sourceParts':source['parts'],'sourceWholeLegNativeSize':[1536,1024],
    'sourceAlpha8OwnershipClaim':{'uniqueVisiblePixels':source['sourceAlpha8PixelsOwnedOnce'],
        'evidence':'Copied coordinator native-crop ownership metadata; not a repeated full source alpha re-audit'},
    'designCanvas':[627,627],'twoContacts':poses,
    'commonWholeLegScale':.24,'upperBodyTranslationBoth':[0,3],'legTranslationA':[0,0],'legTranslationB':[0,2.4],
    'candidateArtGroundY':528.5,'diagnosticRasterLineY':529,
    'originalHipPointsPreserved':True,'fixedAnatomicalIDs':True,'sourceNativeTimingMs':None,
    'worldRoot':None,'gameCallerRootModified':False,'nativeFrameOffsetModified':False,
    'newAiImageCount':0,'newCropCount':0,'oldSegmentedLegsUsed':False,'secondHemUsed':False,
    'armsPresent':False,'newAssemblyCount':2,'isAnimation':False,
    'operation':'One necessary static A/B deterministic registration from the existing exact crops. Head/torso move together3px in both contacts; only B legs move together2.4px. No scaling drift, warp, mirror, source pixel edit, alpha bbox fit or caller/root change.',
    'staticBindAccepted':False,'clientApproved':False,'runtimeAdopted':False,'actuallyViewed':False,
}
save_json(OUT/'proposal.json',record)
save_json(board_path.with_suffix('.png.source.json'),{
    'file':rel(board_path),'sha256':sha(board_path.read_bytes()),'size':[1254,627],
    'operation':'Unscaled side-by-side combination of two627px deterministic ivory diagnostics with text and a diagnostic dashed line only.',
    'derivedFrom':[{'file':p['output'],'sha256':p['outputSha256']} for p in poses],
    'proposal':rel(OUT/'proposal.json'),'newModelGeneration':False,'runtimeAdopted':False})
print(json.dumps({'output':rel(board_path),'contacts':2,'newModelGeneration':False,
    'solePoints':[{p['contact']:p['transformedUnapprovedManualSolePoints']} for p in poses]}))
