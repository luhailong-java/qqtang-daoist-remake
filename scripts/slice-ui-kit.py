"""Mechanical PNG crops only; preserves source alpha and native pixels."""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/ui/qdao-ui-kit-v3.png'
im=Image.open(source).convert('RGBA')
regions={
 'window-frame':(0,85,540,630),
 'paper-card':(540,120,977,600),
 'title-plaque':(977,210,1536,500),
 'primary-normal':(0,660,512,910),
 'primary-hover':(512,660,1024,910),
 'primary-pressed':(1024,660,1536,910),
}
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
records=[]
for name,region in regions.items():
 part=im.crop(region)
 # Native crop tight to pixels above alpha=2, plus two transparent pixels.
 box=part.getchannel('A').point(lambda a:255 if a>2 else 0).getbbox()
 box=(max(0,box[0]-2),max(0,box[1]-2),min(part.width,box[2]+2),min(part.height,box[3]+2))
 crop=(region[0]+box[0],region[1]+box[1],region[0]+box[2],region[1]+box[3])
 part=im.crop(crop)
 target=source.parent/(name+'.png')
 part.save(target)
 record={'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
 'width':part.width,'height':part.height,'format':'RGBA PNG','alphaExtrema':part.getchannel('A').getextrema(),
 'derivedFrom':{'file':'assets/ui/qdao-ui-kit-v3.png','sha256':source_hash,'record':'assets/ui/qdao-ui-kit-v3.png.generation.json'},
 'operation':{'type':'crop','sourceRectLTRB':crop,'resampled':False,'newModelGeneration':False},
 'nineSlice':{'sourcePixels':72 if name in ('window-frame','paper-card') else [30,100,30,100]},
 'notes':'Native crop, alpha retained; CSS centre/edge repeat or stretch is display adaptation, not new source detail.'}
 target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 records.append(record)
(source.parent/'slices.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'name':r['file'],'size':[r['width'],r['height']],'alpha':r['alphaExtrema']} for r in records]))
