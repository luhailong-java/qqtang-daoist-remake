"""Original painted room controls with each source resource's state-position family."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

PATHS = {
    'object/ui/room/btn_selMode.img': ('room-toolbar', '选择模式'),
    'object/ui/room/btn_roomProp.img': ('room-toolbar', '房间属性'),
    'object/ui/room/btn_selMap.img': ('room-toolbar', '选择地图'),
    'object/ui/room/btn_ready.img': ('room-primary', '准备\nready'),
    'object/ui/room/btn_start.img': ('room-primary', '开始\nstart'),
    'object/ui/room/btn_unready.img': ('room-primary', '取消准备\ncancel'),
    'object/ui/room/btn_storage.img': ('room-storage', '我的\n背包'),
    'object/ui/room/dlg_selMode.img': ('room-mode-panel', None),
    'object/ui/room/dlg_roomProp.img': ('room-property-panel', None),
    'object/ui/room/dlg_selMap.img': ('room-map-panel', None),
    'object/ui/room/btn_equipItem.img': ('room-equipment-cell', None),
    'object/ui/room/btn_map.img': ('room-map-row', None),
    'object/ui/room/scl_block.img': ('room-scroll-thumb', None),
    'object/ui/room/dlg_chatPanelSmall.img': ('room-chat-panel', None),
    'object/ui/room/dlg_chatPanelBig.img': ('room-chat-panel', None),
    'object/ui/room/tab_integration.img': ('room-chat-tab', '综合'),
    'object/ui/room/tab_kin.img': ('room-chat-tab', '家族'),
    'object/ui/room/tab_whisper.img': ('room-chat-tab', '私聊'),
}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    ink = '#254e40'
    gold = '#c8ad72'
    pale = '#fff3d5'
    font = ImageFont.truetype(str(font_path), 12)
    small = ImageFont.truetype(str(font_path), 11)

    def muted(image):
        return ImageEnhance.Brightness(ImageEnhance.Color(image).enhance(0.08)).enhance(0.82)

    def button(style):
        pixels = nine_slice(paints['normal' if style == 'alternate' else style], size, 42)
        return muted(pixels) if style == 'alternate' else pixels

    def panel(out, box):
        x, y, width, height = box
        frame = nine_slice(scaled(paints['panel'], (132, 124)), (width, height), 18)
        out.alpha_composite(frame, (x, y))

    def well(out, box, light=False):
        ImageDraw.Draw(out).rounded_rectangle(box, radius=3,
            fill='#f3ead2' if light else '#254d42', outline=gold, width=1)

    if kind in ('room-toolbar', 'room-primary', 'room-storage'):
        # Original toolbar frames differ from ready/start/storage frames.
        states = ('normal', 'hover', 'pressed', 'alternate') if kind == 'room-toolbar' else ('normal', 'alternate', 'hover', 'pressed')
        style = states[index]
        if kind == 'room-storage':
            out = Image.new('RGBA', size)
            panel(out, (0, 0, size[0], size[1]))
            texture = paints['normal' if style == 'alternate' else style].crop((90, 35, 400, 110))
            out.alpha_composite(scaled(texture, (size[0] - 16, size[1] - 16)), (8, 8))
            if style == 'alternate':
                out = muted(out)
        else:
            out = button(style)
        fill = '#e0decd' if style == 'alternate' else pale
        draw = ImageDraw.Draw(out)
        shift = 1 if style == 'pressed' else 0
        if kind == 'room-toolbar':
            draw.text((size[0] // 2, size[1] // 2 + shift), label, font=font, fill=fill, anchor='mm',
                      stroke_width=1, stroke_fill=ink)
        else:
            chinese, second = label.split('\n')
            if kind == 'room-primary':
                heading = ImageFont.truetype(str(font_path), 16 if len(chinese) > 2 else 18)
                draw.text((size[0] // 2, size[1] // 2 - 8 + shift), chinese, font=heading, fill=fill, anchor='mm',
                          stroke_width=1, stroke_fill=ink)
                draw.text((size[0] // 2, size[1] // 2 + 11 + shift), second, font=font, fill=fill, anchor='mm')
            else:
                heading = ImageFont.truetype(str(font_path), 17)
                draw.text((size[0] // 2, size[1] // 2 - 10 + shift), chinese, font=heading, fill=fill, anchor='mm',
                          stroke_width=1, stroke_fill=ink)
                draw.text((size[0] // 2, size[1] // 2 + 10 + shift), second, font=heading, fill=fill, anchor='mm',
                          stroke_width=1, stroke_fill=ink)
        return out

    if kind in ('room-mode-panel', 'room-property-panel'):
        out = Image.new('RGBA', size)
        panel(out, (11, 0, size[0] - 11, size[1]))
        draw = ImageDraw.Draw(out)
        draw.polygon(((0, 69), (12, 62), (12, 76)), fill='#f0e5c9', outline=gold)
        draw.rounded_rectangle((25, 4, 155, 23), radius=3, fill='#f3ead2')
        if kind == 'room-mode-panel':
            draw.text((88, 13), '选择游戏模式', font=font, fill=ink, anchor='mm')
            draw.text((32, 39), '模式', font=font, fill=ink, anchor='mm')
            draw.text((82, 39), '竞技', font=small, fill=ink, anchor='mm')
            draw.text((137, 39), '探险', font=small, fill=ink, anchor='mm')
            draw.line((19, 56, 158, 56), fill=gold)
            draw.text((32, 77), '房间', font=font, fill=ink, anchor='mm')
            draw.text((86, 77), '无道具', font=small, fill=ink, anchor='mm')
            draw.text((137, 77), '道具', font=small, fill=ink, anchor='mm')
        else:
            draw.text((88, 13), '修改房间属性', font=font, fill=ink, anchor='mm')
            draw.text((32, 38), '模式', font=font, fill=ink, anchor='mm')
            draw.text((82, 38), '自由', font=small, fill=ink, anchor='mm')
            draw.text((137, 38), '标准', font=small, fill=ink, anchor='mm')
            draw.text((32, 59), '名称', font=font, fill=ink, anchor='mm')
            well(out, (50, 49, 154, 66), light=True)
            draw.text((32, 79), '保密', font=font, fill=ink, anchor='mm')
            draw.text((76, 79), '是', font=small, fill=ink, anchor='mm')
            draw.text((32, 99), '密码', font=font, fill=ink, anchor='mm')
            well(out, (50, 90, 154, 108), light=True)
        return out

    if kind == 'room-map-panel':
        out = Image.new('RGBA', size)
        panel(out, (0, 0, 167, size[1]))
        well(out, (15, 12, 136, 482))
        panel(out, (167, 0, 160, 149))
        well(out, (174, 8, 320, 141), light=True)
        draw = ImageDraw.Draw(out)
        draw.line((150, 40, 150, 480), fill=gold, width=2)
        return out

    if kind == 'room-equipment-cell':
        out = Image.new('RGBA', size)
        panel(out, (0, 0, size[0], size[1]))
        well(out, (4, 4, size[0] - 5, size[1] - 5))
        return out

    if kind == 'room-map-row':
        out = scaled(paints['normal'].crop((90, 35, 400, 110)), size)
        ImageDraw.Draw(out).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        return out

    if kind == 'room-scroll-thumb':
        out = scaled(paints['hover' if index == 1 else 'normal'].crop((170, 10, 320, 135)), size)
        if index == 2:
            out = ImageEnhance.Brightness(out).enhance(0.85)
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        draw.line((3, size[1] // 2 - 1, size[0] - 4, size[1] // 2 - 1), fill=pale)
        draw.line((3, size[1] // 2 + 2, size[0] - 4, size[1] // 2 + 2), fill=pale)
        return out

    if kind == 'room-chat-panel':
        out = scaled(paints['normal'].crop((90, 35, 400, 110)), size)
        draw = ImageDraw.Draw(out)
        draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        draw.line((size[0] - 7, 5, size[0] - 7, size[1] - 6), fill=gold)
        return out

    if kind == 'room-chat-tab':
        out = nine_slice(paints['hover' if index else 'normal'], size, 42)
        if index == 0:
            out = muted(out)
        ImageDraw.Draw(out).text((size[0] // 2, size[1] // 2), label, font=small, fill=pale, anchor='mm')
        return out
    raise ValueError(f'Unknown room control art kind {kind}')
