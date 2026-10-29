"""One current open/closed pair only: uniform complete-canvas restoration and feet comparison."""
from PIL import Image
import pathlib,json,hashlib,sys
base=pathlib.Path(__file__).resolve().parent;id=sys.argv[1];assert id in['daoist-child','moon-shadow','mountain-guardian','lotus-healer'];folder=base/id
open_path=folder/'open-S.png';meta=json.loads((folder/'open-S.png.source.json').read_text(encoding='utf-8'));src=folder/'closed-S-v1.png';gen=json.loads(pathlib.Path(str(src)+'.generation.json').read_text(encoding='utf-8'))
assert hashlib.sha256(open_path.read_bytes()).hexdigest()==meta['sha256']and hashlib.sha256(src.read_bytes()).hexdigest()==gen['sha256']
opened=Image.open(open_path).convert('RGBA');closed=Image.open(src).convert('RGBA');w,h=closed.size;scale=min(768/w,768/h);new_size=(round(w*scale),round(h*scale));offset=((768-new_size[0])//2,(768-new_size[1])//2)
restored=Image.new('RGBA',(768,768),(0,0,0,0));resized=closed.convert('RGBa').resize(new_size,Image.Resampling.LANCZOS).convert('RGBA');restored.paste(resized,offset)
dest=folder/'closed-S-canvas768.png';restored.save(dest)
def mask(im):return im.getchannel('A').point(lambda v:255 if v>=8 else 0)
oa=opened.getchannel('A');ca=restored.getchannel('A');om=mask(opened);cm=mask(restored)
def edges(a):return{'left':sum(a.getpixel((0,y))>=8 for y in range(a.height)),'right':sum(a.getpixel((a.width-1,y))>=8 for y in range(a.height)),'top':sum(a.getpixel((x,0))>=8 for x in range(a.width)),'bottom':sum(a.getpixel((x,a.height-1))>=8 for x in range(a.width))}
def bbox(rect,m):
 b=m.crop(rect).getbbox();return[b[0]+rect[0],b[1]+rect[1],b[2]+rect[0],b[3]+rect[1]]if b else None
# Soles only: lower-region manual ROIs avoid the guardian's staff tip and dress/anklet above.
rois={key:[v[0],700 if id!='lotus-healer' else 680,v[2],768]for key,v in meta['footROIs'].items()}
feet={}
for key,rect in rois.items():
 b0=bbox(rect,om);b1=bbox(rect,cm);delta=[b1[i]-b0[i]for i in range(4)]if b0 and b1 else None
 feet[key]={'sourceManualSoleROI':rect,'openAlpha8BBoxLTRB':b0,'closedAlpha8BBoxLTRB':b1,'deltaLTRB':delta,'notAnApprovedAnchor':True}
ob=om.getbbox();cb=cm.getbbox();global_delta=[cb[i]-ob[i]for i in range(4)]if ob and cb else None
board=Image.new('RGB',(900,450),(246,240,222))
for i,im in enumerate([opened,restored]):
 ivory=Image.new('RGBA',(768,768),(246,240,222,255));ivory.alpha_composite(im);board.paste(ivory.convert('RGB').resize((450,450),Image.Resampling.LANCZOS),(450*i,0))
preview=folder/'comparison-ivory.jpg';board.save(preview,quality=95)
record={'character':id,'sourceOpen':str(open_path),'sourceOpenSha256':meta['sha256'],'sourceOpenCanvas':[768,768],'generatedClosed':str(src),'generatedClosedSha256':gen['sha256'],'generatedNativeSize':[w,h],'restoredClosed':str(dest),'restoredClosedSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'restoreOperation':{'kind':'entire image canvas uniform premultiplied-alpha LANCZOS resize only; centered transparent letterbox if output aspect differs','uniformScale':scale,'resizedWholeCanvas':new_size,'offset':offset,'aspectRatioMatchesSource':w==h,'noBBoxFit':True,'noIndependentAxisStretch':True,'noMirroring':True},'generatedAlphaExtrema':closed.getchannel('A').getextrema(),'generatedAlpha8OuterEdges':edges(closed.getchannel('A')),'restoredAlphaExtrema':ca.getextrema(),'restoredAlpha8OuterEdges':edges(ca),'openAlpha8BBoxLTRB':ob,'closedAlpha8BBoxLTRB':cb,'wholeSilhouetteBBoxDeltaLTRB':global_delta,'sourceAndClosedSoleRegions':feet,'maxAbsSoleBBoxDelta':max(abs(n)for f in feet.values()for n in f['deltaLTRB'])if all(f['deltaLTRB']for f in feet.values())else None,'preview':str(preview),'actualVisualViewed':False,'root':None,'rootBorrowed':False,'directionApproved':False,'staticIdentityApproved':False,'runtimeEnabled':False,'clientApproved':False,'scope':'Necessary single newly edited pair only; movement metrics are observed comparison, not positional correction.'}
(folder/'closed-S-v1.review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dest.with_suffix('.png.source.json').write_text(json.dumps({'derivedFrom':{'file':str(src),'sha256':gen['sha256'],'generationRecord':str(src)+'.generation.json'},'operation':record['restoreOperation'],'notNewGeneration':True,'outputSha256':record['restoredClosedSha256'],'sourceOpen':str(open_path),'runtimeEnabled':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
preview.with_suffix('.jpg.source.json').write_text(json.dumps({'derivedFrom':[{'file':str(open_path),'sha256':meta['sha256']},{'file':str(dest),'sha256':record['restoredClosedSha256']}],'operation':'Side-by-side whole-canvas450px ivory diagnostic previews; no alignment or art repaint; not new generation.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k]for k in['character','generatedNativeSize','generatedAlphaExtrema','generatedAlpha8OuterEdges','closedAlpha8BBoxLTRB','wholeSilhouetteBBoxDeltaLTRB','sourceAndClosedSoleRegions','maxAbsSoleBBoxDelta','preview']},ensure_ascii=False))
