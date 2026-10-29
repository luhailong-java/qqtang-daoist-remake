"""Persist one explicitly inspected AI edit, preserving independent edit evidence."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent/'creatures'
IMAGE = Path('D:/work/image')
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ident = int(sys.argv[1]); host = Path(sys.argv[2]); version = sys.argv[3]
selected = len(sys.argv)<5 or sys.argv[4]!='not-selected'
assert version in ['v2','v3']
target = OUT/f'{ident}-master-{version}.png'
source = OUT/f'{ident}-master-v1.png'
prompt = OUT/f'{ident}.repair-{version}.prompt.txt'
assert source.is_file() and prompt.is_file() and not target.exists()
shutil.copyfile(host,target)
with Image.open(target) as im:
    im.load(); size=im.size; mode=im.mode; alpha=list(im.convert('RGBA').getchannel('A').getextrema())
refs = [(source,'exact current original master: identity, pose, silhouette and hand-painted details'),
        (IMAGE/'designs/mail-ui-v1/01-mail-event.png','primary Daoist chibi hand-painted style'),
        (IMAGE/'designs/team-ui-v2/team-ui-v2.png','primary Daoist chibi hand-painted style'),
        (ROOT/'assets/characters/daoist-child.png','own head/body proportions and finish only')]
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),
        'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),
        'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),
        'width':size[0],'height':size[1],'format':'PNG','mode':mode,'alphaExtrema':alpha,
        'operation':'AI-edit of existing original master; not deterministic crop/scale',
        'sourceFile':source.relative_to(ROOT).as_posix(),'sourceSHA256':sha(source),'sourceGenerationRecord':source.relative_to(ROOT).as_posix()+'.generation.json',
        'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image',
        'configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),
        'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'promptFile':prompt.relative_to(ROOT).as_posix(),'referenced_image_paths':[str(p)for p,_ in refs],'size':None},
        'actualModel':None,'actualQuality':None,
        'unverifiedReason':'Host image tool exposes no model/quality selector or verifiable actual model/quality metadata.',
        'evidence':{'hostOutputFile':str(host),'officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md','apiOrCliUsed':False},
        'references':[{'file':str(p),'sha256':sha(p),'role':role,'actuallyAttached':True}for p,role in refs],
        'prompt':prompt.relative_to(ROOT).as_posix(),'identityMapping':'assets/maps/exploration/creatures/identity-mapping.json',
        'entityId':ident,'staticMasterOnly':True,'resampled':False,'accepted':False,'inGameAccepted':False}
save(Path(str(target)+'.generation.json'),record)
path=OUT/'art.json'; art=json.loads(path.read_text(encoding='utf-8')); item=next(p for p in art['masters']if p['entityId']==ident)
if selected:
    item.setdefault('previousCandidates',[]).append({k:item[k]for k in ['file','sha256','generationRecord']})
    item.update({'file':record['file'],'sha256':record['sha256'],'width':size[0],'height':size[1],'alphaExtrema':alpha,'generationRecord':record['file']+'.generation.json','accepted':False,'status':'AI-repair-static-candidate-awaiting-targeted-alpha-and-in-game-validation'})
else:
    item.setdefault('unselectedAIRepairs',[]).append({'file':record['file'],'sha256':record['sha256'],'generationRecord':record['file']+'.generation.json','reason':'displayed repair did not resolve the target issue; retain best current candidate'})
save(path,art)
print(json.dumps({'entityId':ident,'nativeSize':size,'alphaExtrema':alpha,'repairFile':record['file'],'selected':selected,'currentCandidate':item['file'],'masterCount':len(art['masters']),'accepted':False}))
