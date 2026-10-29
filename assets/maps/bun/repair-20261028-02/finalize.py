"""Persist the two-gate native generation and uniformly export this batch only."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,shutil,sys,subprocess
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;IMAGE=Path('D:/work/image')
host=Path(sys.argv[1]);target=OUT/'repair-master.png';assert not target.exists();shutil.copyfile(host,target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with Image.open(target)as im:im.load();width,height=im.size;mode=im.mode;alpha=list(im.getchannel('A').getextrema())
refs=[OUT/'source-structure.png',IMAGE/'designs/mail-ui-v1/01-mail-event.png',IMAGE/'designs/team-ui-v2/team-ui-v2.png',ROOT/'assets/maps/pig/repair-20261028-01/repair-master.png']
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),'width':width,'height':height,'mode':mode,'alphaExtrema':alpha,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'promptFile':(OUT/'prompt.txt').relative_to(ROOT).as_posix(),'referenced_image_paths':[str(p)for p in refs],'size':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host does not expose model/quality selectors or verifiable actual return metadata.','hostOutputFile':str(host),'references':[{'file':str(p),'sha256':sha(p),'actuallyAttached':True}for p in refs],'prompt':(OUT/'prompt.txt').relative_to(ROOT).as_posix(),'officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md','resampled':False,'accepted':False,'scope':'two source-structure-preserving original gate repairs; native mother, separately cropped/resampled exports'}
save(Path(str(target)+'.generation.json'),record)
art=json.loads((ROOT/'assets/maps/bun/art.json').read_text(encoding='utf-8'))
before=[p for p in art['pieces']if p['elementId']in[8015,8016]];save(OUT/'before.json',before)
assert next(p for p in before if p['elementId']==8015)['file']=='assets/maps/bun/pieces/8015-gate-down.png'
assert next(p for p in before if p['elementId']==8016)['file']=='assets/maps/bun/pieces/8016-gate-up-panel-v2.png'
spec={'family':'bun','source':record['file'],'items':[
    {'elementId':8015,'name':'gate-down-v2','rect':[0,0,512,600],'mappingNotes':'Lowered placard, top panel filled, bottom center open; exact source40x35, footprint/GridAttr/offset retained.'},
    {'elementId':8016,'name':'gate-up-panel-v3','rect':[512,0,1024,600],'mappingNotes':'Raised placard, lower panel filled, top center open; source40x35 and original map offset[0,-5] retained.'}]}
save(OUT/'export.json',spec)
subprocess.run([sys.executable,str(ROOT/'scripts/export-map-art-batch.py'),str((OUT/'export.json').relative_to(ROOT))],cwd=ROOT,check=True)
art=json.loads((ROOT/'assets/maps/bun/art.json').read_text(encoding='utf-8'))
after=[p for p in art['pieces']if p['elementId']in[8015,8016]]
save(OUT/'selection.json',{'onlyTwoTargetsInspected':True,'fullFamilyQA':False,'before':before,'after':after,'formalGeometryAccepted':False,'samePointAttemptCountThisRepairRound':2,'note':'Select improved candidates; visible outline, gap placement and in-game anchors still need acceptance. Do not claim dimensions/logic changed.'})
