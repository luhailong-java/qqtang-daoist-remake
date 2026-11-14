"""Original painted storage and task controls on their native state geometries."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REF = 'assets/native-client-ui/storage-task-reference/frames'
FONT_INPUTS = {'symbols': 'C:/Windows/Fonts/seguisym.ttf'}
PAINT_INPUTS = {
    'storage-task-crown': 'assets/items/hats/morning-courtesy-b/46-coral-jade-cloud-crown.png',
    'storage-task-red-crown': 'assets/items/hats/ceremony-journey-e/83-crimson-cloud-ceremonial-crown.png',
    'storage-task-crystal': 'assets/items/forge/icons/20057-purple-crystal.png',
    'storage-task-rose': 'assets/items/head-adornments/icons/114-rose-silk-garland.png',
    'storage-task-new-portrait': 'assets/characters/portraits-candidates/daoist-child-256.png',
    'storage-task-free-portrait': 'assets/characters/portraits-candidates/moon-shadow-256.png',
}
STRUCTURAL_ALPHA_INPUTS = {
    'selection': f'{REF}/img_choose-000.png',
    'shadow': f'{REF}/img_shield-000.png',
    'room-grid': f'{REF}/dlg_roomStorage-000.png',
}
for stem in ('btn_first', 'btn_last', 'btn_left', 'btn_right', 'btn_startTask', 'btn_finishTask'):
    for index in range(4):
        STRUCTURAL_ALPHA_INPUTS[f'{stem}-{index}'] = f'{REF}/{stem}-{index:03}.png'

PATHS = {
    'object/ui/storage/btn_cleanUp.img': ('storage-button', '整理'),
    'object/ui/storage/btn_first.img': ('storage-nav', 'btn_first'),
    'object/ui/storage/btn_last.img': ('storage-nav', 'btn_last'),
    'object/ui/storage/btn_left.img': ('storage-nav', 'btn_left'),
    'object/ui/storage/btn_right.img': ('storage-nav', 'btn_right'),
    'object/ui/storage/dlg_roomStorage.img': ('storage-grid-room', None),
    'object/ui/storage/dlg_shopStorage.img': ('storage-grid-shop', None),
    'object/ui/storage/img_choose.img': ('storage-selection', None),
    'object/ui/storage/img_shield.img': ('storage-shadow', None),
    'object/ui/task/bg_taskLevel1.img': ('storage-task-level', '1'),
    'object/ui/task/bg_taskLevel2.img': ('storage-task-level', '2'),
    'object/ui/task/bg_taskLevel3.img': ('storage-task-level', '3'),
    'object/ui/task/bg_taskLevel4.img': ('storage-task-level', '4'),
    'object/ui/task/bg_taskLevel5.img': ('storage-task-level', '5'),
    'object/ui/task/btn_finishTask.img': ('storage-task-step', 'btn_finishTask'),
    'object/ui/task/btn_free.img': ('storage-practice', 'free'),
    'object/ui/task/btn_greenHand.img': ('storage-practice', 'new'),
    'object/ui/task/btn_startTask.img': ('storage-task-step', 'btn_startTask'),
    'object/ui/task/btn_task.img': ('storage-task-entry', '任务\n中心'),
    'object/ui/task/btn_taskName.img': ('storage-task-row', None),
    'object/ui/task/dlg_task.img': ('storage-task-detail', None),
    'object/ui/task/dlg_taskSelect.img': ('storage-task-select', None),
}
VISUAL_MAPPING_ASSUMPTIONS = [
    'Storage buttons retain normal/gray/highlight/pressed stored order; task step icons retain normal/highlight/pressed/gray order.',
    'Task level indices retain their original order, with own gold, silver, red-crown, amethyst and rose artwork.',
    'The practice selector uses two existing own portraits. Its two labels and native click rectangles retain their original functions.',
    'The task detail background is rendered in original 430x532 coordinates, then cropped at the measured native raster (28,21,397,518).',
    'Runtime NPC and reward item images are separate native resources and are not supplied by this background renderer.',
]


def material(paints, key):
    if key in paints:
        return paints[key]
    with Image.open(ROOT / PAINT_INPUTS[key]) as image:
        return image.convert('RGBA')


def source_alpha(key, size):
    with Image.open(ROOT / STRUCTURAL_ALPHA_INPUTS[key]) as image:
        if image.size != size:
            raise ValueError('Functional native alpha extent changed')
        return image.getchannel('A')


def fit_icon(image, size, scaled, margin=1):
    factor = min((size[0]-margin*2)/image.width, (size[1]-margin*2)/image.height)
    extent = (max(1, round(image.width*factor)), max(1, round(image.height*factor)))
    out = Image.new('RGBA', size)
    out.alpha_composite(scaled(image, extent), ((size[0]-extent[0])//2, (size[1]-extent[1])//2))
    return out


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    ink, cream, rim = '#284f40', '#f3ead2', '#bea36b'
    font = ImageFont.truetype(str(font_path), 12)
    title = ImageFont.truetype(str(font_path), 15)
    symbol = ImageFont.truetype(FONT_INPUTS['symbols'], 17)

    def panel(extent):
        return nine_slice(scaled(paints['panel'], (132, 124)), extent, 18)

    def button(state):
        out = nine_slice(paints['normal' if state == 'gray' else state], size, 42)
        if state == 'gray':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.06)).enhance(0.78)
        return out

    def well(out, rect, light=False):
        ImageDraw.Draw(out).rounded_rectangle(rect, radius=4,
            fill=cream if light else '#254d42', outline=rim, width=1)

    def practice(mode, extent):
        out = Image.new('RGBA', extent)
        portrait = material(paints, f'storage-task-{mode}-portrait')
        icon = fit_icon(portrait, (extent[0]-8, extent[1]-20), scaled, 1)
        out.alpha_composite(icon, (4, 0))
        plaque = nine_slice(paints['normal'], (extent[0], 23), 42)
        out.alpha_composite(plaque, (0, extent[1]-23))
        text = '自由练习' if mode == 'free' else '新手任务'
        ImageDraw.Draw(out).text((extent[0]//2, extent[1]-12), text, font=font,
                                fill='#fff4d7', anchor='mm', stroke_width=1, stroke_fill=ink)
        return out

    if kind == 'storage-button':
        out = button(('normal', 'gray', 'hover', 'pressed')[index])
        ImageDraw.Draw(out).text((size[0]//2, size[1]//2), label, font=font, fill='#fff4d7',
                                anchor='mm', stroke_width=1, stroke_fill=ink)
        return out
    if kind == 'storage-nav':
        colors = ('#b8a16b', '#888f86', '#edc76a', '#8d783f')
        out = Image.new('RGBA', size, colors[index])
        out.putalpha(source_alpha(f'{label}-{index}', size))
        return out
    if kind in ('storage-selection', 'storage-shadow'):
        key = 'selection' if kind == 'storage-selection' else 'shadow'
        out = Image.new('RGBA', size, '#dfbc65' if key == 'selection' else '#243e34')
        out.putalpha(source_alpha(key, size))
        return out
    if kind == 'storage-grid-room':
        if size != (325, 294):
            raise ValueError('Room storage native extent changed')
        out = Image.new('RGBA', size, '#eadeba')
        for row in range(4):
            for col in range(5):
                x, y = col*65, row*62
                slot = panel((64, 61))
                out.alpha_composite(slot, (x, y))
                well(out, (x+5, y+4, x+60, y+57))
        well(out, (0, 252, 160, 291))
        out.putalpha(source_alpha('room-grid', size))
        return out
    if kind == 'storage-grid-shop':
        if size != (427, 599):
            raise ValueError('Shop storage native extent changed')
        out = panel(size)
        draw = ImageDraw.Draw(out)
        draw.text((22, 25), '我的背包', font=title, fill=ink, anchor='lm')
        for row in range(8):
            for col in range(6):
                x, y = 14+col*62, 47+row*62
                well(out, (x, y, x+58, y+58))
        well(out, (275, 557, 362, 589))
        return out
    if kind == 'storage-task-level':
        key = {'1': 'crown', '2': 'crown', '3': 'red-crown', '4': 'crystal', '5': 'rose'}[label]
        image = material(paints, f'storage-task-{key}')
        if label == '2':
            image = ImageEnhance.Brightness(ImageEnhance.Color(image).enhance(0.02)).enhance(1.18)
        return fit_icon(image, size, scaled, 0)
    if kind == 'storage-task-step':
        state = ('normal', 'hover', 'pressed', 'gray')[index]
        out = Image.new('RGBA', size, '#3c4b40' if state == 'gray' else '#285747')
        out.alpha_composite(button(state))
        if index == 3:
            ImageDraw.Draw(out).text((size[0]//2, size[1]//2-1), '−', font=symbol,
                                    anchor='mm', fill='#e4e1d6')
        elif label == 'btn_startTask':
            ImageDraw.Draw(out).text((size[0]//2, size[1]//2-1), '✓', font=symbol,
                                    anchor='mm', fill='#fff3d1', stroke_width=1, stroke_fill=ink)
        else:
            emblem = fit_icon(material(paints, 'storage-task-crown'), (size[0]-8, size[1]-8), scaled)
            out.alpha_composite(emblem, (4, 3))
        out.putalpha(source_alpha(f'{label}-{index}', size))
        return out
    if kind == 'storage-practice':
        return practice(label, size)
    if kind == 'storage-task-entry':
        out = button(('normal', 'hover', 'pressed')[index])
        ImageDraw.Draw(out).multiline_text((size[0]//2, size[1]//2), label, font=font,
            anchor='mm', align='center', spacing=1, fill='#fff4d7', stroke_width=1, stroke_fill=ink)
        return out
    if kind == 'storage-task-row':
        out = panel(size)
        return ImageEnhance.Brightness(out).enhance((1, 0.92, 1.06, 0.98)[index])
    if kind == 'storage-task-detail':
        if size != (369, 497):
            raise ValueError('Task detail native raster extent changed')
        canvas = Image.new('RGBA', (430, 532))
        canvas.alpha_composite(panel(size), (28, 21))
        well(canvas, (88, 39, 345, 77))
        well(canvas, (141, 84, 366, 189), light=True)
        draw = ImageDraw.Draw(canvas)
        draw.line((65, 207, 379, 207), fill=rim)
        draw.text((69, 218), '完成条件：', font=font, fill=ink, anchor='lm')
        well(canvas, (66, 287, 361, 377))
        well(canvas, (71, 294, 150, 372), light=True)
        ImageDraw.Draw(canvas).text((160, 306), '任务奖励：', font=font, fill='#f3ead2', anchor='lm')
        return canvas.crop((28, 21, 397, 518))
    if kind == 'storage-task-select':
        if size != (368, 326):
            raise ValueError('Task selector native extent changed')
        out = panel(size)
        well(out, (21, 23, 347, 59))
        well(out, (22, 63, 345, 244))
        draw = ImageDraw.Draw(out)
        draw.text((40, 41), '提示信息', font=title, fill='#fff3d5', anchor='lm')
        for y, text in ((79, '欢迎来到灵葫大作战。为了帮助您'),
                        (96, '更好熟悉游戏，我们准备了丰富的'),
                        (113, '练习方式供您选择。')):
            draw.text((36, y), text, font=font, fill='#f3ead2', anchor='lm')
        out.alpha_composite(practice('new', (100, 89)), (55, 134))
        out.alpha_composite(practice('free', (112, 91)), (198, 132))
        return out
    raise ValueError(f'Unknown native storage/task control kind {kind}')
