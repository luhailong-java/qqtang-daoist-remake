"""Painted native lobby buttons, channel tabs, list tabs and compact dialogs."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

PATHS = {
    'object/ui/selSect/btn_practice.img': ('lobby-stack-button', '新手\n练习'),
    'object/ui/selSect/btn_sysSetup.img': ('lobby-stack-button', '系统\n设置'),
    'object/ui/selSect/tab_practice.img': ('lobby-channel-tab', '练习频道'),
    'object/ui/selSect/tab_greenhand.img': ('lobby-channel-tab', '新手频道'),
    'object/ui/selSect/tab_match.img': ('lobby-channel-tab', '比赛频道'),
    'object/ui/selSect/tab_party.img': ('lobby-channel-tab', '活动频道'),
    'object/ui/selSect/btn_choose.img': ('lobby-region-row', None),
    'object/ui/selRoom/tab_chat.img': ('lobby-mode-tab', '聊天房间'),
    'object/ui/selRoom/tab_explore.img': ('lobby-mode-tab', '探险模式'),
    'object/ui/selRoom/tab_honor.img': ('lobby-list-tab', '抢宝场'),
    'object/ui/selRoom/tab_item.img': ('lobby-list-tab', '道具场'),
    'object/ui/selRoom/tab_noItem.img': ('lobby-list-tab', '无道具场'),
    'object/ui/selRoom/tab_player.img': ('lobby-list-tab', '玩家'),
    'object/ui/selRoom/tab_friend.img': ('lobby-list-tab', '好友'),
    'object/ui/selRoom/tab_allKinMember.img': ('lobby-list-tab', '全家福'),
    'object/ui/selRoom/btn_shop.img': ('lobby-stack-button', '道具\n商城'),
    'object/ui/selRoom/btn_match.img': ('lobby-stack-button', '家族\n联赛'),
    'object/ui/selRoom/dlg_pwRoom.img': ('lobby-password-panel', None),
    'object/ui/selRoom/map/dlg_mapFilter.img': ('lobby-map-filter-panel', None),
    'object/ui/selRoom/btn_mapFilter.img': ('lobby-map-filter-button', None),
}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    font = ImageFont.truetype(str(font_path), 12)
    small = ImageFont.truetype(str(font_path), 11)
    ink = '#254e40'
    gold = '#c8ad72'
    pale = '#fff3d5'

    def panel(out, box):
        x, y, width, height = box
        frame = nine_slice(scaled(paints['panel'], (132, 124)), (width, height), 18)
        out.alpha_composite(frame, (x, y))

    if kind == 'lobby-stack-button':
        style = ('normal', 'hover', 'pressed')[index]
        out = Image.new('RGBA', size)
        panel(out, (0, 0, size[0], size[1]))
        material = paints[style].crop((90, 35, 400, 110))
        out.alpha_composite(scaled(material, (size[0] - 14, size[1] - 14)), (7, 7))
        draw = ImageDraw.Draw(out)
        heading = ImageFont.truetype(str(font_path), 13 if size[0] <= 51 else 15)
        y_shift = 1 if index == 2 else 0
        lines = label.split('\n')
        for line_number, line in enumerate(lines):
            draw.text((size[0] // 2, size[1] // 2 - 8 + line_number * 17 + y_shift), line,
                      font=heading, fill=pale, anchor='mm', stroke_width=1, stroke_fill=ink)
        return out

    if kind in ('lobby-channel-tab', 'lobby-mode-tab', 'lobby-list-tab'):
        if kind == 'lobby-list-tab' and index == 0:
            out = Image.new('RGBA', size)
            panel(out, (0, 0, size[0], size[1]))
            ImageDraw.Draw(out).rounded_rectangle((4, 3, size[0] - 5, size[1] - 3), radius=3, fill='#f3ead2')
            fill = ink
        else:
            out = nine_slice(paints['hover' if index else 'normal'], size, 42)
            if kind == 'lobby-mode-tab' and index == 0:
                out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.08)).enhance(0.85)
            fill = pale
        draw = ImageDraw.Draw(out)
        selected_font = small if size[1] <= 21 or len(label) == 4 and size[0] <= 72 else font
        draw.text((size[0] // 2, size[1] // 2), label, font=selected_font, fill=fill, anchor='mm')
        return out

    if kind == 'lobby-region-row':
        out = scaled(paints['normal'].crop((90, 35, 400, 110)), size)
        ImageDraw.Draw(out).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=3, outline=gold)
        return out

    if kind == 'lobby-password-panel':
        out = Image.new('RGBA', size)
        panel(out, (0, 0, size[0], size[1]))
        draw = ImageDraw.Draw(out)
        title = ImageFont.truetype(str(font_path), 16)
        draw.text((105, 52), '请输入密码！', font=title, fill=ink, anchor='mm')
        draw.rounded_rectangle((27, 78, 339, 113), radius=5, fill='#254d42', outline=gold)
        return out

    if kind == 'lobby-map-filter-panel':
        out = Image.new('RGBA', size)
        panel(out, (0, 0, size[0], size[1]))
        ImageDraw.Draw(out).rounded_rectangle((2, 3, size[0] - 3, size[1] - 3), radius=3, fill='#254d42', outline=gold)
        return out

    if kind == 'lobby-map-filter-button':
        style = ('normal', 'hover', 'pressed')[index]
        out = scaled(paints[style].crop((170, 35, 320, 110)), size)
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        # Original position 0 points down; original positions 1 and 2 point left.
        points = ((4, 6), (14, 6), (9, 13)) if index == 0 else ((6, 9), (13, 4), (13, 14))
        draw.polygon(points, fill=pale)
        return out
    raise ValueError(f'Unknown lobby control kind {kind}')
