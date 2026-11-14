"""Own browser-frame chrome; external page content and navigation stay separate."""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAINT_INPUTS = {}
PATHS = {
    'object/ui/web/bg_web.img': ('web-upper-strip', None),
    'object/ui/web/btn_back_hit.img': ('web-button-back-hit', '后退'),
    'object/ui/web/btn_backward.img': ('web-button-back', '后退'),
    'object/ui/web/btn_cross.img': ('web-cross', None),
    'object/ui/web/btn_forward.img': ('web-button-forward', '前进'),
    'object/ui/web/btn_forward_hit.img': ('web-button-forward-hit', '前进'),
    'object/ui/web/btn_leave.img': ('web-button-leave', '返回游戏'),
    'object/ui/web/btn_return_hit.img': ('web-button-return-hit', '返回游戏'),
    'object/ui/web/frame_webpage_b.img': ('web-lower-strip', None),
    'object/ui/web/webPannel.img': ('web-panel', None),
}
STRUCTURAL_ALPHA_INPUTS = {
    f'{kind}-{index:02}': 'assets/native-client-ui/web-controls-reference/frames/web/'
        + path.rsplit('/',1)[1].removesuffix('.img').lower() + f'/frame-{index:03}.png'
    for path,(kind,_) in PATHS.items()
    for index in range(3 if kind.startswith('web-button') or kind=='web-cross' else 1)
}
VISUAL_MAPPING_ASSUMPTIONS = [
    'The four inspected inert modules have no exact literal binding for these ten source image paths.',
    'Browser chrome is repainted by native source path. External HTML, URLs, click callbacks and live page contents are not replaced by this renderer.',
    'Stored three-position button appearance follows the source rasters; active engine state interpretation remains unverified.',
]


@lru_cache(maxsize=24)
def alpha(kind,index):
    with Image.open(ROOT/STRUCTURAL_ALPHA_INPUTS[f'{kind}-{index:02}']) as image:
        return image.getchannel('A').copy()


def render(kind,label,index,size,paints,font_path,nine_slice,scaled):
    if kind=='web-panel':
        out=nine_slice(scaled(paints['panel'],(132,124)),size,18)
    else:
        state=('normal','hover','pressed')[index] if kind.startswith('web-button') or kind=='web-cross' else 'normal'
        out=Image.new('RGBA',size,'#245544')
        out.alpha_composite(scaled(paints[state].crop((90,35,400,110)),size))
        if kind.startswith('web-button') or kind=='web-cross':
            out=ImageEnhance.Brightness(out).enhance((0.90,1.20,0.75)[index])
        draw=ImageDraw.Draw(out)
        if kind in ('web-upper-strip','web-lower-strip'):
            for y in (1,size[1]-2):
                draw.line((0,y,size[0]-1,y),fill='#c6ac70',width=1)
        elif kind=='web-cross':
            draw.ellipse((1,1,size[0]-2,size[1]-2),outline='#c6ac70',width=1)
            for coords in ((7,7,size[0]-8,size[1]-8),(size[0]-8,7,7,size[1]-8)):
                draw.line(coords,fill='#fff3d5',width=2)
        elif kind.startswith('web-button'):
            draw.rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=4,outline='#c6ac70')
            direction=-1 if 'back' in kind else 1 if 'forward' in kind else 0
            if direction:
                x=8 if direction<0 else size[0]-9
                draw.polygon(((x-3*direction,size[1]//2-4),(x+3*direction,size[1]//2),(x-3*direction,size[1]//2+4)),fill='#eee0ac')
            draw.text((size[0]//2+(4 if direction<0 else -4 if direction>0 else 0),size[1]//2),label,
                      font=ImageFont.truetype(str(font_path),10),anchor='mm',fill='#fff3d5',stroke_width=1,stroke_fill='#254d3e')
        else:
            raise ValueError(f'Unknown web UI renderer kind {kind}')
    source_alpha=alpha(kind,index)
    if source_alpha.size!=size:
        raise ValueError('Native browser chrome alpha extent changed')
    out.putalpha(source_alpha)
    return out
