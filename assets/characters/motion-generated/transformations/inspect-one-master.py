"""Single currently generated source alpha/ivory diagnostic; no batch scanning."""
from PIL import Image
import hashlib,json,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent
name=sys.argv[1]
if '/' in name or '\\' in name or not name.startswith('avatar-'):raise ValueError('One direct identity directory only')
src=base/name/'master.png';record=src.with_name('master.png.generation.json')
raw=src.read_bytes();gen=json.loads(record.read_text(encoding='utf-8'))
assert hashlib.sha256(raw).hexdigest()==gen['sha256']
im=Image.open(src);im.load();im=im.convert('RGBA');a=im.getchannel('A');hist=a.histogram();mask=a.point(lambda v:255 if v>=8 else 0);bbox=mask.getbbox()
ivory=Image.new('RGBA',im.size,(246,240,222,255));ivory.alpha_composite(im);ivory=ivory.convert('RGB');ivory.thumbnail((900,900),Image.Resampling.LANCZOS)
out=base/name/'qa';out.mkdir(exist_ok=True);preview=out/'master-ivory.jpg';ivory.save(preview,quality=93)
edge={'left':sum(a.getpixel((0,y))>=8 for y in range(im.height)),'right':sum(a.getpixel((im.width-1,y))>=8 for y in range(im.height)),'top':sum(a.getpixel((x,0))>=8 for x in range(im.width)),'bottom':sum(a.getpixel((x,im.height-1))>=8 for x in range(im.width))}
data={'source':str(src),'sourceSha256':gen['sha256'],'width':im.width,'height':im.height,'mode':'RGBA','alphaExtrema':a.getextrema(),'alpha0Pixels':hist[0],'alpha1to7Pixels':sum(hist[1:8]),'alpha8PlusPixels':sum(hist[8:]),'alpha8BBoxLTRB':bbox,'outerEdgeAlpha8Counts':edge,'alpha0HiddenRGBNotFailure':True,'ivoryPreview':str(preview),'operation':'Single-file alpha statistics and compositing over ivory, uniformly thumbnail to900max. QA diagnostic only; no source pixel edits, no model generation, no runtime export.','sourceMasterUnmodified':True,'status':'single_source_numeric_evidence_pending_visual_and_client_review'}
(out/'alpha-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'master-ivory.jpg.source.json').write_text(json.dumps({'derivedFrom':{'file':str(src),'sha256':gen['sha256'],'generationRecord':str(record)},'operation':data['operation'],'notNewGeneration':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
gen['review']['singleSourceAlphaEvidence']=str(out/'alpha-review.json');gen['review']['pending']=['ivory preview visual judgment','relative scale/root/directions/animation/client integration'];record.write_text(json.dumps(gen,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
