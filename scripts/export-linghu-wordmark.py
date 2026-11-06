"""One-title crop and uniform PMA resize. No AI edit, repainting or shape reconstruction."""
from pathlib import Path
import json,hashlib
from PIL import Image

root=Path(__file__).resolve().parents[1]
source=root/'assets/branding/linghu-wordmark-v1.png'
im=Image.open(source).convert('RGBA');alpha=im.getchannel('A')
bbox=alpha.point(lambda v:255 if v>=8 else 0).getbbox()
if bbox is None:raise ValueError('Empty title')
roi=[max(0,bbox[0]-8),max(0,bbox[1]-8),min(im.width,bbox[2]+8),min(im.height,bbox[3]+8)]
crop=im.crop(roi);scale=min(960/crop.width,280/crop.height)
size=[round(crop.width*scale),round(crop.height*scale)]
scaled=crop.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
out=Image.new('RGBA',(1024,320));placement=[(1024-size[0])//2,(320-size[1])//2]
out.alpha_composite(scaled,placement)
target=root/'assets/branding/linghu-wordmark-login-1024.png';out.save(target)
record={'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
 'source':source.relative_to(root).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'generationRecord':'assets/branding/linghu-wordmark-v1.png.generation.json','nativeGeneration':False,
 'sourceNativeSize':list(im.size),'sourceROI':roi,'uniformScale':scale,'resizedSize':size,'placementXY':placement,
 'outputCanvas':[1024,320],'operation':'Native ROI crop; uniform premultiplied-alpha LANCZOS resize and transparent canvas placement.',
 'sourceMarginLimitation':'Original alpha8 bbox left/right margins5/1px; output padding does not recover or claim extra native drawing.',
 'textVisuallyRead':'灵葫大作战','textAndStyleLocalReviewPassed':True,'browserVerified':False,'accepted':False}
target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'size':list(out.size),'sourceNativeSize':list(im.size),'uniformScale':scale,'nativeGeneration':False}))
