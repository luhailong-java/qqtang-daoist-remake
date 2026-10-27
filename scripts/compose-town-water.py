"""Image-based texture composite using a reference-derived bank-region mask.

No source RGB is used in the exported art. Mask classification remains a
candidate until visually checked; no map cell, footprint or collider is changed.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'assets/maps/town';source=base/'props-b-v3.png'
im=Image.open(source).convert('RGBA')
stone=im.crop((92,59,477,444)).resize((160,160),Image.Resampling.LANCZOS)
water=im.crop((1052,534,1453,935)).resize((160,160),Image.Resampling.LANCZOS)
stone.putalpha(255);water.putalpha(255)
art=json.loads((base/'art.json').read_text(encoding='utf-8'))
ids=[3011,3012,3013,3022,3023,3024,3025,3026]
inventory=json.loads((ROOT/'assets/maps/production-index.json').read_text(encoding='utf-8'))
by_id={p['elementId']:p for p in inventory['elements']}
art['pieces']=[p for p in art['pieces'] if p['elementId'] not in ids]
for ident in ids:
 ref=ROOT/by_id[ident]['referencePng']['file']
 original=Image.open(ref).convert('RGBA');pixels=np.array(original).astype(np.float32)
 r,g,b=pixels[:,:,0],pixels[:,:,1],pixels[:,:,2]
 water_region=(b>r*1.3)&(b>g*.8)&(b>65)
 bank=(~water_region).astype(np.uint8)*255
 mask=Image.fromarray(bank,'L').resize((160,160),Image.Resampling.NEAREST)
 final=Image.composite(stone,water,mask)
 file=base/'pieces'/f'{ident}-pool-bank.png';final.save(file)
 record={'elementId':ident,'idMapping':'candidate-filename-inference','file':file.relative_to(ROOT).as_posix(),
 'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'width':160,'height':160,
 'worldFrameWidth':40,'worldFrameHeight':40,'exportDensity':4,
 'derivedFrom':[{'file':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'generationRecord':source.relative_to(ROOT).as_posix()+'.generation.json','purpose':'new painted stone and water RGB'},
 {'file':ref.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),
 'purpose':'bank-versus-water classification geometry only, no RGB reused'}],
 'operation':{'type':'reference-mask-image-texture-composite','newModelGeneration':False,'resampled':True,
 'stoneSourceRect':[92,59,477,444],'waterSourceRect':[1052,534,1453,935],
 'maskClassifier':'B>1.3R and B>0.8G and B>65 identifies source water; complementary bank mask',
 'logicalMaskSha256':hashlib.sha256(bank.tobytes()).hexdigest(),'logicalMaskSize':[40,40],
 'waterPixelCount':int(water_region.sum()),'bankPixelCount':int((~water_region).sum()),
 'sourcePixelColoursReused':False},
 'alphaExtrema':[255,255],'geometryAccepted':False,
 'status':'image-composite-candidate-awaiting-region-and-seam-visual-validation','seamlessVerified':False}
 file.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 art['pieces'].append(record)
(base/'art.json').write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pieces':len(art['pieces']),'waterComposites':len(ids),'sourceRgbReused':False,'geometryAccepted':False}))
