"""One authorizedP1/P2 static batch with a shared new-family image offset."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,copy
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
if any(BASE.glob('passing-P*-rgba.png')):raise RuntimeError('The one passing static batch already exists; do not iterate')
rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
crops_path=BASE/'native-crops.json';crops= json.loads(crops_path.read_text(encoding='utf-8'))
landmarks_path=BASE/'manual-landmarks.proposal.json';landmarks=json.loads(landmarks_path.read_text(encoding='utf-8'))
upper_path=BASE.parent.parent/'whole-arm-v1'/'bind-static-v2'/'proposal.json';upper_raw=upper_path.read_bytes();upper=json.loads(upper_raw)
S=.24;GROUND=528.5;hips={'near_R':[307,439],'far_L':[319,438]}
parts={p['partId']:p for p in crops['parts']}
points=landmarks['pointsSourceNative']
unregistered_plants={}
for ident in ['near_R_planted','far_L_planted']:
    side='near_R'if ident.startswith('near')else'far_L'
    unregistered_plants[ident]=hips[side][1]+S*(points[ident]['sole'][1]-points[ident]['cap'][1])
family_y=round(GROUND-sum(unregistered_plants.values())/2,2)
if abs(family_y-(-12.84))>1e-9:raise ValueError('Manual source data changed; do not silently choose a different one-time registration')
fixed=copy.deepcopy([n for n in upper['twoContacts'][0]['nodes']if n['id']in['head','torso_pelvis','near_R_whole','far_L_whole_gourd']])
ring=copy.deepcopy(upper['twoContacts'][0]['newShoulderOcclusion'])
for n in fixed:
    if sha((ROOT/n['file']).read_bytes())!=n['sha256']:raise ValueError('Fixed source changed')
if sha((ROOT/ring['file']).read_bytes())!=ring['sha256']:raise ValueError('Ring source changed')
def transform(im,m):
    a,b,c,d,e,f=m
    if b or c or a!=d or a<=0:raise ValueError('Warp/mirror/rotation not authorized')
    return im.convert('RGBa').transform((627,627),Image.Transform.AFFINE,(1/a,0,-e/a,0,1/d,-f/d),resample=Image.Resampling.BICUBIC).convert('RGBA')
def pt(m,xy):
    a,b,c,d,e,f=m;return[a*xy[0]+c*xy[1]+e,b*xy[0]+d*xy[1]+f]
def alpha_bbox(im):
    return list(im.getchannel('A').point(lambda v:255if v>=8 else 0).getbbox())
poses=[];ivory=[];small_ivory=[]
for label,near,far in [('P1','near_R_planted','far_L_raised'),('P2','near_R_raised','far_L_planted')]:
    nodes=copy.deepcopy(fixed);measurements={}
    for ident,layer in [(far,10),(near,20)]:
        part=parts[ident];side='near_R'if ident.startswith('near')else'far_L';position=hips[side]
        roi=part['sourceROI'];local={n:[xy[0]-roi[0],xy[1]-roi[1]]for n,xy in points[ident].items()};cap=local['cap']
        effective=[cap[0],cap[1]-family_y/S]
        matrix=[S,0,0,S,position[0]-cap[0]*S,position[1]+family_y-cap[1]*S]
        nodes.append({'id':ident,'file':part['file'],'sha256':part['sha256'],'sourceROI':roi,'sourceNativeCropSize':part['nativeCropSize'],
            'sourceGenerationRecord':part['sourceGenerationRecord'],'manualSourceNativeLandmarks':points[ident],'manualCropLocalLandmarks':local,
            'sourceCapPivot':cap,'boneBindPosition':position,'familyArtImageOffset':[0,family_y],
            'effectiveImagePivotForEquivalentMatrix':effective,
            'effectivePivotWarning':'Source cap remains the actual white-cap point. Effective pivot includes an explicitly authorized family art placement offset and is not a measured cap/anatomical hip/native anchor.',
            'sourceCapAfterImageRegistrationWorld':[position[0],position[1]+family_y],
            'scale':S,'layer':layer,'imageMatrix':matrix,
            'anatomicalSide':'RIGHT'if side=='near_R'else'LEFT','state':'planted'if ident.endswith('planted')else'raised',
            'transformedManualLandmarks':{n:pt(matrix,xy)for n,xy in local.items()},'manualLandmarksApproved':False})
    canvas=Image.new('RGBA',(627,627),(0,0,0,0));recorded=[]
    for n in sorted(nodes,key=lambda n:n['layer']):
        p=ROOT/n['file'];raw=p.read_bytes()
        if sha(raw)!=n['sha256']:raise ValueError('Current painted part changed')
        im=Image.open(p).convert('RGBA')
        if n['id']in parts:
            samples={k:list(im.getpixel(tuple(xy)))for k,xy in n['manualCropLocalLandmarks'].items()}
            n['manualLandmarkPixelSamplesRGBA']=samples
            if samples['cap'][3]<8:raise ValueError('Cap point is not on the visible cap')
            if samples['sole'][3]<8:raise ValueError('Sole point is not on source visible sole')
        rendered=transform(im,n['imageMatrix']);canvas.alpha_composite(rendered)
        if n['id']in parts:
            bbox=alpha_bbox(rendered);soleY=n['transformedManualLandmarks']['sole'][1]
            n['renderedLegAlpha8BBoxExclusive']=bbox
            n['actualLowestVisiblePixelRow']=bbox[3]-1
            n['clearanceToArtGroundPixelCenter']=GROUND-(bbox[3]-1)
            n['clearanceToArtGroundPixelBottom']=GROUND-bbox[3]
            n['manualSoleResidualFromArtGround']=soleY-GROUND
            measurements[n['id']]={'state':n['state'],'manualSoleY':soleY,'manualSoleResidual':soleY-GROUND,
              'renderedLegAlpha8BBoxExclusive':bbox,'lowestVisiblePixelRow':bbox[3]-1,
              'clearanceToPixelCenter':GROUND-(bbox[3]-1),'clearanceToPixelBottom':GROUND-bbox[3],
              'clearanceScope':'Current isolated leg rendered at0.24 after the same family placement, before occluding torso; not native physical contact/timing.'}
        im.close();rendered.close();recorded.append(n)
    rim=Image.open(ROOT/ring['file']).convert('RGBA');rendered=transform(rim,ring['cutoutImageMatrix']);canvas.alpha_composite(rendered);rim.close();rendered.close()
    actor_bbox=alpha_bbox(canvas)
    file=BASE/f'passing-{label}-rgba.png';canvas.save(file)
    bg=Image.new('RGBA',canvas.size,(248,242,225,255));bg.alpha_composite(canvas);ivory.append(bg.convert('RGB'))
    small=canvas.convert('RGBa').resize((96,96),Image.Resampling.LANCZOS).convert('RGBA')
    sf=BASE/f'passing-{label}-96.png';small.save(sf)
    sb=Image.new('RGBA',(96,96),(248,242,225,255));sb.alpha_composite(small);small_ivory.append(sb.convert('RGB'))
    common={'pose':label,'nodes':recorded,'fixedTorsoRing':ring,
      'sourceUpperProposal':rel(upper_path),'sourceUpperProposalSha256':sha(upper_raw),
      'familyArtImageOffset':[0,family_y],'newModelGeneration':False,'isAnimation':False,
      'worldRoot':None,'nativeTimingMs':None,'callerRootModified':False,'runtimeAdopted':False,
      'operation':'One deterministicP1/P2 passing static registration from complete native crops; all new legs0.24 and one family image offset, fixed upper matrices/occlusion unchanged. No source alpha edit, bbox fit, warp or mirror.'}
    save(file.with_suffix('.png.source.json'),{'file':rel(file),'sha256':sha(file.read_bytes()),'size':[627,627],
        'actorAlpha8BBoxExclusive':actor_bbox,'legMeasurements':measurements,**common})
    save(sf.with_suffix('.png.source.json'),{'file':rel(sf),'sha256':sha(sf.read_bytes()),'size':[96,96],
        'derivedFrom':{'file':rel(file),'sha256':sha(file.read_bytes()),'sourceRecord':rel(file.with_suffix('.png.source.json'))},
        'operation':'Uniform whole627 canvas PMA LANCZOS resize96/627, no pose bbox fit; not a96px-high actor.',
        'newModelGeneration':False,'runtimeAdopted':False})
    poses.append({'pose':label,'nearPart':near,'farPart':far,'nodes':recorded,'fixedTorsoRing':ring,
        'legMeasurements':measurements,'actorAlpha8BBoxExclusive':actor_bbox,'output':rel(file),'sha256':sha(file.read_bytes()),
        'smallOutput':rel(sf),'smallSha256':sha(sf.read_bytes())})
    canvas.close();small.close()
board=Image.new('RGB',(1254,627),(248,242,225));draw=ImageDraw.Draw(board)
for i,im in enumerate(ivory):
    board.paste(im,(i*627,0));draw.text((i*627+16,16),'P1 near planted / far raised'if i==0 else'P2 near raised / far planted',fill='#244f44')
    for x in range(i*627+100,i*627+550,12):draw.line((x,529,x+5,529),fill='#aa6555',width=1)
board_path=BASE/'two-passing-627-ivory.png';board.save(board_path)
small_board=Image.new('RGB',(192,116),(248,242,225));draw=ImageDraw.Draw(small_board)
for i,im in enumerate(small_ivory):
    small_board.paste(im,(i*96,0));draw.text((i*96+3,100),'P1'if i==0 else'P2',fill='#244f44')
small_path=BASE/'two-passing-96-ivory.png';small_board.save(small_path)
for p,sz,is_small in [(board_path,[1254,627],False),(small_path,[192,116],True)]:
    save(p.with_suffix('.png.source.json'),{'file':rel(p),'sha256':sha(p.read_bytes()),'size':sz,
       'derivedFrom':[{'file':q['smallOutput']if is_small else q['output'],'sha256':q['smallSha256']if is_small else q['sha256']}for q in poses],
       'operation':'Unscaled side-by-side ivory diagnostics, native board has diagnostic art-ground line529, small board20px labels. Not gameplay art or imagegen.',
       'newModelGeneration':False,'runtimeAdopted':False})
proposal={'schemaVersion':1,'projectDisplayName':'灵葫大作战','createdAtUTC':datetime.now(timezone.utc).isoformat(),
 'sourceAtlas':crops['source'],'sourceAtlasSha256':crops['sourceSha256'],'sourceNativeCrops':rel(crops_path),
 'sourceLandmarkProposal':rel(landmarks_path),'sourceLandmarkProposalSha256':sha(landmarks_path.read_bytes()),
 'sourceUpperProposal':rel(upper_path),'sourceUpperProposalSha256':sha(upper_raw),
 'unregisteredManualPlantedSoleY':unregistered_plants,'familyArtImageOffset':[0,family_y],
 'familyOffsetDerivation':'528.5 minus average of two existing manual planted soleY values at fixed bone hips and0.24, rounded once to0.01designpx. Same offset all4 parts/two poses; not from bbox.',
 'commonNewLegScale':S,'boneHips':hips,'candidateArtGroundY':GROUND,
 'sourceCapPointsPreserved':True,'sourceCapIsNotEffectiveImagePivot':True,
 'fixedUpperAndArmAndRingMatricesUnchanged':True,'twoPoses':poses,
 'sourceAlpha8OwnedOnce':crops['sourceAlpha8OwnedOnce'],'mirroring':False,'componentWarping':False,'perPoseBboxFit':False,
 'oneRenderBatch':True,'newAiImageCount':0,'sourcePngsOrAlphaModified':False,
 'sourcePoseIdentityMappingApproved':False,'sixPhaseComplete':False,'worldRoot':None,'nativeTimingMs':None,
 'actuallyViewed':False,'staticAccepted':False,'runtimeEnabled':False,'fullAnimationAccepted':False}
save(BASE/'proposal.json',proposal)
print(json.dumps({'output':rel(board_path),'small':rel(small_path),'familyOffset':family_y,
 'measurements':[{p['pose']:p['legMeasurements']}for p in poses],'actorBounds':[{p['pose']:p['actorAlpha8BBoxExclusive']}for p in poses]}))
