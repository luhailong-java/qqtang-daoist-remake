"""Native shop action buttons and tabs using the existing original painted UI kit."""
from PIL import ImageDraw, ImageEnhance, ImageFont

PATHS = {
    'object/ui/shop/btn_buy.img': ('shop-stack-button', '购\n买'),
    'object/ui/shop/btn_cancelEquip.img': ('shop-button', '默认'),
    'object/ui/shop/btn_collect.img': ('shop-button', '收藏'),
    'object/ui/shop/btn_donate.img': ('shop-button', '赠送'),
    'object/ui/shop/btn_forge.img': ('shop-button', '锻造合成'),
    'object/ui/shop/btn_recycler.img': ('shop-button', '收藏柜'),
    'object/ui/shop/btn_repair.img': ('shop-button', '修复'),
    'object/ui/shop/btn_require.img': ('shop-button', '索要'),
    'object/ui/shop/btn_resume.img': ('shop-button', '恢复'),
    'object/ui/shop/btn_saveEquip.img': ('shop-button', '装备'),
    'object/ui/shop/btn_storage.img': ('shop-button', '背包'),
    'object/ui/shop/tab_advice.img': ('shop-tab', '推荐'),
    'object/ui/shop/tab_func.img': ('shop-tab', '功能'),
    'object/ui/shop/tab_adorn.img': ('shop-tab', '装饰'),
    'object/ui/shop/tab_equip.img': ('shop-tab', '装备'),
    'object/ui/shop/tab_pet.img': ('shop-tab', '宠物'),
    'object/ui/shop/tab_zizuan.img': ('shop-tab', None),
    'object/ui/shop/tab_itemFunc.img': ('shop-tab', '功能'),
    'object/ui/shop/tab_itemAdorn.img': ('shop-tab', '装饰'),
    'object/ui/shop/tab_itemEquip.img': ('shop-tab', '装备'),
}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    """Render a native stored frame at its exact original encoded pixel extent."""
    if kind not in ('shop-button', 'shop-stack-button', 'shop-tab'):
        raise ValueError(f'Unknown native shop control kind {kind}')
    if kind == 'shop-tab':
        if index not in (0, 1):
            raise ValueError('Shop tabs declare two stored frames')
        if index == 1:
            out = nine_slice(scaled(paints['panel'], (132, 124)), size, 18)
        else:
            out = nine_slice(paints['normal'], size, 42)
    else:
        if index not in (0, 1, 2, 3):
            raise ValueError('Shop buttons declare four stored frames')
        style = ('normal', 'normal', 'hover', 'pressed')[index]
        out = nine_slice(paints[style], size, 42)
        if index == 1:
            out = ImageEnhance.Color(out).enhance(0.05)
            out = ImageEnhance.Brightness(out).enhance(0.75)
    if label is None:
        return out

    selected = kind == 'shop-tab' and index == 1
    fill, shadow = ('#24513f', '#fff3d5') if selected else ('#fff4d9', '#24513f')
    if kind != 'shop-tab' and index == 1:
        fill, shadow = '#d0cabc', '#424c42'
    font_size = {2: 13, 3: 12}.get(len(label.replace('\n', '')), 10)
    font = ImageFont.truetype(str(font_path), font_size)
    draw = ImageDraw.Draw(out)
    if kind == 'shop-stack-button':
        draw.multiline_text((size[0]//2, size[1]//2), label, font=font, anchor='mm',
                            align='center', spacing=0, fill=fill, stroke_width=1, stroke_fill=shadow)
    else:
        draw.text((size[0]//2, size[1]//2), label, font=font, anchor='mm',
                  fill=fill, stroke_width=0 if selected else 1, stroke_fill=shadow)
    return out
