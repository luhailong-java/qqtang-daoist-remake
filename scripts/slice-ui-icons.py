from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/ui/qdao-ui-icons-v3.png'
im=Image.open(source).convert('RGBA')
if im.size!=(1254,1254): raise ValueError('Reinspect source rectangles for a different source size')
names=['home','rooms','person','shop','records','help','settings','sound','chat','team','ready','lock','plus','search','refresh','exit']
row_xs=[[0,344,644,946,1254],[0,323,647,946,1254],[0,323,647,946,1254],[0,323,647,946,1254]]
ys=[0,370,672,947,1254]
records=[]
out=ROOT/'assets/ui/icons';out.mkdir(exist_ok=True)
for i,name in enumerate(names):
 row,col=divmod(i,4)
 xs=row_xs[row]
 rect=(xs[col],ys[row],xs[col+1],ys[row+1])
 part=im.crop(rect); target=out/(name+'.png');part.save(target)
 records.append({'id':name,'file':target.relative_to(ROOT).as_posix(),
  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':part.width,'height':part.height,
  'alphaExtrema':part.getchannel('A').getextrema(),
  'derivedFrom':{'file':'assets/ui/qdao-ui-icons-v3.png','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
   'record':'assets/ui/qdao-ui-icons-v3.png.generation.json'},
  'operation':{'type':'native-pixel-crop','sourceRectLTRB':rect,'resampled':False,'newModelGeneration':False},
  'status':'production-candidate-awaiting-in-game-visual-check'})
(out/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(records)} PNG slices; source native {im.width}x{im.height}')
