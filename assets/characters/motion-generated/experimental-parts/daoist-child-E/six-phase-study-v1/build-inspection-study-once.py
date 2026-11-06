"""Reuse4 exact PNGs, assemble only2 new combinations; inspection-only."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,copy
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
if (BASE/'manifest.json').exists()or(BASE/'frames627'/'02-nearB-farRaised.png').exists():
    raise RuntimeError('The single inspection study already exists; do not rebuild/iterate')
FULL=BASE/'frames627';SMALL=BASE/'frames96';FULL.mkdir(exist_ok=True);SMALL.mkdir(exist_ok=True)
rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contact_path=BASE.parent/'whole-arm-v1'/'bind-static-v2'/'proposal.json';cb=contact_path.read_bytes();contacts=json.loads(cb)
passing_path=BASE.parent/'passing-leg-v1'/'bind-static-v1'/'proposal.json';pb=passing_path.read_bytes();passing=json.loads(pb)
A=next(p for p in contacts['twoContacts']if p['contact']=='A');B=next(p for p in contacts['twoContacts']if p['contact']=='B')
P1=next(p for p in passing['twoPoses']if p['pose']=='P1');P2=next(p for p in passing['twoPoses']if p['pose']=='P2')
pick=lambda pose,ident:copy.deepcopy(next(n for n in pose['nodes']if n['id']==ident))
fixed_ids=['far_L_whole_gourd','head','torso_pelvis','near_R_whole']
fixed=[pick(A,i)for i in fixed_ids];ring=copy.deepcopy(A['newShoulderOcclusion'])
for pose in [B,P1,P2]:
    for reference in fixed:
        other=next(n for n in pose['nodes']if n['id']==reference['id'])
        if other['imageMatrix']!=reference['imageMatrix']or other['sha256']!=reference['sha256']:
            raise ValueError('Fixed upper source is no longer equal; stop this composition')
def check(file,expected):
    p=ROOT/file;raw=p.read_bytes()
    if sha(raw)!=expected:raise ValueError('Source bytes changed:'+file)
    return p,raw
def transform(im,m):
    a,b,c,d,e,f=m
    if b or c or a!=d or a<=0:raise ValueError('Unexpected rotation/mirror/warp')
    return im.convert('RGBa').transform((627,627),Image.Transform.AFFINE,
        (1/a,0,-e/a,0,1/d,-f/d),resample=Image.Resampling.BICUBIC).convert('RGBA')
def render(nodes):
    canvas=Image.new('RGBA',(627,627),(0,0,0,0))
    for n in sorted(nodes,key=lambda n:n['layer']):
        p,_=check(n['file'],n['sha256']);im=Image.open(p).convert('RGBA');r=transform(im,n['imageMatrix']);canvas.alpha_composite(r);im.close();r.close()
    p,_=check(ring['file'],ring['sha256']);im=Image.open(p).convert('RGBA');r=transform(im,ring['cutoutImageMatrix']);canvas.alpha_composite(r);im.close();r.close()
    return canvas
specs=[
 {'index':0,'id':'00-contact-A','description':'ContactA / nearF + farB','reuse':A,'near':'near_R_forward','far':'far_L_backward','proposal':rel(contact_path),'proposalSha':sha(cb)},
 {'index':1,'id':'01-passing-P1','description':'P1 / near planted + far raised','reuse':P1,'near':'near_R_planted','far':'far_L_raised','proposal':rel(passing_path),'proposalSha':sha(pb)},
 {'index':2,'id':'02-nearB-farRaised','description':'New assembly / nearB + far raised','newNodes':[pick(B,'near_R_backward'),pick(P1,'far_L_raised')],
  'near':'near_R_backward','far':'far_L_raised','inheritedFrom':[{'proposal':rel(contact_path),'sha256':sha(cb),'pose':'B','node':'near_R_backward'},
   {'proposal':rel(passing_path),'sha256':sha(pb),'pose':'P1','node':'far_L_raised'}]},
 {'index':3,'id':'03-contact-B','description':'ContactB / nearB + farF','reuse':B,'near':'near_R_backward','far':'far_L_forward','proposal':rel(contact_path),'proposalSha':sha(cb)},
 {'index':4,'id':'04-passing-P2','description':'P2 / near raised + far planted','reuse':P2,'near':'near_R_raised','far':'far_L_planted','proposal':rel(passing_path),'proposalSha':sha(pb)},
 {'index':5,'id':'05-nearRaised-farB','description':'New assembly / near raised + farB','newNodes':[pick(P2,'near_R_raised'),pick(A,'far_L_backward')],
  'near':'near_R_raised','far':'far_L_backward','inheritedFrom':[{'proposal':rel(passing_path),'sha256':sha(pb),'pose':'P2','node':'near_R_raised'},
   {'proposal':rel(contact_path),'sha256':sha(cb),'pose':'A','node':'far_L_backward'}]},
]
frames=[]
for spec in specs:
    dest=FULL/(spec['id']+'.png');small_dest=SMALL/(spec['id']+'.png')
    if 'reuse'in spec:
        pose=spec['reuse'];source,raw=check(pose['output'],pose['sha256']);dest.write_bytes(raw)
        source_small,small_raw=check(pose['smallOutput'],pose['smallSha256']);small_dest.write_bytes(small_raw)
        nodes=copy.deepcopy(pose['nodes'])
        operation='Exact encoded PNG byte reuse, not re-rendered, resized, optimized or new model output.'
        evidence={'source':rel(source),'sourceSha256':pose['sha256'],'sourceSmall':rel(source_small),'sourceSmallSha256':pose['smallSha256'],
            'sourceProposal':spec['proposal'],'sourceProposalSha256':spec['proposalSha'],'byteIdenticalReuse':True}
    else:
        nodes=copy.deepcopy(fixed)+copy.deepcopy(spec['newNodes'])
        canvas=render(nodes);canvas.save(dest)
        small=canvas.convert('RGBa').resize((96,96),Image.Resampling.LANCZOS).convert('RGBA');small.save(small_dest);small.close();canvas.close()
        operation='One of exactly2 new deterministic combinations of existing painted parts with every original image matrix and layer inherited unchanged. No new AI, image edit, fit, root change or near/far relabel.'
        evidence={'inheritedLegs':spec['inheritedFrom'],'fixedUpperProposal':rel(contact_path),'fixedUpperProposalSha256':sha(cb),'byteIdenticalReuse':False}
    record={'index':spec['index'],'file':rel(dest),'sha256':sha(dest.read_bytes()),'size':[627,627],
        'smallFile':rel(small_dest),'smallSha256':sha(small_dest.read_bytes()),'smallSize':[96,96],
        'description':spec['description'],'nearPart':spec['near'],'farPart':spec['far'],
        'contentMotionKind':'assembled_static_pose_sequence_study','operation':operation,'sources':evidence,
        'nodes':nodes,'sameTorsoRing':ring,'newModelGeneration':False,'nativeTimingMs':None,'worldRoot':None,
        'inspectionDurationMs':120,'loop':False,'sourceCorrespondence':False,'runtimeAccepted':False,'completeWalk':False}
    save(dest.with_suffix('.png.source.json'),record)
    save(small_dest.with_suffix('.png.source.json'),{'file':rel(small_dest),'sha256':record['smallSha256'],'size':[96,96],
        'derivedFrom':{'file':rel(dest),'sha256':record['sha256']},
        'operation':'Original96 encoded bytes reused without processing'if evidence['byteIdenticalReuse']else'Whole627 canvas uniform PMA LANCZOS resize96/627; no bbox fit.',
        'originalSmallSource':evidence.get('sourceSmall'),'newModelGeneration':False,'runtimeAccepted':False})
    frames.append(record)

# Contact sheets inspect existing saved frames; the four source composites were not re-rendered.
cell_h=659;board=Image.new('RGB',(1881,1318),(248,242,225));d=ImageDraw.Draw(board)
board96=Image.new('RGB',(288,232),(248,242,225));d96=ImageDraw.Draw(board96)
gif_images=[]
for record in frames:
    i=record['index'];im=Image.open(ROOT/record['file']).convert('RGBA');bg=Image.new('RGBA',(627,627),(248,242,225,255));bg.alpha_composite(im)
    x=(i%3)*627;y=(i//3)*cell_h
    board.paste(bg.convert('RGB'),(x,y+32));d.text((x+10,y+8),str(i)+' '+record['description'],fill='#244f44')
    im.close();bg.close()
    small=Image.open(ROOT/record['smallFile']).convert('RGBA');sb=Image.new('RGBA',(96,96),(248,242,225,255));sb.alpha_composite(small)
    rgb=sb.convert('RGB');board96.paste(rgb,((i%3)*96,(i//3)*116));d96.text(((i%3)*96+3,(i//3)*116+100),str(i),fill='#244f44')
    gif_frame=rgb.copy();gd=ImageDraw.Draw(gif_frame);gd.text((2,1),'F'+str(i),fill='#244f44');gif_images.append(gif_frame)
    small.close();sb.close()
sheet=BASE/'six-poses-627-contact.png';board.save(sheet)
sheet96=BASE/'six-poses-96-contact.png';board96.save(sheet96)
# One shared GIF palette, fixed ivory96 canvas. No loop extension: plays one inspection pass.
palette_source=Image.new('RGB',(576,96),(248,242,225))
for i,im in enumerate(gif_images):palette_source.paste(im,(i*96,0))
palette=palette_source.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
paletted=[im.quantize(palette=palette,dither=Image.Dither.NONE)for im in gif_images]
gif_path=BASE/'six-poses-inspection-120ms.gif'
paletted[0].save(gif_path,save_all=True,append_images=paletted[1:],duration=120,disposal=2,optimize=False)
for p,size,op in [(sheet,[1881,1318],'Six unscaled627 static frames placed3x2 with32px label strips; ivory composite contact sheet only.'),
    (sheet96,[288,232],'Six original96 frames placed3x2 with20px labels; no frame-specific scaling.'),
    (gif_path,[96,96],'Six existing96 frames flattened on ivory, one shared256-color palette,120ms each, no loop extension; diagnostic beat only, not native timing.')]:
    save(p.with_suffix(p.suffix+'.source.json'),{'file':rel(p),'sha256':sha(p.read_bytes()),'size':size,
        'derivedFrom':[{'file':q['smallFile']if p==gif_path or p==sheet96 else q['file'],'sha256':q['smallSha256']if p==gif_path or p==sheet96 else q['sha256']}for q in frames],
        'operation':op,'newModelGeneration':False,'nativeTimingMs':None,'inspectionFrameDurationMs':120 if p==gif_path else None,
        'loop':False,'sourceCorrespondence':False,'runtimeAccepted':False})
manifest={'schemaVersion':1,'projectDisplayName':'灵葫大作战','createdAtUTC':datetime.now(timezone.utc).isoformat(),
    'contentMotionKind':'assembled_static_pose_sequence_study','frameCount':6,'frames':frames,
    'exactByteReused627Frames':4,'exactByteReused96Frames':4,'newDeterministicComposites':2,'newImagegenCalls':0,
    'existingSourceAtlasCountScope':'Existing parts/whole-leg/whole-arm/passing paintings only; six slots are not six model originals.',
    'fixedUpperAndRingUnchanged':True,'originalImageMatricesInherited':True,'perPoseBboxFit':False,'mirroring':False,'newNearFarSwap':False,
    'inspectionGif':{'file':rel(gif_path),'sha256':sha(gif_path.read_bytes()),'canvas':[96,96],'durationMsPerFrame':120,
        'nativeTiming':False,'loopExtension':None,'playsOnce':True,'dynamicClientReviewPerformed':False},
    'contactSheet':rel(sheet),'smallContactSheet':rel(sheet96),
    'nativeTimingMs':None,'worldRoot':None,'loop':False,'sourceCorrespondence':False,'runtimeAccepted':False,
    'staticAccepted':False,'completeWalk':False,'actuallyViewedContactSheets':False,
    'sourceMappingCaution':'Proposed own six-slot order only, not the nativeE six frames; phase4 source identity/contact conflict remains pending.',
    'browserOrTestsOrBuildExecuted':False,'formalRigCreated':False,'sourcePngsOrAlphaModified':False}
save(BASE/'manifest.json',manifest)
print(json.dumps({'manifest':rel(BASE/'manifest.json'),'nativeContact':rel(sheet),'smallContact':rel(sheet96),'gif':rel(gif_path),
    'exactByteReused627':4,'newComposites':2,'newImagegenCalls':0,'loop':False,'nativeTimingMs':None}))
