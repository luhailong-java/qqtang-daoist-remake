"""Register builtin output; crop at ownership gaps and preserve shared root/scale.

No pose drawing, no mirrors, no per-frame bounding-box normalization.
"""
from pathlib import Path
from PIL import Image
import argparse,datetime,hashlib,json,sys,numpy as np

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('spec')
args=parser.parse_args()
spec=json.loads((ROOT/args.spec).read_text(encoding='utf-8-sig'))
sheet=ROOT/spec['file'];image=Image.open(sheet).convert('RGBA')
if image.size!=(2048,768):raise ValueError('Registration contract expects native2048x768; revise spec explicitly for other sizes')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
alpha=np.asarray(image.getchannel('A'));cuts=[0];separators=[]
for nominal in [512,1024,1536]:
    candidates=[x for x in range(nominal-64,nominal+65)if int(alpha[:,x].max())<=8]
    cut=min(candidates,key=lambda x:(abs(x-nominal),int(alpha[:,x].max()))) if candidates else nominal
    cuts.append(cut);separators.append({'nominal':nominal,'ownershipCut':cut,'safe':bool(candidates),'maxAlpha':int(alpha[:,cut].max()),'visiblePixelsAlphaGt8':int(np.sum(alpha[:,cut]>8))})
cuts.append(2048)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
references=[{'path':ref['path'],'role':ref['role'],'sha256':sha(Path(ref['path']))}for ref in spec['references']]
record={'schemaVersion':1,'file':spec['file'],'sha256':sha(sheet),'generatedAt':now,
 'timeEvidence':'UTC registration after builtin tool return, not provider creation metadata','width':image.width,'height':image.height,
 'format':'PNG','mode':'RGBA','alphaExtrema':list(image.getchannel('A').getextrema()),'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image',
 'configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[r['path']for r in references]},
 'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有model/quality选择器，返回未披露可核实型号或质量。',
 'prompt':spec['prompt'],'promptSha256':sha(ROOT/spec['prompt']),'references':references,
 'evidence':{'hostSource':spec['hostSource'],'returnedFields':['image_url','output_hint'],'selectorsExposed':False},
 'editTarget':spec.get('editTarget'),'review':spec['review'],'status':'internal_visual_candidate'if spec.get('candidate')else'not_passed',
 'clientApproved':False,'userAccepted':False}
write(Path(str(sheet)+'.generation.json'),record)
source_edges={name:int(np.sum(edge>8))for name,edge in [('top',alpha[0,:]),('bottom',alpha[-1,:]),('left',alpha[:,0]),('right',alpha[:,-1])]}
if not all(item['safe']for item in separators) or any(source_edges.values()):
    record['status']='not_passed';record['review']['sourceEdgePixelsAlphaGt8']=source_edges
    record['review']['failureReasons']=list(set(record['review'].get('failureReasons',[])+['source_visible_halo_or_clipping_prevents_safe_ownership_export']))
    write(Path(str(sheet)+'.generation.json'),record)
    qa=sheet.parent/'qa';qa.mkdir(exist_ok=True)
    for name,colour in [('ivory','#f6f0df'),('dark','#192f31')]:
        composite=Image.new('RGBA',image.size,colour);composite.alpha_composite(image);target=qa/f'{sheet.stem}-{name}.png';composite.convert('RGB').save(target)
        write(Path(str(target)+'.source.json'),{'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'derivedFrom':{'file':spec['file'],'sha256':sha(sheet),'generationRecord':spec['file']+'.generation.json'},'operation':'alpha diagnostic composition, not runtime art'})
    write(sheet.with_suffix('.review.json'),{'status':'not_passed','review':record['review'],'sourceSeparators':separators,'sourceEdgePixelsAlphaGt8':source_edges,'runtimeEnabled':False})
    print(json.dumps({'file':spec['file'],'status':'not_passed','exportedFrames':0,'reason':'unsafe source alpha/edge','sourceSeparators':separators}));sys.exit(0)
common=984;scale=256/common;ground=722 if spec['character']=='daoist-child' else 729
anchor=[128,(ground+108)*scale];frames=[];checks=[];output=sheet.parent/('frames-'+sheet.stem.removeprefix('walk-'))/spec['direction'];output.mkdir(parents=True,exist_ok=True)
contact=Image.new('RGB',(1024,256),'#f6f0df')
for index in range(4):
    rect=[cuts[index],0,cuts[index+1],768];crop=image.crop(rect);root_x=256+512*index-cuts[index];placement=[492-root_x,108]
    canvas=Image.new('RGBA',(common,common));canvas.paste(crop,tuple(placement))
    frame=canvas.convert('RGBa').resize((256,256),Image.Resampling.LANCZOS).convert('RGBA');path=output/f'{index+1:02d}.png';frame.save(path)
    a=np.asarray(frame.getchannel('A'));ys,xs=np.where(a>8);edge=int(np.sum(a[0,:]>8)+np.sum(a[-1,:]>8)+np.sum(a[:,0]>8)+np.sum(a[:,-1]>8))
    if edge:raise ValueError('Visible sprite touches runtime canvas edge')
    bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    provenance={'schemaVersion':1,'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'derivedAt':now,
     'derivedFrom':{'file':spec['file'],'sha256':sha(sheet),'generationRecord':spec['file']+'.generation.json'},
     'operation':{'type':'ownership_crop_fixed_nominal_root_common_transparent_canvas_uniform_downscale','sourceSize':[2048,768],'cropLTRB':rect,
      'nominalCellRootX':root_x,'placementOnCommonCanvas':placement,'commonCanvas':[984,984],'scale':scale,
      'resampler':'LANCZOS premultiplied RGBa','output':[256,256],'perFrameSubjectFit':False,'mirror':False,'interpolatedPoses':False,'newGeneration':False},
     'anchor':anchor,'anchorStatus':'shared_character_root_candidate_not_client_approved','alphaExtrema':list(frame.getchannel('A').getextrema()),'alphaGt8BBox':bbox,
     'boundaryPixelsAlphaGt8':edge,'status':record['status'],'runtimeEnabled':False,'clientApproved':False,'review':spec['review']}
    write(Path(str(path)+'.source.json'),provenance)
    frames.append({'file':'./'+path.relative_to(ROOT).as_posix(),'sha256':sha(path),'provenance':'./'+path.relative_to(ROOT).as_posix()+'.source.json','warnings':['four_frame_loop_client_review_pending']})
    checks.append({'frame':index+1,'alphaGt8BBox':bbox,'boundaryPixelsAlphaGt8':edge})
    composite=Image.new('RGBA',(256,256),'#f6f0df');composite.alpha_composite(frame);contact.paste(composite.convert('RGB'),(index*256,0))
qa=sheet.parent/'qa';qa.mkdir(exist_ok=True);contact.save(qa/f'{sheet.stem}-runtime-contact.png')
for name,colour in [('ivory','#f6f0df'),('dark','#192f31')]:
    composite=Image.new('RGBA',image.size,colour);composite.alpha_composite(image);composite.convert('RGB').save(qa/f'{sheet.stem}-{name}.png')
for path in qa.glob(sheet.stem+'-*.png'):
    write(Path(str(path)+'.source.json'),{'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'derivedFrom':{'file':spec['file'],'sha256':sha(sheet),'generationRecord':spec['file']+'.generation.json'},'operation':'alpha diagnostic composite/contact montage, not runtime art'})
review={'status':record['status'],'runtimeEnabled':False,'clientApproved':False,'userAccepted':False,'review':spec['review'],'sourceSeparators':separators,'frameChecks':checks,'anchor':anchor,'sameScaleAcrossSelectedDirections':True,'wholeCanvasScale':scale}
write(sheet.with_suffix('.review.json'),review)
if spec.get('candidate'):
    manifest_path=BASE/'runtime-candidates.manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'));character=manifest['characters'][spec['character']]
    order=spec.get('sourceFrameOrder',[1,2,3,4]);clip={'frameMs':120,'durationMs':480,'loop':True,'frameCount':4,'anchor':anchor,'anchorStatus':'shared_character_client_candidate','timingStatus':'trial_not_approved',
        'frames':[frames[i-1]for i in order],'sourceFrameOrder':order,'generationRecord':'./'+spec['file']+'.generation.json','warnings':['four_frame_loop_client_review_pending']}
    character['clips'].setdefault('run',{})[spec['direction']]=clip;character['missingDirections']=[d for d in 'NESW'if d not in character['clips']['run']]
    character['status']='client_candidate_partial_actions';write(manifest_path,manifest)
print(json.dumps({'file':spec['file'],'status':record['status'],'frames':len(frames),'anchor':anchor,'cuts':cuts,'review':spec['review']},ensure_ascii=True))
