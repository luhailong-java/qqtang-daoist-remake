"""Native common controls composed from the project's painted jade UI and font."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SYMBOL_FONT = Path('C:/Windows/Fonts/seguisym.ttf')
FONT_INPUTS = {'symbols': str(SYMBOL_FONT)}
PAINT_INPUTS = {
    'common-radio-on': 'assets/ui/controls/radio-on.png',
    'common-radio-off': 'assets/ui/controls/radio-off.png',
    'common-scroll-thumb': 'assets/ui/controls/scroll-thumb.png',
    'common-paper': 'assets/ui/paper-card.png',
}
PATHS = {
    'object/ui/common/btn_agree.img': ('common-button', '同意'),
    'object/ui/common/btn_refuse.img': ('common-button', '拒绝'),
    'object/ui/common/btn_close.img': ('common-button', '关闭'),
    'object/ui/common/btn_next.img': ('common-button', '下一步'),
    'object/ui/common/btn_leave.img': ('common-tall-button', '离开'),
    'object/ui/common/btn_leavegame.img': ('common-tall-button', '离开'),
    'object/ui/common/btn_quit.img': ('common-tall-button', '退出'),
    'object/ui/common/btn_return.img': ('common-tall-button', '返回'),
    'object/ui/common/btn_left.img': ('common-arrow', '◀'),
    'object/ui/common/btn_right.img': ('common-arrow', '▶'),
    'object/ui/common/btn_check.img': ('common-check', None),
    'object/ui/common/btn_ratio.img': ('common-radio', None),
    'object/ui/common/dlg_msgBox.img': ('common-message', None),
    'object/ui/common/img_chat.img': ('common-chat', None),
    'object/ui/common/img_tip.img': ('common-tip', None),
    'object/ui/common/scl_block.img': ('common-scroll', None),
    'object/ui/common/tip_new.img': ('common-new-tip', '道具更新'),
    'object/ui/common/number1.img': ('common-number', 'number1'),
    'object/ui/common/number2.img': ('common-number', 'number2'),
    'object/ui/common/number3.img': ('common-number', 'number3'),
    'object/ui/common/number4.img': ('common-number', 'number4'),
    'object/ui/common/number5.img': ('common-number', 'number5'),
    'object/ui/common/number6.img': ('common-number', 'number6'),
    'object/ui/common/numberMoney.img': ('common-number', 'numberMoney'),
}

# Canvas and cropped raster bounds are the measured DIMG fields. Every full strip
# has 15 cells. Money swaps the colon and slash relative to the other six strips.
NUMBER_LAYOUTS = {
    'number1': ((1545, 130), (0, 0, 1517, 130), 103, '0123456789/:-+.'),
    'number2': ((285, 24), (0, 0, 281, 24), 19, '0123456789/:-+.'),
    'number3': ((405, 36), (0, 0, 398, 36), 27, '0123456789/:-+.'),
    'number4': ((240, 18), (2, 1, 236, 17), 16, '0123456789/:-+.'),
    'number5': ((240, 18), (1, 0, 237, 18), 16, '0123456789/:-+.'),
    'number6': ((210, 18), (0, 1, 208, 18), 14, '0123456789/:-+.'),
    'numberMoney': ((135, 13), (0, 0, 131, 13), 9, '0123456789:/-+.'),
}


def material(paints, name):
    if name in paints:
        return paints[name]
    with Image.open(ROOT / PAINT_INPUTS[name]) as image:
        return image.convert('RGBA')


def number_strip(name, size, font_path):
    canvas, crop, cell_width, characters = NUMBER_LAYOUTS[name]
    if size != (crop[2] - crop[0], crop[3] - crop[1]):
        raise ValueError(f'{name}: unexpected original number-strip raster size')
    height = canvas[1]
    stroke = 2 if height > 60 else int(height > 13)
    font_size = height * 2
    while font_size > 1:
        font = ImageFont.truetype(str(font_path), font_size)
        boxes = [font.getbbox(char, stroke_width=stroke) for char in characters]
        top = min(box[1] for box in boxes)
        bottom = max(box[3] for box in boxes)
        if (max(box[2] - box[0] for box in boxes) <= cell_width - 2
                and bottom - top <= height - 2):
            break
        font_size -= 1
    out = Image.new('RGBA', canvas)
    draw = ImageDraw.Draw(out)
    fill = '#f1d78a' if name in ('number1', 'number3', 'number5') else '#f4ecd0'
    origin_y = (height - (bottom - top)) // 2 - top
    for index, char in enumerate(characters):
        left, _, right, _ = font.getbbox(char)
        center = index * cell_width + cell_width // 2
        draw.text((center - (right - left) // 2 - left, origin_y), char,
                  font=font, fill=fill, stroke_width=stroke, stroke_fill='#234c3e')
    return out.crop(crop)


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    if kind == 'common-number':
        if index != 0:
            raise ValueError('The original number strip has one raster position')
        return number_strip(label, size, font_path)

    ink = '#24513f'
    cream = '#fff2cf'
    font = ImageFont.truetype(str(font_path), 13)
    if kind in ('common-button', 'common-tall-button', 'common-arrow'):
        style = ('normal', 'normal', 'hover', 'pressed')[index]
        out = nine_slice(paints[style], size, 42)
        if index == 1:
            out = ImageEnhance.Color(out).enhance(0.08)
            out = ImageEnhance.Brightness(out).enhance(0.72)
        draw = ImageDraw.Draw(out)
        if kind == 'common-arrow':
            font = ImageFont.truetype(str(SYMBOL_FONT), 18)
        draw.text((size[0] // 2, size[1] // 2), label, font=font,
                  fill='#dedbc8' if index == 1 else cream,
                  anchor='mm', stroke_width=1, stroke_fill=ink)
        return out
    if kind == 'common-check':
        out = Image.new('RGBA', size)
        font = ImageFont.truetype(str(SYMBOL_FONT), 14)
        draw = ImageDraw.Draw(out)
        box = draw.textbbox((0, 0), '✓', font=font)
        glyph = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]))
        ImageDraw.Draw(glyph).text((-box[0], -box[1]), '✓', font=font, fill='#b99a45')
        out.alpha_composite(scaled(glyph, size))
        return out
    if kind == 'common-radio':
        return scaled(material(paints, 'common-radio-on' if index == 0 else 'common-radio-off'), size)
    if kind == 'common-scroll':
        out = scaled(material(paints, 'common-scroll-thumb'), size)
        return ImageEnhance.Brightness(out).enhance(1.14) if index else out
    if kind == 'common-message':
        out = nine_slice(paints['panel'], size, 72)
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((28, 58, size[0] - 29, 256), radius=7,
                               fill='#f0e7cf', outline='#c9ad6c', width=2)
        # Shared LABEL children inherit black text; captions remain runtime data.
        return out
    if kind in ('common-tip', 'common-chat'):
        body_height = size[1] - 7 if kind == 'common-chat' else size[1]
        out = Image.new('RGBA', size)
        paper = material(paints, 'common-paper')
        out.alpha_composite(nine_slice(scaled(paper, (130, 124)), (size[0], body_height), 18))
        if kind == 'common-chat':
            draw = ImageDraw.Draw(out)
            draw.polygon(((size[0] // 2 - 6, body_height - 3),
                          (size[0] // 2, body_height - 3),
                          (size[0] // 2 - 6, size[1] - 1)),
                         fill='#f1e9d1', outline='#b59c63')
        return out
    if kind == 'common-new-tip':
        out = nine_slice(paints['hover'], size, 42)
        ImageDraw.Draw(out).text((size[0] // 2, size[1] // 2), label,
                                font=font, fill=cream, anchor='mm')
        return out
    raise ValueError(f'Unknown native common resource kind {kind}')
