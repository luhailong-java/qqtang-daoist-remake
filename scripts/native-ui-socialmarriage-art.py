"""Own native social, family, profile and Daoist covenant UI art."""
from functools import lru_cache
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
REF='assets/native-client-ui/social-marriage-reference'
RENDERER_PREFIX='socialmarriage-'
REFERENCE_MANIFEST=f'{REF}/manifest.json'
REFERENCE_INPUTS=[f'{REF}/layout-evidence.json',f'{REF}/generation-requests.json',f'{REF}/tool-results.json',f'{REF}/opacity-policy.json',
                 f'{REF}/palette-evidence.json',f'{REF}/illustration-evidence.json',f'{REF}/semantic-contract.json']
PAINT_INPUTS={
 'social-red-court':f'{REF}/illustrations/red-covenant-court-master.png',
 'social-moon-garden':f'{REF}/illustrations/moon-peach-garden-master.png',
 'social-red-officer':f'{REF}/illustrations/cinnabar-ceremony-officer-master.png',
 'social-jade-sage':f'{REF}/illustrations/moon-knot-sage-master.png',
 'social-crown':'assets/items/hats/morning-courtesy-b/46-coral-jade-cloud-crown.png',
 'social-diamond':'assets/items/forge/icons/20056-blue-crystal.png',
 'social-heart':'assets/items/platform/icons/9020-rose-crystal-love-heart.png',
 'social-bun':'assets/runtime/battle-props-20261112/bun.png',
 'social-match':'assets/items/profile-frames/elemental-medals/2401-ice-sword.png',
 'social-sculpture':'assets/maps/sculpture/pieces/12004-grey-idol.png',
 'social-world':'assets/qqtang-world-v2.png',
 'social-ring9021':'assets/items/cards-currency/icons/9021-blue-crystal-ring.png',
 'social-ring9022':'assets/items/cards-currency/icons/9022-ruby-jade-gold-ring.png',
 'social-ring9023':'assets/items/cards-currency/icons/9023-platinum-cloud-ring.png',
 'social-ring9024':'assets/items/cards-currency/icons/9024-clear-diamond-ring.png',
 'social-ring9025':'assets/items/cards-currency/icons/9025-three-gem-heart-ring.png',
 'social-ring9026':'assets/items/cards-currency/icons/9026-cloud-wing-guardian-ring.png',
}
FONT_INPUTS={}
ALPHA_PATHS=(
 'guidebar/img_friendmask','guidebar/player/img_expline','guidebar/player/img_expline2',
 'guidebar/player/img_mask','guidebar/player/img_modeexpline','guidebar/player/mask_demo',
 'guidebar/kin/bg_kin_menu','marriage/dlg_closeline','marriage/dlg_closelinevalue',
)
STRUCTURAL_ALPHA_INPUTS={stem:f'{REF}/frames/{stem}/frame-000.png'for stem in ALPHA_PATHS}
for _key in ('red-covenant-court','moon-peach-garden','cinnabar-ceremony-officer','moon-knot-sage'):
    REFERENCE_INPUTS.append(f'{REF}/illustrations/{_key}-master.png.generation.json')
VISUAL_MAPPING_ASSUMPTIONS=[
 'Only nine explicitly listed empty masks/progress/menu/value surfaces retain source Alpha. Original portraits, scenes, captions, item shapes and checkmark glyph Alpha are not reused.',
 'New Daoist ceremony backgrounds have their own illustrated perspective. Original native path/canvas/offsets are retained, while live avatar placement and occlusion require user review.',
 'The two generated officiant masters supply large/small portrait variants and the two confirmation-dialog inserts; these are derived exports, not eight new model generations.',
 'Social alternate backgrounds are associated with their original kin-tab callbacks. Profile fields are translated by the source mask widget rect(-10,-16). Inert associations do not prove executed flow.',
 'All constant/native callbacks, account labels, dynamic product text and addresses remain unchanged by this art renderer. Live original text is outside bitmap replacement acceptance.',
]


@lru_cache(maxsize=1)
def layouts():
    data=json.loads((ROOT/REFERENCE_INPUTS[0]).read_bytes())
    return {r['nativePath']:r for r in data['resources']}


@lru_cache(maxsize=10)
def structural_alpha(stem):
    with Image.open(ROOT/STRUCTURAL_ALPHA_INPUTS[stem])as image:return image.getchannel('A').copy()


def material(paints,key):
    if key in paints:return paints[key]
    with Image.open(ROOT/PAINT_INPUTS[key])as image:return image.convert('RGBA')


def luminance(rgb):
    values=[v/255 for v in rgb]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722),strict=True))


def text_background(rgba):
    options=('#244b3e','#10251f','#f3ead2')
    for option in options:
        bg=tuple(bytes.fromhex(option[1:]));fore=[round((c*rgba[3]+b*(255-rgba[3]))/255)for c,b in zip(rgba[:3],bg,strict=True)]
        a,b=luminance(fore),luminance(bg)
        if (max(a,b)+.05)/(min(a,b)+.05)>=4.5:return option
    # Keep the best measured option even when the static source color itself
    # cannot meet this selected threshold; the exporter records that limit.
    return max(options,key=lambda v:abs(luminance(tuple(bytes.fromhex(v[1:])))-luminance(rgba[:3])))


def owned_cutout(image,extent,scaled,margin=0):
    alpha=image.getchannel('A');bbox=alpha.point(lambda v:255 if v>=8 else 0).getbbox()
    if bbox is None:raise ValueError('Own art has no visible pixels')
    left,top,right,bottom=bbox
    image=image.crop((max(0,left-1),max(0,top-1),min(image.width,right+1),min(image.height,bottom+1)))
    ratio=min((extent[0]-2*margin)/image.width,(extent[1]-2*margin)/image.height)
    size=(max(1,round(image.width*ratio)),max(1,round(image.height*ratio)))
    out=Image.new('RGBA',extent)
    out.alpha_composite(scaled(image,size),((extent[0]-size[0])//2,(extent[1]-size[1])//2))
    return out


def render(kind,label,index,size,paints,font_path,nine_slice,scaled):
    path=next(p.casefold()for p,(k,_)in PATHS.items()if k==kind)
    stem=path.removeprefix('object/ui/').removesuffix('.img')
    name=stem.rsplit('/',1)[-1]
    data=layouts()[path];frame=data['frames'][index];ox,oy=frame['frameOffset']
    ink,cream,gold,jade='#254e40','#f3ead2','#c8ad72','#244b3e'
    font=ImageFont.truetype(str(font_path),12)
    small=ImageFont.truetype(str(font_path),11)
    title=ImageFont.truetype(str(font_path),15)

    def panel():return nine_slice(scaled(paints['panel'],(132,124)),size,18)
    def well(out,box,light=False,fill=None):
        ImageDraw.Draw(out).rounded_rectangle(box,radius=4,fill=fill or(cream if light else jade),outline=gold,width=1)
    def say(out,xy,text,face=font,fill=ink,anchor='lm'):
        ImageDraw.Draw(out).text(xy,text,font=face,fill=fill,anchor=anchor)
    def fields(out):
        draw=ImageDraw.Draw(out)
        for field in data['textFields']:
            x,y,w,h=field['rectInBackgroundLogicalSpace'];rgba=field['sourceForeground']['value']
            if rgba[3]==0:continue
            box=(x-ox-1,y-oy-1,x+w-ox+1,y+h-oy+1)
            if box[2]<=0 or box[3]<=0 or box[0]>=size[0]or box[1]>=size[1]:continue
            draw.rounded_rectangle(box,radius=min(4,max(1,h//3)),fill=text_background(rgba))
        return out
    def surface(style='normal'):
        out=nine_slice(paints['normal'if style=='disabled'else style],size,42)
        if style=='disabled':out=ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(.06)).enhance(.75)
        return out

    if stem in('marriage/bg/dlg_chinabg','marriage/bg/dlg_westbg'):
        image=material(paints,'social-red-court'if 'china'in name else'social-moon-garden')
        return ImageOps.fit(image,size,method=Image.Resampling.LANCZOS).convert('RGBA')
    if stem in('marriage/bg/dlg_chinaicon','marriage/bg/dlg_westicon'):
        image=material(paints,'social-red-court'if 'china'in name else'social-moon-garden')
        out=ImageOps.fit(image,size,method=Image.Resampling.LANCZOS).convert('RGBA')
        ImageDraw.Draw(out).rectangle((0,0,size[0]-1,size[1]-1),outline=gold,width=2)
        return out
    if stem.startswith('marriage/priest/'):
        image=material(paints,'social-red-officer'if 'china'in name else'social-jade-sage')
        return owned_cutout(image,size,scaled,1)
    if stem.startswith('marriage/ring/'):
        return owned_cutout(material(paints,'social-'+name),size,scaled,1)
    if stem.startswith('marriage/marriagelevel/'):
        key={'dlg_coronet':'social-crown','dlg_diamond':'social-diamond','dlg_heart':'social-heart'}[name]
        return owned_cutout(material(paints,key),size,scaled,0)
    if stem in('guidebar/player/img_bun','guidebar/player/img_match','guidebar/player/img_sculpture'):
        return owned_cutout(material(paints,'social-'+name.removeprefix('img_')),size,scaled,0)
    if stem=='marriage/dlg_priestchat':
        # Repaint this decorative bubble's opacity as our own opaque paper.
        # The old 204-alpha body cannot support its fixed blue text on dark
        # scenery; its original over-height words rectangle is not modified.
        out=Image.new('RGBA',size);draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((0,0,size[0]-1,75),radius=7,fill='#ffffff',outline=gold,width=1)
        draw.polygon(((155,74),(181,size[1]-1),(169,74)),fill='#ffffff',outline=gold)
        draw.line((156,74,168,74),fill='#ffffff',width=2)
        return out
    if stem in ALPHA_PATHS:
        if name=='dlg_closelinevalue':
            out=Image.new('RGBA',size,'#fff8e4')
            ImageDraw.Draw(out).rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=5,outline=gold)
            out=fields(out)
        elif name=='bg_kin_menu':
            out=Image.new('RGBA',size,jade);ImageDraw.Draw(out).rectangle((0,0,size[0]-1,size[1]-1),outline=gold)
        elif name in('img_friendmask','img_mask','mask_demo'):
            out=Image.new('RGBA',size,'#243e34')
        else:
            out=Image.new('RGBA',size,'#c9a74c');draw=ImageDraw.Draw(out)
            draw.line((0,1,size[0]-1,1),fill='#f8e7ac')
            draw.line((0,size[1]-2,size[0]-1,size[1]-2),fill='#8e7235')
        opacity=structural_alpha(stem)
        if opacity.size!=size:raise ValueError('Functional social Alpha extent differs')
        out.putalpha(opacity)
        return out
    if name=='btn_check':
        out=Image.new('RGBA',size)
        ImageDraw.Draw(out).line(((1,3),(3,6),(8,1)),fill='#a88b43',width=2)
        return out
    if stem.startswith('guidebar/kin/arrow_'):
        out=Image.new('RGBA',size);draw=ImageDraw.Draw(out)
        if name.endswith('0'):draw.rounded_rectangle((0,2,size[0]-1,size[1]-3),radius=2,fill=gold)
        elif name.endswith('1'):draw.polygon(((size[0]//2,0),(0,7),(4,7),(4,size[1]-1),(size[0]-5,size[1]-1),(size[0]-5,7),(size[0]-1,7)),fill='#c89359',outline=ink)
        else:draw.polygon(((size[0]//2,size[1]-1),(0,size[1]-8),(4,size[1]-8),(4,0),(size[0]-5,0),(size[0]-5,size[1]-8),(size[0]-1,size[1]-8)),fill='#72a68a',outline=ink)
        return out
    if name=='btn_folderup':
        out=surface(('normal','disabled','hover','pressed')[index]);draw=ImageDraw.Draw(out)
        draw.polygon(((5,14),(17,14),(17,5),(12,5),(22,0),(30,7),(25,7),(25,19),(5,19)),fill='#e6c987',outline=ink)
        return out
    if stem in('marriage/btn_left','marriage/btn_right'):
        out=surface(('normal','disabled','hover','pressed')[index]);cx,cy=size[0]//2,size[1]//2
        direction=-1 if name=='btn_left'else 1
        ImageDraw.Draw(out).polygon(((cx-direction*7,cy-10),(cx+direction*7,cy),(cx-direction*7,cy+10)),fill=cream,outline=gold)
        return out
    if stem=='guidebar/btn_player':
        out=Image.new('RGBA',size,jade)
        ImageDraw.Draw(out).rectangle((0,0,size[0]-1,size[1]-1),outline=gold)
        return out
    if name=='btn_noring':
        out=surface(('normal','disabled','hover','pressed')[index]);draw=ImageDraw.Draw(out)
        draw.ellipse((size[0]//2-18,15,size[0]//2+18,51),outline=gold,width=3)
        draw.line((size[0]//2-21,54,size[0]//2+21,12),fill='#b87a51',width=3)
        say(out,(size[0]//2,76),label,fill=cream,anchor='mm')
        return out
    if name.startswith('btn_')and label:
        count=len(data['frames'])
        if count==2:
            jade_first=name in('tab_allkinmember','tab_kin','tab_kinmatch','tab_team')
            selected=index==0 if jade_first else index==1
            out=surface('hover')if selected else panel();fill=cream if selected else ink
        else:
            state=('normal','hover','pressed')[index]if count==3 else('normal','disabled','hover','pressed')[index]
            out=surface(state);fill='#d3d3c8'if state=='disabled'else cream
        face=small if len(label)>=4 or size[0]<60 else font
        say(out,(size[0]//2,size[1]//2+(1 if index==3 else 0)),label,face=face,fill=fill,anchor='mm')
        return out
    if name.startswith('tab_'):
        jade_first=name in('tab_allkinmember','tab_kin','tab_kinmatch','tab_team')
        selected=index==0 if jade_first else index==1
        out=surface('hover')if selected else panel()
        say(out,(size[0]//2,size[1]//2),label,face=small,fill=cream if selected else ink,anchor='mm')
        return out
    if stem=='guidebar/kin/img_activity':
        out=surface();say(out,(size[0]//2,size[1]//2),label,face=title,fill=cream,anchor='mm');return out
    if stem=='guidebar/tip_entershop':
        out=Image.new('RGBA',size);draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((7,0,size[0]-1,size[1]-1),radius=6,fill=cream,outline=gold)
        draw.polygon(((0,11),(8,5),(8,18)),fill=cream,outline=gold)
        say(out,(39,14),label,face=small,anchor='mm');return out

    out=panel();draw=ImageDraw.Draw(out)
    if stem=='guidebar/dlg_player':
        well(out,(20,34,size[0]-20,size[1]-19))
        for y in range(58,size[1]-20,36):draw.line((22,y,size[0]-23,y),fill='#52735f')
    elif stem=='guidebar/dlg_kinmember':
        well(out,(24,57,153,91));well(out,(163,57,348,91));well(out,(24,132,346,308))
        well(out,(27,340,300,440));well(out,(20,100,354,132))
        for xy,text in(((26,43),'我的家族'),((164,43),'家族荣誉值'),((28,325),'家族公告')):say(out,xy,text,face=font)
        for x,text in((45,'昵称'),(105,'性别'),(150,'等级'),(199,'职位'),(273,'个人荣誉')):say(out,(x,116),text,face=small,fill=cream,anchor='mm')
        say(out,(37,462),'只显示在线成员',face=small);say(out,(165,462),'家族成员    名，在线    人',face=small)
    elif stem=='guidebar/dlg_kinmgr':
        well(out,(33,77,360,175));well(out,(32,207,360,351),fill='#10251f');well(out,(28,176,365,206))
        say(out,(36,59),'家族宣言：');say(out,(94,191),'默认家族职位',fill=cream,anchor='mm');say(out,(278,191),'自定义职位',fill=cream,anchor='mm')
        for n,(text,color)in enumerate(zip(('族长','长老','堂主','护法','弟子'),('#ffad61','#f7a6ee','#8dc5fa','#a5db77','#f3ead2'),strict=True)):
            say(out,(91,219+26*n),text,fill=color,face=font)
        say(out,(35,378),'家族徽章');say(out,(178,378),'家族扩张')
        well(out,(118,367,153,401),light=True);well(out,(263,367,315,389),light=True)
    elif stem=='guidebar/dlg_record':
        say(out,(18,22),'查看录像',face=title);well(out,(27,71,361,369));well(out,(56,42,311,65))
        for y in range(101,362,36):draw.line((29,y,359,y),fill='#52735f')
    elif stem in('guidebar/friend/dlg_addfriends','guidebar/friend/dlg_beaddedfriends'):
        say(out,(25,41),'提示信息',face=title);well(out,(111,69,248,92))
        say(out,(40,81),'我向'if name=='dlg_addfriends'else'来自');say(out,(254,81),'添加好友'if name=='dlg_addfriends'else'的好友请求',face=small)
        say(out,(125,111),'请填写验证信息',anchor='mm');well(out,(30,132,336,217 if name=='dlg_addfriends'else 200))
        if name=='dlg_beaddedfriends':say(out,(49,223),'同时添加对方为好友',face=small)
    elif stem=='guidebar/kin/dlg_createhint':
        say(out,(25,41),'提示信息',face=title)
        picture=ImageOps.fit(material(paints,'social-world'),(306,157),method=Image.Resampling.LANCZOS)
        out.alpha_composite(picture,(30,70));well(out,(35,132,331,177))
        say(out,(184,155),'你现在还没有家族，是否创建一个家族？',face=font,fill=cream,anchor='mm')
    elif stem=='guidebar/kin/dlg_createkin':
        say(out,(24,42),'创建家族',face=title);say(out,(32,86),'家族名称');say(out,(38,129),'家族宣言')
        well(out,(97,74,226,98));well(out,(30,146,298,269))
    elif stem in('guidebar/kin/dlg_kininfo','guidebar/kin/dlg_kininvite'):
        say(out,(22,25),'家族资料'if name=='dlg_kininfo'else'家族邀请',face=title)
        for n,text in enumerate(('区服：','族长：','规模：','等级：','声望：','成员：','公告：')):
            say(out,(54,96+24*n),text)
            draw.line((48,107+24*n,size[0]-28,107+24*n),fill='#d1c49e')
    elif stem=='guidebar/kin/dlg_topkin':
        well(out,(28,69,361,276));well(out,(28,278,361,308))
        for x,text in((78,'家族名称'),(182,'活跃度'),(281,'排名')):say(out,(x,52),text,face=font,anchor='mm')
        for y in range(104,267,36):draw.line((30,y,359,y),fill='#52735f')
    elif stem=='guidebar/player/dlg_playerinfo':
        say(out,(22,40),'玩家资料',face=title)
        for y,text in((75,'QQ号码'),(98,'昵称'),(121,'性别'),(144,'配偶'),(167,'家族'),(190,'状态'),(345,'经验值'),(368,'声望值'),(391,'积分'),(417,'等级'),(444,'战绩')):say(out,(20,y),text)
        well(out,(243,60,362,261));well(out,(251,340,352,438))
        draw.line((48,300,337,300),fill=gold)
    elif stem=='guidebar/player/dlg_modeinfo':
        out=ImageOps.fit(paints['panel'].crop((170,130,350,320)),size,method=Image.Resampling.LANCZOS)
        for y,text in((26,'包子模式'),(71,'比武模式'),(116,'英雄模式')):
            say(out,(9,y),text);well(out,(71,y-15,225,y+7));well(out,(71,y+9,225,y+19),light=True)
    elif stem=='guidebar/player/dlg_pveinfo':
        out=ImageOps.fit(paints['panel'].crop((170,130,350,320)),size,method=Image.Resampling.LANCZOS)
        for y,text in((10,'等级'),(31,'勇气值'),(51,'血量'),(72,'携宠数量'),(93,'回复速度'),(114,'超能力'),(135,'速度')):
            say(out,(7,y),text,face=small);well(out,(98 if y<55 else 84,y-7,224,y+6),light=True)
    elif stem in('marriage/dlg_marriageconfirmchina','marriage/dlg_marriageconfirmwest'):
        well(out,(25,40,269,219),light=True)
        key='social-red-officer'if 'china'in name else'social-jade-sage'
        portrait=owned_cutout(material(paints,key),(174,191),scaled,1)
        out.alpha_composite(portrait,(280,25))
        say(out,(37,61),'红娘：'if 'china'in name else'礼官：',face=title)
    elif stem=='marriage/dlg_divorce':
        say(out,(24,42),'离婚信息',face=title);well(out,(28,88,338,180))
        say(out,(184,133),'你真的准备离婚吗？',face=title,fill=cream,anchor='mm')
    elif stem=='marriage/dlg_loveword':
        say(out,(25,42),'修改爱情宣言',face=title);say(out,(42,90),'请输入爱情宣言：');well(out,(30,106,337,244))
    elif stem=='marriage/dlg_marriageinfo':
        say(out,(19,34),'婚姻信息',face=title)
        for xy,text in(((20,70),'配偶'),((20,92),'婚龄'),((20,120),'等级'),((20,160),'亲密度'),((20,202),'爱情宣言')):say(out,(xy[0]-ox,xy[1]-oy),text)
        well(out,(232-ox,55-oy,349-ox,165-oy));well(out,(26,217,351,335))
    elif stem=='marriage/dlg_receivespark':
        say(out,(57,45),'有人向您求婚',face=title);heart=owned_cutout(material(paints,'social-heart'),(25,25),scaled)
        out.alpha_composite(heart,(20,31));well(out,(25,106,302,300))
    elif stem=='marriage/dlg_setmarriage':
        draw.rectangle((0,0,size[0]-1,39),fill=jade)
        draw.line((0,40,size[0]-1,40),fill=gold)
        well(out,(6,64,133,120),light=True)
    elif stem=='marriage/dlg_spark':
        say(out,(24,42),'求婚宣言',face=title);say(out,(40,75),'您对');say(out,(228,75),'说的话：',face=small)
        well(out,(109,61,223,88));say(out,(40,119),'请填写您的真情告白：',face=font);well(out,(30,136,337,244))
    elif stem=='marriage/dlg_weddingsuccess':
        say(out,(25,42),'恭贺新婚',face=title);well(out,(25,80,302,290))
    else:
        raise ValueError(f'Unmapped social/marriage resource: {stem}')
    return fields(out)
PATHS = {'object/ui/guideBar/btn_amend.img': ('socialmarriage-guidebar__btn_amend', '修改'),
 'object/ui/guideBar/btn_cancel_dismiss.img': ('socialmarriage-guidebar__btn_cancel_dismiss', '恢复解散'),
 'object/ui/guideBar/btn_check.img': ('socialmarriage-guidebar__btn_check', None),
 'object/ui/guideBar/btn_dismiss.img': ('socialmarriage-guidebar__btn_dismiss', '解散家族'),
 'object/ui/guideBar/btn_folderUp.img': ('socialmarriage-guidebar__btn_folderup', None),
 'object/ui/guideBar/btn_issue.img': ('socialmarriage-guidebar__btn_issue', '发布'),
 'object/ui/guideBar/btn_player.img': ('socialmarriage-guidebar__btn_player', None),
 'object/ui/guideBar/btn_quitKin.img': ('socialmarriage-guidebar__btn_quitkin', '退出家族'),
 'object/ui/guideBar/btn_top_kin.img': ('socialmarriage-guidebar__btn_top_kin', '家族排名'),
 'object/ui/guideBar/dlg_kinMember.img': ('socialmarriage-guidebar__dlg_kinmember', None),
 'object/ui/guideBar/dlg_kinMgr.img': ('socialmarriage-guidebar__dlg_kinmgr', None),
 'object/ui/guideBar/dlg_player.img': ('socialmarriage-guidebar__dlg_player', None),
 'object/ui/guideBar/dlg_record.img': ('socialmarriage-guidebar__dlg_record', None),
 'object/ui/guideBar/friend/dlg_addFriends.img': ('socialmarriage-guidebar__friend__dlg_addfriends', None),
 'object/ui/guideBar/friend/dlg_beAddedFriends.img': ('socialmarriage-guidebar__friend__dlg_beaddedfriends',
                                                      None),
 'object/ui/guideBar/img_friendMask.img': ('socialmarriage-guidebar__img_friendmask', None),
 'object/ui/guideBar/kin/arrow_0.img': ('socialmarriage-guidebar__kin__arrow_0', None),
 'object/ui/guideBar/kin/arrow_1.img': ('socialmarriage-guidebar__kin__arrow_1', None),
 'object/ui/guideBar/kin/arrow_2.img': ('socialmarriage-guidebar__kin__arrow_2', None),
 'object/ui/guideBar/kin/bg_kin_menu.img': ('socialmarriage-guidebar__kin__bg_kin_menu', None),
 'object/ui/guideBar/kin/btn_activity.img': ('socialmarriage-guidebar__kin__btn_activity', '活跃度'),
 'object/ui/guideBar/kin/btn_honor.img': ('socialmarriage-guidebar__kin__btn_honor', '声望值'),
 'object/ui/guideBar/kin/btn_netcom.img': ('socialmarriage-guidebar__kin__btn_netcom', '网通'),
 'object/ui/guideBar/kin/btn_telecom.img': ('socialmarriage-guidebar__kin__btn_telecom', '电信'),
 'object/ui/guideBar/kin/dlg_createHint.img': ('socialmarriage-guidebar__kin__dlg_createhint', None),
 'object/ui/guideBar/kin/dlg_createKin.img': ('socialmarriage-guidebar__kin__dlg_createkin', None),
 'object/ui/guideBar/kin/dlg_kinInfo.img': ('socialmarriage-guidebar__kin__dlg_kininfo', None),
 'object/ui/guideBar/kin/dlg_kinInvite.img': ('socialmarriage-guidebar__kin__dlg_kininvite', None),
 'object/ui/guideBar/kin/dlg_topkin.img': ('socialmarriage-guidebar__kin__dlg_topkin', None),
 'object/ui/guideBar/kin/img_activity.img': ('socialmarriage-guidebar__kin__img_activity', '活跃度'),
 'object/ui/guideBar/player/btn_lookupkin.img': ('socialmarriage-guidebar__player__btn_lookupkin', '查看'),
 'object/ui/guideBar/player/dlg_modeInfo.img': ('socialmarriage-guidebar__player__dlg_modeinfo', None),
 'object/ui/guideBar/player/dlg_playerInfo.img': ('socialmarriage-guidebar__player__dlg_playerinfo', None),
 'object/ui/guideBar/player/dlg_pveInfo.img': ('socialmarriage-guidebar__player__dlg_pveinfo', None),
 'object/ui/guideBar/player/img_bun.img': ('socialmarriage-guidebar__player__img_bun', None),
 'object/ui/guideBar/player/img_expLine.img': ('socialmarriage-guidebar__player__img_expline', None),
 'object/ui/guideBar/player/img_expLine2.img': ('socialmarriage-guidebar__player__img_expline2', None),
 'object/ui/guideBar/player/img_mask.img': ('socialmarriage-guidebar__player__img_mask', None),
 'object/ui/guideBar/player/img_match.img': ('socialmarriage-guidebar__player__img_match', None),
 'object/ui/guideBar/player/img_modeExpLine.img': ('socialmarriage-guidebar__player__img_modeexpline', None),
 'object/ui/guideBar/player/img_sculpture.img': ('socialmarriage-guidebar__player__img_sculpture', None),
 'object/ui/guideBar/player/mask_demo.img': ('socialmarriage-guidebar__player__mask_demo', None),
 'object/ui/guideBar/tab_allKinMember.img': ('socialmarriage-guidebar__tab_allkinmember', '全家福'),
 'object/ui/guideBar/tab_kin.img': ('socialmarriage-guidebar__tab_kin', '家族'),
 'object/ui/guideBar/tab_kinMatch.img': ('socialmarriage-guidebar__tab_kinmatch', '联赛'),
 'object/ui/guideBar/tab_kinMember.img': ('socialmarriage-guidebar__tab_kinmember', '家族成员'),
 'object/ui/guideBar/tab_kinMgr.img': ('socialmarriage-guidebar__tab_kinmgr', '家族管理'),
 'object/ui/guideBar/tab_team.img': ('socialmarriage-guidebar__tab_team', '组队'),
 'object/ui/guideBar/tip_enterShop.img': ('socialmarriage-guidebar__tip_entershop', '进入商城'),
 'object/ui/marriage/bg/dlg_chinaBG.img': ('socialmarriage-marriage__bg__dlg_chinabg', None),
 'object/ui/marriage/bg/dlg_chinaIcon.img': ('socialmarriage-marriage__bg__dlg_chinaicon', None),
 'object/ui/marriage/bg/dlg_westBG.img': ('socialmarriage-marriage__bg__dlg_westbg', None),
 'object/ui/marriage/bg/dlg_westIcon.img': ('socialmarriage-marriage__bg__dlg_westicon', None),
 'object/ui/marriage/btn_Iaccept.img': ('socialmarriage-marriage__btn_iaccept', '我愿意'),
 'object/ui/marriage/btn_Ireject.img': ('socialmarriage-marriage__btn_ireject', '我拒绝'),
 'object/ui/marriage/btn_close.img': ('socialmarriage-marriage__btn_close', '关闭'),
 'object/ui/marriage/btn_divorce.img': ('socialmarriage-marriage__btn_divorce', '离婚'),
 'object/ui/marriage/btn_divorceCancel.img': ('socialmarriage-marriage__btn_divorcecancel', '取消'),
 'object/ui/marriage/btn_divorceConfirm.img': ('socialmarriage-marriage__btn_divorceconfirm', '确定'),
 'object/ui/marriage/btn_left.img': ('socialmarriage-marriage__btn_left', None),
 'object/ui/marriage/btn_lookup.img': ('socialmarriage-marriage__btn_lookup', '查看'),
 'object/ui/marriage/btn_modify.img': ('socialmarriage-marriage__btn_modify', '修改'),
 'object/ui/marriage/btn_noRing.img': ('socialmarriage-marriage__btn_noring', '我要戒指'),
 'object/ui/marriage/btn_right.img': ('socialmarriage-marriage__btn_right', None),
 'object/ui/marriage/btn_save.img': ('socialmarriage-marriage__btn_save', '保存'),
 'object/ui/marriage/btn_spark.img': ('socialmarriage-marriage__btn_spark', '求婚'),
 'object/ui/marriage/btn_sparkCancel.img': ('socialmarriage-marriage__btn_sparkcancel', '取消'),
 'object/ui/marriage/btn_sparkSend.img': ('socialmarriage-marriage__btn_sparksend', '发送'),
 'object/ui/marriage/btn_startWedding.img': ('socialmarriage-marriage__btn_startwedding', '婚礼开始'),
 'object/ui/marriage/dlg_closeLine.img': ('socialmarriage-marriage__dlg_closeline', None),
 'object/ui/marriage/dlg_closeLineValue.img': ('socialmarriage-marriage__dlg_closelinevalue', None),
 'object/ui/marriage/dlg_divorce.img': ('socialmarriage-marriage__dlg_divorce', None),
 'object/ui/marriage/dlg_loveWord.img': ('socialmarriage-marriage__dlg_loveword', None),
 'object/ui/marriage/dlg_marriageConfirmChina.img': ('socialmarriage-marriage__dlg_marriageconfirmchina',
                                                     None),
 'object/ui/marriage/dlg_marriageConfirmWest.img': ('socialmarriage-marriage__dlg_marriageconfirmwest', None),
 'object/ui/marriage/dlg_marriageInfo.img': ('socialmarriage-marriage__dlg_marriageinfo', None),
 'object/ui/marriage/dlg_priestChat.img': ('socialmarriage-marriage__dlg_priestchat', None),
 'object/ui/marriage/dlg_receiveSpark.img': ('socialmarriage-marriage__dlg_receivespark', None),
 'object/ui/marriage/dlg_setMarriage.img': ('socialmarriage-marriage__dlg_setmarriage', None),
 'object/ui/marriage/dlg_spark.img': ('socialmarriage-marriage__dlg_spark', None),
 'object/ui/marriage/dlg_weddingSuccess.img': ('socialmarriage-marriage__dlg_weddingsuccess', None),
 'object/ui/marriage/marriageLevel/dlg_coronet.img': ('socialmarriage-marriage__marriagelevel__dlg_coronet',
                                                      None),
 'object/ui/marriage/marriageLevel/dlg_diamond.img': ('socialmarriage-marriage__marriagelevel__dlg_diamond',
                                                      None),
 'object/ui/marriage/marriageLevel/dlg_heart.img': ('socialmarriage-marriage__marriagelevel__dlg_heart',
                                                    None),
 'object/ui/marriage/priest/dlg_chinaPriest.img': ('socialmarriage-marriage__priest__dlg_chinapriest', None),
 'object/ui/marriage/priest/dlg_chinaPriestS.img': ('socialmarriage-marriage__priest__dlg_chinapriests',
                                                    None),
 'object/ui/marriage/priest/dlg_westPriest.img': ('socialmarriage-marriage__priest__dlg_westpriest', None),
 'object/ui/marriage/priest/dlg_westPriestS.img': ('socialmarriage-marriage__priest__dlg_westpriests', None),
 'object/ui/marriage/ring/ring9021.img': ('socialmarriage-marriage__ring__ring9021', None),
 'object/ui/marriage/ring/ring9022.img': ('socialmarriage-marriage__ring__ring9022', None),
 'object/ui/marriage/ring/ring9023.img': ('socialmarriage-marriage__ring__ring9023', None),
 'object/ui/marriage/ring/ring9024.img': ('socialmarriage-marriage__ring__ring9024', None),
 'object/ui/marriage/ring/ring9025.img': ('socialmarriage-marriage__ring__ring9025', None),
 'object/ui/marriage/ring/ring9026.img': ('socialmarriage-marriage__ring__ring9026', None)}
