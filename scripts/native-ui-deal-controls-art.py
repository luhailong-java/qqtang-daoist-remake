"""Native trading and consignment controls using the project's painted jade kit."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAINT_INPUTS = {'deal-pet': 'assets/ui/semantic-extra/pet-card.png'}
VISUAL_MAPPING_ASSUMPTIONS = [
    {'nativePaths':['object/ui/deal/cancelbtn.img','object/ui/deal/confirmbtn.img'],
     'evidence':'Source image captions are legible; exact path binding was not found in the four inspected inert UI modules.',
     'runtimeBindingVerified':False},
    {'nativePath':'object/ui/deal/lookuppetBtn.img',
     'evidence':'Native PetInfo path binding is confirmed; its smile face is replaced by the existing original pet-card paw crop.',
     'runtimeInteractionVerified':False},
]
PATHS = {
    'object/ui/deal/AgreeBtn.img': ('deal-button', '成交'),
    'object/ui/deal/C2CDealPanel.img': ('deal-exchange-panel', None),
    'object/ui/deal/DisagreeBtn.img': ('deal-button', '出价'),
    'object/ui/deal/LittleAgreeBtn.img': ('deal-button', '同意'),
    'object/ui/deal/LittleRefuseBtn.img': ('deal-button', '拒绝'),
    'object/ui/deal/RequestDealPanel.img': ('deal-invite-panel', None),
    'object/ui/deal/bg_pawnshop.img': ('deal-market-panel', None),
    'object/ui/deal/cancelbtn.img': ('deal-button', '取消修改'),
    'object/ui/deal/cancelhorizontal.img': ('deal-button', '取消'),
    'object/ui/deal/commitbtn.img': ('deal-button', '我要寄售'),
    'object/ui/deal/commiteditem.img': ('deal-committed-row', None),
    'object/ui/deal/commitpanel.img': ('deal-consign-panel', None),
    'object/ui/deal/confirmbtn.img': ('deal-button', '确认交易'),
    'object/ui/deal/lookuppetBtn.img': ('deal-pet-button', None),
    'object/ui/deal/mystoragebtn.img': ('deal-button', '我的背包'),
    'object/ui/deal/pawnSettingPanel.img': ('deal-settings-panel', None),
    'object/ui/deal/pawnedcancelBtn.img': ('deal-cancel-stack', '取\n消'),
    'object/ui/deal/tab_pawned.img': ('deal-tab', '已寄售'),
    'object/ui/deal/tab_pawning.img': ('deal-tab', '寄售'),
    'object/ui/deal/updateBtn.img': ('deal-button', '刷新'),
}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    ink, cream, gold, jade = '#254e40', '#fff3d5', '#c8ad72', '#254d42'
    font = ImageFont.truetype(str(font_path), 12)
    small = ImageFont.truetype(str(font_path), 11)

    def shell():
        return nine_slice(scaled(paints['panel'], (132, 124)), size, 18)

    def well(draw, box, radius=4):
        draw.rounded_rectangle(box, radius=radius, fill=jade, outline=gold, width=1)

    def write(draw, xy, text, face=font, fill=ink, anchor='lm'):
        draw.text(xy, text, font=face, fill=fill, anchor=anchor)

    if kind in ('deal-button', 'deal-cancel-stack', 'deal-tab'):
        # Source tabs have two positions; tall Cancel alone has grey position 1.
        if kind == 'deal-tab':
            style, disabled = ('normal', 'hover')[index], False
        elif kind == 'deal-cancel-stack':
            style, disabled = ('normal', 'normal', 'hover', 'pressed')[index], index == 1
        else:
            style, disabled = ('normal', 'hover', 'pressed', 'normal')[index], index == 3
        out = nine_slice(paints[style], size, 42)
        if disabled:
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.08)).enhance(0.72)
        draw = ImageDraw.Draw(out)
        face = small if size[0] < 60 or len(label.replace('\n', '')) >= 4 else font
        lines = label.split('\n')
        for line_no, line in enumerate(lines):
            y = size[1] // 2 + (line_no - (len(lines)-1)/2) * 15
            draw.text((size[0]//2, y), line, font=face, fill='#dfddcf' if disabled else cream,
                      anchor='mm', stroke_width=1, stroke_fill=ink)
        return out
    if kind == 'deal-pet-button':
        style = ('normal', 'hover', 'pressed', 'normal')[index]
        out = nine_slice(paints[style], size, 42)
        material = paints.get('deal-pet')
        if material is None:
            with Image.open(ROOT / PAINT_INPUTS['deal-pet']) as source:
                material = source.convert('RGBA')
        # Crop the paw emblem, retaining its own painted pixels at the tiny 17px size.
        icon = scaled(material.crop((68, 48, 198, 190)), (max(1, size[0]-4), max(1, size[1]-4)))
        out.alpha_composite(icon, (2, 2))
        if index == 3:
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.08)).enhance(0.72)
        return out
    if kind == 'deal-committed-row':
        # CommittedItem0's four live fields explicitly load lightColor.
        out = nine_slice(paints['normal'], size, 42)
        ImageDraw.Draw(out).rounded_rectangle((2, 2, size[0]-3, size[1]-3), radius=3, fill=jade, outline=gold)
        return out
    out = shell()
    draw = ImageDraw.Draw(out)
    if kind == 'deal-exchange-panel':
        # Native name at (83,35), bills at (187,70)/(187,152)/(187,495).
        write(draw, (34, 42), '与')
        well(draw, (57, 29, 218, 55))
        write(draw, (282, 42), '正在交易', fill=ink, anchor='mm')
        for y, heading in ((76, '对方开出的价格'), (164, '我开出的价格')):
            write(draw, (31, y), heading)
            well(draw, (184, y-11, 281, y+12))
            write(draw, (287, y), '灵玉')
        for y in (90, 178):
            for x in (32, 95, 158, 221, 284):
                well(draw, (x, y, x+57, y+58), radius=7)
        # The source leaves x157..349/y242..280 for two live buttons.
        write(draw, (35, 270), '可交易物品')
        for y in (295, 357, 419):
            for x in (32, 95, 158, 221, 284):
                well(draw, (x, y, x+58, y+57), radius=7)
        well(draw, (187, 493, 281, 518))
        write(draw, (287, 505), '灵玉')
        return out
    if kind == 'deal-invite-panel':
        # Native invite name uses zoneChooseColor; do not bake a sample name.
        well(draw, (32, 10, 174, 34))
        write(draw, (99, 46), '请求与您交易', fill=ink, anchor='mm')
        return out
    if kind == 'deal-market-panel':
        title = ImageFont.truetype(str(font_path), 18)
        write(draw, (48, 22), '交易中心', face=title)
        write(draw, (17, 53), '物品名称')
        well(draw, (91, 43, 201, 63))
        write(draw, (215, 53), '级别')
        well(draw, (255, 43, 281, 63))
        write(draw, (605, 53), '灵玉')
        well(draw, (680, 43, 764, 64))
        # Preserve the source's list/content regions and dynamic child rectangles.
        well(draw, (183, 71, 351, 513))
        well(draw, (360, 71, 787, 513))
        # Slim rails are baked into this source panel; live thumbs are separate.
        for x in (337, 773):
            draw.rounded_rectangle((x, 84, x+6, 501), radius=3, fill='#527663', outline=gold)
        return out
    if kind == 'deal-consign-panel':
        well(draw, (15, 13, 300, 215), radius=6)
        # Dynamic committed rows overlay this area; no invented field heading.
        for x in (313,):
            draw.rounded_rectangle((x, 21, x+6, 208), radius=3, fill='#527663', outline=gold)
            draw.rounded_rectangle((x, 271, x+6, 458), radius=3, fill='#527663', outline=gold)
        write(draw, (21, 239), '请选择您要寄售的物品')
        for y in (263, 326, 389):
            for x in (33, 95, 157, 219):
                well(draw, (x, y, x+57, y+57), radius=7)
        return out
    if kind == 'deal-settings-panel':
        # Source frame is offset (1,2) from the native widget origin.
        write(draw, (16, 19), '我的定价')
        well(draw, (87, 11, 166, 29), radius=2)
        write(draw, (172, 19), '灵玉')
        write(draw, (16, 44), '出售数量')
        well(draw, (101, 36, 139, 54), radius=2)
        write(draw, (147, 44), '个')
        write(draw, (16, 69), '寄售时长')
        for x, text in ((87, '12H'), (147, '24H')):
            draw.ellipse((x, 60, x+11, 71), fill=jade, outline=gold)
            write(draw, (x+16, 67), text, face=small)
        return out
    raise ValueError(f'Unknown native deal kind {kind}')
