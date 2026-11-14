"""Native HUD surfaces and replay controls derived from the project's painted UI."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_INPUTS = {'replay-symbols':'C:/Windows/Fonts/seguisym.ttf'}
PAINT_INPUTS = {'game-play':'assets/ui/action-icons-20261112/play.png',
                'game-replay-ring':'assets/ui/controls/radio-off.png'}
PATHS = {
    'object/ui/game/btn_cancelSaveReplay.img':('game-button','取消保存'),
    'object/ui/game/btn_saveReplay.img':('game-button','保存录像'),
    'object/ui/game/btn_storage.img':('game-button','查看背包'),
    'object/ui/game/chatpopo.img':('game-chat',None),
    'object/ui/game/chatpopo2.img':('game-chat',None),
    'object/ui/game/chatpopo3.img':('game-chat',None),
    'object/ui/game/dlg_pveFunc.img':('game-panel',None),
    'object/ui/game/gameLeft.img':('game-edge',None),
    'object/ui/game/gameTop.img':('game-edge',None),
    'object/ui/game/img_itemMask.img':('game-alpha','img_itemmask'),
    'object/ui/game/img_lifeNull.img':('game-alpha','img_lifenull'),
    'object/ui/game/img_lifeRed.img':('game-alpha','img_lifered'),
    'object/ui/game/img_maskCycle.img':('game-alpha','img_maskcycle'),
    'object/ui/game/img_playerLife.img':('game-alpha','img_playerlife'),
    'object/ui/game/img_playerLifeBlue.img':('game-alpha','img_playerlifeblue'),
    'object/ui/game/img_playerLifeRed.img':('game-alpha','img_playerlifered'),
    'object/ui/game/mask_player.img':('game-alpha','mask_player'),
    'object/ui/game/newplayerpopo.img':('game-chat',None),
    'object/ui/game/record/btn_2xSpeedPlay.img':('game-replay','2×'),
    'object/ui/game/record/btn_4xSpeedPlay.img':('game-replay','4×'),
    'object/ui/game/record/btn_Pause.img':('game-replay','■'),
    'object/ui/game/record/btn_Resume.img':('game-replay','play'),
    'object/ui/game/record/ProcessBar.img':('game-alpha','processbar'),
}
STRUCTURAL_ALPHA_INPUTS = {name:f'assets/native-client-ui/game-controls-reference/frames/{name}-000.png'
    for name in ('img_itemmask','img_lifenull','img_lifered','img_maskcycle','img_playerlife',
                 'img_playerlifeblue','img_playerlifered','mask_player','processbar')}


def render(kind,label,index,size,paints,font_path,nine_slice,scaled):
    if kind == 'game-button':
        style = ('normal','normal','hover','pressed')[index]
        out = nine_slice(paints[style],size,42)
        if index == 1:
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.05)).enhance(0.75)
        font = ImageFont.truetype(str(font_path),14)
        ImageDraw.Draw(out).text((size[0]//2,size[1]//2),label,font=font,anchor='mm',
                                 fill='#fff2d0',stroke_width=1,stroke_fill='#244f40')
        return out
    if kind == 'game-replay':
        style = ('normal','hover','pressed')[index]
        if label == 'play':
            out = scaled(paints['game-play'],size)
            return ImageEnhance.Brightness(out).enhance((1,1.16,0.83)[index])
        out = scaled(paints['game-replay-ring'],size)
        out = ImageEnhance.Brightness(out).enhance((1,1.14,0.85)[index])
        font = ImageFont.truetype(FONT_INPUTS['replay-symbols'] if label == '■' else str(font_path),10)
        ImageDraw.Draw(out).text((size[0]//2,size[1]//2),label,font=font,anchor='mm',
                                 fill='#244f40',stroke_width=0)
        return out
    if kind == 'game-chat':
        out = Image.new('RGBA',size)
        left = 34 if size[1] < 100 else 44
        body = nine_slice(scaled(paints['panel'],(132,124)),(size[0]-left,size[1]),18)
        out.alpha_composite(body,(left,0))
        ImageDraw.Draw(out).polygon(((0,round(size[1]*0.79)),(left+1,round(size[1]*0.56)),
                                    (left+1,round(size[1]*0.72))),fill='#f3ead2',outline='#b9a06a')
        return out
    if kind == 'game-panel':
        return nine_slice(scaled(paints['panel'],(132,124)),size,18)
    if kind == 'game-edge':
        out = scaled(paints['normal'].crop((90,35,400,110)),size)
        draw = ImageDraw.Draw(out)
        if size[0] < size[1]:
            draw.line((size[0]-2,0,size[0]-2,size[1]-1),fill='#cbb37b',width=1)
        else:
            draw.line((0,size[1]-2,size[0]-1,size[1]-2),fill='#cbb37b',width=1)
        return out
    if kind == 'game-alpha':
        with Image.open(ROOT/STRUCTURAL_ALPHA_INPUTS[label]) as source:
            if source.size != size:
                raise ValueError('Native functional alpha dimensions changed')
            alpha = source.getchannel('A')
        out = scaled(paints['normal'].crop((90,35,400,110)),size)
        colors = {'img_lifenull':('#233f35','#1a302a'),'img_lifered':('#ffb38b','#a33232'),
                  'img_playerlife':('#e0ed94','#4d904a'),'img_playerlifeblue':('#a1e5f2','#34669c'),
                  'img_playerlifered':('#f4b4a1','#ac3c3c'),'processbar':('#eee0a0','#3b9b74')}
        if label in colors:
            from PIL import ImageColor
            top,bottom = (ImageColor.getrgb(color) for color in colors[label])
            draw = ImageDraw.Draw(out)
            for y in range(size[1]):
                fraction = y/max(1,size[1]-1)
                color = tuple(round(a+(b-a)*fraction) for a,b in zip(top,bottom,strict=True))
                draw.line((0,y,size[0]-1,y),fill=(*color,255))
        elif label in ('img_itemmask','mask_player'):
            out = ImageEnhance.Brightness(out).enhance(0.6)
        out.putalpha(alpha)
        return out
    raise ValueError(f'Unknown game UI kind: {kind}')
