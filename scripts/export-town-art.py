"""Crop model-painted props; fit uniformly into source-matched 4x canvases.

This is a mechanical export, never a native-detail or exact-anchor assertion.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'assets/maps/town'
ref=json.loads((ROOT/'references/qqtang-map-data/visual-reference/manifest.json').read_text(encoding='utf-8'))
# The reference ID-to-file lookup remains a filename inference, not a proven
# client lookup. Fixed render boxes below are the inspected candidate frames.
items=[
 (3002,'pavement-light','b',(89,55,482,452),(40,40)),
 (3003,'pavement-dark','b',(571,55,968,453),(40,40)),
 (3004,'drum','a',(455,574,794,938),(42,54)),
 (3007,'house-gold','a',(40,53,389,474),(43,58)),
 (3008,'house-grey','a',(477,54,835,473),(43,58)),
 (3009,'house-jade','a',(1017,53,1376,474),(43,58)),
 (3010,'shrub','a',(50,568,376,932),(43,53)),
 (3014,'pedestal-blue','b',(1090,96,1425,445),(43,53)),
 (3015,'pedestal-jade','b',(113,571,456,928),(43,53)),
 (3019,'courtyard-shop','a',(830,537,1518,963),(161,110)),
 (3020,'lantern-column','b',(581,500,965,954),(40,54)),
]
records=[]
out=base/'pieces';out.mkdir(exist_ok=True)
for ident,name,sheet,rect,size in items:
 source=base/f'props-{sheet}-v3.png'
 im=Image.open(source).convert('RGBA');part=im.crop(rect)
 if ident not in (3002,3003):
  box=part.getchannel('A').point(lambda a:255 if a>2 else 0).getbbox()
  part=part.crop(box)
  rect=(rect[0]+box[0],rect[1]+box[1],rect[0]+box[2],rect[1]+box[3])
 target_size=(size[0]*4,size[1]*4)
 scale=min(target_size[0]/part.width,target_size[1]/part.height)
 scaled=part.resize((round(part.width*scale),round(part.height*scale)),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',target_size)
 # Bottom-align the artwork within its prescribed visible-frame rectangle.
 placement=((target_size[0]-scaled.width)//2,target_size[1]-scaled.height)
 canvas.alpha_composite(scaled,placement)
 target=out/f'{ident}-{name}.png';canvas.save(target)
 r={'elementId':ident,'idMapping':'candidate-filename-inference','file':target.relative_to(ROOT).as_posix(),
  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':canvas.width,'height':canvas.height,
  'worldFrameWidth':size[0],'worldFrameHeight':size[1],'exportDensity':4,
  'derivedFrom':{'file':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
   'generationRecord':source.relative_to(ROOT).as_posix()+'.generation.json'},
  'operation':{'type':'crop-uniform-fit-bottom-align','sourceRectLTRB':rect,'uniformScale':scale,
   'placementPx':placement,'resampled':True,'newModelGeneration':False},
  'alphaExtrema':canvas.getchannel('A').getextrema(),'geometryAccepted':False,
  'status':'painted-candidate-awaiting-source-lookup-anchor-and-in-game-validation',
  'seamlessVerified':False if ident in (3002,3003) else None}
 target.with_suffix('.png.provenance.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 records.append(r)
(base/'art.json').write_text(json.dumps({'schemaVersion':1,'tilePixels':40,
 'tilePixelEvidence':'community logic constant and native reference ground frames, official specification unverified',
 'status':'production-candidates','pieces':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'paintedProps':len(records),'exportDensity':4,'exactPixelArtMatchClaimed':False}))
