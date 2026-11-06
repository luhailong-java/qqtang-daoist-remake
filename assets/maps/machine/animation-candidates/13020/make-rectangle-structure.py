"""Actual six selected opaque source strips, x2 nearest-neighbor reference only."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[5]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--element',type=int,default=13020);p.add_argument('--family',default='machine');a=p.parse_args()
OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}'
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'));assert len(context['sourceFrames'])==6
board=Image.new('RGBA',(1440,1040));frames=[];base=None
for ordinal,source in enumerate(context['sourceFrames']):
    im=Image.open(ROOT/source['file']).convert('RGBA');assert im.size==(120,520) and im.getchannel('A').getextrema()==(255,255)
    if base is None:base=im
    diff=ImageChops.difference(base,im)
    rect=[ordinal*240,0,(ordinal+1)*240,1040]
    board.paste(im.resize((240,1040),Image.Resampling.NEAREST),(rect[0],0))
    frames.append({'sourceFrameIndex':source['frameIndex'],'file':source['file'],'sha256':source['sha256'],'referenceRect':rect,
        'RGBAChangeBBoxVsFrame0':list(diff.getbbox(alpha_only=False))if diff.getbbox(alpha_only=False)else None})
path=OUT/'source-full-rectangle-grid.png';assert not path.exists();board.save(path)
(OUT/'source-full-rectangle-grid.source.json').write_text(json.dumps({'elementId':a.element,'file':path.relative_to(ROOT).as_posix(),
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':1440,'height':1040,'sourceFrames':frames,
    'operation':'six source120x520 frames x2 nearest-neighbor without margins or offset application',
    'alphaExtrema':[255,255],'newModelGeneration':False,'referenceOnly':True,'runtimeArt':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(frames))
