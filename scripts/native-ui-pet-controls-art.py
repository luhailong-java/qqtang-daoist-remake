"""Own jade/ivory pet controls, preserving all native resource state slots."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REF = 'assets/native-client-ui/pet-controls-reference'
FONT_INPUTS = {'symbols': 'C:/Windows/Fonts/seguisym.ttf'}
PAINT_INPUTS = {f'pet-face-{i}': f'{REF}/emotions/face{i}-master.png' for i in range(5)}
ART_GENERATION_RECORDS = [f'{REF}/emotions/face{i}-master.png.generation.json' for i in range(5)]
STRUCTURAL_ALPHA_INPUTS = {key: f'{REF}/frames/{key}-000.png' for key in ('dlg_food', 'img_exp')}
for stem in ('btn_first_page', 'btn_last_page', 'btn_next_page', 'btn_pre_page'):
    for index in range(4):
        STRUCTURAL_ALPHA_INPUTS[f'{stem}-{index}'] = f'{REF}/frames/{stem}-{index:03}.png'

PATHS = {
    'object/ui/pet/btn_adopt.img': ('pet-button', '领养'),
    'object/ui/pet/btn_change_name.img': ('pet-button', '更改'),
    'object/ui/pet/btn_first_page.img': ('pet-nav', 'btn_first_page'),
    'object/ui/pet/btn_free.img': ('pet-button', '放生'),
    'object/ui/pet/btn_last_page.img': ('pet-nav', 'btn_last_page'),
    'object/ui/pet/btn_next_page.img': ('pet-nav', 'btn_next_page'),
    'object/ui/pet/btn_pre_page.img': ('pet-nav', 'btn_pre_page'),
    'object/ui/pet/btn_raise.img': ('pet-fold', 'raise'),
    'object/ui/pet/btn_raise1.img': ('pet-fold', 'raise1'),
    'object/ui/pet/btn_skill.img': ('pet-fold', 'skill'),
    'object/ui/pet/btn_skill1.img': ('pet-fold', 'skill1'),
    'object/ui/pet/btn_stop_take.img': ('pet-button', '休息'),
    'object/ui/pet/btn_take.img': ('pet-button', '携带'),
    'object/ui/pet/dlg_baseskill.img': ('pet-base-skills', None),
    'object/ui/pet/dlg_food.img': ('pet-food-grid', None),
    'object/ui/pet/dlg_pet.img': ('pet-main', None),
    'object/ui/pet/dlg_skill.img': ('pet-skills', None),
    'object/ui/pet/face0.img': ('pet-face', '0'),
    'object/ui/pet/face1.img': ('pet-face', '1'),
    'object/ui/pet/face2.img': ('pet-face', '2'),
    'object/ui/pet/face3.img': ('pet-face', '3'),
    'object/ui/pet/face4.img': ('pet-face', '4'),
    'object/ui/pet/img_exp.img': ('pet-progress', None),
}
VISUAL_MAPPING_ASSUMPTIONS = [
    'Button captions and per-slot fold arrows were read directly from native rasters; original native callbacks and slot indices are retained.',
    'The five face indices retain five distinct observed facial expressions; the mood value to index computation is not promoted to verified runtime behavior.',
    'Each emotion has a separately generated own transparent master. Slot 1 is an own brighter material variant with the original raster extent and offset, not a claim to reproduce every original subpixel facial change.',
    'Emotion packing uses the alpha>=8 visible bounding box plus one pixel padding; excluded host-cutout dust has alpha<8. The body alpha is retained, then premultiplied scaling and native quantization apply.',
    'The main panel is laid out in its original 257x290 declared coordinate space and cropped at native raster box (2,2,253,287).',
    'White dynamic name, values and skill labels keep dark jade wells; brown dynamic level text keeps an ivory surface, based on static source symbolic assignments.',
    'Pet creature previews and inventory food icons are separate resources, not baked into this control group.',
]


def material(paints, key):
    if key in paints:
        return paints[key]
    with Image.open(ROOT / PAINT_INPUTS[key]) as image:
        return image.convert('RGBA')


def source_alpha(key, size):
    with Image.open(ROOT / STRUCTURAL_ALPHA_INPUTS[key]) as image:
        if image.size != size:
            raise ValueError('Functional source alpha geometry changed')
        return image.getchannel('A')


def emotion_geometry(master, face_index):
    alpha = master.getchannel('A')
    bounds = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
    if not bounds or alpha.getextrema() != (0, 255):
        raise ValueError('Emotion master must be a real transparent cutout')
    left, top, right, bottom = bounds
    crop = (max(0, left-1), max(0, top-1), min(master.width, right+1), min(master.height, bottom+1))
    outside = []
    for box in ((0, 0, master.width, crop[1]), (0, crop[3], master.width, master.height),
                (0, crop[1], crop[0], crop[3]), (crop[2], crop[1], master.width, crop[3])):
        if box[2] > box[0] and box[3] > box[1]:
            outside.append(alpha.crop(box).getextrema()[1])
    if max(outside, default=0) >= 8:
        raise ValueError('Emotion crop would exclude visible expression art')
    common_box = [0, 0 if str(face_index) == '2' else 1, 34, 33]
    return {'alphaThreshold': 8, 'sourceBox': list(crop), 'excludedMaxAlpha': max(outside, default=0),
            'logicalCanvas': [34, 33], 'commonNativeLogicalBox': common_box,
            'operation': 'Bound visible cutout plus one-pixel padding; premultiplied fit once into both native state windows intersection; cut each original state window'}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    ink, cream, gold, jade = '#284f40', '#f3ead2', '#bea36b', '#254d42'
    font = ImageFont.truetype(str(font_path), 12)
    title = ImageFont.truetype(str(font_path), 15)
    symbol = ImageFont.truetype(FONT_INPUTS['symbols'], 16)

    def panel(extent):
        return nine_slice(scaled(paints['panel'], (132, 124)), extent, 18)

    def well(out, rect, light=False):
        ImageDraw.Draw(out).rounded_rectangle(rect, radius=4, fill=cream if light else jade,
                                               outline=gold, width=1)

    def button(state):
        out = nine_slice(paints['normal' if state == 'gray' else state], size, 42)
        if state == 'gray':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.06)).enhance(0.78)
        return out

    if kind == 'pet-button':
        state = ('normal', 'hover', 'pressed', 'gray')[index]
        out = button(state)
        draw = ImageDraw.Draw(out)
        draw.text((size[0]//2, size[1]//2 + (1 if index == 2 else 0)), label,
                  font=font, fill=cream if index != 3 else '#d2d0c6', anchor='mm', stroke_width=0)
        return out

    if kind == 'pet-nav':
        out = Image.new('RGBA', size, ('#89b694', '#96968d', '#e5d19b', '#4d9071')[index])
        out.putalpha(source_alpha(f'{label}-{index}', size))
        return out

    if kind == 'pet-fold':
        state = ('normal', 'hover', 'pressed', 'gray')[index]
        out = button(state)
        draw = ImageDraw.Draw(out)
        text = '背包' if label.startswith('raise') else '技能'
        draw.text((43, size[1]//2 + (1 if index == 2 else 0)), text, font=title,
                  fill=cream if index != 3 else '#d2d0c6', anchor='mm')
        # Source raise0 f0 opens down; skill0 f0 opens right. Alternate resource
        # swaps that pose to pressed f2. The other slots use a left arrow.
        opened = (label.endswith('1') and index == 2) or (not label.endswith('1') and index == 0)
        arrow = ('▾' if label.startswith('raise') else '▸') if opened else '◂'
        draw.text((88, size[1]//2), arrow, font=symbol,
                  fill=cream if index != 3 else '#d2d0c6', anchor='mm')
        return out

    if kind == 'pet-main':
        out = panel((257, 290))
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((12, 8, 243, 37), radius=7, fill=jade, outline=gold)
        draw.text((128, 22), '我的宠物', font=title, fill=cream, anchor='mm')
        well(out, (53, 46, 151, 144))
        well(out, (55, 154, 181, 177))
        draw.text((16, 165), '名称', font=font, fill=ink, anchor='lm')
        draw.text((16, 192), '等级', font=font, fill=ink, anchor='lm')
        # Native level is darkColor, unlike the neighboring white fields.
        well(out, (82, 183, 191, 204), light=True)
        draw.text((16, 214), '成长值', font=font, fill=ink, anchor='lm')
        draw.text((16, 232), '体力', font=font, fill=ink, anchor='lm')
        for y in (209, 227):
            well(out, (73, y, 168, y+10))
        for y in (207, 225):
            well(out, (172, y, 252, y+17))
        return out.crop((2, 2, 253, 287))

    if kind == 'pet-food-grid':
        out = Image.new('RGBA', size, cream)
        out.alpha_composite(panel(size))
        draw = ImageDraw.Draw(out)
        for row in range(3):
            for col in range(4):
                x, y = 3+col*62, 1+row*62
                well(out, (x, y, x+60, y+60))
                draw.rounded_rectangle((x+5, y+5, x+55, y+55), radius=4,
                                       fill='#e7dfc6', outline='#ab9465')
                # Source itemNum explicitly uses lightColor, not default black.
                draw.rounded_rectangle((x+20, y+38, x+58, y+57), radius=3, fill=jade)
        well(out, (3, 190, 251, 222), light=True)
        out.putalpha(source_alpha('dlg_food', size))
        return out

    if kind in ('pet-base-skills', 'pet-skills'):
        # Both source rasters begin at x=2 in a 109-wide declared panel.
        out = panel(size)
        draw = ImageDraw.Draw(out)
        if kind == 'pet-base-skills':
            draw.rounded_rectangle((5, 10, size[0]-5, size[1]-5), radius=4,
                                   fill=jade, outline=gold)
            for y in (37, 64):
                draw.line((7, y, size[0]-7, y), fill='#547462')
        else:
            draw.rounded_rectangle((5, 1, size[0]-5, size[1]-5), radius=4,
                                   fill=jade, outline=gold)
            for y in range(29, size[1]-8, 27):
                draw.line((7, y, size[0]-7, y), fill='#547462')
        return out

    if kind == 'pet-progress':
        out = Image.new('RGBA', size, '#c4a348')
        draw = ImageDraw.Draw(out)
        draw.line((1, 1, size[0]-2, 1), fill='#f9edb6', width=1)
        draw.line((1, size[1]-2, size[0]-2, size[1]-2), fill='#8a713b', width=1)
        out.putalpha(source_alpha('img_exp', size))
        return out

    if kind == 'pet-face':
        master = material(paints, f'pet-face-{label}')
        geometry = emotion_geometry(master, label)
        cutout = master.crop(geometry['sourceBox'])
        # Both stored native windows must contain the complete own face.
        # Register once into their logical intersection, never fit each slot.
        left, top, right, bottom = geometry['commonNativeLogicalBox']
        common_width, common_height = right-left, bottom-top
        factor = min(common_width/cutout.width, common_height/cutout.height)
        extent = (max(1, round(cutout.width*factor)), max(1, round(cutout.height*factor)))
        out = Image.new('RGBA', (34, 33))
        out.alpha_composite(scaled(cutout, extent),
                            (left+(common_width-extent[0])//2, top+(common_height-extent[1])//2))
        if index:
            out = ImageEnhance.Brightness(out).enhance(1.10)
        # All native second states except face2 store y=1 with one row less.
        if size == (34, 32):
            out = out.crop((0, 1, 34, 33))
        if out.size != size:
            raise ValueError('Emotion native raster changed')
        return out
    raise ValueError(f'Unknown pet kind: {kind}')
