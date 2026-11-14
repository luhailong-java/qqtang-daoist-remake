"""Native region and room-list chrome, composed from the existing own painted UI kit."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

PATHS = {
    'object/ui/bg/bg_selSect.img': ('post-region-background', None),
    'object/ui/bg/bg_selRoom.img': ('post-room-background', None),
    'object/ui/selSect/dlg_selserver.img': ('post-country-panel', None),
    'object/ui/selSect/img_sect.img': ('post-region-row', None),
    'object/ui/selRoom/dlg_room.img': ('post-room-card', None),
    'object/ui/selSect/btn_selzone.img': ('post-stack-button', '区域\n选择'),
    'object/ui/selSect/btn_quickjoin.img': ('post-stack-button', '快速\n加入'),
    'object/ui/selRoom/btn_createroom.img': ('post-stack-button', '创建\n房间'),
    'object/ui/selRoom/tab_compete.img': ('post-tab', '竞技模式'),
    'object/ui/selSect/tab_freedom.img': ('post-tab', '自由频道'),
}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    font = ImageFont.truetype(str(font_path), 13)
    title = ImageFont.truetype(str(font_path), 19)

    def panel(out, rect):
        x, y, width, height = rect
        frame = scaled(paints['panel'], (132, 124))
        out.alpha_composite(nine_slice(frame, (width, height), 18), (x, y))

    def jade_area(out, rect):
        left, top, right, bottom = rect
        dimensions = (right-left+1, bottom-top+1)
        edge = min(10, dimensions[0]//4, dimensions[1]//4)
        frame = nine_slice(scaled(paints['panel'], (132, 124)), dimensions, 18)
        material = paints['normal'].crop((90, 35, 400, 110))
        frame.alpha_composite(scaled(material, (dimensions[0]-2*edge, dimensions[1]-2*edge)), (edge, edge))
        out.alpha_composite(frame, (left, top))

    if kind in ('post-region-background', 'post-room-background'):
        out = ImageOps.fit(paints['background'], size, method=Image.Resampling.LANCZOS).convert('RGBA')
        if kind == 'post-region-background':
            panel(out, (5, 19, 350, 558))
            panel(out, (360, 19, 433, 558))
            draw = ImageDraw.Draw(out)
            draw.text((180, 39), '公告栏', font=title, fill='#245c49', anchor='mm')
            draw.text((576, 39), '小区选择', font=title, fill='#245c49', anchor='mm')
            # The client paints announcements and region controls into these existing extents.
            jade_area(out, (19, 51, 338, 218))
            jade_area(out, (24, 238, 333, 552))
            jade_area(out, (376, 91, 773, 509))
        else:
            panel(out, (3, 67, 426, 528))
            panel(out, (432, 84, 364, 444))
            draw = ImageDraw.Draw(out)
            jade_area(out, (449, 98, 773, 359))
            for y in range(122, 356, 24):
                draw.line((461, y, 761, y), fill='#597b64', width=1)
            jade_area(out, (479, 496, 772, 519))
            jade_area(out, (328, 43, 789, 61))
        return out
    if kind == 'post-country-panel':
        out = nine_slice(scaled(paints['panel'], (132, 124)), size, 18)
        draw = ImageDraw.Draw(out)
        draw.text((size[0]//2, 24), '区域选择', font=font, fill='#245c49', anchor='mm')
        jade_area(out, (24, 49, size[0]-30, size[1]-57))
        return out
    if kind == 'post-room-card':
        out = nine_slice(scaled(paints['panel'], (132, 124)), size, 18)
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((9, 8, 47, 27), radius=3, fill='#4e725c')
        draw.rounded_rectangle((55, 34, size[0]-9, size[1]-10), radius=5, fill='#28584d')
        if index == 0:
            out = ImageEnhance.Color(out).enhance(0.1)
            out = ImageEnhance.Brightness(out).enhance(0.85)
        elif index == 2:
            out = ImageEnhance.Brightness(out).enhance(1.12)
        return out
    if kind == 'post-region-row':
        return nine_slice(paints['normal'], size, 42)
    if kind == 'post-tab':
        out = nine_slice(paints['hover' if index else 'normal'], size, 42)
        draw = ImageDraw.Draw(out)
        draw.text((size[0]//2, size[1]//2), label, font=font, fill='#fff4d5', anchor='mm')
        return out
    if kind == 'post-stack-button':
        # Each original image position is retained, including its separate cropped dimensions.
        style = ('normal', 'hover', 'pressed')[index]
        out = nine_slice(paints[style], size, 42)
        draw = ImageDraw.Draw(out)
        lines = label.split('\n')
        for row, line in enumerate(lines):
            draw.text((size[0]//2, size[1]//2 - 8 + row*16), line, font=font, fill='#fff4d5',
                      anchor='mm', stroke_width=1, stroke_fill='#245b45')
        return out
    raise ValueError(f'Unknown native post-login asset kind {kind}')
