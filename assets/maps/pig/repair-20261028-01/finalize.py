"""Persist this three-target generation and export only the improved two pieces."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,shutil,sys,subprocess
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;IMAGE=Path('D:/work/image')
host=Path(sys.argv[1]);target=OUT/'repair-master.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not target.exists();shutil.copyfile(host,target)
with Image.open(target)as im:im.load();width,height=im.size;mode=im.mode;alpha=list(im.getchannel('A').getextrema())
refs=[OUT/'source-structure.png',IMAGE/'designs/mail-ui-v1/01-mail-event.png',IMAGE/'designs/team-ui-v2/team-ui-v2.png',OUT/'current-own-reference.png']
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),'width':width,'height':height,'mode':mode,'alphaExtrema':alpha,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'promptFile':(OUT/'prompt.txt').relative_to(ROOT).as_posix(),'referenced_image_paths':[str(p)for p in refs],'size':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host does not expose model/quality selectors or verifiable actual return metadata.','hostOutputFile':str(host),'references':[{'file':str(p),'sha256':sha(p),'actuallyAttached':True}for p in refs],'prompt':'assets/maps/pig/repair-20261028-01/prompt.txt','officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md','resampled':False,'accepted':False,'scope':'three source-structure-preserving original prop repairs; mother is native; exports separately cropped/resampled'}
save(Path(str(target)+'.generation.json'),record)
before=json.loads((OUT/'before.json').read_text(encoding='utf-8'))
for item in before['items']:
    current=json.loads((ROOT/item['currentArtManifest']).read_text(encoding='utf-8'))
    old=next(p for p in current['pieces']if p['elementId']==item['elementId'])
    assert old['file']==item['currentPiece']['file'] and old['sha256']==item['currentPiece']['sha256'], 'Target changed after repair context; do not overwrite newer work.'
specs=[{'family':'pig','source':record['file'],'items':[{'elementId':9012,'name':'wooden-crate-v3','rect':[0,0,512,620],'mappingNotes':'Source42x52 tall front crate structure repainted; unchanged footprint/GridAttr/offset; before.json pins prior candidate.'}]},
       {'family':'bun','source':record['file'],'items':[{'elementId':8016,'name':'gate-up-panel-v2','rect':[1024,0,1536,620],'mappingNotes':'Source40x35 with raised placard and filled lower panel; top gap open, downward triangle preserved; original offset[0,-5] unchanged.'}]}]
for spec in specs:
    path=OUT/(spec['family']+'-export.json');save(path,spec)
    subprocess.run([sys.executable,str(ROOT/'scripts/export-map-art-batch.py'),str(path.relative_to(ROOT))],cwd=ROOT,check=True)
save(OUT/'selection.json',{'source':record['file'],'targets':[{'elementId':9012,'selected':True,'newFile':'assets/maps/pig/pieces/9012-wooden-crate-v3.png','formalGeometryAccepted':False},{'elementId':8015,'selected':False,'reason':'new visible aspect ratio is worse than current approximately9.96%; retain existing gate-down.png and make second focused attempt'},{'elementId':8016,'selected':True,'newFile':'assets/maps/bun/pieces/8016-gate-up-panel-v2.png','formalGeometryAccepted':False}], 'onlyThreeTargetsInspected':True,'fullFamilyQA':False})
