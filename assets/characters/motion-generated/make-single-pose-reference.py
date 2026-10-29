"""One lightweight source crop and geometric model-input guide; not game art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
base=Path(__file__).resolve().parent;root=base.parents[2]
source=base/'moon-shadow/walk-east-v4.png';target=base/'moon-shadow/east-frame3-edit-target-v5.png'
image=Image.open(source).convert('RGBA');image.crop((1024,0,1536,768)).save(target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target.with_suffix('.png.source.json').write_text(json.dumps({'file':target.relative_to(root).as_posix(),'sha256':sha(target),'referenceOnly':True,'notRuntimeArt':True,
 'derivedFrom':{'file':source.relative_to(root).as_posix(),'sha256':sha(source),'generationRecord':source.relative_to(root).as_posix()+'.generation.json'},
 'operation':{'type':'single-cell crop for AI edit input only','rectLTRB':[1024,0,1536,768],'newModelGeneration':False,'resampled':False}},indent=2)+'\n',encoding='utf-8')
guide=Image.new('RGB',(512,768),'#fcfbf6');d=ImageDraw.Draw(guide);font=ImageFont.load_default(size=18)
d.text((16,18),'POSE GUIDE ONLY - NOT GAME ART',font=font,fill='#233b43')
d.text((16,52),'E/right-facing. Toes still point RIGHT.',font=font,fill='#233b43')
d.text((16,90),'BLUE = NEAR / foreground leg',font=font,fill='#156aa7')
d.text((16,120),'ORANGE = FAR / behind leg',font=font,fill='#bc672a')
d.line([(270,530),(320,600),(350,680),(390,687)],fill='#bc672a',width=12)
for x,y in [(270,530),(320,600),(350,680)]:d.ellipse((x-8,y-8,x+8,y+8),fill='#bc672a')
d.line([(250,530),(207,600),(175,680),(210,687)],fill='#156aa7',width=18)
for x,y in [(250,530),(207,600),(175,680)]:d.ellipse((x-10,y-10,x+10,y+10),fill='#156aa7')
d.line([(0,700),(512,700)],fill='#bdb9ab',width=2)
d.text((16,160),'NEAR hip250 -> toe210 = -40px',font=font,fill='#156aa7')
d.text((16,190),'FAR  hip270 -> toe390 = +120px',font=font,fill='#bc672a')
d.text((16,235),'Change only lower limbs. Keep identity,',font=font,fill='#233b43')
d.text((16,265),'camera, torso and held daggers intact.',font=font,fill='#233b43')
d.text((16,735),'Never render guide lines/text in final.',font=font,fill='#233b43')
out=base/'moon-shadow/east-frame3-pose-guide-v5.png';guide.save(out)
out.with_suffix('.png.source.json').write_text(json.dumps({'file':out.relative_to(root).as_posix(),'sha256':sha(out),'referenceOnly':True,'notRuntimeArt':True,
 'operation':'code-drawn geometric pose diagram for model input; not a character sprite or deliverable artwork','nearHip':[250,530],'nearToe':[210,687],'farHip':[270,530],'farToe':[390,687]},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'singleEditTarget':str(target),'guide':str(out),'notRuntimeArt':True}))
