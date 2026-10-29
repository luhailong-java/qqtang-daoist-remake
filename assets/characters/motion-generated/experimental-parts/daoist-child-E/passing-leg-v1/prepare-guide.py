"""Synthetic passing-leg engineering intent, not original skeleton/game art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json,hashlib
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
BASE.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',21)
im=Image.new('RGB',(1536,1024),'#fcfaf4');d=ImageDraw.Draw(im)
planted={'hip':[330,86],'knee':[346,235],'ankle':[338,395],'toe':[458,451],'sole':[395,469]}
raised={'hip':[330,86],'knee':[435,193],'ankle':[338,320],'toe':[458,376],'sole':[395,394]}
records=[]
for i,(side,state,points)in enumerate([
 ('near RIGHT','PLANTED UNDER HIP',planted),('near RIGHT','RAISED BENT PASSING',raised),
 ('far LEFT','PLANTED UNDER HIP',planted),('far LEFT','RAISED BENT PASSING',raised)]):
    ox=(i%2)*768;oy=(i//2)*512;color='#176ca0'if i<2 else'#a35c13'
    d.rectangle((ox+2,oy+2,ox+765,oy+509),outline='#c9beaa',width=2)
    d.text((ox+14,oy+8),f'{i+1} {side} / {state}',font=bold,fill=color)
    d.text((ox+14,oy+36),'SYNTHETIC ART INTENT / NOT QQ BONES / NOT GAME ART',font=small,fill='#9b3546')
    hp=points['hip'];d.ellipse((ox+hp[0]-35,oy+hp[1]-29,ox+hp[0]+35,oy+hp[1]+29),fill='white',outline=color,width=3)
    d.text((ox+15,oy+88),'PLAIN WHITE HIDDEN CAP',font=small,fill=color)
    for y in range(oy+120,oy+460,14):d.line((ox+330,y,ox+330,y+6),fill='#bcb5a3',width=1)
    names=['hip','knee','ankle','toe'];xy=[(ox+points[n][0],oy+points[n][1])for n in names]
    d.line(xy[:3],fill=color,width=10,joint='curve');d.line(xy[2:],fill='#713780',width=9)
    for name,(x,y)in zip(names,xy):
        d.ellipse((x-6,y-6,x+6,y+6),fill='#fcfaf4',outline='#222222',width=2)
        dx,dy={'hip':(42,-10),'knee':(20,-6),'ankle':(-185,-15),'toe':(18,-13)}[name]
        d.text((x+dx,y+dy),name+str(tuple(points[name])),font=font,fill='#222222')
    sx,sy=points['sole'];d.line((ox+sx-55,oy+sy,ox+sx+65,oy+sy),fill='#17602f',width=4)
    d.text((ox+sx+78,oy+sy-6),f'soleY={sy}',font=font,fill='#17602f')
    for x in range(ox+210,ox+600,12):d.line((x,oy+469,min(x+5,ox+600),oy+469),fill='#aa6555',width=1)
    if state.startswith('RAISED'):
        d.line((ox+600,oy+394,ox+600,oy+469),fill='#aa6555',width=2)
        d.text((ox+610,oy+415),'LIFT75px',font=font,fill='#aa6555')
    d.text((ox+15,oy+490),'Same source-pixel scale / toe SCREEN RIGHT / no mirror / no labels in final art',font=small,fill='#244f44')
    records.append({'id':('near_R'if i<2 else'far_L')+('_planted'if i%2==0 else'_raised'),
        'cell':[i%2,i//2],'cellOrigin':[ox,oy],'pointsCellLocal':points,
        'pointsAtlas':{n:[ox+p[0],oy+p[1]]for n,p in points.items()},
        'hipToKnee':math.dist(points['hip'],points['knee']),'kneeToAnkle':math.dist(points['knee'],points['ankle']),
        'footLiftRelativeToPlant':469-points['sole'][1]})
guide=BASE/'synthetic-passing-guide.png';im.save(guide)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'schemaVersion':1,'file':guide.name,'sha256':sha(guide),'createdAtUTC':datetime.now(timezone.utc).isoformat(),
 'canvasSize':[1536,1024],'cellSize':[768,512],'poses':records,
 'operation':'Pillow project-authored bone-point/line engineering guide, not AI game art/nativeQQ anatomical evidence.',
 'newModelGeneration':False,'samePixelScaleIntent':True,'actualOutputScaleApproved':False,
 'materialReference':'../whole-leg-v1/whole-leg-v1.png',
 'parentAuthoredPlantedTargets':'hip330,86/ankle338,395/toe458,451/soleY469. Raised retains approximate physical bone lengths through a true knee bend, ankle/sole75sourcepx higher.',
 'projectedLiftMath':{'sourceLift':75,'futureCandidateSourceToDesignScale':.24,'fixedDesignToLogicalScale':56.25/444,
     'logicalLiftIfThoseScalesAreLaterAccepted':75*.24*(56.25/444),'notNativeScaleClaim':True},
 'nativePhase4IdentityConflict':'still unconfirmed, no source time or native support-side recovery claimed',
 'nativeTimingMs':None,'worldRoot':None,'attachmentPivots':None,'runtimeAdopted':False}
guide.with_suffix('.png.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
headers_path=ROOT/'assets/characters/motion-generated/daoist-child/native-role9-evidence/native-walk-headers.json'
headers=json.loads(headers_path.read_text(encoding='utf-8'));ini=headers['playerIni']
keys=[line.split('=',1)[0].strip()for line in ini['text'].splitlines()if '='in line]
timing_keys=[k for k in keys if any(t in k.lower()for t in['time','duration','fps','delay','interval','tick'])]
ini_record={'sourceRecord':headers_path.relative_to(ROOT).as_posix(),'sourceRecordSha256':sha(headers_path),
 'field':'playerIni.text','storedOriginalIniSha256':ini['sha256'],'existingStoredTextActuallyRead':ini['text'],
 'timingKeysFound':timing_keys,'explicitTimingFound':bool(timing_keys),'nativeTimingMs':None,
 'operation':'Read existing stored player9.ini plaintext snapshot only; no ZIP extraction/new client execution. Layer IDs are not durations.'}
(BASE/'player9-existing-text-timing-check.json').write_text(json.dumps(ini_record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guide':str(guide),'sourceLift':75,'logicalLiftIntent':record['projectedLiftMath']['logicalLiftIfThoseScalesAreLaterAccepted'],
 'explicitIniTimingKeys':timing_keys,'nativeTimingMs':None}))
