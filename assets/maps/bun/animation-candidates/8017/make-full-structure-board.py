"""Nearest-neighbor source-only reference board for one explicit <=6-frame batch."""
from pathlib import Path
from PIL import Image
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[5]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);a=p.parse_args()
OUT=Path(__file__).resolve().parent/a.batch
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'));frames=context['sourceFrames'];assert 1<=len(frames)<=6
board=Image.new('RGBA',(1536,1024),(0,0,0,0));records=[]
for ordinal,f in enumerate(frames):
    image=Image.open(ROOT/f['file']).convert('RGBA');assert image.size==(40,40)
    rect=[ordinal%3*512,ordinal//3*512,(ordinal%3+1)*512,(ordinal//3+1)*512]
    board.paste(image.resize((512,512),Image.Resampling.NEAREST),(rect[0],rect[1]));records.append({'frameIndex':f['frameIndex'],'file':f['file'],'sha256':f['sha256'],'referenceRect':rect})
path=OUT/'source-full-grid.png';assert not path.exists();board.save(path)
record={'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':[1536,1024],
    'operation':'source native 40x40 frames enlarged nearest-neighbor into 512-square inspection cells; no source offset applied',
    'referenceOnly':True,'runtimeArt':False,'newModelGeneration':False,'sourceFrames':records,'unusedCellCount':6-len(frames)}
(OUT/'source-full-grid.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
