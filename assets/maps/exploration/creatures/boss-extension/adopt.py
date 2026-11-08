"""Persist one real generated master and its own bounded-batch index."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];IMAGE=Path('D:/work/image')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ident=int(sys.argv[1]);host=Path(sys.argv[2]);target=OUT/f'{ident}-master-v1.png';prompt=OUT/f'{ident}.prompt.txt';mapping_path=OUT/'identity-mapping.json'
mapping=json.loads(mapping_path.read_text(encoding='utf-8'));identity=next(x for x in mapping['mappedIdentities']if x['entityId']==ident)
assert ident in [30006,30009,30012,30014]and prompt.is_file()
if target.exists():assert sha(target)==sha(host)
else:shutil.copyfile(host,target)
with Image.open(target)as im:
 im.load();width,height=im.size;mode=im.mode;alpha=list(im.convert('RGBA').getchannel('A').getextrema())
refs=[(IMAGE/'designs/mail-ui-v1/01-mail-event.png','primary Daoist chibi hand-painted style'),(IMAGE/'designs/team-ui-v2/team-ui-v2.png','primary Daoist chibi hand-painted style'),(ROOT/'assets/characters/daoist-child.png','own character oversized-head/short-body proportions and finish only; not identity')]
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host output file last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),'width':width,'height':height,'format':'PNG','mode':mode,'alphaExtrema':alpha,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'promptFile':prompt.relative_to(ROOT).as_posix(),'referenced_image_paths':[str(p)for p,_ in refs],'size':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed image tool exposes no model/quality selector and returns no verifiable model/quality metadata.','evidence':{'hostOutputFile':str(host),'returnedFields':['image_url','output_hint'],'officialCheckDate':'2026-10-28','officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md','apiOrCliUsed':False},'prompt':prompt.relative_to(ROOT).as_posix(),'references':[{'file':str(p),'sha256':sha(p),'role':role,'actuallyAttached':True}for p,role in refs],'identityMapping':mapping_path.relative_to(ROOT).as_posix(),'entityId':ident,'entityIdNamespace':mapping['entityIdNamespace'],'entityClass':'boss','projectOriginalChineseIdentityName':identity['projectOriginalChineseIdentityName'],'originalIdentityReproductionClaimed':False,'staticMasterOnly':True,'resampled':False,'accepted':False,'inGameAccepted':False}
save(Path(str(target)+'.generation.json'),record)
art_path=OUT/'art.json';art=json.loads(art_path.read_text(encoding='utf-8'))if art_path.exists()else{'schemaVersion':1,'scope':'four independent source-confirmed Boss static masters; own original appearance','fullSetStaticComplete':False,'fullSetActionsComplete':False,'masters':[]}
item={'entityId':ident,'entityClass':'boss','originalName':None,'projectOriginalChineseIdentityName':identity['projectOriginalChineseIdentityName'],'file':record['file'],'sha256':record['sha256'],'width':width,'height':height,'generationRecord':record['file']+'.generation.json','identityMappingRecord':mapping_path.relative_to(ROOT).as_posix(),'sourceMapCount':identity['occurrenceMapCount'],'alphaExtrema':alpha,'accepted':False,'runtimeIntegrated':False,'actionsProduced':[],'staticMasterOnly':True,'status':'original-static-master-candidate-awaiting-identity-scale-and-in-game-validation'}
assert ident not in [p['entityId']for p in art['masters']];art['masters'].append(item);save(art_path,art)
print(json.dumps({'id':ident,'file':record['file'],'nativeSize':[width,height],'alphaExtrema':alpha,'masterCount':len(art['masters']),'staticMasterOnly':True,'accepted':False}))
