"""Two necessary static whole-leg composition proposals; no AI repaint or complete animation."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime

base=Path(__file__).resolve().parent
root=next(p for p in base.parents if (p/'package.json').is_file() and (p/'src').is_dir())
out=base/'root-contact-diagnostic';out.mkdir(exist_ok=True)
native=base/'whole-leg-v1.png';sheet=Image.open(native).convert('RGBA')
if sheet.size!=(1536,1024):raise ValueError('Whole-leg source changed')
source_sha=hashlib.sha256(native.read_bytes()).hexdigest()
specs=[
 ('near_R_forward',[0,0,768,512],[377,93],[576,378],[713,428],[631,466]),
 ('near_R_backward',[768,0,1536,512],[1224,105],[1047,391],[1160,451],[1081,468]),
 ('far_L_forward',[0,512,768,1024],[372,576],[566,890],[710,925],[623,943]),
 ('far_L_backward',[768,512,1536,1024],[1225,591],[1048,892],[1170,950],[1090,968]),
]
parts={};ownership_visible=0
for ident,cell,hip,ankle,toe,sole in specs:
    full=sheet.crop(cell);a=full.getchannel('A');mask=a.point(lambda v:255 if v>=8 else 0)
    box=mask.getbbox()
    if not box:raise ValueError('Missing whole-leg silhouette')
    if any(sum(v>=8 for v in a.crop(r).getdata())for r in[(0,0,1,full.height),(0,0,full.width,1),(full.width-1,0,full.width,full.height),(0,full.height-1,full.width,full.height)]):raise ValueError('Cell boundary crosses painted leg')
    ownership_visible+=sum(v>=8 for v in a.getdata())
    rect=[cell[0]+max(0,box[0]-8),cell[1]+max(0,box[1]-8),cell[0]+min(full.width,box[2]+8),cell[1]+min(full.height,box[3]+8)]
    crop=sheet.crop(rect);path=out/(ident+'.png');crop.save(path)
    local=lambda xy:[xy[0]-rect[0],xy[1]-rect[1]]
    parts[ident]={'file':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'sourceCropRect':rect,'sourceNativeSize':list(crop.size),'hip':local(hip),'ankle':local(ankle),'toe':local(toe),'soleCandidate':local(sole),
      'landmarksEvidence':'Manual visual estimates in actual native whole-leg image. Not native anatomy, approved bind or recovered original root.'}
if ownership_visible!=sum(v>=8 for v in sheet.getchannel('A').getdata()):raise ValueError('Whole-leg ownership incomplete')
old_base=base.parent
proposal=json.loads((old_base/'bind-static-v1.proposal.json').read_text(encoding='utf-8'))
nodes={n['id']:n for n in proposal['nodes']}
head=nodes['head'];torso=nodes['torso_pelvis']
# Reuse the prior exact head/torso composition only. No second hem or old segmented legs.
fixed=[]
for ident,pos in [('torso_pelvis',[313.5,398]),('head',[307,321])]:
    node=nodes[ident];p=root/node['file']
    if hashlib.sha256(p.read_bytes()).hexdigest()!=node['partSha256']:raise ValueError('Existing part source changed')
    fixed.append({'id':ident,'file':node['file'],'sha256':node['partSha256'],'pivot':node['pivot'],
      'scale':node['imageScale'],'position':pos,'layer':node['layer']})
scale=.24;poses=[];contact_images=[]
for label,near,far in [('A','near_R_forward','far_L_backward'),('B','near_R_backward','far_L_forward')]:
    draw_list=[]
    for ident,pos,layer in [(far,[319,438],10),(near,[307,439],20)]:
        part=parts[ident];draw_list.append({'id':ident,'file':part['file'],'sha256':part['sha256'],'pivot':part['hip'],'scale':scale,'position':pos,'layer':layer})
    draw_list+=fixed
    canvas=Image.new('RGBA',(627,627),(246,240,222,255));rendered_nodes=[]
    for item in sorted(draw_list,key=lambda n:n['layer']):
        im=Image.open(root/item['file']).convert('RGBA');s=item['scale'];px,py=item['pivot'];x,y=item['position']
        e=x-px*s;f=y-py*s
        rendered=im.convert('RGBa').transform((627,627),Image.Transform.AFFINE,(1/s,0,-e/s,0,1/s,-f/s),resample=Image.Resampling.BICUBIC).convert('RGBA')
        canvas.alpha_composite(rendered)
        rendered_nodes.append({**item,'imageMatrix':[s,0,0,s,e,f]})
    clean=out/f'contact-{label}-ivory.png';canvas.convert('RGB').save(clean)
    diagnostic=canvas.convert('RGB');d=ImageDraw.Draw(diagnostic)
    for x in range(80,550,12):d.line((x,529,min(x+6,550),529),fill='#b86a59',width=1)
    d.text((20,16),f'CONTACT {label} | whole-leg / head+torso only | unapproved',fill='#214a3d')
    d.text((20,560),'Arms missing. Dashed line is diagnostic, not native world root.',fill='#214a3d')
    contact_images.append(diagnostic)
    poses.append({'contact':label,'nearPart':near,'farPart':far,'nodes':rendered_nodes,'output':clean.relative_to(root).as_posix()})
board=Image.new('RGB',(1254,627),'#f6f0df')
for i,im in enumerate(contact_images):board.paste(im,(i*627,0))
board.save(out/'two-contacts-ivory.png')
record={'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':native.relative_to(root).as_posix(),
 'sourceSHA256':source_sha,'sourceNativeSize':[1536,1024],'parts':parts,'sourceAlpha8PixelsOwnedOnce':ownership_visible,
 'designCanvas':[627,627],'twoContacts':poses,'wholeLegUniformScale':scale,
 'nearHipPosition':[307,439],'farHipPosition':[319,438],'diagnosticGroundY':529,
 'nearFarIDsFixed':True,'mirroring':False,'componentWarping':False,'oldSecondHemUsed':False,'oldSegmentedLegsUsed':False,
 'armsPresent':False,'landmarksApproved':False,'staticBindAccepted':False,'runtimeIntegrated':False,
 'sourceNativeTimingMs':None,'worldRoot':None,'completeAnimation':False,
 'operation':'Exact native whole-leg crops and fixed manual isotropic affine composition; head/torso retained. No new AI image, repaint, mirror, per-pose fit or world-root claim.'}
(out/'proposal.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':(out/'two-contacts-ivory.png').relative_to(root).as_posix(),'parts':4,'wholeLegUniformScale':scale,'runtimeIntegrated':False}))
