"""Slice whole generated UI subjects using transparent ownership gutters."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def cuts(alpha, count, axis):
    extent = alpha.width if axis == 0 else alpha.height
    other = alpha.height if axis == 0 else alpha.width
    result = [0]
    for i in range(1, count):
        lo, hi = round((i-.25)*extent/count), round((i+.25)*extent/count)
        runs, start = [], None
        for pos in range(lo, hi+1):
            box = (pos,0,pos+1,other) if axis == 0 else (0,pos,other,pos+1)
            clear = pos < hi and alpha.crop(box).getextrema()[1] < 8
            if clear and start is None:
                start = pos
            if not clear and start is not None:
                runs.append((pos-start,start,pos));start = None
        if not runs:
            raise ValueError('No transparent ownership gutter; a measured manual split is required')
        _, start, end = max(runs)
        result.append((start+end)//2)
    return result+[extent]


def save_image(path, image, check):
    if check:
        old = Image.open(path).convert('RGBA')
        if old.size != image.size or old.tobytes() != image.tobytes():
            raise ValueError(f'Cutout replay differs: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, optimize=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    check=parser.parse_args().check
    sheets={'rank-bronze-v2':(3,3),'rank-silver-v1':(3,3),'rank-gold-v1':(3,3),'mode-specials-v1':(3,2)}
    records=[]
    for stem,(cols,rows) in sheets.items():
        source=HERE/'masters'/f'{stem}.png';image=Image.open(source).convert('RGBA');alpha=image.getchannel('A')
        if alpha.getextrema()[0] != 0 or alpha.getextrema()[1] < 240:
            raise ValueError('Generated source is not a genuine alpha cutout')
        xs,ys=cuts(alpha,cols,0),cuts(alpha,rows,1)
        for y in range(rows):
            for x in range(cols):
                cell=(xs[x],ys[y],xs[x+1],ys[y+1]);piece=image.crop(cell);a=piece.getchannel('A')
                bounds=a.point(lambda v:255 if v>=8 else 0).getbbox()
                if not bounds:
                    raise ValueError('Empty generated subject')
                l,t,r,b=bounds;crop=(max(0,l-1),max(0,t-1),min(piece.width,r+1),min(piece.height,b+1))
                excluded=[]
                for box in ((0,0,piece.width,crop[1]),(0,crop[3],piece.width,piece.height),
                            (0,crop[1],crop[0],crop[3]),(crop[2],crop[1],piece.width,crop[3])):
                    if box[2]>box[0] and box[3]>box[1]:excluded.append(a.crop(box).getextrema()[1])
                if max(excluded,default=0)>=8:raise ValueError('Visible subject would be cut')
                out=HERE/'cutouts'/f'{stem}-{y*cols+x:02}.png';save_image(out,piece.crop(crop),check)
                records.append({**record(out),'source':record(source),'generationRecord':record(source.with_suffix('.png.generation.json')),
                    'grid':[cols,rows],'ownershipCutsX':xs,'ownershipCutsY':ys,'sourceCell':list(cell),
                    'contentCropWithinCell':list(crop),'alphaThreshold':8,'excludedMaxAlpha':max(excluded,default=0),
                    'operation':'Whole subject crop through alpha<8 gutters; no recoloring, subject redraw, component deletion or resampling',
                    'visualAccepted':False,'nativeRuntimeVerified':False})
    data={'schemaVersion':1,'processor':record(Path(__file__)),'subjects':records,'visualAccepted':False}
    path=HERE/'cutouts.json'
    if check:
        if json.loads(path.read_bytes()) != data:raise ValueError('Cutout metadata replay differs')
    else:path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'cutouts':len(records),'replay':check}))


if __name__=='__main__':main()
