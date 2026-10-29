"""Read only chosen landmark pixels of these four current native crops."""
from pathlib import Path
from PIL import Image
import json
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
crops=json.loads((BASE/'native-crops.json').read_text(encoding='utf-8'))
points=json.loads((BASE/'manual-landmarks.proposal.json').read_text(encoding='utf-8'))['pointsSourceNative']
rows=[]
for part in crops['parts']:
    im=Image.open(ROOT/part['file']).convert('RGBA');roi=part['sourceROI']
    samples={}
    for name,xy in points[part['partId']].items():
        local=(xy[0]-roi[0],xy[1]-roi[1]);samples[name]={'source':xy,'cropLocal':list(local),'rgba':list(im.getpixel(local))}
    rows.append({'part':part['partId'],'points':samples})
    im.close()
print(json.dumps(rows))
