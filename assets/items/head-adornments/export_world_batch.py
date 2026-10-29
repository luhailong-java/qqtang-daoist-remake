"""Bounded 1–6 frame exports; preserve source canvas, order and raw offsets."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
spec_path=ROOT/sys.argv[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=read(spec_path);assert 1<=len(spec['frames'])<=6
source=ROOT/spec['source'];mother=Image.open(source).convert('RGBA');w,h=mother.size
manifest=OUT/'world-art.json'
doc=read(manifest)if manifest.exists()else{'schemaVersion':1,'status':'world-frame-candidates-not-runtime-approved','items':[]}
reports=[]
for n,item in enumerate(spec['frames']):
    ident=item['itemId'];idx=item['sourceFrameIndex']
    contract=read(OUT/f'references/world/{ident}/source-contract.json')
    original=contract['frames'][idx]
    rect=item.get('manualRect',[round(n%3*w/3),round(n//3*h/2),round((n%3+1)*w/3),round((n//3+1)*h/2)])
    crop=mother.crop(rect);bbox=crop.getchannel('A').point(lambda a:255 if a>=16 else 0).getbbox();assert bbox
    native_w,native_h=original['nativeFrameSize'];target_w,target_h=native_w*4,native_h*4
    ob=original['sourceAlphaBBoxAt16'];region_w=(ob[2]-ob[0])*4;region_h=(ob[3]-ob[1])*4
    content=crop.crop(bbox);scale=min(region_w/content.width,region_h/content.height)
    new_size=(round(content.width*scale),round(content.height*scale))
    painted=content.convert('RGBa').resize(new_size,Image.Resampling.LANCZOS).convert('RGBA')
    placement=(ob[0]*4+(region_w-new_size[0])//2,ob[1]*4+region_h-new_size[1])
    output=Image.new('RGBA',(target_w,target_h));output.alpha_composite(painted,placement)
    target=OUT/f'world/{ident}/frame-{idx:03d}-{spec["version"]}.png';target.parent.mkdir(parents=True,exist_ok=True);output.save(target)
    source_aspect=(ob[2]-ob[0])/(ob[3]-ob[1]);paint_aspect=content.width/content.height;error=abs(paint_aspect/source_aspect-1)
    record={'itemId':ident,'sourceFrameIndex':idx,'sourcePhaseIndex':idx,'directionIndex':original.get('directionIndex',0),'directionSemantic':None,
            'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':target_w,'height':target_h,
            'logicalFrameSize':[native_w,native_h],'exportDensity':4,'frameOffsetRaw':original['frameOffsetRaw'],
            'frameOffsetPxAtDensity4':[q*4 for q in original['frameOffsetRaw']],
            'sourceReference':{'file':original['file'],'sha256':original['sha256'],'record':original['file']+'.source.json'},
            'derivedFrom':{'file':spec['source'],'sha256':sha(source),'generationRecord':spec['source']+'.generation.json'},
            'operation':{'type':'crop-uniform-fit-original-world-alpha-envelope','newModelGeneration':False,
                         'sourceCellRectLTRB':rect,'generatedContentBBoxAt16':list(bbox),
                         'sourceLogicalAlphaBBoxAt16':ob,'uniformScale':scale,'placementPx':list(placement),
                         'resampler':'premultiplied-alpha LANCZOS','registration':'source alpha envelope centred X and bottom aligned Y; raw frame offset untouched'},
            'frameDurationMs':None,'loop':None,'geometryAccepted':False,'visualAccepted':False,'runtimeAdopted':False,'accepted':False,
            'qa':{'sourceVisibleAspect':source_aspect,'generatedVisibleAspect':paint_aspect,'relativeAspectDeviation':error},
            'warnings':['native head-layer origin, sign and actor attachment unverified','source timing not supplied; do not invent frame duration',
                        'per-frame source phase, silhouette and alpha edges await review']+(['visible aspect differs by more than 10%']if error>.1 else[])}
    save(Path(str(target)+'.provenance.json'),record)
    entry=next((e for e in doc['items']if e['itemId']==ident),None)
    if entry is None:
        entry={'itemId':ident,'sourceName':contract['sourceName'],'sourceDescription':contract['sourceDescription'],
               'sourceContract':f'assets/items/head-adornments/references/world/{ident}/source-contract.json',
               'sourceSha256':contract['sourceSha256'],'sourceDeclaredCanvas':contract['sourceDimg']['declaredCanvas'],
               'sourceHeaderUnknownWordsAt24And28':contract['sourceDimg'].get('unknownHeaderWordsAt24And28'),
               'sourceFrameOrder':contract['frameOrder'],'sourceFrameCount':len(contract['frames']),
               'directions':contract['directions'],'directionSemantic':None,'frameDurationsMs':None,'loop':None,
               'sourceStandWalkByteIdentical':True,'stateAliasEvidence':'exact source stand/walk bytes and SHA equal; same candidate frame list may represent both',
               'sourceStates':['stand','walk'],'frames':[],'accepted':False,'runtimeAdopted':False,
               'headAttachmentContract':'assets/items/head-adornments/docs/HEAD_ATTACHMENT_CONTRACT.md'}
        doc['items'].append(entry)
    entry['frames']=[f for f in entry['frames']if f['sourceFrameIndex']!=idx]+[record]
    entry['frames'].sort(key=lambda f:f['sourceFrameIndex']);entry['candidateFrameCoverage']=len(entry['frames'])
    entry['sourceDeclaredFrameCoverageComplete']=len(entry['frames'])==entry['sourceFrameCount']
    entry['animationTimingKnown']=False;entry['completeAnimationAccepted']=False
    reports.append({'itemId':ident,'frameIndex':idx,'target':[target_w,target_h],'rawOffset':original['frameOffsetRaw'],'visibleAspectDeviation':error})
doc['items'].sort(key=lambda e:e['itemId']);save(manifest,doc)
save(OUT/f'exports/{spec["version"]}.world-observations.json',{'scope':'current bounded frame batch only, not full QA','frames':reports,'accepted':False})
print(json.dumps({'worldFrameCandidatesInCurrentBatch':reports,'accepted':0}))
