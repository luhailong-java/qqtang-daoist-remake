"""Core native screen chrome from the existing original painted UI kit."""
from PIL import Image, ImageDraw, ImageFont, ImageOps

PATHS = {
    'object/ui/bg/bg_room.img': ('core-room', None),
    'object/ui/bg/bg_shop.img': ('core-shop', None),
    'object/ui/bg/bg_game.img': ('core-game-sidebar', None),
    'object/ui/bg/bg_logo.img': ('core-logo', None),
    'object/ui/common/dlg_setup.img': ('core-setup', None),
    'object/ui/game/dlg_playerList.img': ('core-player-sidebar', None),
}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    font = ImageFont.truetype(str(font_path), 12)
    small = ImageFont.truetype(str(font_path), 11)
    title = ImageFont.truetype(str(font_path), 16)
    muted = '#426452'
    ink = '#24513f'
    rim = '#ba9d60'

    def panel(out, box):
        x, y, width, height = box
        source = scaled(paints['panel'], (132, 124))
        out.alpha_composite(nine_slice(source, (width, height), 18), (x, y))

    def well(out, box, light=False):
        ImageDraw.Draw(out).rounded_rectangle(box, radius=4,
            fill='#f3ead2' if light else '#254d42', outline=rim, width=1)

    def background():
        return ImageOps.fit(paints['background'], size, method=Image.Resampling.LANCZOS).convert('RGBA')

    if kind == 'core-logo':
        out = background()
        panel(out, (54, 128, 692, 338))
        logo = ImageOps.contain(paints['logo'], (620, 234), method=Image.Resampling.LANCZOS)
        out.alpha_composite(logo, ((size[0] - logo.width) // 2, (size[1] - logo.height) // 2))
        return out

    if kind == 'core-room':
        out = background()
        panel(out, (5, 43, 503, 454))
        well(out, (12, 62, 501, 80))
        panel(out, (5, 489, 503, 109))
        well(out, (10, 499, 501, 567))
        well(out, (30, 572, 393, 591))
        panel(out, (516, 47, 114, 135))
        panel(out, (631, 47, 162, 153))
        well(out, (637, 49, 787, 173), light=True)
        panel(out, (518, 210, 275, 116))
        well(out, (541, 217, 769, 317))
        draw = ImageDraw.Draw(out)
        colors = ('#dd4440', '#366fd1', '#e6ce37', '#489d50', '#d34993', '#e99335', '#8c42be', '#4aabc4')
        for i, color in enumerate(colors):
            x = 525 + i * 32
            draw.rectangle((x, 325, x + 29, 358), fill=color, outline=rim)
            draw.text((x + 15, 351), chr(65 + i), fill='#fff4d6', font=small, anchor='mm', stroke_width=1, stroke_fill=ink)
        panel(out, (518, 368, 275, 144))
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((624, 369, 700, 383), radius=3, fill='#f3ead2')
        draw.text((662, 376), '装备道具栏', fill=ink, font=small, anchor='mm')
        slots = ((596, 385), (658, 385), (720, 385), (534, 442), (597, 442), (657, 442), (719, 442))
        for number, (x, y) in enumerate(slots, 1):
            well(out, (x, y, x + 59, y + 55), light=True)
            ImageDraw.Draw(out).text((x + 5, y + 4), str(number), fill=muted, font=small)
        return out

    if kind == 'core-shop':
        out = background()
        panel(out, (3, 33, 425, 556))
        panel(out, (434, 70, 358, 177))
        well(out, (440, 98, 545, 202))
        well(out, (471, 217, 784, 241))
        panel(out, (435, 269, 357, 262))
        for y in (285, 354, 423):
            for x in (441, 510, 579, 648, 717):
                well(out, (x, y, x + 65, y + 65))
        well(out, (700, 4, 790, 24))
        well(out, (700, 28, 790, 47))
        draw = ImageDraw.Draw(out)
        draw.text((695, 15), '灵玉', fill='#fff4d6', font=font, anchor='rm', stroke_width=1, stroke_fill=ink)
        draw.text((695, 37), '灵币', fill='#fff4d6', font=font, anchor='rm', stroke_width=1, stroke_fill=ink)
        draw.text((455, 229), '我的\n名片', fill=ink, font=small, anchor='mm', spacing=0)
        draw.text((781, 260), '我的道具箱', fill='#fff4d6', font=small, anchor='rm', stroke_width=1, stroke_fill=ink)
        return out

    if kind in ('core-game-sidebar', 'core-player-sidebar'):
        out = Image.new('RGBA', size)
        x = 28 if kind == 'core-game-sidebar' else 7
        panel(out, (x, 0, size[0] - x, 104))
        well(out, (x + 5, 45, size[0] - 4, 97))
        well(out, (x + 86, 10, size[0] - 5, 40))
        draw = ImageDraw.Draw(out)
        draw.text((x + 26, 25), '时间', fill=ink, font=title, anchor='mm')
        for y in range(107, 465, 51):
            panel(out, (max(0, x - 7), y, size[0] - max(0, x - 7), 47))
            well(out, (x + 35, y + 1, size[0] - 5, y + 45))
        panel(out, (x, 519, size[0] - x, 80))
        return out

    if kind == 'core-setup':
        out = Image.new('RGBA', size)
        panel(out, (0, 0, size[0], size[1]))
        draw = ImageDraw.Draw(out)
        draw.text((58, 40), '键盘设置', fill=ink, font=title, anchor='mm')
        draw.text((265, 64), '游戏中的快捷键设置', fill=ink, font=font, anchor='mm')
        draw.line((203, 57, 203, 320), fill=rim)
        draw.text((224, 85), '使用道具', fill=muted, font=small)
        draw.text((322, 85), '购买道具', fill=muted, font=small)
        for i in range(7):
            y = 97 + i * 16
            well(out, (249, y, 299, y + 13), light=True)
            well(out, (347, y, 397, y + 13), light=True)
            ImageDraw.Draw(out).text((246, y + 6), f'道具{i + 1}', fill=ink, font=small, anchor='rm')
            ImageDraw.Draw(out).text((345, y + 6), f'商店{i + 1}', fill=ink, font=small, anchor='rm')
        for box in ((80, 79, 134, 94), (22, 119, 76, 135), (140, 119, 194, 135), (80, 143, 134, 159),
                    (56, 207, 111, 223), (141, 207, 194, 223), (55, 246, 112, 262), (141, 246, 195, 262),
                    (90, 271, 145, 288), (90, 298, 145, 314), (204, 298, 258, 314), (316, 298, 371, 314)):
            well(out, box, light=True)
        draw = ImageDraw.Draw(out)
        for x, y, text in ((107, 70, '向上移动'), (50, 109, '向左移动'), (166, 109, '向右移动'), (107, 170, '向下移动'),
                (83, 197, '放置灵葫'), (168, 197, '道具切换'), (82, 236, '使用道具'), (166, 236, '对话'),
                (58, 279, '自定义对话'), (58, 306, '自定义对话'), (176, 306, '快速帮助'), (286, 306, '快速回复')):
            draw.text((x, y), text, fill=ink, font=small, anchor='mm')
        for x, y, arrow in ((106, 108, '↑'), (90, 126, '←'), (106, 126, '↓'), (122, 126, '→')):
            draw.rounded_rectangle((x - 7, y - 8, x + 7, y + 8), radius=2, fill='#ebddac', outline=rim)
            draw.text((x, y), arrow, fill=ink, font=font, anchor='mm')
        draw.rounded_rectangle((268, 231, 335, 284), radius=25, fill='#f3ead2', outline=ink, width=2)
        draw.line((301, 232, 301, 284), fill=ink)
        draw.rounded_rectangle((296, 244, 306, 265), radius=3, fill=muted)
        draw.line((250, 250, 280, 250), fill=ink, width=2)
        draw.line((325, 250, 355, 250), fill=ink, width=2)
        draw.polygon(((248, 250), (257, 245), (257, 255)), fill=ink)
        draw.polygon(((358, 250), (349, 245), (349, 255)), fill=ink)
        for x, text in ((216, '角色选择'), (230, '队伍选择'), (374, '玩家资料'), (388, '系统设置')):
            for i, char in enumerate(text):
                draw.text((x, 233 + i * 12), char, fill=ink, font=small, anchor='mm')
        draw.line((15, 326, 399, 326), fill=rim)
        draw.text((58, 344), '游戏设置', fill=ink, font=title, anchor='mm')
        for x, y, text in ((49, 372, '音效'), (135, 372, '背景音乐'), (229, 372, '特效'), (296, 372, '全屏'),
                (42, 389, '启动游戏时显示设置界面'), (225, 389, '软件渲染'), (225, 407, '硬件渲染')):
            draw.text((x, y), text, fill=ink, font=small, anchor='lm')
        draw.line((15, 423, 399, 423), fill=rim)
        return out
    raise ValueError(f'Unknown core native UI kind {kind}')
