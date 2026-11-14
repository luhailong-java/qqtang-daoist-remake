"""Own Daoist Q forge controls; functional source alpha and frame geometry retained.

Only confirmation-interior alpha is normalized to remove source sample glyphs.
"""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'assets/native-client-ui/forge-controls-reference'
PAINT_INPUTS = {'forge-anvil': 'assets/ui/semantic-extra/forge.png',
                'forge-compose': 'assets/ui/semantic-extra/compose.png'}
PATHS = {
    'object/ui/forge/btn_avatarforge.img': ('forge-avatar-forge', '锻造'),
    'object/ui/forge/btn_avatarrevert.img': ('forge-avatar-revert', '还原'),
    'object/ui/forge/btn_avatarsplit.img': ('forge-avatar-split', '拆分'),
    'object/ui/forge/btn_forgeconfirm.img': ('forge-confirm-button', '确定'),
    'object/ui/forge/btn_item.img': ('forge-item-row', None),
    'object/ui/forge/btn_startCompose.img': ('forge-start-compose', '开始合成'),
    'object/ui/forge/btn_startForge.img': ('forge-start-forge', '开始锻造'),
    'object/ui/forge/btn_type.img': ('forge-type-row', None),
    'object/ui/forge/dlg_avatarforge.img': ('forge-avatar-panel', None),
    'object/ui/forge/dlg_forge.img': ('forge-compose-panel', None),
    'object/ui/forge/dlg_forgeconfirm.img': ('forge-confirm-panel', None),
    'object/ui/forge/dlg_forgeMask.img': ('forge-slot-mask', None),
    'object/ui/forge/dlg_meterial.img': ('forge-material-panel', None),
    'object/ui/forge/scl_down.img': ('forge-scroll-down', None),
    'object/ui/forge/scl_up.img': ('forge-scroll-up', None),
    'object/ui/forge/tab_compose.img': ('forge-compose-tab', '合成'),
    'object/ui/forge/tab_forge.img': ('forge-forge-tab', '锻造'),
    'object/ui/forge/tab_forgetype0.img': ('forge-head-tab', '头部'),
    'object/ui/forge/tab_forgetype1.img': ('forge-body-tab', '身体'),
    'object/ui/forge/tab_forgetype2.img': ('forge-back-tab', '背面'),
    'object/ui/forge/tab_forgetype3.img': ('forge-bubble-tab', '糖泡'),
}
SOURCE_COUNTS = (4, 4, 4, 4, 2, 4, 4, 1, 1, 1, 1, 1, 1, 4, 4, 2, 2, 2, 2, 2, 2)
KIND_SOURCE_STEMS = {kind: path.removeprefix('object/ui/').removesuffix('.img').replace('/', '__')
                     for path, (kind, _) in PATHS.items()}
STRUCTURAL_ALPHA_INPUTS = {
    f'{kind}-{index:02}': f'{REFERENCE}/source/{KIND_SOURCE_STEMS[kind]}-{index:02}.png'
    for ((_, (kind, _)), count) in zip(PATHS.items(), SOURCE_COUNTS, strict=True) for index in range(count)
}
STATE_LAYOUTS = {
    **{kind: ['normal', 'disabled', 'bright', 'pressed'] for kind in (
        'forge-avatar-forge', 'forge-avatar-revert', 'forge-avatar-split', 'forge-confirm-button',
        'forge-start-compose', 'forge-start-forge', 'forge-scroll-down', 'forge-scroll-up')},
    'forge-item-row': ['gradient-row', 'flat-row'],
    **{kind: ['pale-short-tab', 'jade-tall-tab'] for kind in (
        'forge-compose-tab', 'forge-forge-tab', 'forge-head-tab', 'forge-body-tab', 'forge-back-tab', 'forge-bubble-tab')},
}
ALPHA_NORMALIZATIONS = {
    'forge-confirm-panel': {
        'sourceRoiXYXY': [6, 5, 221, 107], 'targetAlpha': 255,
        'reason': 'Original interior alpha embeds legacy sample confirmation text, button and close block; those are not a functional occlusion mask',
        'sourceExteriorAlphaExactlyPreserved': True,
        'dynamicForgeTextRectAndColorUnchanged': True,
    }
}
VISUAL_MAPPING_ASSUMPTIONS = [
    'forge-confirm-panel only: source alpha interior ROI(6,5,221,107) is flattened to255 to remove embedded legacy example glyph/button silhouettes; source exterior including rounded contour and pointer tail is exact. Other51 source alpha planes are exact.',
    'TButton category/item caption engine color, forge history per-message colors, framescheme execution, btn_startForge/dlg_forgeMask exact bindings and native runtime/visual acceptance remain unknown.',
]
# Source slots: the first three exact PYC prototypes plus observed repeating
# native raster wells. Per-position offsets remain in the native container.
AVATAR_SLOT_ROWS = ((18, 47, 56, 56), (18, 150, 56, 56), (18, 220, 56, 56))


@lru_cache(maxsize=52)
def source_alpha(kind, index):
    with Image.open(ROOT / STRUCTURAL_ALPHA_INPUTS[f'{kind}-{index:02}']) as picture:
        result = picture.getchannel('A').copy()
    if kind in ALPHA_NORMALIZATIONS:
        change = ALPHA_NORMALIZATIONS[kind]
        result.paste(change['targetAlpha'], tuple(change['sourceRoiXYXY']))
    return result


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    ink, jade, gold, pale = '#254e40', '#244a3d', '#c8ad72', '#fff3d5'
    font = ImageFont.truetype(str(font_path), 12)
    small = ImageFont.truetype(str(font_path), 11)
    state = STATE_LAYOUTS.get(kind, ['single'])[index]

    def material(name):
        if name in paints:
            return paints[name]
        with Image.open(ROOT / PAINT_INPUTS[name]) as picture:
            return picture.convert('RGBA')

    def base(color=jade):
        return Image.new('RGBA', size, color)

    def panel():
        out = base('#f3ead2')
        out.alpha_composite(nine_slice(scaled(paints['panel'], (132, 124)), size, 18))
        return out

    def button():
        style = 'hover' if state == 'bright' else 'pressed' if state == 'pressed' else 'normal'
        out = base()
        out.alpha_composite(nine_slice(paints[style], size, 42))
        if state == 'disabled':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.05)).enhance(0.8)
        return out

    def well(out, rect, light=False):
        ImageDraw.Draw(out).rounded_rectangle(rect, radius=4,
            fill='#fff8e6' if light else '#203f35', outline=gold)

    def title(out, text, y, left=18, right=412):
        draw = ImageDraw.Draw(out)
        draw.rectangle((left - 5, y - 9, right, y + 9), fill=jade)
        draw.text((left, y), text, font=font, fill=pale, anchor='lm')

    if kind in ('forge-avatar-forge', 'forge-avatar-revert', 'forge-avatar-split', 'forge-confirm-button',
                'forge-start-compose', 'forge-start-forge'):
        out = button()
        draw = ImageDraw.Draw(out)
        text_x = size[0] // 2
        if kind in ('forge-avatar-forge', 'forge-start-forge', 'forge-start-compose'):
            name = 'forge-compose' if kind == 'forge-start-compose' else 'forge-anvil'
            symbol = scaled(material(name), (24, 24))
            if state == 'disabled':
                symbol = ImageEnhance.Color(symbol).enhance(0.05)
            out.alpha_composite(symbol, (5, (size[1] - 24) // 2))
            text_x += 11
        elif kind == 'forge-avatar-revert':
            # Original source uses a bent return arrow at left of its caption.
            draw.arc((9, 11, 32, 30), 195, 360, fill=gold, width=3)
            draw.polygon(((7, 13), (16, 10), (12, 21)), fill=pale)
            text_x += 9
        elif kind == 'forge-avatar-split':
            draw.line((12, 12, 28, 30), fill=gold, width=3)
            draw.line((28, 12, 12, 30), fill=pale, width=3)
            text_x += 9
        caption_font = ImageFont.truetype(str(font_path), 14 if len(label) == 4 else 16)
        draw.text((text_x, size[1] // 2 + (state == 'pressed')), label, font=caption_font,
                  fill='#d4d6cf' if state == 'disabled' else pale, anchor='mm', stroke_width=1, stroke_fill=ink)
    elif kind in ('forge-scroll-down', 'forge-scroll-up'):
        style = 'hover' if state == 'bright' else 'pressed' if state == 'pressed' else 'normal'
        out = base()
        out.alpha_composite(scaled(paints[style].crop((160, 35, 330, 110)), size))
        if state == 'disabled':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.05)).enhance(0.8)
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, 17, 17), outline=gold if state != 'disabled' else '#92958a')
        points = ((4, 6), (13, 6), (9, 12)) if kind == 'forge-scroll-down' else ((4, 12), (13, 12), (9, 6))
        draw.polygon(points, fill=pale if state != 'disabled' else '#c4c9be')
    elif kind in ('forge-item-row', 'forge-type-row'):
        out = base('#315c49')
        if state != 'flat-row':
            out.alpha_composite(scaled(paints['normal'].crop((90, 35, 400, 110)), size))
        ImageDraw.Draw(out).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        # Actual dynamic category/item captions are never baked or renamed.
        # Their TButton engine default color is not declared in uiTemplate.
    elif kind in ('forge-compose-tab', 'forge-forge-tab', 'forge-head-tab', 'forge-body-tab', 'forge-back-tab', 'forge-bubble-tab'):
        if index == 0:
            out = panel()
            ImageDraw.Draw(out).rectangle((3, 2, size[0] - 4, size[1] - 2), fill='#f3ead2')
        else:
            out = base()
            out.alpha_composite(nine_slice(paints['normal'], size, 42))
        ImageDraw.Draw(out).text((size[0] // 2, size[1] // 2), label, font=font,
                                 fill=ink if index == 0 else pale, anchor='mm')
    elif kind == 'forge-avatar-panel':
        out = panel()
        draw = ImageDraw.Draw(out)
        well(out, (9, 34, 415, 113))
        well(out, (9, 131, 415, 289))
        for x, y, w, h in AVATAR_SLOT_ROWS:
            for column in range(5):
                well(out, (x - 2 + column * 61, y - 1, x + w + column * 61, y + h + 1))
        for y in (51, 154, 224):
            well(out, (320, y - 1, 386, y + 18))
        for text, y in (('材料栏', 57), ('可锻造', 160), ('已锻造', 230)):
            for row, char in enumerate(text):
                draw.text((400, y + row * 16), char, font=font, fill=pale, anchor='mm')
        draw.line((16, 213, 319, 213), fill=gold)
        well(out, (10, 294, 415, 439), light=True)
        well(out, (48, 309, 152, 413))
        well(out, (206, 300, 271, 365))
        well(out, (206, 369, 271, 434))
        draw.text((238, 333), '材料', font=font, fill='#a7b79d', anchor='mm')
        draw.text((238, 401), '装备', font=font, fill='#a7b79d', anchor='mm')
        draw.polygon(((160, 367), (180, 336), (180, 356), (196, 356),
                      (196, 377), (180, 377), (180, 396)), fill=jade, outline=gold)
        title(out, '历史信息', 450)
        well(out, (10, 461, 415, 557))
        draw.line((400, 470, 400, 548), fill=gold, width=2)
    elif kind == 'forge-compose-panel':
        out = panel()
        draw = ImageDraw.Draw(out)
        title(out, '物品列表', 49)
        well(out, (10, 63, 180, 403))
        draw.line((170, 78, 170, 391), fill=gold, width=2)
        well(out, (191, 85, 250, 145))
        # curItemName and curItemInfo directly inherit black TLabel; preserve
        # their exact67/87 y positions on light paper, not a dark jade well.
        well(out, (261, 65, 409, 164), light=True)
        draw.line((267, 82, 402, 82), fill='#d8caa2')
        title(out, '材料列表', 180, left=191)
        well(out, (182, 191, 411, 402))
        title(out, '历史信息', 414)
        well(out, (10, 424, 415, 519))
        draw.line((400, 432, 400, 510), fill=gold, width=2)
        symbol = scaled(material('forge-anvil'), (36, 36))
        out.alpha_composite(symbol, (26, 536))
    elif kind == 'forge-material-panel':
        out = base('#24483c')
        for y in (1, 66, 133):
            well(out, (2, y, 60, y + 58))
        # meterialInfo0 is explicitly white; 1/2 inherit it through proven
        # BUILD_CLASS windows. Leave their local x80 text region dark.
    elif kind == 'forge-confirm-panel':
        out = panel()
        ImageDraw.Draw(out).rounded_rectangle((7, 5, size[0] - 8, 48), radius=4, fill='#fff8e6')
        # The original dynamic forgeText is brown(135,113,87) at10,10,180,28.
        # Do not bake an action/price/message into this shared confirmation.
    elif kind == 'forge-slot-mask':
        out = base('#254d42')
        draw = ImageDraw.Draw(out)
        for y in (0, 102, 173):
            draw.line((0, y, size[0] - 1, y), fill=gold)
        # The fifteen exact source holes and separator transparency are
        # restored below. No opaque material is painted over a slot hole.
    else:
        raise ValueError(f'Unknown native forge control kind {kind}')
    opacity = source_alpha(kind, index)
    if opacity.size != size:
        raise ValueError('Source forge structural alpha size changed')
    out.putalpha(opacity)
    return out
