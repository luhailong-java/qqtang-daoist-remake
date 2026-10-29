"""One newly generated branding image; diagnostic composites only, no pixel repair."""
from pathlib import Path
import json, hashlib
from PIL import Image

root=Path(__file__).resolve().parents[1]
p=root/'assets/branding/linghu-wordmark-v1.png'
im=Image.open(p).convert('RGBA');a=im.getchannel('A');w,h=im.size
visible=a.point(lambda v:255 if v>=8 else 0)
edge=lambda crop:sum(v>=8 for v in a.crop(crop).getdata())
record={'source':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
    'actualNativeSize':[w,h],'alphaExtrema':list(a.getextrema()),'alpha8BBox':visible.getbbox(),
    'alpha8OuterEdgesLTRB':[edge((0,0,1,h)),edge((0,0,w,1)),edge((w-1,0,w,h)),edge((0,h-1,w,h))],
    'textExpected':'灵葫大作战','geometryAccepted':False,'runtimeIntegrated':False,
    'operation':'Single-source inspection and standard alpha composite; no recolour, padding, repair or geometry edit.'}
preview=Image.new('RGB',(1000,510),'#f6f0df')
for i,col in enumerate(['#f6f0df','#183e37']):
    band=Image.new('RGBA',(1000,255),col)
    scaled=im.convert('RGBa');scaled.thumbnail((960,225),Image.Resampling.LANCZOS)
    scaled=scaled.convert('RGBA');band.alpha_composite(scaled,((1000-scaled.width)//2,(255-scaled.height)//2))
    preview.paste(band.convert('RGB'),(0,i*255))
preview.save(root/'assets/branding/linghu-wordmark-v1-light-dark.png')
(root/'assets/branding/linghu-wordmark-v1.review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=True))
