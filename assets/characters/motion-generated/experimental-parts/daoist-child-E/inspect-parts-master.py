"""One new experimental parts sheet only; never crop/adopt automatically."""
from PIL import Image
import pathlib,json,hashlib
base=pathlib.Path(__file__).resolve().parent;src=base/'parts-master-v1.png'
im=Image.open(src).convert('RGBA');a=im.getchannel('A');mask=a.point(lambda v:255 if v>=8 else 0)
xs=[round(i*im.width/4)for i in range(5)];ys=[round(i*im.height/4)for i in range(5)]
def cx(x):return sum(a.getpixel((x,y))>=8 for y in range(im.height))
def cy(y):return sum(a.getpixel((x,y))>=8 for x in range(im.width))
qa=base/'qa';qa.mkdir(exist_ok=True)
bg=Image.new('RGBA',im.size,(246,240,222,255));bg.alpha_composite(im);bg=bg.convert('RGB');bg.thumbnail((1100,1100),Image.Resampling.LANCZOS);bg.save(qa/'parts-master-v1-ivory.jpg',quality=94)
out={'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'nativeSize':im.size,'alphaExtrema':a.getextrema(),'alpha8BBoxLTRB':mask.getbbox(),'outerAlpha8Edges':{'left':cx(0),'right':cx(im.width-1),'top':cy(0),'bottom':cy(im.height-1)},'nominalGrid':{'columns':4,'rows':4,'xCuts':xs,'yCuts':ys},'verticalSeams':[{'x':x,'alpha8Before':cx(x-1),'alpha8At':cx(x)}for x in xs[1:-1]],'horizontalSeams':[{'y':y,'alpha8Before':cy(y-1),'alpha8At':cy(y)}for y in ys[1:-1]],'ownershipCutsApproved':False,'partsExported':False,'accuratePivots':False,'bindApproved':False,'clientApproved':False,'operation':'single new atlas alpha statistics + ivory whole-canvas thumbnail diagnostic only, no crop/resize source or new model generation'}
(qa/'parts-master-v1.alpha-review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
(qa/'parts-master-v1-ivory.jpg.source.json').write_text(json.dumps({'derivedFrom':{'file':str(src),'sha256':out['sha256'],'generationRecord':str(src)+'.generation.json'},'operation':out['operation'],'notNewGeneration':True},indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
