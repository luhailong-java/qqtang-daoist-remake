"""Save one native four-frame generation with exact references/parameters."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent;IMAGE=Path('D:/work/image')
version=sys.argv[1];host=Path(sys.argv[2]);assert version in['v1','v2','v3']
target=OUT/f'sequence-{version}.png';assert not target.exists();shutil.copyfile(host,target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
own=ROOT/'assets/maps/town/pieces/3050-dragon-lantern.png';structure=OUT/'four-source-structure.png'
style=[IMAGE/'designs/mail-ui-v1/01-mail-event.png',IMAGE/'designs/team-ui-v2/team-ui-v2.png']
previous='v2'if version=='v3'else'v1'
refs=[own,structure,*style]if version=='v1'else[OUT/f'sequence-{previous}.png',structure,own,*style]
roles={str(own):'existing own identity/material master; old narrow geometry is not accepted',str(structure):'all4 actual source frame positions, NN4x reference only'}
roles.update({str(p):'primary Daoist Q hand-painted style'for p in style})
if version!='v1':roles[str(OUT/f'sequence-{previous}.png')]='exact prior native four-frame atlas being AI edited'
with Image.open(target)as image:
    im=image.convert('RGBA');size=list(im.size);alpha=list(im.getchannel('A').getextrema());bounds=[]
    for index in range(4):
        columns=4 if version=='v3'else 2;rows=1 if version=='v3'else 2
        cell_w=im.width//columns;cell_h=im.height//rows
        x=(index%columns)*cell_w;y=(index//columns)*cell_h
        box=im.getchannel('A').crop((x,y,x+cell_w,y+cell_h)).point(lambda a:255 if a>8 else 0).getbbox()
        bounds.append({'frameIndex':index,'cellRect':[x,y,x+cell_w,y+cell_h],'localAlpha8BBox':list(box)if box else None,
                       'visibleAspectRatioRelativeError':abs((box[2]-box[0])/(box[3]-box[1])/(43/101)-1)if box else None})
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(host.stat().st_mtime,timezone.utc).isoformat(),
    'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),'width':size[0],'height':size[1],'mode':'RGBA','alphaExtrema':alpha,
    'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'promptFile':(OUT/f'prompt-{version}.txt').relative_to(ROOT).as_posix(),'referenced_image_paths':[str(p)for p in refs],'size':None},
    'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes no model/quality selector or verifiable actual return metadata.',
    'hostOutputFile':str(host),'officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md','references':[{'file':str(p),'sha256':sha(p),'role':roles[str(p)],'actuallyAttached':True}for p in refs],
    'prompt':(OUT/f'prompt-{version}.txt').relative_to(ROOT).as_posix(),'sourceFrameEvidence':'assets/maps/town/animation-candidates/3050/source-frame-provenance.json',
    'operation':'new four-frame generation'if version=='v1'else'AI edit of existing four-frame atlas; not deterministic crop or component shift',
    'frameIndexOrder':[0,1,2,3],'nativeTimingMs':None,'nativeStateSemantics':None,'resampled':False,'accepted':False,'runtimeIntegrated':False}
if version!='v1':record['editedFrom']={'file':(OUT/f'sequence-{previous}.png').relative_to(ROOT).as_posix(),'sha256':sha(OUT/f'sequence-{previous}.png'),'generationRecord':(OUT/f'sequence-{previous}.png.generation.json').relative_to(ROOT).as_posix()}
Path(str(target)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/f'native-check-{version}.json').write_text(json.dumps({'nativeSize':size,'alphaExtrema':alpha,'onlyCurrentAtlasInspected':True,'frames':bounds,'accepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'nativeSize':size,'alphaExtrema':alpha,'frames':bounds,'accepted':False}))
