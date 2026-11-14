"""Own room UI artwork, exact native source slots and proven identity joins."""
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REF = 'assets/native-client-ui/room-extra-reference'
RENDERER_PREFIX = 'roomextra-'
REFERENCE_MANIFEST = f'{REF}/manifest.json'
REFERENCE_INPUTS = [f'{REF}/roster-mapping-audit.json', f'{REF}/owned-portrait-derivations.json',
                    f'{REF}/extra-icon-source-semantics.json', f'{REF}/extra-icon-generation-requests.json']
FONT_INPUTS = {'symbols': 'C:/Windows/Fonts/seguisym.ttf'}
_SOURCE = json.loads((ROOT / REFERENCE_MANIFEST).read_bytes())
_BY_PATH = {r['nativePath']: r for r in _SOURCE['resources']}
_MAPPING = json.loads((ROOT / f'{REF}/roster-mapping-audit.json').read_bytes())
_ROLES = {e['nativeAlias']: e for e in _MAPPING['entries']+_MAPPING['pveAdditionalEntries']}
_EXTRA = ['67','69','72','73','75','77','78','79','81','85','117','118','119','124','125','xxm','zjl']
PAINT_INPUTS = {f'roomextra-role-{alias}': f'{REF}/own-busts/{alias}-512.png' for alias in _ROLES}
PAINT_INPUTS.update({f'roomextra-extra-{key}': f'{REF}/extra-icons/icon-{key}-master.png' for key in _EXTRA})
PAINT_INPUTS['roomextra-crown'] = 'assets/items/hats/morning-courtesy-b/46-coral-jade-cloud-crown.png'
ART_GENERATION_RECORDS = [f'{REF}/extra-icons/icon-{key}-master.png.generation.json' for key in _EXTRA]

MAP_CAPTIONS = {'bomb':('足球','⚽'), 'box':('推箱子','□'), 'bun':('抢包山','♜'),
    'desert':('沙漠','☀'), 'field':('野外','♧'), 'machine':('机械世界','⚙'),
    'match':('比武','⚔'), 'mine':('矿洞','♦'), 'pig':('功夫','✦'), 'pve':('探险','⚑'),
    'rand':('随机','?'), 'sculpture':('英雄','♞'), 'snow':('雪地','❄'),
    'tank':('糖客战','▣'), 'town':('中国城','⌂'), 'treasure':('夺宝','◆'), 'water':('水面','≈')}
PATHS = {}
for _path in _BY_PATH:
    _stem = Path(_path).stem
    if '/char/' in _path:
        if _stem.startswith('name_'):
            PATHS[_path] = ('roomextra-role-name', _stem[5:])
        elif _stem.startswith('icon_'):
            _alias = _stem[5:]
            PATHS[_path] = ('roomextra-random', None) if _alias == 'random' else (
                'roomextra-role-icon' if _alias in _ROLES else 'roomextra-extra-icon', _alias)
        elif _stem in _ROLES:
            PATHS[_path] = ('roomextra-role-bust', _stem)
        elif _stem.startswith('img_role'):
            PATHS[_path] = ('roomextra-attribute-unit', _stem)
        else:
            PATHS[_path] = ('roomextra-attribute-panel', _stem)
    elif '/map/' in _path:
        PATHS[_path] = ('roomextra-map-filter', _stem[4:])
    else:
        PATHS[_path] = ({
            'btn_check': 'roomextra-check', 'btn_leftRole':'roomextra-role-arrow', 'btn_rightRole':'roomextra-role-arrow',
            'btn_playerDown':'roomextra-player-slot', 'btn_playerUp':'roomextra-player-slot',
            'dlg_helpKB':'roomextra-help', 'dlg_matchroom':'roomextra-match-panel', 'dlg_roleProp':'roomextra-attribute-panel',
            'equipTip':'roomextra-equip-tip', 'img_master':'roomextra-master', 'img_popo':'roomextra-broadcast-fill',
            'img_ready':'roomextra-ready', 'img_roomStop':'roomextra-stop', 'leftTip':'roomextra-role-arrow',
            'rightTip':'roomextra-role-arrow', 'mask_equip':'roomextra-equipment-mask', 'mask_speaker':'roomextra-broadcast-mask',
            'tab_normalChar':'roomextra-role-tab', 'tab_vipChar':'roomextra-role-tab', 'teamColorStrip':'roomextra-team-strip',
        }[_stem], _stem)
STRUCTURAL_ALPHA_INPUTS = {}
_EXACT_ALPHA_KINDS = {'roomextra-role-arrow','roomextra-player-slot','roomextra-check','roomextra-broadcast-fill',
    'roomextra-broadcast-mask','roomextra-team-strip','roomextra-equipment-mask','roomextra-attribute-unit',
    'roomextra-map-filter','roomextra-help','roomextra-role-icon','roomextra-extra-icon','roomextra-random'}
for _path, (_kind, _label) in PATHS.items():
    if _kind in _EXACT_ALPHA_KINDS:
        for _frame in _BY_PATH[_path]['frames']:
            _index = _frame['sourceFrameIndex']
            STRUCTURAL_ALPHA_INPUTS[f'{Path(_path).stem}-{_index}'] = _frame['file']
VISUAL_MAPPING_ASSUMPTIONS = [
    'Eighteen room/shop aliases are paired to sourceRoleId by exact parallel native lists; two additional PVE aliases cbz/xz are proven by direct g_RoleNameList indices10/11.',
    'Numeric extra icon suffixes are selected from PVEBossInfo.m_iImageID, not established role IDs. Seventeen independent original UI identities are allocated at stable paths; world model/NPC bindings remain unverified.',
    'Role busts and portraits use the existing project-approved head/hair/collar ROIs, directly derived512px from their own high-resolution masters. These are UI images, not world stand/walk motion.',
    'Old baked character-name and Ready/Master/tab/attribute-label alpha is replaced with own lettering and surfaces; it is not inherited as ghost glyph outlines.',
    'For generic source controls without old baked glyph-alpha, final decoded functional alpha is preserved exactly. Team-color state indices and sampled base hues are retained.',
    'Keyboard help retains the observed original single-player controls and key meanings; its bitmap diagram is rebuilt as own UI shapes/text without changing key callbacks.',
]


def material(paints, key):
    if key in paints:
        return paints[key]
    with Image.open(ROOT / PAINT_INPUTS[key]) as image:
        return image.convert('RGBA')


def source_alpha(key, size):
    with Image.open(ROOT / STRUCTURAL_ALPHA_INPUTS[key]) as image:
        if image.size != size:
            raise ValueError('Native functional alpha raster changed')
        return image.getchannel('A')


def source_frame(stem, index):
    return next(r for p,r in _BY_PATH.items() if Path(p).stem == stem)['metadata']['frames'][index]


def icon_geometry(image):
    alpha = image.getchannel('A')
    visible = alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()
    if not visible or alpha.getextrema() != (0,255):
        raise ValueError('Own portrait must be a genuinely transparent RGBA cutout')
    box = (max(0,visible[0]-1),max(0,visible[1]-1),min(image.width,visible[2]+1),min(image.height,visible[3]+1))
    outside=[]
    for part in ((0,0,image.width,box[1]),(0,box[3],image.width,image.height),
                 (0,box[1],box[0],box[3]),(box[2],box[1],image.width,box[3])):
        if part[2]>part[0] and part[3]>part[1]:outside.append(alpha.crop(part).getextrema()[1])
    if max(outside,default=0)>=8:raise ValueError('Own portrait crop would exclude visible subject pixels')
    return {'alphaThreshold':8, 'sourceBox':list(box),'excludedMaxAlpha':max(outside,default=0),
            'nativeIconLogicalCanvas':[55,55],'ownSubjectBox':[4,4,51,51],
            'operation':'Complete visible own silhouette plus one pixel; premultiplied uniform resize, same registered subject for every native state window'}


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    cream, ink, gold, jade = '#f3ead2','#284f40','#bea36b','#254d42'
    font = ImageFont.truetype(str(font_path),12)
    small = ImageFont.truetype(str(font_path),10)
    title = ImageFont.truetype(str(font_path),16)
    symbols = ImageFont.truetype(FONT_INPUTS['symbols'],19)

    def panel(extent):
        return nine_slice(scaled(paints['panel'],(132,124)),extent,18)

    def well(out, box, light=False):
        ImageDraw.Draw(out).rounded_rectangle(box,radius=4,fill=cream if light else jade,outline=gold)

    def owned_fit(picture, extent, padding=2):
        geometry = icon_geometry(picture)
        cut = picture.crop(geometry['sourceBox'])
        factor = min((extent[0]-padding*2)/cut.width,(extent[1]-padding*2)/cut.height)
        target = (max(1,round(cut.width*factor)),max(1,round(cut.height*factor)))
        out = Image.new('RGBA',extent)
        out.alpha_composite(scaled(cut,target),((extent[0]-target[0])//2,extent[1]-padding-target[1]))
        return out

    def exact_alpha(out, stem):
        out.putalpha(source_alpha(f'{stem}-{index}',size))
        return out

    if kind == 'roomextra-role-name':
        out = Image.new('RGBA',size)
        draw = ImageDraw.Draw(out)
        font_size=min(20,size[1]-5)
        while True:
            f = ImageFont.truetype(str(font_path),font_size)
            bounds=draw.textbbox((0,0),_ROLES[label]['uiShortName'],font=f,stroke_width=2)
            if bounds[2]-bounds[0] <= size[0]-2 and bounds[3]-bounds[1] <= size[1]-2:
                break
            font_size-=1
        draw.text((size[0]//2,size[1]//2),_ROLES[label]['uiShortName'],font=f,
                                fill=cream,stroke_width=2,stroke_fill=ink,anchor='mm')
        return out

    if kind == 'roomextra-role-bust':
        return owned_fit(material(paints,f'roomextra-role-{label}'),size,1)

    if kind in ('roomextra-role-icon','roomextra-extra-icon','roomextra-random'):
        stem = 'icon_random' if kind == 'roomextra-random' else f'icon_{label}'
        frame = source_frame(stem,index)
        out = Image.new('RGBA',(55,55),jade)
        draw = ImageDraw.Draw(out)
        draw.rounded_rectangle((1,1,53,53),radius=7,fill=jade,outline=gold,width=2)
        if index:
            draw.rounded_rectangle((2,2,52,52),radius=6,outline='#f4d68c',width=2)
        if kind == 'roomextra-random':
            q = ImageFont.truetype(str(font_path),34)
            draw.text((28,29),'?',font=q,fill=cream,stroke_width=1,stroke_fill=gold,anchor='mm')
        else:
            key = f'roomextra-role-{label}' if kind == 'roomextra-role-icon' else f'roomextra-extra-{label}'
            # All own subject pixels lie within every state window; rims may differ.
            own = owned_fit(material(paints,key),(47,47),1)
            out.alpha_composite(own,(4,4))
        x,y = frame['frameOffset']
        return exact_alpha(out.crop((x,y,x+size[0],y+size[1])),stem)

    if kind == 'roomextra-role-arrow':
        out = Image.new('RGBA',size,cream)
        out.alpha_composite(nine_slice(paints['hover' if index==1 else 'normal'],size,10))
        draw = ImageDraw.Draw(out)
        left = 'left' in label.lower()
        cx,cy = size[0]//2,size[1]//2
        # Original six stored states are retained as distinct material positions.
        colors = [cream,'#ffe3a6','#bca270','#f7edcd','#e3c785','#cba95f']
        draw.polygon([(cx-5 if left else cx+5,cy),(cx+4 if left else cx-4,cy-15),
                      (cx+4 if left else cx-4,cy+15)],fill=colors[index],outline=gold)
        return exact_alpha(out,label)

    if kind == 'roomextra-player-slot':
        frame=source_frame(label,index)
        out=Image.new('RGBA',(132,137),jade)
        out.alpha_composite(panel((132,137)))
        well(out,(7,7,125,131))
        draw=ImageDraw.Draw(out)
        name_top=8 if label=='btn_playerUp' else 109
        draw.rounded_rectangle((9,name_top,123,name_top+21),radius=3,fill='#1b3e33')
        if index:
            draw.rounded_rectangle((3,3,128,134),radius=8,outline='#e5c77c',width=2)
        x,y=frame['frameOffset']
        out=out.crop((x,y,x+size[0],y+size[1]))
        return exact_alpha(out,label)

    if kind == 'roomextra-check':
        return exact_alpha(Image.new('RGBA',size,'#d7b965'),label)

    if kind == 'roomextra-role-tab':
        out=nine_slice(paints['hover' if index else 'normal'],size,8)
        caption='普通角色' if label=='tab_normalChar' else 'VIP角色'
        ImageDraw.Draw(out).text((size[0]//2,size[1]//2),caption,font=small,fill=cream,anchor='mm')
        return out

    if kind == 'roomextra-team-strip':
        colors=[(232,60,40),(0,70,168),(217,201,66),(62,163,25),(224,36,136),(240,156,40),(176,24,192),(88,88,88)]
        out=Image.new('RGBA',size,colors[index]+(255,))
        draw=ImageDraw.Draw(out)
        # Keep the indexed team hue as a broad left chip and top band, with a
        # dark name surface at the original white-name coordinates.
        draw.rectangle((40,2,size[0]-2,size[1]-2),fill=jade)
        draw.rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=4,outline=gold)
        draw.line((3,2,size[0]-4,2),fill='#ecd9a7')
        return exact_alpha(out,label)

    if kind == 'roomextra-attribute-unit':
        color={'img_roleBomb':'#d7b43f','img_rolePower':'#c77929','img_roleSpeed':'#719b3c'}[label]
        out=Image.new('RGBA',size,color)
        ImageDraw.Draw(out).rectangle((1,1,size[0]-2,size[1]-2),outline='#e8d4a0',width=1)
        return exact_alpha(out,label)

    if kind == 'roomextra-attribute-panel':
        out=Image.new('RGBA',size)
        draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((0,0,152,73),radius=5,fill=jade,outline=gold)
        draw.polygon([(70,73),(76,82),(82,73)],fill=jade,outline=gold)
        for text,y in [('糖果',21),('威力',38),('速度',55)]:
            draw.text((17,y),text,font=font,fill=cream,anchor='mm')
            draw.rounded_rectangle((34,y-7,144,y+7),radius=2,fill='#17382f',outline='#657b63')
        return out

    if kind == 'roomextra-equip-tip':
        frame=source_frame(label,index)
        out=Image.new('RGBA',(82,75))
        draw=ImageDraw.Draw(out)
        top=frame['frameOffset'][1]
        draw.polygon([(24,top+2),(58,top+2),(58,top+20),(70,top+20),(41,top+39),
                      (12,top+20),(24,top+20)],fill='#dfc98f',outline=ink)
        draw.rounded_rectangle((1,56,80,74),radius=8,fill=jade,outline=gold)
        draw.text((41,65),'请装备道具',font=small,fill=cream,anchor='mm')
        x,y=frame['frameOffset']
        return out.crop((x,y,x+size[0],y+size[1]))

    if kind == 'roomextra-master':
        out=Image.new('RGBA',size)
        out.alpha_composite(owned_fit(material(paints,'roomextra-crown'),(27,20),0),(2,0))
        ImageDraw.Draw(out).text((15,24),'房主',font=small,fill=cream,stroke_width=1,stroke_fill=ink,anchor='mm')
        return out

    if kind == 'roomextra-ready':
        out=Image.new('RGBA',size)
        f=ImageFont.truetype(str(font_path),20)
        draw=ImageDraw.Draw(out)
        for text,y in [('准',14),('备',39)]:
            draw.text((14,y),text,font=f,fill='#efd18a',stroke_width=2,stroke_fill=ink,anchor='mm')
        return out

    if kind in ('roomextra-equipment-mask','roomextra-stop'):
        out=Image.new('RGBA',size,jade)
        out.alpha_composite(panel(size))
        draw=ImageDraw.Draw(out)
        cx,cy=size[0]//2,size[1]//2;r=min(size)//3
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline='#b49364',width=5)
        draw.line((cx-r+8,cy+r-8,cx+r-8,cy-r+8),fill='#b49364',width=5)
        if kind=='roomextra-equipment-mask':return exact_alpha(out,label)
        return out

    if kind in ('roomextra-broadcast-fill','roomextra-broadcast-mask'):
        return exact_alpha(Image.new('RGBA',size,cream if kind.endswith('fill') else jade),label)

    if kind == 'roomextra-map-filter':
        out=Image.new('RGBA',size,cream)
        out.alpha_composite(nine_slice(paints['normal'],size,15))
        text,symbol=MAP_CAPTIONS[label]
        draw=ImageDraw.Draw(out)
        draw.text((17,17),symbol,font=symbols,fill='#edd399',anchor='mm')
        draw.text((74,17),text,font=font,fill=cream,anchor='mm')
        return exact_alpha(out,'btn_'+label)

    if kind == 'roomextra-match-panel':
        out=panel(size)
        draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((18,35,270,82),radius=8,fill=jade,outline=gold)
        draw.text((144,59),'休息室',font=ImageFont.truetype(str(font_path),23),fill=cream,anchor='mm')
        well(out,(30,94,258,260))
        well(out,(30,280,258,447))
        return out

    if kind == 'roomextra-help':
        out=Image.new('RGBA',size,cream)
        out.alpha_composite(panel(size))
        draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((12,8,355,48),radius=6,fill=jade,outline=gold)
        draw.text((23,28),'单人操作说明',font=title,fill=cream,anchor='lm')
        def key(box,text,active=False):
            draw.rounded_rectangle(box,radius=2,fill='#e9d5a0' if active else '#f4eedc',outline='#8f805f')
            draw.text(((box[0]+box[2])//2,(box[1]+box[3])//2),text,font=ImageFont.truetype(str(font_path),8),fill=ink,anchor='mm')
        key((23,78,39,93),'Esc')
        for i in range(12):key((55+i*18,78,71+i*18,93),f'F{i+1}')
        rows=['`1234567890-=','QWERTYUIOP[]','ASDFGHJKL;\'','ZXCVBNM,./']
        for row,letters in enumerate(rows):
            y=99+row*18;start=23 if row==0 else 54
            if row>0:key((23,y,51,y+15),('TAB','Caps','Shift')[row-1],row==1)
            for i,text in enumerate(letters):key((start+i*17,y,start+i*17+15,y+15),text,row==0 and 1<=i<=6)
        key((23,171,54,187),'Ctrl');key((58,171,85,187),'Alt');key((89,171,223,187),'SPACE',True)
        key((227,171,259,187),'Alt');key((260,135,280,168),'Enter',True)
        for box,text in [((308,160,324,176),'↑'),((291,178,307,194),'←'),((308,178,324,194),'↓'),((325,178,341,194),'→')]:key(box,text,True)
        labels=[((22,217),'1–6 使用道具'),((172,217),'空格 放置糖果'),((22,247),'Tab 切换道具'),((172,247),'Enter 调出对话'),((290,217),'方向控制')]
        for xy,text in labels:draw.text(xy,text,font=font,fill=ink)
        return exact_alpha(out,label)
    raise ValueError(f'Unknown room-extra artwork kind: {kind}')
