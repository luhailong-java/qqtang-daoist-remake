"""One own S editing source. No generated image, bbox fit or borrowed character root."""
from PIL import Image
import pathlib,json,hashlib,sys
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3];id=sys.argv[1]
cuts={'daoist-child':[1000,1540],'moon-shadow':[1010,1580],'mountain-guardian':[1000,1580]}
assert id in list(cuts)+['lotus-healer'];dest=base/id;dest.mkdir(exist_ok=True)
if id in cuts:
 src=base.parent/id/'idle-four-directions-v1.png';raw=src.read_bytes();generation=str(src)+'.generation.json';gen=json.loads(pathlib.Path(generation).read_text(encoding='utf-8'));assert hashlib.sha256(raw).hexdigest()==gen['sha256']
 im=Image.open(src).convert('RGBA');assert im.size==(2048,768);a=im.getchannel('A');left,right=cuts[id]
 assert sum(a.getpixel((left,y))>=8 for y in range(768))==0 and sum(a.getpixel((right,y))>=8 for y in range(768))==0
 canvas=Image.new('RGBA',(768,768),(0,0,0,0));canvas.paste(im.crop((left,0,right,768)),(left-896,0))
 op={'kind':'measured blank-column ownership crop then unscaled whole-height placement','sourceCropLTRB':[left,0,right,768],'sourceToCanvasTranslation':[-896,0],'scale':1,'SNominalSourceAxis1280ToCanvas384':True,'cutAlpha8Counts':[0,0],'noBBoxFit':True,'noMirroring':True}
else:
 src=root/'assets/characters/runtime/lotus-healer.png';raw=src.read_bytes();generation=None;im=Image.open(src).convert('RGBA');assert im.size==(1024,1024)
 canvas=im.convert('RGBa').resize((768,768),Image.Resampling.LANCZOS).convert('RGBA');op={'kind':'complete own runtime S master canvas uniformly resized only','sourceCropLTRB':[0,0,1024,1024],'sourceToCanvasTranslation':[0,0],'scale':0.75,'reason':'Idle strip S lantern/robe has no full-height empty left cut; existing own runtime frontS keeps complete lantern/body instead','noBBoxFit':True,'noMirroring':True,'nativeGenerationDimensions':None,'history':'runtime master is an existing derived own identity; original4096 history is compatibility canvas, not proved native4K'}
target=dest/'open-S.png';canvas.save(target);a=canvas.getchannel('A');mask=a.point(lambda v:255 if v>=8 else 0)
roi={'daoist-child':{'screenLeftBoot':[205,675,350,750],'screenRightBoot':[365,675,510,750]},'moon-shadow':{'screenLeftBoot':[230,675,355,750],'screenRightBoot':[385,675,515,750]},'mountain-guardian':{'screenLeftBoot':[250,675,385,750],'screenRightBoot':[430,675,560,750]},'lotus-healer':{'screenLeftBoot':[320,660,425,750],'screenRightBoot':[425,660,535,750]}}[id]
def global_bbox(rect):
 b=mask.crop(rect).getbbox();return[b[0]+rect[0],b[1]+rect[1],b[2]+rect[0],b[3]+rect[1]]if b else None
rec={'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':[768,768],'notNewGeneration':True,'derivedFrom':{'file':str(src),'sha256':hashlib.sha256(raw).hexdigest(),'sourceSize':list(im.size),'generationRecord':generation},'operation':op,'character':id,'direction':'S','directionActuallyViewed':True,'sourceBodyHandsActuallyViewed':True,'alphaExtrema':a.getextrema(),'alpha8BBoxLTRB':mask.getbbox(),'footROIs':roi,'footAlpha8BBoxLTRB':{k:global_bbox(v)for k,v in roi.items()},'root':None,'rootEvidence':'No other character anchor borrowed; foot ROI is manual source-image inspection region only, not native game anchor.','runtimeEnabled':False}
target.with_suffix('.png.source.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ivory=Image.new('RGBA',canvas.size,(246,240,222,255));ivory.alpha_composite(canvas);ivory.convert('RGB').save(dest/'open-S-ivory.jpg',quality=94)
print(json.dumps(rec,ensure_ascii=False))
