"""One explicitly named current candidate only; no directory walk or runtime output."""
from PIL import Image
import pathlib,json,hashlib,sys
base=pathlib.Path(__file__).resolve().parent
rel=pathlib.PurePosixPath(sys.argv[1])
if rel.is_absolute() or '..' in rel.parts or rel.suffix!='.png':raise ValueError('One owned relative PNG required')
src=base.joinpath(*rel.parts);record=pathlib.Path(str(src)+'.generation.json')
raw=src.read_bytes();gen=json.loads(record.read_text(encoding='utf-8'))
assert hashlib.sha256(raw).hexdigest()==gen['sha256']
im=Image.open(src).convert('RGBA');a=im.getchannel('A');mask=a.point(lambda v:255 if v>=8 else 0);bbox=mask.getbbox()
qa=src.parent/'qa';qa.mkdir(exist_ok=True);stem=src.stem
ivory=Image.new('RGBA',im.size,(246,240,222,255));ivory.alpha_composite(im);ivory=ivory.convert('RGB');ivory.thumbnail((900,900),Image.Resampling.LANCZOS);preview=qa/(stem+'-ivory.jpg');ivory.save(preview,quality=93)
def line_x(x):return sum(a.getpixel((x,y))>=8 for y in range(im.height))
def line_y(y):return sum(a.getpixel((x,y))>=8 for x in range(im.width))
data={'source':str(src),'sha256':gen['sha256'],'size':im.size,'alphaExtrema':a.getextrema(),'alpha8BBoxLTRB':bbox,'alpha8OuterEdges':{'left':line_x(0),'right':line_x(im.width-1),'top':line_y(0),'bottom':line_y(im.height-1)},'preview':str(preview),'operation':'Single named candidate alpha statistics and ivory compositing/whole-canvas thumbnail; diagnostic only, no source edits or runtime export.','actualVisualViewed':False,'clientApproved':False}
if len(sys.argv)>2 and sys.argv[2]=='2x2':
 assert im.width%2==0 and im.height%2==0
 cx=im.width//2;cy=im.height//2
 order=sys.argv[3].split(',') if len(sys.argv)>3 else ['N','E','S','W']
 assert len(order)==4 and all(d in ['N','E','S','W'] for d in order)
 data['atlas']={'columns':2,'rows':2,'cellSize':[cx,cy],'actualObservedOrder':order,'requestedOrder':['N','E','S','W'],'alpha8SeamCounts':{'leftOfVertical':line_x(cx-1),'rightOfVertical':line_x(cx),'aboveHorizontal':line_y(cy-1),'belowHorizontal':line_y(cy)},'notOwnershipApproval':True}
 data['cells']=[]
 for i,d in enumerate(order):
  x=(i%2)*cx;y=(i//2)*cy;crop=a.crop((x,y,x+cx,y+cy));b=crop.point(lambda v:255 if v>=8 else 0).getbbox();data['cells'].append({'direction':d,'nominalCell':[x,y,x+cx,y+cy],'localAlpha8BBox':b,'marginsLTRB':[b[0],b[1],cx-b[2],cy-b[3]] if b else None,'pivot':None,'status':'pending_identity_direction_shared_root_and_ownership'})
(qa/(stem+'.alpha-review.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(qa/(stem+'-ivory.jpg.source.json')).write_text(json.dumps({'derivedFrom':{'file':str(src),'sha256':gen['sha256'],'generationRecord':str(record)},'operation':data['operation'],'notNewGeneration':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
