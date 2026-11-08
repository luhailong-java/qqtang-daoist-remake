"""One authorized arm crop + fixed A/B static bind, no animation or AI repair."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,hashlib,json,copy
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
OUT=BASE/'bind-static-v1';OUT.mkdir(exist_ok=True)
if any(OUT.glob('*.png')):
    raise RuntimeError('One-time static bind already rendered. Do not iterate automatically.')
rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v3_path=BASE.parent/'whole-leg-v1'/'registered-contact-v3'/'proposal.json'
v3_raw=v3_path.read_bytes();v3=json.loads(v3_raw)
native=BASE/'whole-arm-v1.png';native_raw=native.read_bytes()
if sha(native_raw)!='ac6c54c86e05094b17d538c5982de3c10a3f7d7961616f79c0c46398b51035f0':
    raise ValueError('Arm source changed')
sheet=Image.open(native).convert('RGBA')
if sheet.size!=(1536,1024):raise ValueError('Arm source canvas changed')
all_a=np.asarray(sheet.getchannel('A'));all_visible=int((all_a>=8).sum())
specs=[
    ('near_R_whole',[0,0,768,1024],{'shoulder':[165,329],'elbow':[230,550],'wrist':[535,650],'fingers':[642,663]},[262.5,359.5],70),
    ('far_L_whole_gourd',[768,0,1536,1024],{'shoulder':[884,330],'elbow':[927,531],'wrist':[1162,583],'fingers':[1364,594]},[340,355],5),
]
scale=.18;parts={};staged=[];owned=0
for ident,cell,points,position,layer in specs:
    full=sheet.crop(cell);a=np.asarray(full.getchannel('A'));visible=a>=8
    if any([visible[0].any(),visible[-1].any(),visible[:,0].any(),visible[:,-1].any()]):
        raise ValueError('Native cell boundary crosses visible arm')
    yy,xx=np.nonzero(visible);owned+=int(visible.sum())
    box=[max(0,int(xx.min())-8),max(0,int(yy.min())-8),min(full.width,int(xx.max())+9),min(full.height,int(yy.max())+9)]
    rect=[cell[0]+box[0],cell[1]+box[1],cell[0]+box[2],cell[1]+box[3]]
    crop=sheet.crop(rect);local={n:[p[0]-rect[0],p[1]-rect[1]] for n,p in points.items()}
    p=OUT/(ident+'.png')
    record={'partId':ident,'file':rel(p),'source':rel(native),'sourceSha256':sha(native_raw),
      'sourceCanvasSize':[1536,1024],'sourceGenerationRecord':rel(BASE/'whole-arm-v1.png.generation.json'),
      'ownershipCellRect':cell,'sourceCropRect':rect,'nativeCropSize':list(crop.size),
      'sourceAlpha8VisiblePixels':int(visible.sum()),'manualNativeLandmarks':points,'manualCropLocalLandmarks':local,
      'landmarksEvidence':'One hand-authored visual estimate on actual native PNG. Not recovered anatomy, native frameOffset or approved joints.',
      'pivot':local['shoulder'],'position':position,'scale':scale,'layer':layer,
      'anatomicalSide':'RIGHT' if ident.startswith('near') else 'LEFT',
      'holdingIdentity':'empty RIGHT fist' if ident.startswith('near') else 'LEFT hand fixed to complete own Taiji gourd',
      'operation':'Complete owned native crop with8px transparent margin where source allows, no resize/mirror/warp/source-pixel or alpha repair',
      'runtimeAdopted':False}
    parts[ident]=record;staged.append((p,crop))
if owned!=all_visible or owned!=319473:raise ValueError('Incomplete/duplicate arm source ownership')
# All source crop boundaries have passed before any output PNG is written.
for p,crop in staged:
    crop.save(p);parts[p.stem]['sha256']=sha(p.read_bytes())
    save(p.with_suffix('.png.source.json'),parts[p.stem])
sheet.close()

def transformed(im,m,size=(627,627)):
    a,b,c,d,e,f=m
    if b or c or a!=d or a<=0:raise ValueError('Unexpected warp/mirror/rotation')
    return im.convert('RGBa').transform(size,Image.Transform.AFFINE,(1/a,0,-e/a,0,1/d,-f/d),resample=Image.Resampling.BICUBIC).convert('RGBA')
def point(m,p):
    a,b,c,d,e,f=m;return[a*p[0]+c*p[1]+e,b*p[0]+d*p[1]+f]

pose_records=[];ivory_images=[];small_ivory=[]
for pose in v3['twoContacts']:
    label=pose['contact'];nodes=copy.deepcopy(pose['nodes'])
    for ident in parts:
        part=parts[ident];px,py=part['pivot'];x,y=part['position']
        nodes.append({'id':ident,'file':part['file'],'sha256':part['sha256'],'pivot':part['pivot'],
            'position':part['position'],'scale':scale,'layer':part['layer'],
            'imageMatrix':[scale,0,0,scale,x-px*scale,y-py*scale],
            'anatomicalSide':part['anatomicalSide'],'holdingIdentity':part['holdingIdentity'],
            'sourceCropRect':part['sourceCropRect'],'sourceGenerationRecord':part['sourceGenerationRecord'],
            'manualLocalLandmarks':part['manualCropLocalLandmarks']})
    canvas=Image.new('RGBA',(627,627),(0,0,0,0));rendered_records=[]
    for n in sorted(nodes,key=lambda n:n['layer']):
        p=ROOT/n['file'];raw=p.read_bytes()
        if sha(raw)!=n['sha256']:raise ValueError('Source changed:'+n['id'])
        im=Image.open(p).convert('RGBA');image=transformed(im,n['imageMatrix']);canvas.alpha_composite(image)
        n['sourceCropSize']=list(im.size)
        if 'manualLocalLandmarks' in n:
            n['transformedManualLandmarks']={name:point(n['imageMatrix'],xy) for name,xy in n['manualLocalLandmarks'].items()}
        rendered_records.append(n);im.close();image.close()
    # Same-source torso shoulder-port foreground pass, identical body matrix.
    torso=next(n for n in nodes if n['id']=='torso_pelvis')
    torso_path=ROOT/torso['file'];torso_im=Image.open(torso_path).convert('RGBA')
    roi=[20,25,132,172]
    shoulder_patch=Image.new('RGBA',torso_im.size,(0,0,0,0))
    shoulder_patch.paste(torso_im.crop(roi),(roi[0],roi[1]))
    patch=transformed(shoulder_patch,torso['imageMatrix']);canvas.alpha_composite(patch)
    occlusion={'source':torso['file'],'sourceSha256':torso['sha256'],'sourceROI':roi,
        'imageMatrix':torso['imageMatrix'],'layer':80,
        'purpose':'Same fixed torso shoulder-port material covers near white attachment cap after whole-arm foreground. No new art, hem, source repaint or repaired arm alpha.',
        'wholeTorsoMatrixChanged':False,'sourceAlphaChanged':False}
    shoulder_patch.close();torso_im.close();patch.close()
    clean=OUT/f'contact-{label}-rgba.png';canvas.save(clean)
    bg=Image.new('RGBA',canvas.size,(248,242,225,255));bg.alpha_composite(canvas);ivory_images.append(bg.convert('RGB'))
    small=canvas.convert('RGBa').resize((96,96),Image.Resampling.LANCZOS).convert('RGBA')
    small_path=OUT/f'contact-{label}-96.png';small.save(small_path)
    sb=Image.new('RGBA',(96,96),(248,242,225,255));sb.alpha_composite(small);small_ivory.append(sb.convert('RGB'))
    common={'contact':label,'projectDisplayName':'灵葫大作战','nodes':rendered_records,'torsoShoulderOcclusionPass':occlusion,
        'derivedFromFixedV3':{'file':rel(v3_path),'sha256':sha(v3_raw)},
        'newModelGeneration':False,'animation':False,'runtimeAdopted':False,
        'sourceNativeTimingMs':None,'worldRoot':None,'gameCallerRootModified':False}
    save(clean.with_suffix('.png.source.json'),{'file':rel(clean),'sha256':sha(clean.read_bytes()),'size':[627,627],
        'operation':'One deterministic static assembly from exact painted parts, PMA bicubic isotropic transforms; no new imagegen or new frames.',**common})
    save(small_path.with_suffix('.png.source.json'),{'file':rel(small_path),'sha256':sha(small_path.read_bytes()),'size':[96,96],
        'derivedFrom':{'file':rel(clean),'sha256':sha(clean.read_bytes()),'sourceRecord':rel(clean.with_suffix('.png.source.json'))},
        'operation':'Whole627 canvas uniform PMA LANCZOS scale96/627; no bbox fit. Character visible height is less than96px.',
        'scale':96/627,'newModelGeneration':False,'runtimeAdopted':False})
    pose_records.append({'contact':label,'nearLeg':pose['nearPart'],'farLeg':pose['farPart'],
        'nodes':rendered_records,'torsoShoulderOcclusionPass':occlusion,
        'output':rel(clean),'outputSha256':sha(clean.read_bytes()),'smallOutput':rel(small_path),'smallSha256':sha(small_path.read_bytes())})
    canvas.close();small.close()

board=Image.new('RGB',(1254,627),(248,242,225))
for i,im in enumerate(ivory_images):board.paste(im,(627*i,0))
board_path=OUT/'two-contacts-627-ivory.png';board.save(board_path)
board96=Image.new('RGB',(192,116),(248,242,225));draw=ImageDraw.Draw(board96)
for i,im in enumerate(small_ivory):
    board96.paste(im,(96*i,0));draw.text((96*i+3,100),'A' if i==0 else 'B',fill='#244f44')
board96_path=OUT/'two-contacts-96-ivory.png';board96.save(board96_path)
for name,file,size,derived in [
    ('native',board_path,[1254,627],[{'file':p['output'],'sha256':p['outputSha256']} for p in pose_records]),
    ('small',board96_path,[192,116],[{'file':p['smallOutput'],'sha256':p['smallSha256']} for p in pose_records])]:
    save(file.with_suffix('.png.source.json'),{'file':rel(file),'sha256':sha(file.read_bytes()),'size':size,
        'derivedFrom':derived,'operation':'Unscaled side-by-side ivory composites; small board adds20px label strip below96px cells.',
        'newModelGeneration':False,'runtimeAdopted':False})
record={'schemaVersion':1,'projectDisplayName':'灵葫大作战','createdAtUTC':datetime.now(timezone.utc).isoformat(),
    'sourceArm':rel(native),'sourceArmSha256':sha(native_raw),'sourceArmNativeSize':[1536,1024],
    'sourceArmGenerationRecord':rel(BASE/'whole-arm-v1.png.generation.json'),
    'sourceV3':rel(v3_path),'sourceV3Sha256':sha(v3_raw),
    'armParts':parts,'sourceAlpha8OwnedOnce':owned,'unassignedVisiblePixels':all_visible-owned,'duplicateOwnership':0,
    'commonArmScale':scale,'commonLegScale':.24,'nearShoulder':[262.5,359.5],'farShoulder':[340,355],
    'sameArmBindInBothContacts':True,'fixedV3HeadTorsoLegMatricesPreserved':True,
    'twoContacts':pose_records,'newAiImageCount':0,'oneTimeAssemblyBatch':True,
    'mirroring':False,'componentWarping':False,'perPoseAlphaBboxFit':False,
    'sourceNativeTimingMs':None,'worldRoot':None,'gameCallerRootModified':False,'nativeFrameOffsetModified':False,
    'oldSegmentedArmsUsed':False,'oldStandaloneHandGourdUsed':False,'extraHemUsed':False,
    'manualLandmarksApproved':False,'fullStaticAccepted':False,'actuallyViewed':False,
    'runtimeAdopted':False,'clientApproved':False,'completeAnimation':False}
save(OUT/'proposal.json',record)
print(json.dumps({'output':rel(board_path),'smallOutput':rel(board96_path),'armParts':2,'ownedAlpha8':owned,
    'commonArmScale':scale,'oneTimeBatch':True,'newAiImageCount':0}))
