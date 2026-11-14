"""Own47 loose UI control rasters; retain132 native slots including one empty."""
from functools import lru_cache
from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'assets/native-client-ui/loose-controls-reference'
REFERENCE_MANIFEST = REFERENCE + '/manifest.json'
RENDERER_PREFIX = 'loosecontrols-'
REFERENCE_INPUTS = [REFERENCE + '/dynamic-layout-evidence.json']
PAINT_INPUTS = {'loosecontrols-play': 'assets/ui/action-icons-20261112/play.png'}
# Every family/slot below was observed from the pinned native source images.
ROWS = [
    ('face/biaoq_you', 'arrow3', 'right', 'source', 3),
    ('face/biaoq_zuo', 'arrow3', 'left', 'source', 3),
    ('face/biaoqingxuandan_di', 'face-menu', None, 'source', 1),
    ('face/btn_member', 'face-tab', '会员', 'source', 3),
    ('face/btn_normal', 'face-tab', '普通', 'source', 3),
    ('game/chatpopo1', 'chat-bubble', None, 'source', 1),
    ('game/chatpopo2', 'chat-bubble', None, 'source', 1),
    ('game/chatpopo3', 'chat-bubble', None, 'source', 1),
    ('gameChat/anniu_biaoqing', 'chat-button', 'smile', 'redraw', 2),
    ('gameChat/anniu_bugle', 'chat-button', 'horn', 'redraw', 2),
    ('gameChat/anniu_bugle_hit', 'chat-button', 'horn-hit', 'redraw', 1),
    ('gameChat/anniu_bugle_none', 'chat-button', 'horn-none', 'redraw', 1),
    ('gameChat/anniu_bugle_normal', 'chat-button', 'horn-normal', 'redraw', 1),
    ('gameChat/anniu_fasong', 'chat-button', 'send', 'redraw', 2),
    ('gameChat/duihuakuang', 'chat-slice', None, 'source', 3),
    ('gameChat/liaotianshurukuang_di', 'chat-input', None, 'source', 1),
    ('number/fenye', 'numeric', '/', 'redraw', 1),
    ('number/itemNum', 'numeric', 'digits', 'redraw', 10),
    ('number/num', 'numeric', 'digits-colon', 'redraw', 11),
    ('number/youxibi_shuzi', 'numeric', 'digits-underscore-point', 'redraw', 12),
    ('selRoom/diamond_bk', 'gem', 'jade', 'redraw', 14),
    ('selRoom/goldDiamond', 'gem', 'gold', 'redraw', 15),
    ('selRoom/icon/chat', 'room-chat', None, 'redraw', 1),
    ('selRoom/icon/fangjiananniu_suo', 'lock3', None, 'source', 3),
    ('selRoom/icon/nan', 'gender', 'male', 'redraw', 1),
    ('selRoom/icon/nv', 'gender', 'female', 'redraw', 1),
    ('selRoom/icon/tubiao_biaozhun', 'mode', 'whistle', 'redraw', 1),
    ('selRoom/icon/tubiao_ziyou', 'mode', 'flag', 'redraw', 1),
    ('selRoom/mapFilter/mapfilter_selected_dashl', 'selection', None, 'source', 2),
    ('selRoom/recorder/botton_videostart', 'replay', '播放录像', 'source', 2),
    ('selRoom/recorder/channel', 'scroll-channel', None, 'source', 1),
    ('selRoom/recorder/computer_icon', 'file-icon', 'computer', 'redraw', 1),
    ('selRoom/recorder/downarrow', 'arrow1', 'down', 'source', 1),
    ('selRoom/recorder/file_icon', 'file-icon', 'file', 'redraw', 1),
    ('selRoom/recorder/folder_icon', 'file-icon', 'folder', 'redraw', 1),
    ('selRoom/recorder/hardrive_icon', 'file-icon', 'drive', 'redraw', 1),
    ('selRoom/recorder/uparrow', 'arrow1', 'up', 'source', 1),
    ('selRoom/recorder/upbotton', 'parent-folder', None, 'source', 2),
    ('selRoom/room/num_player', 'numeric', 'digits-slash', 'redraw', 11),
    ('selSect/fuwuqizhuangtai', 'server', 'normal', 'redraw', 1),
    ('selSect/fuwuqizhuangtaihong', 'server', 'red', 'redraw', 1),
    ('selSect/netspeed_fast', 'network', '快', 'redraw', 1),
    ('selSect/netspeed_mid', 'network', '中', 'redraw', 1),
    ('selSect/netspeed_slow', 'network', '慢', 'redraw', 1),
    ('selSect/netspeed_test', 'network', '测试中', 'redraw', 1),
    ('selSect/netspeed_unknown', 'network', '未知', 'redraw', 1),
    ('shop/salou', 'hourglass', None, 'redraw', 1),
]
PATHS = {'res/uiRes/' + path + '.img': (RENDERER_PREFIX + path.lower().replace('/', '-').replace('_', '-'), label)
         for path, family, label, alpha, count in ROWS}
SPECS = {kind: {'nativePath': native, 'family': family, 'label': label, 'alpha': alpha, 'count': count}
         for (native, (kind, _)), (_, family, label, alpha, count) in zip(PATHS.items(), ROWS, strict=True)}
STRUCTURAL_ALPHA_INPUTS = {
    f'{kind}-{index:02}': f"{REFERENCE}/source/{native.removeprefix('res/uiRes/').removesuffix('.img').replace('/', '__')}-{index:02}.png"
    for native, (kind, _) in PATHS.items() if SPECS[kind]['alpha'] == 'source'
    for index in range(SPECS[kind]['count'])
    if not (SPECS[kind]['family'] == 'selection' and index == 1)
}
VISUAL_MAPPING_ASSUMPTIONS = [
    'All47 loose controls retain132 declared native slots, with131 nonempty positions. Source map-filter slot1 remains empty; it is never filled as an assumed button state.',
    'Number source positions are separately observed: itemNum0-9, num0-9 plus colon, youxibi0-9 plus bottom baseline and decimal point, room num_player0-9 plus slash, fenye slash. Unproven loader/index semantics remain unknown.',
    'GameChat duihuakuang raw0/1/2 are top/body/tail raster slices, not a normal/hover/pressed animation family.',
    'Structural alpha is source-exact for31 positions;100 glyph/icon/cosmetic positions replace old alpha inside each complete original stored frame. Functional crop/offset/native mode and all nonpixel bytes remain source values.',
    'The blue uiGame input drawcolor51,113,149 at12,4,244,12 and hint words55,20,180,140 require pale paper wells. This is separate from white-caption room chat controls.',
    'Seven loose resources are byte-identical source copies of packed resources, not proven loader aliases. Every loose destination is exported separately.',
    'Gem14/15 samples preserve source slots with own distinct glosses; original durations, live activation, text widths and final user visuals remain unverified.',
]


@lru_cache(maxsize=31)
def source_alpha(kind, index):
    with Image.open(ROOT / STRUCTURAL_ALPHA_INPUTS[f'{kind}-{index:02}']) as picture:
        return picture.getchannel('A').copy()


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    spec = SPECS[kind]
    family = spec['family']
    if not 0 <= index < spec['count'] or family == 'selection' and index == 1:
        raise ValueError('Loose UI source slot is invalid/empty')
    jade, gold, pale, ink = '#244d3f', '#c9ad70', '#fff3d6', '#254d3f'
    w, h = size
    factor = 4

    def surface(bright=False):
        texture = paints['hover' if bright else 'normal']
        return scaled(texture.crop((90, 35, 400, 110)), size)

    def font_raster(text, maximum=14, color=pale, edge=1):
        out = Image.new('RGBA', (w * factor, h * factor))
        draw = ImageDraw.Draw(out)
        stroke = edge * factor
        for fs in range(maximum, 3, -1):
            font = ImageFont.truetype(str(font_path), fs * factor)
            box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
            if box[2] - box[0] <= max(1, w - 1) * factor and box[3] - box[1] <= max(1, h - 1) * factor:
                break
        origin = ((out.width - box[2] - box[0]) // 2, (out.height - box[3] - box[1]) // 2)
        draw.text(origin, text, font=font, fill=color, stroke_width=stroke, stroke_fill=ink)
        return scaled(out, size)

    def symbol_canvas():
        return Image.new('RGBA', (w * factor, h * factor))

    def small_button(bright=False):
        out = surface(bright)
        ImageDraw.Draw(out).rounded_rectangle((0, 0, w - 1, h - 1), radius=min(4, h // 4), outline=gold)
        return out

    if family in ('arrow3', 'arrow1'):
        out = small_button(index == 1)
        d = ImageDraw.Draw(out)
        x, y = w // 2, h // 2 + (index == 2)
        vertices = {'right': ((x-3,y-5),(x+4,y),(x-3,y+5)),
                    'left': ((x+3,y-5),(x-4,y),(x+3,y+5)),
                    'up': ((x-4,y+2),(x,y-3),(x+4,y+2)),
                    'down': ((x-4,y-2),(x,y+3),(x+4,y-2))}[label]
        d.polygon(vertices, fill=pale)
    elif family == 'face-menu':
        out = Image.new('RGBA',size,'#f3ead2')
        out.alpha_composite(nine_slice(scaled(paints['panel'], (132,124)), size, 18))
        d = ImageDraw.Draw(out)
        d.rounded_rectangle((4,4,168,113), 3, fill=jade, outline=gold)
        for x in (31,58,86,113,140):
            d.line((x,5,x,112), fill='#6c916e')
        for y in (31,58,86):
            d.line((5,y,167,y), fill='#6c916e')
    elif family == 'face-tab':
        out = small_button(index == 1)
        if index == 2:
            out = ImageEnhance.Brightness(out).enhance(0.88)
        text = font_raster(label, 12)
        out.alpha_composite(text, (0, 1 if index == 2 else 0))
    elif family == 'chat-bubble':
        out = Image.new('RGBA', size, '#f3ead2')
        left = 42 if h > 100 else 34
        body = nine_slice(scaled(paints['panel'],(132,124)), (w-left,h), 18)
        out.alpha_composite(body, (left,0))
        d = ImageDraw.Draw(out)
        d.polygon(((0,round(h*.79)),(left+1,round(h*.56)),(left+1,round(h*.72))), fill='#f3ead2', outline=gold)
    elif family == 'chat-button':
        bright = index == 1 or label.endswith('normal') or label.endswith('none')
        out = small_button(bright)
        d = ImageDraw.Draw(out)
        if label == 'smile':
            d.ellipse((4,2,14,13),fill=pale)
            d.point((7,6), fill=ink);d.point((11,6), fill=ink)
            d.arc((6,6,12,11),0,180,fill=ink)
        elif label == 'send':
            d.rounded_rectangle((3,3,15,11),3,fill=pale)
            d.polygon(((6,10),(6,14),(10,10)), fill=pale)
            for x in (6,9,12): d.point((x,7),fill=ink)
        else:
            d.polygon(((4,5),(8,5),(13,2),(13,12),(8,9),(4,9)),fill=gold,outline=pale)
            d.line((7,9,8,13), fill=pale, width=2)
            if not label.endswith('none'): d.arc((12,3,17,11),270,90,fill=pale)
            if label.endswith('none'): out=ImageEnhance.Color(out).enhance(0.05)
        if label.endswith('hit'): out=ImageEnhance.Brightness(out).enhance(1.16)
    elif family == 'chat-slice':
        out = Image.new('RGBA',size,'#f3ead2');d=ImageDraw.Draw(out)
        if index == 0: d.line((0,0,w-1,0),fill=gold,width=2)
        if index == 1:
            d.line((0,0,0,h-1),fill=gold);d.line((w-1,0,w-1,h-1),fill=gold)
        if index == 2:
            d.line((0,0,w-1,0),fill=gold,width=2)
            d.line((18,0,18,h-2),fill=gold)
    elif family == 'chat-input':
        out = surface();d=ImageDraw.Draw(out)
        d.rounded_rectangle((7,2,259,19),4,fill='#fff8e6',outline=gold)
        for x in (263,285,307): d.rounded_rectangle((x,2,x+20,19),3,fill=jade,outline=gold)
    elif family == 'numeric':
        if label == '/': text='/'
        elif index < 10: text=str(index)
        else: text={'digits-colon':':','digits-slash':'/','digits-underscore-point':'_' if index == 10 else '.'}[label]
        if label == 'digits-underscore-point' and index == 10:
            # Source is a bottom horizontal baseline:7x1 at off1,12.
            out = Image.new('RGBA',size,pale)
        elif label == 'digits-underscore-point' and index == 11:
            out=Image.new('RGBA',size,pale)
        elif text == '1':
            out=symbol_canvas();d=ImageDraw.Draw(out)
            color='#e6c781' if label in ('digits','digits-colon') else pale
            cx=w*factor//2
            if w <= 2:
                d.line((cx,0,cx,h*factor-1),fill=color,width=factor)
            else:
                thickness=factor if w<7 else factor+1
                stem=(max(0,cx-2*factor),3*factor,cx,factor,cx,(h-2)*factor)
                foot=(max(0,cx-2*factor),(h-2)*factor,min(w*factor-1,cx+2*factor),(h-2)*factor)
                for stroke,fill in ((thickness+2*factor,ink),(thickness,color)):
                    d.line(stem,fill=fill,width=stroke);d.line(foot,fill=fill,width=stroke)
            out=scaled(out,size)
        elif text == ':':
            out=symbol_canvas();d=ImageDraw.Draw(out)
            cx=w*factor//2;radius=max(2,factor//2)
            for cy in (2*factor,(h-3)*factor):
                d.ellipse((cx-radius-factor,cy-radius-factor,cx+radius+factor,cy+radius+factor),fill=ink)
                d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill='#e6c781')
            out=scaled(out,size)
        else:
            out=font_raster(text,17 if label == 'digits-slash' else 14,
                            '#e6c781' if label in ('digits','digits-colon') else pale,
                            0 if label == 'digits-underscore-point' else 1)
    elif family == 'gem':
        out=symbol_canvas();d=ImageDraw.Draw(out)
        points=((2,4),(5,1),(12,1),(15,4),(8,13))
        d.polygon(tuple((x*factor,y*factor) for x,y in points),fill='#b7caa1' if label=='jade' else '#e5c77d',outline=gold,width=3)
        d.polygon(((2*factor,4*factor),(8*factor,6*factor),(8*factor,13*factor)),fill='#6da88c' if label=='jade' else '#aa804b')
        d.polygon(((5*factor,1*factor),(8*factor,6*factor),(12*factor,1*factor)),fill='#f1eed0')
        x,y=(2+index*.91,4) if index < 12 else (8,6+(index-12)*2)
        d.line(((x-1.4)*factor,y*factor,(x+1.4)*factor,y*factor),fill='#fff8db',width=3)
        d.line((x*factor,(y-1.4)*factor,x*factor,(y+1.4)*factor),fill='#fff8db',width=3)
        out=scaled(out,size)
    elif family == 'room-chat':
        out=Image.new('RGBA',size);d=ImageDraw.Draw(out)
        d.rounded_rectangle((6,22,37,46),3,fill=jade,outline=gold,width=2)
        d.polygon(((2,24),(22,8),(42,24)),fill='#7ca183',outline=gold)
        d.rectangle((18,32,26,45),fill=pale,outline=gold)
        d.rounded_rectangle((22,1,47,22),7,fill=pale,outline=gold,width=2)
        d.polygon(((24,18),(23,28),(32,20)),fill=pale)
        for x in (28,34,40): d.ellipse((x,9,x+2,11),fill=ink)
    elif family == 'lock3':
        out=small_button(index==1);d=ImageDraw.Draw(out)
        d.arc((6,3,13,12),180,360,fill=pale,width=2)
        d.rounded_rectangle((5,8,14,17),2,fill=gold,outline=pale)
        d.line((9,11,9,14),fill=ink,width=2)
        if index==2: out=ImageEnhance.Brightness(out).enhance(.9)
    elif family == 'gender':
        out=symbol_canvas();d=ImageDraw.Draw(out)
        color='#a7d3b0' if label=='male' else '#ebc4b2'
        if label=='male':
            d.ellipse((1*factor,5*factor,11*factor,15*factor),outline=color,width=5)
            d.line((10*factor,7*factor,15*factor,2*factor),fill=color,width=5)
            d.line((10*factor,2*factor,15*factor,2*factor,15*factor,7*factor),fill=color,width=5)
        else:
            d.ellipse((1*factor,1*factor,11*factor,11*factor),outline=color,width=5)
            d.line((6*factor,11*factor,6*factor,17*factor),fill=color,width=5)
            d.line((2*factor,14*factor,10*factor,14*factor),fill=color,width=5)
        out=scaled(out,size)
    elif family == 'mode':
        out=Image.new('RGBA',size);d=ImageDraw.Draw(out)
        if label=='whistle':
            d.polygon(((1,7),(9,3),(15,4),(12,9),(9,10),(8,14),(3,14),(1,11)),fill=pale,outline=gold)
            d.rectangle((8,5,11,7),fill=jade)
            d.ellipse((4,9,7,12),fill=jade)
        else:
            d.line((2,0,2,17),fill=gold,width=2)
            d.polygon(((3,1),(16,3),(16,12),(3,10)),fill=pale,outline=gold)
            for x,y in ((5,3),(10,4),(14,7),(6,8)): d.rectangle((x,y,x+2,y+2),fill=jade)
    elif family == 'selection':
        out=Image.new('RGBA',size,'#497b62');d=ImageDraw.Draw(out)
        for x in range(1,w,6):
            d.line((x,0,min(x+3,w-1),0),fill=pale);d.line((x,h-1,min(x+3,w-1),h-1),fill=pale)
        d.line((0,1,0,h-2),fill=gold);d.line((w-1,1,w-1,h-2),fill=gold)
    elif family == 'replay':
        out=Image.new('RGBA',size,jade)
        out.alpha_composite(nine_slice(paints['hover' if index else 'normal'],size,42))
        d=ImageDraw.Draw(out);d.text((w//2-10,h//2),label,font=ImageFont.truetype(str(font_path),14),fill=pale,
                                  anchor='mm',stroke_width=1,stroke_fill=ink)
        with Image.open(ROOT/PAINT_INPUTS['loosecontrols-play']) as p: icon=scaled(p,(18,18))
        out.alpha_composite(icon,(w-25,(h-18)//2))
    elif family == 'scroll-channel':
        out=Image.new('RGBA',size,'#254c3e');d=ImageDraw.Draw(out)
        d.rounded_rectangle((2,0,w-3,h-1),4,fill='#517e62',outline=gold)
    elif family == 'file-icon':
        out=Image.new('RGBA',size);d=ImageDraw.Draw(out)
        if label=='computer':
            d.rounded_rectangle((1,0,w-2,h-5),2,fill=jade,outline=pale)
            d.rectangle((3,3,w-4,h-7),fill='#80a789')
            d.line((w//2,h-4,w//2,h-2),fill=gold,width=2);d.line((1,h-1,w-2,h-1),fill=pale)
        elif label=='file':
            d.rectangle((1,0,w-2,h-1),fill='#f3ead2',outline=gold)
            for y in (4,7,10): d.line((3,y,w-4,y),fill=ink)
        elif label=='folder':
            d.polygon(((0,2),(5,2),(7,4),(w-1,4),(w-2,h-1),(1,h-1)),fill=jade,outline=gold)
            d.line((2,6,w-3,6),fill=pale)
        else:
            d.rounded_rectangle((1,0,w-2,h-1),2,fill=jade,outline=gold)
            d.ellipse((3,3,w-4,h-5),outline=pale);d.point((w-4,h-3),fill=pale)
    elif family == 'parent-folder':
        out=small_button(index==1);d=ImageDraw.Draw(out)
        d.line((8,17,23,17,23,6),fill=pale,width=3)
        d.polygon(((17,9),(23,3),(29,9)),fill=pale)
    elif family == 'server':
        out=Image.new('RGBA',size);d=ImageDraw.Draw(out)
        d.rounded_rectangle((1,0,w-2,h-1),3,fill='#d77e59' if label=='red' else '#a5c899',outline=gold)
        d.line((w//2,3,w//2,h-4),fill=pale,width=1)
    elif family == 'network':
        color={'快':'#a9d997','中':'#e4c47c','慢':'#efa083','测试中':'#b6d6c7','未知':'#dfdccb'}[label]
        out=font_raster(label+('›››' if label in ('快','中','慢') else ''),10,color)
    elif family == 'hourglass':
        out=Image.new('RGBA',size);d=ImageDraw.Draw(out)
        d.rectangle((2,1,w-3,4),fill=gold,outline=pale)
        d.rectangle((2,h-5,w-3,h-2),fill=gold,outline=pale)
        d.polygon(((5,5),(w-6,5),(w-8,14),(w//2+1,h//2),(w-8,h-14),(w-6,h-6),
                   (5,h-6),(7,h-14),(w//2-1,h//2),(7,14)),fill='#6fa68b',outline=gold)
        d.polygon(((8,8),(w-9,8),(w//2,h//2-1)),fill=pale)
        d.polygon(((w//2,h//2+3),(w-9,h-8),(8,h-8)),fill=gold)
    else:
        raise ValueError('Unknown loose native UI family')
    if spec['alpha']=='source':
        alpha=source_alpha(kind,index)
        if alpha.size!=size: raise ValueError('Loose UI structural alpha native size differs')
        out.putalpha(alpha)
    return out
