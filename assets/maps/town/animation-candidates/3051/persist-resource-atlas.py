"""Record one explicitly generated single-row map-frame atlas; no global edits."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,re
ROOT=Path(__file__).resolve().parents[5];IMAGE=Path('D:/work/image')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--element',type=int,required=True);p.add_argument('--version',required=True);p.add_argument('--host',type=Path,required=True);p.add_argument('--previous');p.add_argument('--family',required=True);p.add_argument('--batch')
a=p.parse_args();OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}'
if a.batch:
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',a.batch)
    OUT=OUT/a.batch
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'))
indices=[x['frameIndex']for x in context['sourceFrames']if not x['structuralEmpty']and not x.get('fullyTransparentPixels')and x.get('exactVisibleAliasOfFrameIndex')is None]
assert indices and a.version in['v1','v2','v3']
own=ROOT/context['currentOwnMaster']['file'];structure=ROOT/context['referenceBoard']
style=[IMAGE/'designs/mail-ui-v1/01-mail-event.png',IMAGE/'designs/team-ui-v2/team-ui-v2.png']
previous=OUT/f'sequence-{a.previous}.png'if a.previous else None
refs=[previous,structure,own,*style]if previous else[own,structure,*style]
roles=['exact previous own atlas being AI-edited','actual source frame structure/reference','current own identity/material master','primary Daoist Q style','primary Daoist Q style']if previous else['current own identity/material master','actual source frame structure/reference','primary Daoist Q style','primary Daoist Q style']
target=OUT/f'sequence-{a.version}.png';assert not target.exists();shutil.copyfile(a.host,target)
atlas=Image.open(target).convert('RGBA');frames=[]
for col,index in enumerate(indices):
    left=round(col*atlas.width/len(indices));right=round((col+1)*atlas.width/len(indices))
    box=atlas.getchannel('A').crop((left,0,right,atlas.height)).point(lambda v:255 if v>8 else 0).getbbox();assert box
    source=next(x for x in context['sourceFrames']if x['frameIndex']==index);ratio=source['sourceFrameSize'][0]/source['sourceFrameSize'][1]
    frames.append({'sourceFrameIndex':index,'cellRect':[left,0,right,atlas.height],'localAlpha8BBox':list(box),
        'sourceFrameSize':source['sourceFrameSize'],'sourceFrameOffset':source['sourceFrameOffset'],
        'visibleAspectRatioRelativeError':abs((box[2]-box[0])/(box[3]-box[1])/ratio-1),
        'touchesNominalCellAlpha8':box[0]==0 or box[1]==0 or box[2]==right-left or box[3]==atlas.height})
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(a.host.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),
    'width':atlas.width,'height':atlas.height,'mode':'RGBA','alphaExtrema':list(atlas.getchannel('A').getextrema()),
    'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'promptFile':(OUT/f'prompt-{a.version}.txt').relative_to(ROOT).as_posix(),'referenced_image_paths':[str(x)for x in refs],'size':None},
    'actualModel':None,'actualQuality':None,'unverifiedReason':'Host tool exposes no model/quality selector or verifiable actual result metadata.',
    'hostOutputFile':str(a.host),'officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md',
    'references':[{'file':str(x),'sha256':sha(x),'role':role,'actuallyAttached':True}for x,role in zip(refs,roles)],
    'prompt':(OUT/f'prompt-{a.version}.txt').relative_to(ROOT).as_posix(),'operation':'AI-edit whole atlas'if previous else'new source-corresponding distinct frame atlas',
    'sourceFrameIndices':indices,'sourceContext':(OUT/'source-context.json').relative_to(ROOT).as_posix(),'resampled':False,'accepted':False,'runtimeIntegrated':False}
if previous:record['editedFrom']={'file':previous.relative_to(ROOT).as_posix(),'sha256':sha(previous),'generationRecord':str(previous.relative_to(ROOT))+'.generation.json'}
save(Path(str(target)+'.generation.json'),record)
check={'elementId':a.element,'version':a.version,'actualNativeAtlasSize':list(atlas.size),'alphaExtrema':record['alphaExtrema'],'representativeFrameIndices':indices,'frames':frames,'accepted':False}
save(OUT/f'native-check-{a.version}.json',check)
print(json.dumps(check,ensure_ascii=True))
