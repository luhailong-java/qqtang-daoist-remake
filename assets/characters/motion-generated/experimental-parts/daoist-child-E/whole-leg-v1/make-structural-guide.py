"""Draw one explicitly synthetic engineering reference, never delivery art."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hashlib, json, math
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
W, H, CW, CH = 1536, 1024, 768, 512
font_path = 'C:/Windows/Fonts/arial.ttf'
bold_path = 'C:/Windows/Fonts/arialbd.ttf'
font = ImageFont.truetype(font_path, 18)
small = ImageFont.truetype(font_path, 15)
bold = ImageFont.truetype(bold_path, 20)
im = Image.new('RGB', (W, H), '#fcfaf4')
d = ImageDraw.Draw(im)
front = {'hip':[300,60], 'knee':[345,203], 'ankle':[400,343], 'toe':[458,363]}
back = {'hip':[420,60], 'knee':[370,201], 'ankle':[310,339], 'toe':[368,359]}
poses = []
for index, (side, phase, points) in enumerate([
    ('near_RIGHT','forward',front), ('near_RIGHT','backward',back),
    ('far_LEFT','forward',front), ('far_LEFT','backward',back),
]):
    ox, oy = (index % 2)*CW, (index // 2)*CH
    color = '#176ca0' if side == 'near_RIGHT' else '#a35c13'
    d.rectangle((ox+2, oy+2, ox+CW-3, oy+CH-3), outline='#c6bda8', width=2)
    d.text((ox+16,oy+8), f'{index+1}  {side} / {phase.upper()}', fill=color, font=bold)
    d.text((ox+16,oy+CH-78), 'SYNTHETIC STRUCTURAL POSE GUIDE', fill='#9d2640', font=bold)
    d.text((ox+16,oy+CH-52), 'PROJECT INTENT ONLY / NOT QQ SOURCE / NOT GAME ART', fill='#6a4d40', font=small)
    delta = points['toe'][0]-points['hip'][0]
    d.text((ox+16,oy+CH-30), f'toeX - hipX = {delta:+d}px; ALL boot tips face SCREEN RIGHT', fill='#333333', font=font)
    hx = ox+points['hip'][0]
    for y in range(oy+48,oy+397,12):
        d.line((hx,y,hx,min(y+5,oy+397)), fill='#bbb5a4', width=2)
    names = ['hip','knee','ankle','toe']
    xy = [(ox+points[n][0],oy+points[n][1]) for n in names]
    d.ellipse((xy[0][0]-37,xy[0][1]-25,xy[0][0]+37,xy[0][1]+25), outline=color, width=3)
    d.text((ox+24,oy+65), 'HIDDEN WHITE HIP CAP', fill=color, font=small)
    d.line(xy[:3], fill=color, width=12, joint='curve')
    d.line(xy[2:], fill='#713780', width=12)
    tx, ty = xy[3]
    d.polygon([(tx,ty),(tx-14,ty-11),(tx-14,ty+10)], fill='#713780')
    for name, (x,y) in zip(names,xy):
        d.ellipse((x-8,y-8,x+8,y+8), fill='#fcfaf4', outline='#222222', width=3)
        dx,dy = {'hip':(45,-8),'knee':(24,-8),'ankle':(-180,5),'toe':(18,10)}[name]
        d.text((x+dx,y+dy), f'{name} ({points[name][0]},{points[name][1]})', fill='#222222', font=font)
    # A separate arrow indicates boot-tip orientation, not foot-vs-hip position.
    ax, ay = ox+CW-185, oy+322
    d.line((ax,ay,ax+95,ay), fill='#17602f', width=4)
    d.polygon([(ax+95,ay),(ax+82,ay-8),(ax+82,ay+8)],fill='#17602f')
    d.text((ax-25,ay+14),'SCREEN RIGHT',fill='#17602f',font=small)
    lengths = {f'{a}To{b.title()}': math.dist(points[a],points[b]) for a,b in zip(names,names[1:])}
    poses.append({'id':side+'_'+phase,'cell':[index%2,index//2], 'cellOrigin':[ox,oy],
                  'pointsCellLocal':points, 'pointsAtlas':{k:[ox+p[0],oy+p[1]] for k,p in points.items()},
                  'toeMinusHipX':delta,'toeMinusAnkleX':points['toe'][0]-points['ankle'][0],
                  'segmentLengths':lengths,'anatomicalIdentityAssignedByProject':True})
path=OUT/'synthetic-structural-pose-guide.png'
im.save(path)
record={'schemaVersion':1,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'createdAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[W,H], 'cellSize':[CW,CH],
        'artSource':'code_engineering_reference_only', 'operation':'Pillow bone-point and line schematic from parent supplied project intent',
        'isAiGenerated':False,'isOfficialGameArt':False,'isOriginalQQEvidence':False,
        'physicalSource':'Synthetic project-local human pose intent. Coordinates are examples, not recovered native bones.',
        'pixelScale':'one shared atlas pixel scale; no per-cell bbox normalization',
        'near':'anatomical RIGHT', 'far':'anatomical LEFT', 'screenFacing':'E / RIGHT',
        'poses':poses,'worldRoot':None,'timing':None,'runtimeAdopted':False}
(OUT/'synthetic-structural-pose-guide.png.source.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(path),'sha256':record['sha256'],'canvasSize':[W,H],'toeMinusHipX':[p['toeMinusHipX'] for p in poses]}))
