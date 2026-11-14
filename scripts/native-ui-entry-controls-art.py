"""Own login accessory, connection-state and replay-file native UI art."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAINT_INPUTS = {
    'entry-wordmark': 'assets/branding/linghu-wordmark-login-1024.png',
    'entry-replay': 'assets/ui/semantic-extra/save-replay.png',
    'entry-folder': 'assets/ui/semantic-extra/warehouse.png',
}
STRUCTURAL_ALPHA_INPUTS = {
    'Source segmented status silhouette; RGB is fully replaced':
        'assets/native-client-ui/entry-controls-reference/frames/selsect/img_state/frame-000.png',
}
PATHS = {
    'object/ui/login/btn_nextpic.img': ('entry-four-button', '看不清，换一个'),
    'object/ui/login/btn_playAnim.img': ('entry-three-button', '播放动画'),
    'object/ui/login/btn_vnetLogin.img': ('entry-three-button', 'VNET登录'),
    'object/ui/login/dlg_verify.img': ('entry-verify-panel', None),
    'object/ui/login/dlg_vnetLogin.img': ('entry-vnet-panel', None),
    'object/ui/login/dlg_wait.img': ('entry-wait-panel', None),
    'object/ui/login/img_lago.img': ('entry-wordmark', None),
    'object/ui/login/img_link.img': ('entry-connection-strip', None),
    'object/ui/selSect/img_state.img': ('entry-state-strip', None),
    'object/ui/selSect/netspeed_fast.img': ('entry-network', '快'),
    'object/ui/selSect/netspeed_mid.img': ('entry-network', '中'),
    'object/ui/selSect/netspeed_slow.img': ('entry-network', '慢'),
    'object/ui/selSect/netspeed_test.img': ('entry-network', '测试中'),
    'object/ui/selSect/netspeed_unknown.img': ('entry-network', '未知'),
    'object/ui/record/icon_file.img': ('entry-file', None),
    'object/ui/record/icon_folder.img': ('entry-folder-icon', None),
}


def material(paints, key):
    if key in paints:
        return paints[key]
    with Image.open(ROOT / PAINT_INPUTS[key]) as source:
        return source.convert('RGBA')


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    if kind in ('entry-four-button', 'entry-three-button'):
        style = ('normal', 'normal', 'hover', 'pressed')[index] if kind == 'entry-four-button' else ('normal', 'hover', 'pressed')[index]
        out = nine_slice(paints[style], size, 42)
        if kind == 'entry-four-button' and index == 1:
            out = ImageEnhance.Color(out).enhance(0.08)
            out = ImageEnhance.Brightness(out).enhance(0.72)
        font = ImageFont.truetype(str(font_path), 12)
        ImageDraw.Draw(out).text((size[0] // 2, size[1] // 2), label, font=font,
                                fill='#fff3d6', anchor='mm', stroke_width=1, stroke_fill='#254d3e')
        return out
    if kind in ('entry-verify-panel', 'entry-vnet-panel', 'entry-wait-panel'):
        out = nine_slice(scaled(paints['panel'], (132, 124)), size, 18)
        draw = ImageDraw.Draw(out)
        if kind == 'entry-verify-panel':
            draw.text((size[0] // 2, 30), '身份验证', font=ImageFont.truetype(str(font_path), 20),
                      fill='#245c49', anchor='mm')
            draw.text((40, 92), '进入仙境，请输入验证码：', font=ImageFont.truetype(str(font_path), 15), fill='#245c49')
            # verifyEdit rect=(50,120,100,24), captionrect=(0,6,100,12).
            # It assigns the symbolic darkColor to drawcolor; keep a pale field.
            draw.rounded_rectangle((48, 118, 152, 146), 4, fill='#fff8e4', outline='#b69a60', width=2)
            # The native CAPTCHA widget paints its own image at (43,154).
            draw.rectangle((41, 152, 182, 210), fill='#e7e5cb', outline='#7e9a7c', width=2)
        elif kind == 'entry-wait-panel':
            draw.text((size[0] // 2, 14), '正在连接仙境…', font=ImageFont.truetype(str(font_path), 13),
                      fill='#245c49', anchor='mm')
        # VNET dialog supplies its content dynamically. Leave the pale well free.
        return out
    if kind == 'entry-wordmark':
        out = Image.new('RGBA', size)
        draw = ImageDraw.Draw(out)
        cx, cy, radius = size[0] // 2, 40, 29
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill='#255b47', outline='#c9aa63', width=2)
        draw.ellipse((cx-8, cy-22, cx+8, cy-6), fill='#e3c27b')
        draw.ellipse((cx-13, cy-9, cx+13, cy+18), fill='#e3c27b')
        draw.arc((cx-4, cy-31, cx+9, cy-18), 90, 230, fill='#83b495', width=3)
        logo = material(paints, 'entry-wordmark')
        ratio = (size[0]-8) / logo.width
        logo = scaled(logo, (size[0]-8, max(1, round(logo.height*ratio))))
        out.alpha_composite(logo, (4, 84))
        draw.text((cx, 156), '道家 Q 版', font=ImageFont.truetype(str(font_path), 13),
                  fill='#fff3d6', stroke_fill='#254d3e', stroke_width=1, anchor='mm')
        return out
    if kind == 'entry-connection-strip':
        out = nine_slice(paints['normal'], size, 42)
        draw = ImageDraw.Draw(out)
        # Two original positions remain two positions; their runtime duration is unknown.
        for x in range(8 + 12*index, size[0]-5, 24):
            draw.polygon(((x, 5), (x+6, 5), (x+12, size[1]-6), (x+6, size[1]-6)), fill='#b8c78a')
        return out
    if kind == 'entry-state-strip':
        source_path = ROOT / next(iter(STRUCTURAL_ALPHA_INPUTS.values()))
        with Image.open(source_path) as source:
            alpha = source.convert('RGBA').getchannel('A')
        if alpha.size != size:
            raise ValueError('Native status strip silhouette geometry differs')
        out = Image.new('RGBA', size)
        draw = ImageDraw.Draw(out)
        for x in range(size[0]):
            t = x / max(1, size[0]-1)
            color = tuple(round(a+(b-a)*t) for a,b in zip((221,187,94),(93,168,124),strict=True))
            draw.line((x, 0, x, size[1]-1), fill=(*color,255))
        out.putalpha(alpha)
        return out
    if kind == 'entry-network':
        out = Image.new('RGBA', size)
        draw = ImageDraw.Draw(out)
        color = {'快':'#a9d997','中':'#e4c47c','慢':'#efa083','测试中':'#b6d6c7','未知':'#dfdccb'}[label]
        font = ImageFont.truetype(str(font_path), 10)
        text = label + ('›››' if label in ('快','中','慢') else '')
        draw.text((size[0] // 2, size[1] // 2), text, font=font, anchor='mm',
                  fill=color, stroke_width=1, stroke_fill='#294e3e')
        return out
    if kind in ('entry-file', 'entry-folder-icon'):
        out = Image.new('RGBA', size)
        symbol = material(paints, 'entry-replay' if kind == 'entry-file' else 'entry-folder')
        symbol = symbol.crop(symbol.getchannel('A').getbbox())
        ratio = min(size[0]/symbol.width, size[1]/symbol.height)
        symbol = scaled(symbol, (max(1, round(symbol.width*ratio)), max(1, round(symbol.height*ratio))))
        if kind == 'entry-folder-icon' and index == 0:
            symbol = ImageEnhance.Brightness(symbol).enhance(0.87)
        out.alpha_composite(symbol, ((size[0]-symbol.width)//2, (size[1]-symbol.height)//2))
        return out
    raise ValueError(f'Unknown entry UI resource kind {kind}')
