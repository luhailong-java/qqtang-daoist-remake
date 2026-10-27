from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FAMILY = OUT.name

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

batch = sys.argv[1]
ids = [int(x) for x in sys.argv[2:]]
assert batch.startswith('batch-') and 1 <= len(ids) <= 6 and len(set(ids)) == len(ids)
index_path = ROOT / 'assets/maps/production-index.json'
index = json.loads(index_path.read_text(encoding='utf-8-sig'))
by_id = {x['elementId']: x for x in index['elements'] if x.get('family') == FAMILY}
folder = OUT / batch
folder.mkdir(parents=True, exist_ok=True)
target = folder / 'structure-reference.png'
assert not target.exists(), 'Use a new batch directory; existing contact is retained.'
canvas = Image.new('RGB', (1536, 1024), '#f2f5f2')
draw = ImageDraw.Draw(canvas)
font_path = Path('C:/Windows/Fonts/arial.ttf')
font = ImageFont.truetype(str(font_path), 22)
small = ImageFont.truetype(str(font_path), 18)
items = []
columns = 2 if len(ids) <= 4 else 3
cell_width = 1536 // columns
inspection_scale = min(4.0, (cell_width-72) / max(by_id[x]['selectedFrameSize'][0] for x in ids), 330 / max(by_id[x]['selectedFrameSize'][1] for x in ids))
inspection_scale = int(inspection_scale * 100) / 100
for i, element_id in enumerate(ids):
    e = by_id[element_id]
    ref = ROOT / e['referencePng']['file']
    assert sha(ref) == e['referencePng']['sha256']
    with Image.open(ref) as source:
        source.load()
        assert list(source.size) == e['selectedFrameSize']
        rgba = source.convert('RGBA')
    col, row = i % columns, i // columns
    ox, oy = col * cell_width, row * 512
    draw.rectangle((ox+2, oy+2, ox+cell_width-3, oy+509), outline='#829788', width=2)
    draw.text((ox+18,oy+16), f'{FAMILY.upper()} ID {element_id} | STRUCTURE ONLY', fill='#183e34', font=font)
    draw.text((ox+18,oy+52), f'Native frame {rgba.width}x{rgba.height} px | footprint {e["footprintCells"][0]}x{e["footprintCells"][1]} cells', fill='#343d38', font=small)
    draw.text((ox+18,oy+80), f'raw element offset {e["mapElemOffsetRaw"]}; frame offset {e["selectedFrameOffsetRaw"]}', fill='#343d38', font=small)
    display = rgba.resize((round(rgba.width*inspection_scale),round(rgba.height*inspection_scale)), Image.Resampling.NEAREST)
    x, y = ox+(cell_width-display.width)//2, oy+452-display.height
    canvas.paste(display, (x,y), display)
    draw.rectangle((x-1,y-1,x+display.width,y+display.height), outline='#8ea9a0', width=1)
    draw.text((ox+18,oy+474), f'{inspection_scale:g}x inspection only; anchors UNVERIFIED', fill='#a14426', font=small)
    items.append({'elementId':element_id,'family':FAMILY,'candidatePath':e['candidatePath'],'idMapping':e['familyMappingStatus'],'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameSize':e['selectedFrameSize'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'referencePng':e['referencePng'],'visualGroupId':e['visualGroupId'],'contactCellLTRB':[ox,oy,ox+cell_width,oy+512],'contactSourceFrameLTRB':[x,y,x+display.width,y+display.height],'inspectionUniformScale':inspection_scale,'inspectionResample':'NEAREST','anchorStatus':'unverified-not-applied','accepted':False})
canvas.save(target)
plan={'schemaVersion':1,'batch':batch,'family':FAMILY,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'sourceProductionIndexSHA256':sha(index_path),'contact':{'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':1536,'height':1024,'source':'mechanical placement of existing reference pixels, text and frame outlines only; not generated art; source pixels not runtime art'},'pieces':items,'invariants':['Do not modify map data, footprint, gridAttr, element offset or selected frame offset.','Source package authenticity, ID lookup and anchors remain unverified.','Generate own surface art with same structure, orientation and proportions; no UI/person/text in artwork.','Export canvas is selected native reference frame multiplied uniformly by four; scaling is not native generation.']}
(folder/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan':str(folder/'plan.json'),'contact':str(target),'ids':ids,'sha256':sha(target)},ensure_ascii=True))
