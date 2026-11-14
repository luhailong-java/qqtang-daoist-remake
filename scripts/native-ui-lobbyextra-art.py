"""Own native lobby chat, notifications, room digits and guide bubbles."""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'assets/native-client-ui/lobbyextra-reference'
PAINT_INPUTS = {'lobbyextra-crown': 'assets/items/hats/morning-courtesy-b/46-coral-jade-cloud-crown.png'}
PATHS = {
    'object/ui/selRoom/btn_commandPrompt.img': ('lobbyextra-command', None),
    'object/ui/selRoom/btn_flexDown.img': ('lobbyextra-flexdown', None),
    'object/ui/selRoom/btn_flexUp.img': ('lobbyextra-flexup', None),
    'object/ui/selRoom/btn_left.img': ('lobbyextra-left', None),
    'object/ui/selRoom/btn_message.img': ('lobbyextra-message', None),
    'object/ui/selRoom/btn_right.img': ('lobbyextra-right', None),
    'object/ui/selRoom/dlg_chatMax.img': ('lobbyextra-chatmax', None),
    'object/ui/selRoom/dlg_chatMin.img': ('lobbyextra-chatmin', None),
    'object/ui/selRoom/dlg_chatNormal.img': ('lobbyextra-chatnormal', None),
    'object/ui/selRoom/icon_vip.img': ('lobbyextra-vip', 'VIP'),
    'object/ui/selRoom/img_popo.img': ('lobbyextra-popo', None),
    'object/ui/selRoom/mask_speaker.img': ('lobbyextra-speaker-mask', None),
    'object/ui/selRoom/num.img': ('lobbyextra-digit', '0123456789'),
    'object/ui/selRoom/tip_GuideMidRight.img': ('lobbyextra-guide-right', None),
    'object/ui/selRoom/tip_GuideMidUnder.img': ('lobbyextra-guide-under', None),
    'object/ui/selRoom/tip_GuideMidUpper.img': ('lobbyextra-guide-upper', None),
    'object/ui/selRoom/tip_enterShop.img': ('lobbyextra-shop-tip', '进入商城'),
}
SOURCE_COUNTS = (4,3,3,4,3,4,1,1,1,1,1,1,10,1,1,1,1)
STRUCTURAL_ALPHA_INPUTS = {
    f'{kind}-{index}': f'{REFERENCE}/frames/{path.casefold().removeprefix("object/ui/").removesuffix(".img")}/frame-{index:03}.png'
    for (path,(kind,_)),count in zip(PATHS.items(),SOURCE_COUNTS,strict=True)
    if kind != 'lobbyextra-digit'
    for index in range(count)
}
DIGIT_LAYOUT = (
    ((10,14),(0,0)), ((6,13),(2,1)), ((10,14),(1,0)), ((10,14),(1,0)),
    ((11,14),(0,0)), ((10,13),(0,1)), ((10,14),(0,0)), ((10,13),(0,1)),
    ((10,14),(0,0)), ((10,14),(0,0)),
)
VISUAL_MAPPING_ASSUMPTIONS = [
    'num.img contains ten separate source positions visibly numbered 0 through 9; no atlas slicing or extra separators are introduced.',
    'Message envelope positions keep their source offsets (0,5),(0,3),(0,4); their runtime notification timing is unknown.',
    'The command button and three blank guide bubbles have no exact path binding in the four inspected modules; they remain same-path candidates.',
    'VIP uses the existing own crown image and newly rasterized VIP letters. Dynamic membership logic is unchanged.',
    'Chat message foreground updates and native speaker-mask blending remain runtime behavior; exact Alpha planes alone do not establish runtime acceptance.',
]


@lru_cache(maxsize=31)
def source_alpha(kind,index):
    with Image.open(ROOT/STRUCTURAL_ALPHA_INPUTS[f'{kind}-{index}']) as image:
        return image.getchannel('A').copy()


def render(kind,label,index,size,paints,font_path,nine_slice,scaled):
    deep, ink, cream, gold = '#244b3e', '#254e40', '#fff3d5', '#c8ad72'
    font = ImageFont.truetype(str(font_path),11)
    if kind == 'lobbyextra-digit':
        if size != DIGIT_LAYOUT[index][0]:
            raise ValueError('Native room digit cropped extent differs')
        # One fixed 13px type size fits every measured source crop, including
        # the six-pixel-wide 1. No per-digit stretching or source glyph mask.
        glyph = Image.new('RGBA',(40,40))
        ImageDraw.Draw(glyph).text((20,20),str(index),font=ImageFont.truetype(str(font_path),13),
                                  fill=cream,stroke_fill=ink,stroke_width=1,anchor='mm')
        glyph = glyph.crop(glyph.getchannel('A').getbbox())
        if glyph.width > size[0] or glyph.height > size[1]:
            raise ValueError('Own room digit would clip in the native crop')
        out = Image.new('RGBA',size)
        out.alpha_composite(glyph,((size[0]-glyph.width)//2,(size[1]-glyph.height)//2))
        return out

    alpha = source_alpha(kind,index)
    if alpha.size != size:
        raise ValueError('Native lobby functional Alpha extent differs')

    def surface(style='normal'):
        out = Image.new('RGBA',size,deep)
        out.alpha_composite(nine_slice(paints['normal' if style=='disabled' else style],size,42))
        if style == 'disabled':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.06)).enhance(0.75)
        return out

    if kind in ('lobbyextra-command','lobbyextra-left','lobbyextra-right'):
        out = surface(('normal','disabled','hover','pressed')[index])
        draw = ImageDraw.Draw(out)
        cx,cy = size[0]//2,size[1]//2
        if kind == 'lobbyextra-command':
            points = ((cx-6,cy-4),(cx+6,cy-4),(cx,cy+5))
        elif kind == 'lobbyextra-left':
            points = ((cx+3,cy-6),(cx+3,cy+6),(cx-3,cy))
        else:
            points = ((cx-3,cy-6),(cx-3,cy+6),(cx+3,cy))
        draw.polygon(points,fill='#cbcfc4' if index==1 else cream,outline=gold)
    elif kind in ('lobbyextra-flexdown','lobbyextra-flexup'):
        out = surface(('normal','hover','pressed')[index])
        draw = ImageDraw.Draw(out)
        cx,cy = size[0]//2,size[1]//2
        points = ((cx-5,cy-3),(cx+5,cy-3),(cx,cy+3)) if kind.endswith('down') else ((cx-5,cy+3),(cx+5,cy+3),(cx,cy-3))
        draw.polygon(points,fill=cream)
    elif kind == 'lobbyextra-message':
        out = surface(('normal','hover','pressed')[index])
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((2,2,size[0]-3,size[1]-3),radius=2,fill='#e6d6a2',outline=gold)
        draw.line(((3,3),(size[0]//2,size[1]//2+1),(size[0]-4,3)),fill=ink,width=1)
        draw.line(((3,size[1]-4),(10,10)),fill=ink,width=1)
        draw.line(((size[0]-4,size[1]-4),(size[0]-11,10)),fill=ink,width=1)
        draw.ellipse((size[0]//2-2,size[1]//2-1,size[0]//2+2,size[1]//2+3),fill='#9c613c')
    elif kind in ('lobbyextra-chatmax','lobbyextra-chatmin','lobbyextra-chatnormal'):
        out = Image.new('RGBA',size,deep)
        strip = scaled(paints['normal'].crop((90,35,400,110)),(size[0],17))
        out.alpha_composite(strip,(0,0))
        draw = ImageDraw.Draw(out)
        draw.line((0,17,size[0]-1,17),fill=gold)
        draw.rectangle((0,18,size[0]-1,size[1]-1),outline='#718569')
        # Native flex buttons at132,2 and173,2 overlay this header.
        # ChatList starts3,20; retain the right-hand scroll gutter.
        draw.line((size[0]-12,22,size[0]-12,size[1]-4),fill='#718569')
    elif kind == 'lobbyextra-vip':
        out = surface()
        icon = paints.get('lobbyextra-crown')
        if icon is None:
            with Image.open(ROOT/PAINT_INPUTS['lobbyextra-crown'])as image:
                icon=image.convert('RGBA')
        icon=icon.crop(icon.getchannel('A').getbbox())
        ratio=min(25/icon.width,22/icon.height)
        icon=scaled(icon,(max(1,round(icon.width*ratio)),max(1,round(icon.height*ratio))))
        out.alpha_composite(icon,(5,(size[1]-icon.height)//2))
        ImageDraw.Draw(out).text((43,size[1]//2),'VIP',font=font,fill=cream,anchor='mm',stroke_width=1,stroke_fill=ink)
    elif kind == 'lobbyextra-popo':
        out=Image.new('RGBA',size,'#e8dfc0')
        draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=5,outline=gold)
        draw.ellipse((3,4,10,11),fill='#b58a44',outline=ink)
        draw.line((7,3,7,12),fill='#f6e8be')
    elif kind == 'lobbyextra-speaker-mask':
        out=Image.new('RGBA',size,'#1e4036')
    elif kind in ('lobbyextra-guide-right','lobbyextra-guide-under','lobbyextra-guide-upper','lobbyextra-shop-tip'):
        out=Image.new('RGBA',size,cream)
        paper=scaled(paints['panel'].crop((170,130,350,320)),size)
        out.alpha_composite(paper)
        # Derive only the structural edge from Alpha; original RGB/captions
        # are never sampled. Padding makes cropped frame edges count too.
        padded=Image.new('L',(size[0]+4,size[1]+4))
        padded.paste(alpha,(2,2))
        interior=padded.filter(ImageFilter.MinFilter(3)).crop((2,2,size[0]+2,size[1]+2))
        rim=ImageChops.subtract(alpha,interior)
        out.alpha_composite(Image.composite(Image.new('RGBA',size,gold),Image.new('RGBA',size),rim))
        if kind == 'lobbyextra-shop-tip':
            ImageDraw.Draw(out).text((size[0]//2,11),label,font=font,fill='#764a31',anchor='mm')
    else:
        raise ValueError(f'Unknown native lobby extra kind {kind}')
    out.putalpha(alpha)
    return out
