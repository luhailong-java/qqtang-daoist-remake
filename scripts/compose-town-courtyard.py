"""Reassemble newly painted floor materials at reference-derived decoration positions.
All output RGB comes from the new AI painting. This is an image composition,
not a newly generated/native-4K image or proof of original-client fidelity.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[1];folder=root/'assets/maps/town'
source=folder/'floor-g-v2.png';im=Image.open(source).convert('RGBA')
reference=root/'references/qqtang-map-data/visual-reference/families/town/frames/candidate-3059-34bdb810e5cd.png'
density=4;canvas=Image.new('RGBA',(2400,1600))
def export_part(box,size):
    return im.crop(box).convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
stone=export_part((0,0,108,108),(160,160))
for y in range(0,1600,160):
    for x in range(0,2400,160):canvas.alpha_composite(stone,(x,y))
# Edge-reference red spans measured in source pixels: column0 y99..175,
# row0 x262..338. Central outer square coordinates remain an inspection candidate.
hbox=(0,99,600,176);vbox=(262,0,339,400);center=(200,38,400,238)
horizontal=export_part((0,356,235,591),(308,308))
vertical=export_part((649,0,888,239),(308,308))
for x in range(0,2400,308):
    width=min(308,2400-x);canvas.alpha_composite(horizontal.crop((0,0,width,308)),(x,hbox[1]*4))
for y in range(0,1600,308):
    height=min(308,1600-y);canvas.alpha_composite(vertical.crop((0,0,308,height)),(vbox[0]*4,y))
square=export_part((539,251,998,690),(800,800));canvas.alpha_composite(square,(center[0]*4,center[1]*4))
target=folder/'pieces/3059-palace-courtyard-floor.png';canvas.save(target)
record={'elementId':3059,'idMapping':'candidate-filename-inference','file':target.relative_to(root).as_posix(),
    'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':2400,'height':1600,
    'worldFrameWidth':600,'worldFrameHeight':400,'exportDensity':4,
    'derivedFrom':[{'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'generationRecord':source.relative_to(root).as_posix()+'.generation.json','purpose':'all newly painted output RGB'},
        {'file':reference.relative_to(root).as_posix(),'sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'purpose':'decoration extent and placement inspection only; no source RGB reused'}],
    'operation':{'type':'existing-image-crop-resize-and-composite','newModelGeneration':False,'resampled':True,
        'stoneSourceRect':[0,0,108,108],'horizontalSourceRect':[0,356,235,591],'verticalSourceRect':[649,0,888,239],
        'centerSourceRect':[539,251,998,690],'sourcePixelColoursReused':False,
        'logicalHorizontalRect':list(hbox),'logicalVerticalRect':list(vbox),'logicalCenterRectCandidate':list(center),
        'centerResizeUniform':False,'centerScaleXY':[800/459,800/439],
        'placementEvidence':'source edge red-colour spans; central square manually inspected, not accepted exact-geometry proof'},
    'alphaExtrema':list(canvas.getchannel('A').getextrema()),'geometryAccepted':False,'seamlessVerified':False,
    'status':'painted-composite-candidate-awaiting-decoration-and-game-validation',
    'warnings':['central-decoration-bounds-and-texture-joins-await-validation','minor-anisotropic-central-carpet-resize-recorded']}
target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
art=json.loads((folder/'art.json').read_text(encoding='utf-8'));art['pieces']=[p for p in art['pieces'] if p['elementId']!=3059];art['pieces'].append(record)
(folder/'art.json').write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'townPieces':len(art['pieces']),'newModelGeneration':False,'geometryAccepted':False}))
