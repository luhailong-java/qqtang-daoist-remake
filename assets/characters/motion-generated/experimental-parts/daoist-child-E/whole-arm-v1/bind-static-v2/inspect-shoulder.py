"""One native torso-region crop, nearest4x for manual ownership inspection only."""
from pathlib import Path
from PIL import Image
import hashlib,json
BASE=Path(__file__).resolve().parent
SOURCE=BASE.parent.parent/'parts-v1'/'torso_pelvis.png'
im=Image.open(SOURCE).convert('RGBA')
roi=[18,25,145,190]
crop=im.crop(roi)
bg=Image.new('RGBA',crop.size,(248,242,225,255));bg.alpha_composite(crop)
out=BASE/'torso-shoulder-inspection-4x.png'
bg.convert('RGB').resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST).save(out)
record={'file':out.name,'source':str(SOURCE),'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'sourceROI':roi,'sourceCropSize':list(crop.size),'exportSize':[crop.width*4,crop.height*4],
 'operation':'Nearest4x native torso crop on ivory for manual visual polygon ownership inspection only, no new detail/artwork.',
 'newModelGeneration':False,'isRuntimeArt':False}
out.with_suffix('.png.source.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
