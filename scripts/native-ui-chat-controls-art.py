"""Own painted chat controls, retaining every original native source alpha plane.

The source PNGs below are structural masks only. No original color or caption
pixels are reused. State positions were inspected from all65 source rasters.
"""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'assets/native-client-ui/chat-controls-reference'
PAINT_INPUTS = {
    'chat-private': 'assets/ui/semantic-extra/private-chat.png',
    'chat-shop': 'assets/ui/icons/shop.png',
}
PATHS = {
    'object/ui/chat/btn_commandPrompt.img': ('chat-command-arrow', None),
    'object/ui/chat/btn_expression.img': ('chat-face-button', None),
    'object/ui/chat/btn_facemember.img': ('chat-member-button', '会员'),
    'object/ui/chat/btn_facenormal.img': ('chat-normal-button', '普通'),
    'object/ui/chat/btn_ldspker_disable.img': ('chat-speaker-disabled', None),
    'object/ui/chat/btn_ldspker_pushdown.img': ('chat-speaker-pressed', None),
    'object/ui/chat/btn_send.img': ('chat-send-button', None),
    'object/ui/chat/btn_speaker.img': ('chat-speaker-button', None),
    'object/ui/chat/dlg_face.img': ('chat-face-panel', None),
    'object/ui/chat/img_chatMenu.img': ('chat-legacy-menu-panel', None),
    'object/ui/chat/img_cmdChoose.img': ('chat-command-highlight', None),
    'object/ui/chat/img_commandPrompt.img': ('chat-command-panel', None),
    'object/ui/chat/tab_integration.img': ('chat-integration-tab', '综合'),
    'object/ui/chat/tab_kin.img': ('chat-kin-tab', '家族'),
    'object/ui/chat/tab_whisper.img': ('chat-whisper-tab', '密聊'),
    'object/ui/chatRoom/btn_cancel.img': ('chat-cancel-button', '取消'),
    'object/ui/chatRoom/btn_chatConfirm.img': ('chat-confirm-button', '确定'),
    'object/ui/chatRoom/btn_chatFlexDown.img': ('chat-flex-down', None),
    'object/ui/chatRoom/btn_chatFlexUp.img': ('chat-flex-up', None),
    'object/ui/chatRoom/btn_chatShop.img': ('chat-shop-button', '道具商城'),
    'object/ui/chatRoom/btn_kickOut.img': ('chat-kick-button', '踢人'),
    'object/ui/chatRoom/btn_lookOver.img': ('chat-look-button', '查看'),
    'object/ui/chatRoom/dlg_bgPreview.img': ('chat-background-preview', None),
    'object/ui/chatRoom/dlg_chatAreaBig.img': ('chat-transcript-big', None),
    'object/ui/chatRoom/dlg_chatAreaSmall.img': ('chat-transcript-small', None),
    'object/ui/chatRoom/dlg_isKickOut.img': ('chat-kick-panel', None),
    'object/ui/chatRoom/dlg_mapFilterMask.img': ('chat-map-filter-mask', None),
}
SOURCE_COUNTS = (4, 4, 3, 3, 1, 1, 4, 4, 1, 1, 1, 1, 2, 2, 2, 4, 4, 3, 3, 4, 4, 4, 1, 1, 1, 1, 1)
KIND_SOURCE_STEMS = {kind: path.removeprefix('object/ui/').removesuffix('.img').replace('/', '__')
                     for path, (kind, _) in PATHS.items()}
STRUCTURAL_ALPHA_INPUTS = {
    f'{kind}-{index:02}': f'{REFERENCE}/source/{KIND_SOURCE_STEMS[kind]}-{index:02}.png'
    for ((_, (kind, _)), count) in zip(PATHS.items(), SOURCE_COUNTS, strict=True)
    for index in range(count)
}
STATE_LAYOUTS = {
    'chat-command-arrow': ['normal', 'disabled', 'hover', 'pressed'],
    'chat-face-button': ['normal', 'disabled', 'hover', 'pressed'],
    'chat-send-button': ['normal', 'disabled', 'hover', 'pressed'],
    'chat-speaker-button': ['normal', 'hover', 'pressed', 'disabled'],
    'chat-speaker-disabled': ['disabled'], 'chat-speaker-pressed': ['pressed'],
    'chat-member-button': ['normal', 'hover', 'pressed'],
    'chat-normal-button': ['normal', 'hover', 'pressed'],
    'chat-flex-down': ['normal', 'hover', 'pressed'], 'chat-flex-up': ['normal', 'hover', 'pressed'],
    **{kind: ['normal', 'disabled', 'hover', 'pressed'] for kind in (
       'chat-cancel-button', 'chat-confirm-button', 'chat-shop-button', 'chat-kick-button', 'chat-look-button')},
    **{kind: ['paper', 'jade'] for kind in ('chat-integration-tab', 'chat-kin-tab', 'chat-whisper-tab')},
}


@lru_cache(maxsize=65)
def source_alpha(kind, index):
    path = ROOT / STRUCTURAL_ALPHA_INPUTS[f'{kind}-{index:02}']
    with Image.open(path) as picture:
        return picture.getchannel('A').copy()


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    ink, deep, gold, pale = '#254e40', '#23483c', '#c8ad72', '#fff3d5'
    font = ImageFont.truetype(str(font_path), 12)
    small = ImageFont.truetype(str(font_path), 11)
    style = STATE_LAYOUTS.get(kind, ['normal'])[index]
    disabled = style == 'disabled'

    def fill_base(color=deep):
        return Image.new('RGBA', size, color)

    def material(name):
        if name in paints:
            return paints[name]
        with Image.open(ROOT / PAINT_INPUTS[name]) as picture:
            return picture.convert('RGBA')

    def surface():
        out = fill_base()
        texture = paints['normal' if disabled else style]
        if size[0] <= 45 or size[1] <= 22:
            # Small original slots need a clear symbol/caption area. Reuse the
            # existing jade material without shrinking its large scroll ends
            # across the glyphs.
            out.alpha_composite(scaled(texture.crop((90, 35, 400, 110)), size))
            ImageDraw.Draw(out).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=3, outline=gold)
        else:
            out.alpha_composite(nine_slice(texture, size, 42))
        if disabled:
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.05)).enhance(0.8)
        return out

    def panel():
        out = fill_base('#f3ead2')
        out.alpha_composite(nine_slice(scaled(paints['panel'], (132, 124)), size, 18))
        return out

    if kind in ('chat-command-arrow', 'chat-face-button', 'chat-send-button', 'chat-speaker-button',
                'chat-speaker-disabled', 'chat-speaker-pressed'):
        out = surface()
        draw = ImageDraw.Draw(out)
        cx, cy = size[0] // 2, size[1] // 2
        mark = '#d4d6cf' if disabled else pale
        accent = '#9c9d95' if disabled else gold
        if kind == 'chat-command-arrow':
            draw.polygon(((cx - 6, cy - 4), (cx + 6, cy - 4), (cx, cy + 5)), fill=mark)
            draw.line((cx - 6, cy - 5, cx + 6, cy - 5), fill=accent, width=1)
        elif kind == 'chat-face-button':
            draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=mark, outline=accent)
            draw.point((cx - 3, cy - 2), fill=ink)
            draw.point((cx + 3, cy - 2), fill=ink)
            draw.arc((cx - 4, cy - 2, cx + 4, cy + 4), 5, 175, fill=ink, width=1)
        elif kind == 'chat-send-button':
            # Source is a leftward return/send arrow, not a next-page arrow.
            draw.line(((cx + 9, cy - 6), (cx + 9, cy + 1), (cx - 7, cy + 1)), fill=accent, width=4)
            draw.line(((cx + 8, cy - 6), (cx + 8, cy), (cx - 7, cy)), fill=mark, width=2)
            draw.polygon(((cx - 11, cy), (cx - 4, cy - 5), (cx - 4, cy + 5)), fill=mark)
        else:
            draw.polygon(((cx - 10, cy - 4), (cx - 3, cy - 4), (cx + 6, cy - 8),
                          (cx + 6, cy + 6), (cx - 3, cy + 3), (cx - 10, cy + 3)), fill=mark, outline=accent)
            draw.polygon(((cx - 5, cy + 3), (cx - 1, cy + 3), (cx + 1, cy + 8), (cx - 3, cy + 8)), fill=accent)
            draw.arc((cx + 4, cy - 6, cx + 13, cy + 5), 290, 70, fill=mark, width=1)
    elif kind in ('chat-member-button', 'chat-normal-button', 'chat-cancel-button', 'chat-confirm-button',
                  'chat-shop-button', 'chat-kick-button', 'chat-look-button'):
        out = surface()
        draw = ImageDraw.Draw(out)
        shift = 1 if style == 'pressed' else 0
        text_x = size[0] // 2
        if kind == 'chat-shop-button':
            icon = scaled(material('chat-shop'), (25, 25))
            out.alpha_composite(icon, (5, (size[1] - 25) // 2))
            text_x += 10
        caption_font = ImageFont.truetype(str(font_path), 14) if kind == 'chat-shop-button' else font
        draw.text((text_x, size[1] // 2 + shift), label, font=caption_font,
                  fill='#d4d6cf' if disabled else pale, anchor='mm', stroke_width=1, stroke_fill=ink)
    elif kind in ('chat-flex-up', 'chat-flex-down'):
        out = fill_base()
        out.alpha_composite(scaled(paints[style].crop((160, 35, 330, 110)), size))
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        cx = size[0] // 2
        points = ((cx - 5, 7), (cx + 5, 7), (cx, 2)) if kind == 'chat-flex-up' else ((cx - 5, 2), (cx + 5, 2), (cx, 7))
        draw.polygon(points, fill=pale)
    elif kind in ('chat-integration-tab', 'chat-kin-tab', 'chat-whisper-tab'):
        if index == 0:
            out = panel()
            ImageDraw.Draw(out).rectangle((3, 2, size[0] - 4, size[1] - 3), fill='#f3ead2')
        else:
            out = fill_base()
            out.alpha_composite(nine_slice(paints['normal'], size, 42))
        ImageDraw.Draw(out).text((size[0] // 2, size[1] // 2), label, font=font,
                                 fill=ink if index == 0 else pale, anchor='mm')
    elif kind == 'chat-face-panel':
        out = fill_base()
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((1, 1, size[0] - 2, size[1] - 2), radius=4, outline=gold, width=2)
        # The original face0 starts at8,6 with26x26 cells; no new face images.
        for x in range(6, 176, 28):
            draw.line((x, 4, x, 110), fill='#536d58')
        for y in range(4, 111, 26):
            draw.line((6, y, 174, y), fill='#536d58')
        draw.line((4, 112, size[0] - 5, 112), fill=gold)
    elif kind in ('chat-command-panel', 'chat-legacy-menu-panel', 'chat-command-highlight'):
        out = fill_base('#2b5743' if kind == 'chat-command-highlight' else '#224a3b')
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        # These captions are runtime data. TButton's engine caption color is
        # not declared in the inspected template; retain source dark polarity.
    elif kind == 'chat-background-preview':
        out = panel()
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((9, 42, 183, 186), radius=5, fill='#e7dec6', outline=gold)
        draw.rounded_rectangle((53, 68, 121, 133), radius=4, fill='#f7f0de', outline=gold)
        symbol = scaled(material('chat-private'), (83, 83))
        out.alpha_composite(symbol, (194, 65))
        draw.rounded_rectangle((10, 148, 183, 182), radius=4, fill=deep, outline=gold)
        draw.text((29, 163), '密码', font=small, fill=pale, anchor='mm')
        draw.rectangle((53, 154, 152, 175), fill='#1d3e34')
        # chatPwd is explicit white at53,155,100,16; confirm overlays142,151.
    elif kind in ('chat-transcript-big', 'chat-transcript-small'):
        out = fill_base('#24483f')
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((0, 1, size[0] - 2, size[1] - 1), radius=3, outline=gold)
        draw.line((size[0] - 11, 6, size[0] - 11, size[1] - 4), fill='#8e936e')
        # All128-alpha transcript regions and transparent top notches are
        # restored exactly below; message colors remain runtime data.
    elif kind == 'chat-kick-panel':
        out = panel()
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((15, 24, size[0] - 16, 131), radius=5, fill='#f3ead2', outline=gold)
        draw.rounded_rectangle((15, 24, size[0] - 16, 48), radius=4, fill=deep)
        draw.text((27, 35), '提示信息', font=font, fill=pale, anchor='lm')
    elif kind == 'chat-map-filter-mask':
        out = fill_base('#254d42')
        ImageDraw.Draw(out).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
    else:
        raise ValueError(f'Unknown native chat control kind {kind}')
    opacity = source_alpha(kind, index)
    if opacity.size != size:
        raise ValueError('Source chat structural alpha dimensions differ')
    out.putalpha(opacity)
    return out
