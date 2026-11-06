"""One parent-authorized627px ivory static composition. Not a test, animation or AI redraw."""
from PIL import Image
import pathlib,json,hashlib,math,datetime
base=pathlib.Path(__file__).resolve().parent
root=base.parents[4]
proposal_path=base/'bind-static-v1.proposal.json'
raw=proposal_path.read_bytes();rig=json.loads(raw)
assert rig['direction']=='E' and rig['designCanvas']==[627,627]
assert rig['proposalStatus']=='manual_static_bind_proposal_unassembled_unapproved'
assert len(rig['nodes'])==16 and list(rig['actions'])==['idle'] and not rig['actions']['idle']['tracks']
def multiply(a,b):
 return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]]
def rotation(degrees,x=0,y=0):
 rad=degrees*math.pi/180;c=math.cos(rad);s=math.sin(rad)
 return[c,s,-s,c,x,y]
nodes={n['id']:n for n in rig['nodes']};bones={}
def bone(id):
 if id in bones:return bones[id]
 n=nodes[id];local=rotation(n.get('bindRotationDegrees',0),*n['bindPosition'])
 result=multiply(bone(n['parent']) if n['parent'] else [1,0,0,1,0,0],local);bones[id]=result
 return result
def image_matrix(n):
 s=n['imageScale'];px,py=n['pivot']
 return multiply(multiply(bone(n['id']),rotation(n.get('imageRotationDegrees',0))),[s,0,0,s,-px*s,-py*s])
def inverse_for_pillow(m):
 a,b,c,d,e,f=m;det=a*d-b*c
 return[d/det,-c/det,(c*f-d*e)/det,-b/det,a/det,(b*e-a*f)/det]
canvas=Image.new('RGBA',(627,627),(246,240,222,255));sources=[]
for n in sorted(rig['nodes'],key=lambda n:n['layer']):
 p=root.joinpath(*pathlib.PurePosixPath(n['file']).parts);src=p.read_bytes();sha=hashlib.sha256(src).hexdigest()
 if sha!=n['partSha256']:raise ValueError('Current source bytes changed: '+n['id'])
 im=Image.open(p).convert('RGBA')
 if list(im.size)!=n['partNativeCropSize']:raise ValueError('Current source dimensions changed: '+n['id'])
 matrix=image_matrix(n)
 # Premultiplied alpha prevents alpha0 hidden RGB from bleeding into transformed boundaries.
 rendered=im.convert('RGBa').transform((627,627),Image.Transform.AFFINE,inverse_for_pillow(matrix),resample=Image.Resampling.BICUBIC).convert('RGBA')
 canvas.alpha_composite(rendered)
 sources.append({'id':n['id'],'file':n['file'],'sha256':sha,'nativeSize':im.size,'pivot':n['pivot'],'bindPosition':n['bindPosition'],'imageScale':n['imageScale'],'bindRotationDegrees':n.get('bindRotationDegrees',0),'imageRotationDegrees':n.get('imageRotationDegrees',0),'layer':n['layer'],'boneMatrix':bone(n['id']),'imageMatrix':matrix})
out=base/'qa'/'bind-static-v1-ivory.png';out.parent.mkdir(exist_ok=True);canvas.convert('RGB').save(out)
meta={'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':[627,627],'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operation':'Deterministic16-painted-part static assembly from fixed manual proposal, premultiplied-alpha bicubic affine transforms on ivory; no new image generation, pixel repaint, source mirroring or per-frame fit.','renderer':'Pillow RGBa affine using exact Canvas2D cutout-rig matrix multiplication semantics; one still only','authorization':'Parent root explicitly authorized only one627px necessary static assembly; machine heavy freeze remains.','derivedFrom':{'proposal':str(proposal_path),'proposalSha256':hashlib.sha256(raw).hexdigest(),'sourceAtlas':rig['sourceAtlas'],'sourceAtlasSha256':rig['sourceAtlasSha256'],'sourceAtlasGenerationRecord':rig['sourceAtlas']+'.generation.json','parts':sources},'actualModel':None,'actualQuality':None,'modelScope':'No model called for this deterministic render. Trace painted-part model evidence through source atlas generation record.','staticBindApproved':False,'runtimeEnabled':False,'animationComplete':False,'actualVisualViewed':False}
(out.with_suffix(out.suffix+'.source.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'size':meta['size'],'sourceParts':len(sources),'sha256':meta['sha256'],'runtimeEnabled':False}))
