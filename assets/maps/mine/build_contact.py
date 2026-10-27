"""Review current painted candidates only. This is not a runtime atlas."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
manifest = json.loads((OUT / 'art.json').read_text(encoding='utf-8-sig'))
pieces = manifest['pieces']
cols, cw, ch = 8, 192, 206
sheet = Image.new('RGB', (cw*cols, 70+ch*math.ceil(len(pieces)/cols)), (239,236,226))
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=14)
small = ImageFont.load_default(size=11)
draw.text((15,14), f'{OUT.name.upper()}: {len(pieces)} ELEMENT CANDIDATES / ACCEPTED 0', fill=(20,52,42), font=font)
draw.text((15,38), 'Inspection contact only. Uniform fitting is not in-game placement or geometric acceptance.', fill=(100,58,35), font=small)
sources = []
for i, piece in enumerate(pieces):
    x, y = (i % cols)*cw, 70+(i//cols)*ch
    image = Image.open(ROOT / piece['file']).convert('RGBA')
    scale = min((cw-16)/image.width, (ch-52)/image.height)
    size = (max(1,round(image.width*scale)), max(1,round(image.height*scale)))
    preview = image.resize(size, Image.Resampling.LANCZOS)
    draw.rectangle((x+3,y+3,x+cw-4,y+ch-4), outline=(178,173,158))
    px, py = x+(cw-size[0])//2, y+30+(ch-42-size[1])//2
    sheet.paste(preview, (px,py), preview)
    draw.text((x+10,y+9), f"{piece['elementId']}  {piece['width']}x{piece['height']}", fill=(18,44,35), font=font)
    sources.append({'elementId': piece['elementId'], 'file': piece['file'], 'sha256': piece['sha256'], 'inspectionUniformScale': scale, 'contactCellLTRB': [x,y,x+cw,y+ch]})
path = OUT / 'candidate-contact.png'
sheet.save(path)
record = {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'operation': 'labelled-contact-of-current-ai-painted-candidates-uniform-inspection-fit-only', 'newModelGeneration': False, 'runtimeAsset': False, 'inGameValidation': False, 'width': sheet.width, 'height': sheet.height, 'derivedFrom': sources}
path.with_suffix('.png.provenance.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'file': record['file'], 'size': sheet.size, 'hash': record['sha256']}))
