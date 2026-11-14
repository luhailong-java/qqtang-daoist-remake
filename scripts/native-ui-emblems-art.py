"""Own Daoist UI emblems, rank strips, map selectors and cursor candidates."""
import json
import math
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance
ROOT=Path(__file__).resolve().parents[1]
REF='assets/native-client-ui/emblems-reference'
RENDERER_PREFIX='emblems-'
REFERENCE_MANIFEST=f'{REF}/manifest.json'
REFERENCE_INPUTS=[f'{REF}/own-mapping.json',f'{REF}/cutouts.json']
DATA=json.loads((ROOT/REF/'own-mapping.json').read_bytes())
BINDINGS={e['nativePath']:e for e in DATA['items']}
PAINT_INPUTS={f'emblems-art-{i}':p for i,p in enumerate(dict.fromkeys(a['file'] for e in DATA['items'] for a in e['ownArt']))}
ART_GENERATION_RECORDS=[f'{REF}/masters/{s}.png.generation.json' for s in ('rank-bronze-v2','rank-silver-v1','rank-gold-v1','cursor-arrow-v1','cursor-click-v1','cursor-click-pressed-v1','mode-specials-v1')]
@lru_cache(maxsize=None)
def original(path):
    return Image.open(ROOT/path).convert('RGBA')


def visible(image):
    alpha=image.getchannel('A');box=alpha.point(lambda v:255 if v>=8 else 0).getbbox()
    if box is None:raise ValueError('Empty own UI artwork')
    l,t,r,b=box
    return image.crop((max(0,l-1),max(0,t-1),min(image.width,r+1),min(image.height,b+1)))


def fit(image,size,scaled,padding=0):
    image=visible(image);width,height=size
    factor=min(max(1,width-2*padding)/image.width,max(1,height-2*padding)/image.height)
    dims=tuple(max(1,round(v*factor)) for v in image.size)
    out=Image.new('RGBA',size);out.alpha_composite(scaled(image,dims),((width-dims[0])//2,(height-dims[1])//2))
    return out


def gleam(image,index,count):
    # A real moving narrow diagonal sheen, clipped exclusively to own subject Alpha.
    if count<2:return image
    out=image.copy();width,height=image.size
    stripe=Image.new('RGBA',image.size);draw=ImageDraw.Draw(stripe)
    x=-height+round((width+height+4)*index/(count-1))
    draw.polygon(((x,0),(x+2,0),(x+height+2,height),(x+height,height)),fill=(255,250,225,150))
    stripe.putalpha(ImageChops.multiply(stripe.getchannel('A'),image.getchannel('A')))
    out.alpha_composite(stripe)
    return out


def strip(label,size):
    # Native UI pips/cartouches use the project's jade/gold/ivory control vocabulary.
    stem=Path(label).stem;family,level=stem[0],int(stem[1:])
    family='c' if family=='d' else family
    colors=('#d8dad5','#b7a5da','#79bd88','#6b9fcb','#dca560','#cb6e64')
    width,height=size;out=Image.new('RGBA',size);draw=ImageDraw.Draw(out)
    fill=colors[level-1];metal='#c5cbd0' if family=='a' else '#c8aa65'
    if family in ('a','b','t'):
        n=level if family=='t' else min(3,1+(level-1)//2)
        draw.rounded_rectangle((0,max(0,height//2-2),width-1,height-1),radius=2,fill='#355d4e',outline=metal)
        for i in range(n):
            cx=round((i+.5)*width/n);r=max(1,min(3,height//2))
            draw.polygon(((cx-r,height//2),(cx,max(0,height//2-r)),(cx+r,height//2),(cx,min(height-2,height//2+r))),fill=fill,outline=metal)
        if family=='b':draw.line((1,height-1,width-2,height-1),fill='#f4df94')
    else:
        draw.rounded_rectangle((0,0,width-1,height-1),radius=2,fill='#315546',outline=metal)
        n={'c':2,'e':3,'f':1}[family]
        for i in range(n):
            x0=1+round(i*(width-2)/n);x1=round((i+1)*(width-2)/n)
            draw.polygon(((x0,1),(max(x0,x1-1),1),(x1,max(1,height//2)),(max(x0,x1-1),height-2),(x0,height-2)),fill=fill)
    return out


def render(kind,label,index,size,paints,font_path,nine_slice,scaled):
    entry=BINDINGS[label];art=[original(a['file']) for a in entry['ownArt']];stem=Path(label).stem
    if kind=='emblems-tie':return strip(label,size)
    if kind=='emblems-kin':
        if not art:
            out=Image.new('RGBA',size);ImageDraw.Draw(out).rounded_rectangle((1,1,size[0]-2,size[1]-2),radius=3,fill=(82,125,102,151));return out
        return fit(art[0],size,scaled,1)
    if kind=='emblems-map':
        if stem=='all':
            out=Image.new('RGBA',size)
            for i,image in enumerate(art):
                small=fit(image,(10,10),scaled)
                out.alpha_composite(small,((i%2)*5,(i//2)*5))
            return out
        return fit(art[0],size,scaled,0 if min(size)<=15 else 1)
    if kind=='emblems-medal':
        if stem in ('010','020'):
            out=Image.new('RGBA',size);draw=ImageDraw.Draw(out)
            draw.rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=min(2,size[1]//2),fill='#875735',outline='#d39257')
            n=1 if stem=='010' else 2
            for i in range(n):
                x=round((i+1)*size[0]/(n+1));draw.line((x,1,x,max(1,size[1]-2)),fill='#b5d3a5',width=2)
            return out
        count=entry['nativeGeometry']['frameCount']
        image=fit(art[0],size,scaled)
        if int(stem) in (27,28,29):
            # Four native vertical squash windows retain the observed wide/flat sequence.
            image=scaled(visible(art[0]),size)
        return gleam(image,index,count)
    if kind=='emblems-cursor':
        if stem in ('arror','fight'):return gleam(fit(art[0],size,scaled),index,9)
        # Both source gesture masters share their original image coordinates and a common fit.
        boxes=[a.getchannel('A').point(lambda v:255 if v>=8 else 0).getbbox() for a in art]
        box=(min(b[0] for b in boxes)-1,min(b[1] for b in boxes)-1,max(b[2] for b in boxes)+1,max(b[3] for b in boxes)+1)
        full=Image.new('RGBA',(33,26));crop=art[index].crop(box);factor=min(31/crop.width,26/crop.height)
        dims=tuple(max(1,round(v*factor)) for v in crop.size)
        full.alpha_composite(scaled(crop,dims),(1+(31-dims[0])//2,(26-dims[1])//2))
        frame=entry['nativeGeometry']['frames'][index];x,y=frame['frameOffset']
        return full.crop((x,y,x+size[0],y+size[1]))
    raise ValueError(kind)


VISUAL_MAPPING_ASSUMPTIONS=[
 'All mappings are original UI slot reinterpretations. Existing item/map motifs do not establish a world resource or numeric item binding.',
 'The 48 clan choices have distinct own subjects; 000 stays a plain empty-looking swatch without inventing a clan identity.',
 'c01..c06 and d01..d06 are six exact original byte aliases; matching own strips are deliberately shared.',
 'Narrow rank strips extend the original project UI material and pip system; no old lettering or subject alpha is copied.',
 'Medal states retain source windows and indices. Own gleam/squash candidates require visual and timing review.',
 'Cursor arrow has nine material gleam states. Click cursor uses two separately generated extended and bent index gestures, registered in a shared logical canvas.',
 'Native cursor hotspots, GSA loader behavior, source real-time state timing, thresholds and runtime use are not verified.',
]
PATHS = {'object/ui/kintotem/000.img': ('emblems-kin', 'object/ui/kintotem/000.img'), 'object/ui/kintotem/001.img': ('emblems-kin', 'object/ui/kintotem/001.img'), 'object/ui/kintotem/002.img': ('emblems-kin', 'object/ui/kintotem/002.img'), 'object/ui/kintotem/003.img': ('emblems-kin', 'object/ui/kintotem/003.img'), 'object/ui/kintotem/004.img': ('emblems-kin', 'object/ui/kintotem/004.img'), 'object/ui/kintotem/005.img': ('emblems-kin', 'object/ui/kintotem/005.img'), 'object/ui/kintotem/006.img': ('emblems-kin', 'object/ui/kintotem/006.img'), 'object/ui/kintotem/007.img': ('emblems-kin', 'object/ui/kintotem/007.img'), 'object/ui/kintotem/008.img': ('emblems-kin', 'object/ui/kintotem/008.img'), 'object/ui/kintotem/009.img': ('emblems-kin', 'object/ui/kintotem/009.img'), 'object/ui/kintotem/010.img': ('emblems-kin', 'object/ui/kintotem/010.img'), 'object/ui/kintotem/011.img': ('emblems-kin', 'object/ui/kintotem/011.img'), 'object/ui/kintotem/012.img': ('emblems-kin', 'object/ui/kintotem/012.img'), 'object/ui/kintotem/013.img': ('emblems-kin', 'object/ui/kintotem/013.img'), 'object/ui/kintotem/014.img': ('emblems-kin', 'object/ui/kintotem/014.img'), 'object/ui/kintotem/015.img': ('emblems-kin', 'object/ui/kintotem/015.img'), 'object/ui/kintotem/016.img': ('emblems-kin', 'object/ui/kintotem/016.img'), 'object/ui/kintotem/017.img': ('emblems-kin', 'object/ui/kintotem/017.img'), 'object/ui/kintotem/018.img': ('emblems-kin', 'object/ui/kintotem/018.img'), 'object/ui/kintotem/019.img': ('emblems-kin', 'object/ui/kintotem/019.img'), 'object/ui/kintotem/020.img': ('emblems-kin', 'object/ui/kintotem/020.img'), 'object/ui/kintotem/021.img': ('emblems-kin', 'object/ui/kintotem/021.img'), 'object/ui/kintotem/022.img': ('emblems-kin', 'object/ui/kintotem/022.img'), 'object/ui/kintotem/023.img': ('emblems-kin', 'object/ui/kintotem/023.img'), 'object/ui/kintotem/024.img': ('emblems-kin', 'object/ui/kintotem/024.img'), 'object/ui/kintotem/025.img': ('emblems-kin', 'object/ui/kintotem/025.img'), 'object/ui/kintotem/026.img': ('emblems-kin', 'object/ui/kintotem/026.img'), 'object/ui/kintotem/027.img': ('emblems-kin', 'object/ui/kintotem/027.img'), 'object/ui/kintotem/028.img': ('emblems-kin', 'object/ui/kintotem/028.img'), 'object/ui/kintotem/029.img': ('emblems-kin', 'object/ui/kintotem/029.img'), 'object/ui/kintotem/030.img': ('emblems-kin', 'object/ui/kintotem/030.img'), 'object/ui/kintotem/031.img': ('emblems-kin', 'object/ui/kintotem/031.img'), 'object/ui/kintotem/032.img': ('emblems-kin', 'object/ui/kintotem/032.img'), 'object/ui/kintotem/033.img': ('emblems-kin', 'object/ui/kintotem/033.img'), 'object/ui/kintotem/034.img': ('emblems-kin', 'object/ui/kintotem/034.img'), 'object/ui/kintotem/035.img': ('emblems-kin', 'object/ui/kintotem/035.img'), 'object/ui/kintotem/036.img': ('emblems-kin', 'object/ui/kintotem/036.img'), 'object/ui/kintotem/037.img': ('emblems-kin', 'object/ui/kintotem/037.img'), 'object/ui/kintotem/038.img': ('emblems-kin', 'object/ui/kintotem/038.img'), 'object/ui/kintotem/039.img': ('emblems-kin', 'object/ui/kintotem/039.img'), 'object/ui/kintotem/040.img': ('emblems-kin', 'object/ui/kintotem/040.img'), 'object/ui/kintotem/041.img': ('emblems-kin', 'object/ui/kintotem/041.img'), 'object/ui/kintotem/042.img': ('emblems-kin', 'object/ui/kintotem/042.img'), 'object/ui/kintotem/043.img': ('emblems-kin', 'object/ui/kintotem/043.img'), 'object/ui/kintotem/044.img': ('emblems-kin', 'object/ui/kintotem/044.img'), 'object/ui/kintotem/045.img': ('emblems-kin', 'object/ui/kintotem/045.img'), 'object/ui/kintotem/046.img': ('emblems-kin', 'object/ui/kintotem/046.img'), 'object/ui/kintotem/047.img': ('emblems-kin', 'object/ui/kintotem/047.img'), 'object/ui/kintotem/048.img': ('emblems-kin', 'object/ui/kintotem/048.img'), 'object/ui/level/medal/001.img': ('emblems-medal', 'object/ui/level/medal/001.img'), 'object/ui/level/medal/002.img': ('emblems-medal', 'object/ui/level/medal/002.img'), 'object/ui/level/medal/003.img': ('emblems-medal', 'object/ui/level/medal/003.img'), 'object/ui/level/medal/004.img': ('emblems-medal', 'object/ui/level/medal/004.img'), 'object/ui/level/medal/005.img': ('emblems-medal', 'object/ui/level/medal/005.img'), 'object/ui/level/medal/006.img': ('emblems-medal', 'object/ui/level/medal/006.img'), 'object/ui/level/medal/007.img': ('emblems-medal', 'object/ui/level/medal/007.img'), 'object/ui/level/medal/008.img': ('emblems-medal', 'object/ui/level/medal/008.img'), 'object/ui/level/medal/009.img': ('emblems-medal', 'object/ui/level/medal/009.img'), 'object/ui/level/medal/010.img': ('emblems-medal', 'object/ui/level/medal/010.img'), 'object/ui/level/medal/011.img': ('emblems-medal', 'object/ui/level/medal/011.img'), 'object/ui/level/medal/012.img': ('emblems-medal', 'object/ui/level/medal/012.img'), 'object/ui/level/medal/013.img': ('emblems-medal', 'object/ui/level/medal/013.img'), 'object/ui/level/medal/014.img': ('emblems-medal', 'object/ui/level/medal/014.img'), 'object/ui/level/medal/015.img': ('emblems-medal', 'object/ui/level/medal/015.img'), 'object/ui/level/medal/016.img': ('emblems-medal', 'object/ui/level/medal/016.img'), 'object/ui/level/medal/017.img': ('emblems-medal', 'object/ui/level/medal/017.img'), 'object/ui/level/medal/018.img': ('emblems-medal', 'object/ui/level/medal/018.img'), 'object/ui/level/medal/019.img': ('emblems-medal', 'object/ui/level/medal/019.img'), 'object/ui/level/medal/020.img': ('emblems-medal', 'object/ui/level/medal/020.img'), 'object/ui/level/medal/021.img': ('emblems-medal', 'object/ui/level/medal/021.img'), 'object/ui/level/medal/022.img': ('emblems-medal', 'object/ui/level/medal/022.img'), 'object/ui/level/medal/023.img': ('emblems-medal', 'object/ui/level/medal/023.img'), 'object/ui/level/medal/024.img': ('emblems-medal', 'object/ui/level/medal/024.img'), 'object/ui/level/medal/025.img': ('emblems-medal', 'object/ui/level/medal/025.img'), 'object/ui/level/medal/026.img': ('emblems-medal', 'object/ui/level/medal/026.img'), 'object/ui/level/medal/027.img': ('emblems-medal', 'object/ui/level/medal/027.img'), 'object/ui/level/medal/028.img': ('emblems-medal', 'object/ui/level/medal/028.img'), 'object/ui/level/medal/029.img': ('emblems-medal', 'object/ui/level/medal/029.img'), 'object/ui/level/medal/030.img': ('emblems-medal', 'object/ui/level/medal/030.img'), 'object/ui/level/tie/a01.img': ('emblems-tie', 'object/ui/level/tie/a01.img'), 'object/ui/level/tie/a02.img': ('emblems-tie', 'object/ui/level/tie/a02.img'), 'object/ui/level/tie/a03.img': ('emblems-tie', 'object/ui/level/tie/a03.img'), 'object/ui/level/tie/a04.img': ('emblems-tie', 'object/ui/level/tie/a04.img'), 'object/ui/level/tie/a05.img': ('emblems-tie', 'object/ui/level/tie/a05.img'), 'object/ui/level/tie/a06.img': ('emblems-tie', 'object/ui/level/tie/a06.img'), 'object/ui/level/tie/b01.img': ('emblems-tie', 'object/ui/level/tie/b01.img'), 'object/ui/level/tie/b02.img': ('emblems-tie', 'object/ui/level/tie/b02.img'), 'object/ui/level/tie/b03.img': ('emblems-tie', 'object/ui/level/tie/b03.img'), 'object/ui/level/tie/b04.img': ('emblems-tie', 'object/ui/level/tie/b04.img'), 'object/ui/level/tie/b05.img': ('emblems-tie', 'object/ui/level/tie/b05.img'), 'object/ui/level/tie/b06.img': ('emblems-tie', 'object/ui/level/tie/b06.img'), 'object/ui/level/tie/c01.img': ('emblems-tie', 'object/ui/level/tie/c01.img'), 'object/ui/level/tie/c02.img': ('emblems-tie', 'object/ui/level/tie/c02.img'), 'object/ui/level/tie/c03.img': ('emblems-tie', 'object/ui/level/tie/c03.img'), 'object/ui/level/tie/c04.img': ('emblems-tie', 'object/ui/level/tie/c04.img'), 'object/ui/level/tie/c05.img': ('emblems-tie', 'object/ui/level/tie/c05.img'), 'object/ui/level/tie/c06.img': ('emblems-tie', 'object/ui/level/tie/c06.img'), 'object/ui/level/tie/d01.img': ('emblems-tie', 'object/ui/level/tie/d01.img'), 'object/ui/level/tie/d02.img': ('emblems-tie', 'object/ui/level/tie/d02.img'), 'object/ui/level/tie/d03.img': ('emblems-tie', 'object/ui/level/tie/d03.img'), 'object/ui/level/tie/d04.img': ('emblems-tie', 'object/ui/level/tie/d04.img'), 'object/ui/level/tie/d05.img': ('emblems-tie', 'object/ui/level/tie/d05.img'), 'object/ui/level/tie/d06.img': ('emblems-tie', 'object/ui/level/tie/d06.img'), 'object/ui/level/tie/e01.img': ('emblems-tie', 'object/ui/level/tie/e01.img'), 'object/ui/level/tie/e02.img': ('emblems-tie', 'object/ui/level/tie/e02.img'), 'object/ui/level/tie/e03.img': ('emblems-tie', 'object/ui/level/tie/e03.img'), 'object/ui/level/tie/e04.img': ('emblems-tie', 'object/ui/level/tie/e04.img'), 'object/ui/level/tie/e05.img': ('emblems-tie', 'object/ui/level/tie/e05.img'), 'object/ui/level/tie/e06.img': ('emblems-tie', 'object/ui/level/tie/e06.img'), 'object/ui/level/tie/f01.img': ('emblems-tie', 'object/ui/level/tie/f01.img'), 'object/ui/level/tie/f02.img': ('emblems-tie', 'object/ui/level/tie/f02.img'), 'object/ui/level/tie/f03.img': ('emblems-tie', 'object/ui/level/tie/f03.img'), 'object/ui/level/tie/f04.img': ('emblems-tie', 'object/ui/level/tie/f04.img'), 'object/ui/level/tie/f05.img': ('emblems-tie', 'object/ui/level/tie/f05.img'), 'object/ui/level/tie/f06.img': ('emblems-tie', 'object/ui/level/tie/f06.img'), 'object/ui/level/tie/t01.img': ('emblems-tie', 'object/ui/level/tie/t01.img'), 'object/ui/level/tie/t02.img': ('emblems-tie', 'object/ui/level/tie/t02.img'), 'object/ui/level/tie/t03.img': ('emblems-tie', 'object/ui/level/tie/t03.img'), 'object/ui/level/tie/t04.img': ('emblems-tie', 'object/ui/level/tie/t04.img'), 'object/ui/level/tie/t05.img': ('emblems-tie', 'object/ui/level/tie/t05.img'), 'object/ui/level/tie/t06.img': ('emblems-tie', 'object/ui/level/tie/t06.img'), 'object/ui/map/midicon/all.img': ('emblems-map', 'object/ui/map/midicon/all.img'), 'object/ui/map/midicon/bomb.img': ('emblems-map', 'object/ui/map/midicon/bomb.img'), 'object/ui/map/midicon/box.img': ('emblems-map', 'object/ui/map/midicon/box.img'), 'object/ui/map/midicon/bun.img': ('emblems-map', 'object/ui/map/midicon/bun.img'), 'object/ui/map/midicon/desert.img': ('emblems-map', 'object/ui/map/midicon/desert.img'), 'object/ui/map/midicon/field.img': ('emblems-map', 'object/ui/map/midicon/field.img'), 'object/ui/map/midicon/match.img': ('emblems-map', 'object/ui/map/midicon/match.img'), 'object/ui/map/midicon/mine.img': ('emblems-map', 'object/ui/map/midicon/mine.img'), 'object/ui/map/midicon/normal.img': ('emblems-map', 'object/ui/map/midicon/normal.img'), 'object/ui/map/midicon/pig.img': ('emblems-map', 'object/ui/map/midicon/pig.img'), 'object/ui/map/midicon/rand.img': ('emblems-map', 'object/ui/map/midicon/rand.img'), 'object/ui/map/midicon/sculpture.img': ('emblems-map', 'object/ui/map/midicon/sculpture.img'), 'object/ui/map/midicon/snow.img': ('emblems-map', 'object/ui/map/midicon/snow.img'), 'object/ui/map/midicon/tank.img': ('emblems-map', 'object/ui/map/midicon/tank.img'), 'object/ui/map/midicon/town.img': ('emblems-map', 'object/ui/map/midicon/town.img'), 'object/ui/map/midicon/treasure.img': ('emblems-map', 'object/ui/map/midicon/treasure.img'), 'object/ui/map/midicon/water.img': ('emblems-map', 'object/ui/map/midicon/water.img'), 'object/ui/cursor/arror.img': ('emblems-cursor', 'object/ui/cursor/arror.img'), 'object/ui/cursor/dianji.img': ('emblems-cursor', 'object/ui/cursor/dianji.img'), 'object/ui/cursor/fight.gsa': ('emblems-cursor', 'object/ui/cursor/fight.gsa')}
