"""Native guide bar, system menu and social controls from existing painted UI."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAINT_INPUTS = {
    'guidebar-shop': 'assets/ui/icons/shop.png',
    'guidebar-social': 'assets/ui/semantic-extra/friends.png',
    'guidebar-task': 'assets/ui/semantic-extra/task.png',
    'guidebar-person': 'assets/ui/icons/person.png',
    'guidebar-pet': 'assets/ui/semantic-extra/pet-card.png',
    'guidebar-menu': 'assets/ui/icons/settings.png',
    'guidebar-paper': 'assets/ui/paper-card.png',
}
PATHS = {
    'object/ui/guideBar/btn_shop.img': ('guidebar-navigation', '道具商城'),
    'object/ui/guideBar/btn_trade.img': ('guidebar-navigation', '交易中心'),
    'object/ui/guideBar/btn_sociality.img': ('guidebar-navigation', '社交'),
    'object/ui/guideBar/btn_task.img': ('guidebar-navigation', '任务'),
    'object/ui/guideBar/btn_member.img': ('guidebar-navigation', '会员'),
    'object/ui/guideBar/btn_info.img': ('guidebar-navigation', '资料'),
    'object/ui/guideBar/btn_pet.img': ('guidebar-navigation', '宠物'),
    'object/ui/guideBar/btn_menu.img': ('guidebar-navigation', '菜单'),
    'object/ui/guideBar/btn_setup.img': ('guidebar-button', '系统设置'),
    'object/ui/guideBar/btn_help.img': ('guidebar-button', '帮助说明'),
    'object/ui/guideBar/btn_GCS.img': ('guidebar-button', '在线客服'),
    'object/ui/guideBar/btn_record.img': ('guidebar-button', '观看录像'),
    'object/ui/guideBar/btn_web.img': ('guidebar-button', '进入官网'),
    'object/ui/guideBar/player/btn_addFriend.img': ('guidebar-button', '加为好友'),
    'object/ui/guideBar/player/btn_deleteFriend.img': ('guidebar-button', '删除好友'),
    'object/ui/guideBar/player/btn_privateChat.img': ('guidebar-button', '密聊'),
    'object/ui/guideBar/player/btn_trace.img': ('guidebar-button', '追踪'),
    'object/ui/guideBar/player/btn_spark.img': ('guidebar-button', '求婚'),
    'object/ui/guideBar/player/btn_lookup.img': ('guidebar-button', '查看'),
    'object/ui/guideBar/player/tab_modeInfo.img': ('guidebar-tab', '模式等级'),
    'object/ui/guideBar/player/tab_pveInfo.img': ('guidebar-tab', '探险资历'),
    'object/ui/guideBar/player/tab_pvpInfo.img': ('guidebar-tab', '竞技资历'),
    'object/ui/guideBar/img_guide.img': ('guidebar-strip', None),
    'object/ui/guideBar/dlg_menu.img': ('guidebar-menu-panel', None),
    'object/ui/guideBar/dlg_playermenu.img': ('guidebar-context-panel', None),
    'object/ui/guideBar/btn_playermenuChoose.img': ('guidebar-context-hover', None),
}
NAVIGATION_ICONS = {
    '道具商城': 'guidebar-shop', '交易中心': 'guidebar-shop', '社交': 'guidebar-social',
    '任务': 'guidebar-task', '会员': 'guidebar-person', '资料': 'guidebar-person',
    '宠物': 'guidebar-pet', '菜单': 'guidebar-menu',
}


def material(paints, name):
    if name in paints:
        return paints[name]
    with Image.open(ROOT / PAINT_INPUTS[name]) as image:
        return image.convert('RGBA')


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    if kind in ('guidebar-navigation', 'guidebar-button', 'guidebar-tab'):
        if kind == 'guidebar-navigation':
            style = ('normal', 'hover', 'pressed')[index]
            text, icon_name = label, NAVIGATION_ICONS[label]
        elif kind == 'guidebar-tab':
            style = ('normal', 'hover')[index]
            text, icon_name = label, None
        else:
            style = ('normal', 'normal', 'hover', 'pressed')[index]
            text, icon_name = label, None
        out = nine_slice(paints[style], size, 42)
        if kind == 'guidebar-button' and index == 1:
            out = ImageEnhance.Color(out).enhance(0.08)
            out = ImageEnhance.Brightness(out).enhance(0.72)
        draw = ImageDraw.Draw(out)
        font = ImageFont.truetype(str(font_path), 12 if len(text) > 2 else 13)
        text_x = size[0] // 2
        if icon_name:
            symbol = material(paints, icon_name)
            target = min(22, size[1] - 8)
            ratio = min(target / symbol.width, target / symbol.height)
            symbol = scaled(symbol, tuple(max(1, round(v * ratio)) for v in symbol.size))
            text_width = draw.textbbox((0, 0), text, font=font)[2]
            width = symbol.width + 4 + text_width
            left = (size[0] - width) // 2
            out.alpha_composite(symbol, (left, (size[1] - symbol.height) // 2))
            text_x = left + symbol.width + 4 + text_width // 2
        draw.text((text_x, size[1] // 2), text, font=font,
                  fill='#e0decf' if kind == 'guidebar-button' and index == 1 else '#fff3d6',
                  anchor='mm', stroke_width=1, stroke_fill='#254d3e')
        return out
    if kind == 'guidebar-strip':
        return nine_slice(paints['normal'], size, 42)
    if kind == 'guidebar-menu-panel':
        paper = material(paints, 'guidebar-paper')
        return nine_slice(scaled(paper, (132, 124)), size, 18)
    if kind in ('guidebar-context-panel', 'guidebar-context-hover'):
        # uiMain.messageBtn explicitly uses white lightColor without a text edge.
        # Its sibling menu classes inherit that caption style.
        out = nine_slice(paints['normal'], size, 42)
        edge = 2 if kind == 'guidebar-context-hover' else 3
        ImageDraw.Draw(out).rectangle((edge, edge, size[0] - edge - 1, size[1] - edge - 1),
                                      fill='#2b5743' if kind == 'guidebar-context-hover' else '#224a3b')
        return out
    raise ValueError(f'Unknown native guide bar resource kind {kind}')
