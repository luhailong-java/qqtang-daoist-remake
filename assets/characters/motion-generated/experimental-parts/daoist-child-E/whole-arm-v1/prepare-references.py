"""Small native-size material board and synthetic engineering guide only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,math
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'package.json').is_file() and (p/'src').is_dir())
PARTS=OUT.parent/'parts-v1'
OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
board=Image.new('RGBA',(1400,820),(248,242,225,255));d=ImageDraw.Draw(board)
d.text((16,10),'OWN MATERIAL ONLY - DO NOT COPY SEGMENTED JOINT RIMS',font=bold,fill='#9b3546')
names=['torso_pelvis','upper_arm_near_R','forearm_near_R','hand_near_R','upper_arm_far_L','forearm_far_L','hand_gourd_far_L']
records=[]
for i,n in enumerate(names):
    x=(i%4)*350;y=(i//4)*380+55
    p=PARTS/(n+'.png');im=Image.open(p).convert('RGBA')
    d.text((x+10,y),n,font=font,fill='#244f44')
    pos=(x+(350-im.width)//2,y+30+(330-im.height)//2)
    board.alpha_composite(im,pos)
    records.append({'id':n,'source':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'sourceCanvasSize':list(im.size),
      'placement':list(pos),'scale':1,'originalRecord':(str(p.relative_to(ROOT)).replace('\\','/')+'.provenance.json'),
      'sourceGenerationRecord':(OUT.parent/'parts-master-v1.png.generation.json').relative_to(ROOT).as_posix()})
    im.close()
d.text((16,790),'Native crop pixels at1:1. Ivory = cloth; gold cloud = wrist trim; gourd stays in LEFT hand.',font=font,fill='#244f44')
bp=OUT/'own-material-reference-board.png';board.convert('RGB').save(bp)
save(bp.with_suffix('.png.source.json'),{'file':bp.name,'sha256':digest(bp),'createdAt':datetime.now(timezone.utc).isoformat(),
 'operation':'Unscaled native crops placed at1:1 onto one ivory material-reference board, no pixel repaint or source edit.',
 'sources':records,'newModelGeneration':False,'isGameArt':False,'role':'Material identity reference only, not segmented-interface construction or current pose.'})
W,H,CW=1536,1024,768
guide=Image.new('RGB',(W,H),'#fcfaf4');g=ImageDraw.Draw(guide)
poses=[]
for i,(side,wrist,hand) in enumerate([('near RIGHT / EMPTY RIGHT FIST',[450,460],[505,448]),('far LEFT / LEFT HAND + GOURD',[450,330],[505,318])]):
    ox=i*CW;color='#176ca0' if i==0 else '#a35c13'
    g.rectangle((ox+2,2,ox+CW-3,H-3),outline='#bfb7a2',width=2)
    g.text((ox+16,18),side,font=bold,fill=color)
    g.text((ox+16,56),'SYNTHETIC STRUCTURAL GUIDE',font=bold,fill='#9b3546')
    g.text((ox+16,86),'INTERNAL INTENT / NOT QQ SOURCE / NOT GAME ART',font=small,fill='#794c40')
    points={'shoulder':[240,180],'elbow':[300,395],'wrist':wrist,'hand':hand}
    xy=[(ox+v[0],v[1]) for v in points.values()]
    g.line(xy,fill=color,width=14,joint='curve')
    g.ellipse((ox+195,140,ox+285,220),outline=color,width=4)
    g.text((ox+24,143),'PLAIN HIDDEN WHITE CAP',font=small,fill=color)
    for name,(x,y) in zip(points.keys(),xy):
        g.ellipse((x-8,y-8,x+8,y+8),fill='#fcfaf4',outline='#222222',width=3)
        dx,dy={'shoulder':(52,-10),'elbow':(-200,-20),'wrist':(-90,34),'hand':(24,10)}[name]
        g.text((x+dx,y+dy),name,font=font,fill='#222222')
    if i==0:
        g.rounded_rectangle((ox+480,420,ox+540,480),radius=17,outline=color,width=3)
        g.text((ox+435,502),'EMPTY FIST',font=font,fill=color)
    else:
        # Gourd envelope is intentionally a schematic, not painted costume art.
        g.ellipse((ox+405,222,ox+514,315),outline='#8b7937',width=3)
        g.ellipse((ox+375,292,ox+535,450),outline='#8b7937',width=3)
        g.line((ox+442,224,ox+446,194),fill='#8b7937',width=4)
        g.text((ox+370,470),'GOURD ENVELOPE ONLY',font=small,fill='#8b7937')
        g.text((ox+370,495),'Grip/shape from OWN material photo',font=small,fill='#8b7937')
    g.text((ox+20,650),'ONE CONTINUOUS IVORY SLEEVE + HAND',font=bold,fill='#244f44')
    g.text((ox+20,690),'No gold shoulder cup. No mid-elbow finished cuff.',font=font,fill='#244f44')
    g.text((ox+20,725),'Only one natural wrist cuff / same sleeve pixel scale.',font=font,fill='#244f44')
    g.text((ox+20,850),'Camera E; both independent arms, never mirrored.',font=font,fill='#244f44')
    g.text((ox+20,887),'Points are artistic intent, not recovered anatomy.',font=font,fill='#244f44')
    poses.append({'id':'near_RIGHT_empty' if i==0 else 'far_LEFT_gourd','cellOrigin':[ox,0],
        'pointsCellLocal':points,'pointsAtlas':{n:[ox+p[0],p[1]] for n,p in points.items()},
        'upperArmLength':math.dist(points['shoulder'],points['elbow']),
        'forearmLength':math.dist(points['elbow'],points['wrist']),
        'holdingHand':'RIGHT empty' if i==0 else 'LEFT holding complete own Taiji gourd'})
gp=OUT/'synthetic-structural-guide.png';guide.save(gp)
save(gp.with_suffix('.png.source.json'),{'file':gp.name,'sha256':digest(gp),'createdAt':datetime.now(timezone.utc).isoformat(),
 'canvasSize':[W,H],'cellSize':[CW,H],'operation':'Pillow bone/line diagram of project-authored intended continuous-arm structure. Not AI art, game art, original QQ evidence or exact anatomy.',
 'samePixelScale':True,'newModelGeneration':False,'near':'RIGHT','far':'LEFT','poses':poses,
 'registeredTorsoReference':'../whole-leg-v1/registered-contact-v3/proposal.json',
 'registeredTorsoShoulderReference':{'nearRIGHT':[262.5,359.5],'farLEFT':[346.5,353.5],
    'evidence':'Previous hand-authored shoulder proposal + registered torso3px translation, not an approved native anchor. Far port is partly occluded.'},
 'ratioIntent':'upper223.22 / forearm163.48 guide pixels, equal in both arms; possible future fixed scale around0.27 yields60/44 designpx. This is not measured output or bind approval.',
 'attachmentPivots':None,'bindScale':None,'worldRoot':None,'timing':None,'runtimeAdopted':False})
print(json.dumps({'materialBoard':str(bp),'guide':str(gp),'sourceParts':7,'resizing':False,'modelCalls':0}))
