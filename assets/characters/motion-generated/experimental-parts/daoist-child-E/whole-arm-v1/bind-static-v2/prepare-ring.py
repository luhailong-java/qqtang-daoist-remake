"""Manual ring-only ownership cutout; never edits the source torso/arm."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
ownership_path=BASE/'shoulder-ring-ownership.json';spec=json.loads(ownership_path.read_text(encoding='utf-8'))
src=ROOT/spec['source'];raw=src.read_bytes()
if hashlib.sha256(raw).hexdigest()!=spec['sourceSha256']:raise ValueError('Source torso changed')
im=Image.open(src).convert('RGBA')
mask=Image.new('L',im.size,0);d=ImageDraw.Draw(mask)
d.polygon([tuple(p)for p in spec['outerPolygonSource']],fill=255)
d.polygon([tuple(p)for p in spec['excludedInnerHoleSource']],fill=0)
for p in spec['excludedControlPointsSource']:
    if 0<=p[0]<mask.width and 0<=p[1]<mask.height and mask.getpixel(tuple(p))!=0:
        raise ValueError('Selected excluded old white/lower-cloth point')
for p in spec['positiveControlPointsSource']:
    if mask.getpixel(tuple(p))!=255:raise ValueError('Missing intended ring point')
original_alpha=im.getchannel('A')
im.putalpha(ImageChops.multiply(original_alpha,mask))
crop=im.crop(spec['sourceROI']);out=BASE/'torso-shoulder-ring-native.png';crop.save(out)
bg=Image.new('RGBA',crop.size,(248,242,225,255));bg.alpha_composite(crop)
preview=BASE/'torso-shoulder-ring-ivory-4x.png'
bg.convert('RGB').resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST).save(preview)
a=crop.getchannel('A');visible=sum(v>=8 for v in a.tobytes())
record={**spec,'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'nativeCropSize':list(crop.size),'alpha8VisiblePixels':visible,
 'operation':'Exact native torso crop selected by the stored manual compound polygon, no scaling/repaint/feather/color key. Source torso PNG unchanged.',
 'ownershipRecord':ownership_path.relative_to(ROOT).as_posix(),
 'sourceGenerationRecord':(BASE.parent.parent/'parts-master-v1.png.generation.json').relative_to(ROOT).as_posix(),
 'sourceAlphaUnmodifiedForOwnedPixels':True,'runtimeAdopted':False}
out.with_suffix('.png.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
preview.with_suffix('.png.source.json').write_text(json.dumps({'file':preview.name,
 'sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),'derivedFrom':{'file':out.name,'sha256':record['sha256']},
 'operation':'Ivory composite, nearest4x for ownership inspection only; not new detail or runtime asset',
 'newModelGeneration':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'nativeSize':list(crop.size),'alpha8':visible,'sourceUnchanged':hashlib.sha256(src.read_bytes()).hexdigest()==spec['sourceSha256']}))
