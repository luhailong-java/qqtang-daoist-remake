"""Final authorized ring-only occlusion / far-attachment static repair, once."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,copy
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
if any(BASE.glob('contact-*.png')):raise RuntimeError('Final static render already performed; no automatic third repair')
rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v1_path=BASE.parent/'bind-static-v1'/'proposal.json';v1_raw=v1_path.read_bytes();v1=json.loads(v1_raw)
v3_path=BASE.parent.parent/'whole-leg-v1'/'registered-contact-v3'/'proposal.json';v3_raw=v3_path.read_bytes();v3=json.loads(v3_raw)
ring_path=BASE/'torso-shoulder-ring-native.png';ring_raw=ring_path.read_bytes()
ring_source_path=ring_path.with_suffix('.png.source.json');ring=json.loads(ring_source_path.read_text(encoding='utf-8'))
if sha(ring_raw)!=ring['sha256']:raise ValueError('Ring ownership crop changed')

def transform(im,m):
    a,b,c,d,e,f=m
    if b or c or a!=d or a<=0:raise ValueError('Unexpected mirror, warp or rotation')
    return im.convert('RGBa').transform((627,627),Image.Transform.AFFINE,
        (1/a,0,-e/a,0,1/d,-f/d),resample=Image.Resampling.BICUBIC).convert('RGBA')
def pt(m,xy):
    a,b,c,d,e,f=m;return[a*xy[0]+c*xy[1]+e,b*xy[0]+d*xy[1]+f]
poses=[];ivory=[];small_ivory=[]
for pose in v1['twoContacts']:
    label=pose['contact'];nodes=copy.deepcopy(pose['nodes'])
    fixed_pose=next(p for p in v3['twoContacts']if p['contact']==label)
    for fixed in fixed_pose['nodes']:
        current=next(n for n in nodes if n['id']==fixed['id'])
        if current['imageMatrix']!=fixed['imageMatrix']:raise ValueError('v3 fixed matrix mismatch')
    for n in nodes:
        n['previousV1ImageMatrix']=list(n['imageMatrix']);n['previousV1Position']=list(n['position'])
        if n['id']=='far_L_whole_gourd':
            if n['position']!=[340,355] or n['scale']!=.18:raise ValueError('Source far bind changed')
            n['position']=[334,360]
            n['imageMatrix'][4]-=6;n['imageMatrix'][5]+=5
            n['artisticAttachmentDeltaFromV1']=[-6,5]
        else:n['artisticAttachmentDeltaFromV1']=[0,0]
        if 'manualLocalLandmarks'in n:
            n['previousV1TransformedManualLandmarks']=n['transformedManualLandmarks']
            n['transformedManualLandmarks']={k:pt(n['imageMatrix'],xy)for k,xy in n['manualLocalLandmarks'].items()}
    canvas=Image.new('RGBA',(627,627),(0,0,0,0))
    for n in sorted(nodes,key=lambda n:n['layer']):
        p=ROOT/n['file'];raw=p.read_bytes()
        if sha(raw)!=n['sha256']:raise ValueError('Painted source changed:'+n['id'])
        im=Image.open(p).convert('RGBA');rendered=transform(im,n['imageMatrix']);canvas.alpha_composite(rendered)
        im.close();rendered.close()
    torso=next(n for n in nodes if n['id']=='torso_pelvis')
    # Crop is in source torso coordinates. Preserve its exact fixed torso matrix.
    a,b,c,d,e,f=torso['imageMatrix'];sx,sy=ring['sourceROI'][:2]
    ring_matrix=[a,b,c,d,e+a*sx+c*sy,f+b*sx+d*sy]
    im=Image.open(ring_path).convert('RGBA');rendered=transform(im,ring_matrix);canvas.alpha_composite(rendered)
    im.close();rendered.close()
    occlusion={'file':rel(ring_path),'sha256':sha(ring_raw),'sourceRecord':rel(ring_source_path),
        'sourceTorso':ring['source'],'sourceTorsoSha256':ring['sourceSha256'],'sourceROI':ring['sourceROI'],
        'outerPolygonSource':ring['outerPolygonSource'],'excludedInnerHoleSource':ring['excludedInnerHoleSource'],
        'torsoOriginalMatrix':torso['imageMatrix'],'cutoutImageMatrix':ring_matrix,'layer':80,
        'previousRectPassRemoved':True,'originalTorsoAndArmAlphaUnmodified':True,
        'operation':'Same-source hand-authored green/gold shoulder-ring ownership cutout only. Old white sleeve inner patch and lower draped cloth excluded, no color extraction or repaint.'}
    file=BASE/f'contact-{label}-rgba.png';canvas.save(file)
    bg=Image.new('RGBA',canvas.size,(248,242,225,255));bg.alpha_composite(canvas);ivory.append(bg.convert('RGB'))
    small=canvas.convert('RGBa').resize((96,96),Image.Resampling.LANCZOS).convert('RGBA')
    small_file=BASE/f'contact-{label}-96.png';small.save(small_file)
    sb=Image.new('RGBA',(96,96),(248,242,225,255));sb.alpha_composite(small);small_ivory.append(sb.convert('RGB'))
    record={'contact':label,'nodes':nodes,'newShoulderOcclusion':occlusion,'unchangedV3Source':rel(v3_path),
        'unchangedV3SourceSha256':sha(v3_raw),'previousV1Source':rel(v1_path),'previousV1SourceSha256':sha(v1_raw),
        'operation':'Final authorized deterministic static repair: existing same-source ring-only occlusion, far whole arm artistic attachment(-6,+5); no new AI/source repaint/arm alpha edit/animation.',
        'newModelGeneration':False,'sourceNativeTimingMs':None,'worldRoot':None,'runtimeAdopted':False}
    save(file.with_suffix('.png.source.json'),{'file':rel(file),'sha256':sha(file.read_bytes()),'size':[627,627],**record})
    save(small_file.with_suffix('.png.source.json'),{'file':rel(small_file),'sha256':sha(small_file.read_bytes()),'size':[96,96],
        'derivedFrom':{'file':rel(file),'sha256':sha(file.read_bytes()),'sourceRecord':rel(file.with_suffix('.png.source.json'))},
        'operation':'Whole627 canvas uniform96/627 PMA LANCZOS resize, no per-pose bbox fit; body visible height is less than96.',
        'newModelGeneration':False,'runtimeAdopted':False})
    poses.append({'contact':label,'nearLeg':pose['nearLeg'],'farLeg':pose['farLeg'],'nodes':nodes,
        'newShoulderOcclusion':occlusion,'output':rel(file),'sha256':sha(file.read_bytes()),'smallOutput':rel(small_file),'smallSha256':sha(small_file.read_bytes())})
    canvas.close();small.close()
board=Image.new('RGB',(1254,627),(248,242,225))
for i,im in enumerate(ivory):board.paste(im,(i*627,0))
board_path=BASE/'two-contacts-627-ivory.png';board.save(board_path)
sb=Image.new('RGB',(192,116),(248,242,225));draw=ImageDraw.Draw(sb)
for i,im in enumerate(small_ivory):
    sb.paste(im,(i*96,0));draw.text((i*96+3,100),'A'if i==0 else'B',fill='#244f44')
small_board=BASE/'two-contacts-96-ivory.png';sb.save(small_board)
for file,size,sm in [(board_path,[1254,627],False),(small_board,[192,116],True)]:
    save(file.with_suffix('.png.source.json'),{'file':rel(file),'sha256':sha(file.read_bytes()),'size':size,
        'derivedFrom':[{'file':p['smallOutput']if sm else p['output'],'sha256':p['smallSha256']if sm else p['sha256']}for p in poses],
        'operation':'Unscaled side-by-side ivory composites;96px board includes20px label strip. Not AI-generated art.',
        'newModelGeneration':False,'runtimeAdopted':False})
proposal={'schemaVersion':1,'projectDisplayName':'灵葫大作战','createdAtUTC':datetime.now(timezone.utc).isoformat(),
    'sourceV1':rel(v1_path),'sourceV1Sha256':sha(v1_raw),'sourceV3':rel(v3_path),'sourceV3Sha256':sha(v3_raw),
    'sourceRingOwnership':rel(BASE/'shoulder-ring-ownership.json'),'sourceRing':rel(ring_path),'sourceRingSha256':sha(ring_raw),
    'twoContacts':poses,'commonArmScale':.18,'nearShoulder':[262.5,359.5],'farShoulder':[334,360],
    'fixedV3HeadTorsoLegMatricesUnchanged':True,'sameArmBindBothContacts':True,
    'oldRectPassRemoved':True,'originalSourcePngsEdited':False,'newAiImageCount':0,
    'oneRenderBatch':True,'finalSamePointRepair':True,'perPoseAlphaBboxFit':False,'mirroring':False,'componentWarping':False,
    'sourceNativeTimingMs':None,'worldRoot':None,'gameCallerRootModified':False,'nativeFrameOffsetModified':False,
    'actuallyViewed':False,'staticBindAccepted':False,'completeAnimation':False,'runtimeAdopted':False}
save(BASE/'proposal.json',proposal)
print(json.dumps({'nativeBoard':rel(board_path),'smallBoard':rel(small_board),'farShoulder':[334,360],
    'armScale':.18,'fixedV3Unchanged':True,'newAiImageCount':0,'oneBatch':True}))
