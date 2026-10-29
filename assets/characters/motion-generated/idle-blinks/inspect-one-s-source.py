"""One explicitly selected main-character idle strip: necessary source cut measurement only."""
from PIL import Image
import pathlib,json,hashlib,sys
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3]
id=sys.argv[1];assert id in['daoist-child','moon-shadow','mountain-guardian','lotus-healer']
src=base.parent/id/'idle-four-directions-v1.png';raw=src.read_bytes();gen=json.loads(pathlib.Path(str(src)+'.generation.json').read_text(encoding='utf-8'));assert hashlib.sha256(raw).hexdigest()==gen['sha256']
im=Image.open(src).convert('RGBA');assert im.size==(2048,768);a=im.getchannel('A');pixels=a.load()
def count_col(x):return sum(pixels[x,y]>=8 for y in range(768))
def runs(start,stop):
 result=[];begin=None
 for x in range(start,stop):
  if count_col(x)==0:
   if begin is None:begin=x
  elif begin is not None:result.append([begin,x]);begin=None
 if begin is not None:result.append([begin,stop])
 return result
record={'character':id,'source':str(src),'sourceSha256':gen['sha256'],'sourceSize':[2048,768],'sourceActualOrder':['N','E','S','W'],'SVisualConfirmed':True,'sourceRoles':{'daoist-child':'S front, LEFT holds golden Taiji gourd screen-right, RIGHT empty screen-left','moon-shadow':'S front, two crescent blades in their original hands, LEFT moon-flower screen-right','mountain-guardian':'S front, RIGHT ring-staff screen-left, LEFT round shield screen-right','lotus-healer':'S front, RIGHT lotus lantern screen-left, LEFT jade bottle screen-right'}[id],'leftBlankColumnRuns950to1080':runs(950,1080),'rightBlankColumnRuns1480to1640':runs(1480,1640),'nominalCutAlpha8Counts':{'x1023':count_col(1023),'x1024':count_col(1024),'x1535':count_col(1535),'x1536':count_col(1536)},'scope':'Necessary one historical source strip only for S editing target. No character-family scan, runtime export or presumed root.'}
dest=base/id;dest.mkdir(exist_ok=True);(dest/'source-cut-measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
