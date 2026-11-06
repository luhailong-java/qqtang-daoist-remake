"""Only current W13 edit + its single source; no batch images or runtime export."""
from PIL import Image,ImageDraw
import pathlib,json,hashlib
base=pathlib.Path(__file__).resolve().parent
src=pathlib.Path('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy/frames/run/W/frame_13.png')
candidate=base/'west-frame13-edge-v1.png'
qa=base/'qa';qa.mkdir(exist_ok=True)
old=Image.open(src).convert('RGBA');new=Image.open(candidate).convert('RGBA');new.load()
assert old.size==(1024,1024)
assert new.width==new.height
def stats(im):
 a=im.getchannel('A');mask=a.point(lambda v:255 if v>=8 else 0);b=mask.getbbox()
 return dict(size=im.size,alphaExtrema=a.getextrema(),alpha8BBoxLTRB=b,alpha8Edges=dict(left=sum(a.getpixel((0,y))>=8 for y in range(im.height)),right=sum(a.getpixel((im.width-1,y))>=8 for y in range(im.height)),top=sum(a.getpixel((x,0))>=8 for x in range(im.width)),bottom=sum(a.getpixel((x,im.height-1))>=8 for x in range(im.width))),rightAlpha8Margin=im.width-b[2])
normalized=new.convert('RGBa').resize((1024,1024),Image.Resampling.LANCZOS).convert('RGBA')
normalized.save(qa/'west-frame13-edge-v1.canvas1024.png')
contact=Image.new('RGB',(1536,800),(246,240,222));draw=ImageDraw.Draw(contact)
for i,(label,im) in enumerate([('SOURCE W13 1024',old),('AI EDIT whole canvas ->1024',normalized)]):
 bg=Image.new('RGBA',im.size,(246,240,222,255));bg.alpha_composite(im);bg=bg.convert('RGB').resize((768,768),Image.Resampling.LANCZOS);contact.paste(bg,(i*768,32));draw.text((i*768+8,8),label,fill=(30,45,35))
contact.save(qa/'west-frame13-edge-v1.source-comparison.jpg',quality=93)
data={'source':str(src),'candidate':str(candidate),'candidateSha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'sourceStats':stats(old),'nativeCandidateStats':stats(new),'normalizedCandidateStats':stats(normalized),'operation':{'type':'QA_only_uniform_complete_canvas_premultiplied_alpha_LANCZOS','input':new.size,'output':[1024,1024],'translation':[0,0],'crop':None,'perFrameBBoxFit':False,'modelGeneration':False},'rootEvidence':{'sourceDeclaredLayoutRoot':[512,928],'notPhysicalGroundApproval':True,'candidateRoot':None,'status':'pending_visual_body_landmark_alignment; do not assume declared old root stayed fixed'},'runtimeExported':False,'clientApproved':False,'preview':str(qa/'west-frame13-edge-v1.source-comparison.jpg')}
(qa/'west-frame13-edge-v1.canvas1024.png.source.json').write_text(json.dumps({'derivedFrom':{'file':str(candidate),'sha256':data['candidateSha256'],'generationRecord':str(candidate)+'.generation.json'},'operation':data['operation'],'purpose':'QA only, not runtime adoption'},indent=2)+'\n',encoding='utf-8')
(qa/'west-frame13-edge-v1.edge-review.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps(data))
