"""Inspect only the three current candidates chosen for one repair batch."""
from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
selection=[('pig',9012),('bun',8015),('bun',8016)]
board=Image.new('RGBA',(1536,1024));items=[]
for i,(family,ident)in enumerate(selection):
    manifest=ROOT/f'assets/maps/{family}/art.json';art=json.loads(manifest.read_text(encoding='utf-8'))
    piece=next(p for p in art['pieces']if p['elementId']==ident);file=ROOT/piece['file']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==piece['sha256']
    with Image.open(file)as im:
        rgba=im.convert('RGBA');scale=min(380/im.width,410/im.height)
        display=rgba.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
        x=512*i+(512-display.width)//2;y=460-display.height;board.alpha_composite(display,(x,y))
    items.append({'family':family,'elementId':ident,'currentArtManifest':manifest.relative_to(ROOT).as_posix(),
                  'manifestSHA256AtStart':hashlib.sha256(manifest.read_bytes()).hexdigest(),'currentPiece':piece,
                  'readCurrentFileSHA256':hashlib.sha256(file.read_bytes()).hexdigest(),'inspectionRect':[x,y,x+display.width,y+display.height]})
board.save(OUT/'current-own-reference.png')
(OUT/'before.json').write_text(json.dumps({'items':items,'notRuntimeArt':True,'operation':'current exported candidate frames enlarged uniformly with nearest-neighbor for reference only'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'targetCount':3,'currentCandidateHashesMatch':True,'files':[x['currentPiece']['file']for x in items]}))
