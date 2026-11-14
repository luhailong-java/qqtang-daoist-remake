"""Own Daoist promotional cards and two default profile illustrations."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
REF='assets/native-client-ui/promo-reference'
RENDERER_PREFIX='promo-'
REFERENCE_MANIFEST=f'{REF}/manifest.json'
REFERENCE_INPUTS=[f'{REF}/format-contract.json']
PAINT_INPUTS={
 'promo-world':'assets/qqtang-world-v2.png',
 'promo-brand':'assets/branding/linghu-wordmark-v1.png',
 'promo-boy':'assets/characters/daoist-child.png',
 'promo-girl':'assets/characters/lotus-healer.png',
 'promo-moon':'assets/native-client-ui/social-marriage-reference/illustrations/moon-peach-garden-master.png',
 'promo-red':'assets/native-client-ui/social-marriage-reference/illustrations/red-covenant-court-master.png',
}
FONT_INPUTS={}
STRUCTURAL_ALPHA_INPUTS={}
VISUAL_MAPPING_ASSUMPTIONS=[
 'All 15 loose source paths retain original format, native canvas, frame count and offsets. No old promotional captions, portraits, brand pixels or silhouette Alpha are reused.',
 'Thirteen promotion cards are timeless own-world theme art, not evidence that a named campaign, prize, date or external URL is implemented.',
 'Two GIFs are default player-profile illustrations, using existing own Daoist child and lotus healer masters; the original ui_getPlayerDetail sex mapping and playerInfoDlg binding are unchanged.',
 'GIFs stay genuine one-frame opaque GIF89a with original 500ms duration, loop 0, disposal 1, background index 0 and no interlace. Own palette/compression/file length can change.',
 'No new model generation was invoked. Native runtime loading, click targets, external campaigns and user visual acceptance remain unverified.',
]
PATHS={
 'ui/pawnshop/pawnshopad.img':('promo-treasure','仙葫宝阁'),
 'ui/selSect/ad2_0113_xinnian.img':('promo-newyear','新岁纳福'),
 'ui/selSect/ad2_0216_qingren.img':('promo-bond','桃花结缘'),
 'ui/selSect/ad2_0310_zhishu.img':('promo-wood','青木生灵'),
 'ui/selSect/ad2_0817_jianh.img':('promo-sword','剑鸣云海'),
 'ui/selSect/ad2_0826_huanlegu.img':('promo-adventure','灵葫奇游'),
 'ui/selSect/ad2_0831_aizxl.tga':('promo-stars','星阵初成'),
 'ui/selSect/ad2_0831_bianf.img':('promo-moonwalk','月影巡游'),
 'ui/selSect/ad2_0831_kaixue.img':('promo-initiation','道童入门'),
 'ui/selSect/ad2_1110_boss.img':('promo-mountains','山海试炼'),
 'ui/selSect/ad2_1216_sdj.img':('promo-lanterns','冬夜灯会'),
 'ui/selSect/ad_0910_girl.img':('promo-lotus','莲灯照路'),
 'ui/selSect/ad_1007_icetea.img':('promo-tea','清风竹影'),
 'res/uiRes/avt_boy.gif':('promo-profile-boy',''),
 'res/uiRes/avt_girl.gif':('promo-profile-girl',''),
}
THEMES={
 'promo-treasure':('promo-world','promo-boy','玲珑法宝 · 云锦珍藏','#244b3e'),
 'promo-newyear':('promo-red','promo-boy','祥云相伴 · 福满仙山','#833e36'),
 'promo-bond':('promo-moon','promo-girl','携友同行 · 桃源相会','#70434e'),
 'promo-wood':('promo-moon','promo-boy','春山游记 · 草木有灵','#244b3e'),
 'promo-sword':('promo-world','promo-boy','灵符相随 · 踏云而行','#244b3e'),
 'promo-adventure':('promo-world','promo-girl','仙山秘境 · 一起出发','#244b3e'),
 'promo-stars':('promo-world','promo-girl','云端相会 · 星海相伴','#344760'),
 'promo-moonwalk':('promo-moon','promo-girl','踏云入梦 · 月照桃源','#344760'),
 'promo-initiation':('promo-world','promo-boy','初识仙途 · 与友同游','#244b3e'),
 'promo-mountains':('promo-world','promo-boy','灵兽图卷 · 山海奇游','#244b3e'),
 'promo-lanterns':('promo-red','promo-girl','灯暖云间 · 瑞雪迎春','#833e36'),
 'promo-lotus':('promo-moon','promo-girl','一盏莲灯 · 相伴仙途','#70434e'),
 'promo-tea':('promo-moon','promo-boy','一盏云茶 · 悠然仙游','#244b3e'),
}


def cutout(source,size,scaled):
    image=source.convert('RGBA');box=image.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
    if box is None:raise ValueError('Own painting has no visible pixels')
    image=image.crop(box);ratio=min(size[0]/image.width,size[1]/image.height)
    return scaled(image,(max(1,round(image.width*ratio)),max(1,round(image.height*ratio))))


def render(kind,label,index,size,paints,font_path,nine_slice,scaled):
    if index!=0:raise ValueError('Promotional sources have exactly one position')
    w,h=size;out=Image.new('RGBA',size,'#f3ead2');draw=ImageDraw.Draw(out)
    def font(n):return ImageFont.truetype(str(font_path),n)
    def fit_text(text,box,n,fill,anchor='mm'):
        x,y,ww,hh=box
        while n>7:
            f=font(n);b=draw.textbbox((0,0),text,font=f)
            if b[2]-b[0]<=ww and b[3]-b[1]<=hh:break
            n-=1
        draw.text((x+ww/2,y+hh/2),text,font=f,fill=fill,anchor=anchor)
    if kind.startswith('promo-profile-'):
        person=paints['promo-boy'if kind.endswith('-boy')else'promo-girl']
        draw.rounded_rectangle((3,3,w-4,h-4),radius=12,fill='#f7f0df',outline='#c8ad72',width=1)
        draw.ellipse((12,h-24,w-12,h-11),fill='#d6d3b8')
        painted=cutout(person,(w-20,h-30),scaled);out.alpha_composite(painted,((w-painted.width)//2,h-17-painted.height))
        return out
    backdrop,person,subtitle,ink=THEMES[kind]
    draw.rounded_rectangle((3,3,w-4,h-4),radius=9,fill=ink,outline='#c8ad72',width=2)
    if h>w:
        # Two original portrait-format ad slots use a complete own character
        # and scene, not a horizontally cropped old advertising rectangle.
        scene=ImageOps.fit(paints[backdrop].convert('RGBA'),(w-14,round(h*.48)),method=Image.Resampling.LANCZOS,centering=(.5,.45))
        out.alpha_composite(scene,(7,round(h*.25)))
        brand=cutout(paints['promo-brand'],(w-22,52),scaled);out.alpha_composite(brand,((w-brand.width)//2,16))
        fit_text(label,(7,76,w-14,34),25,'#fff0c7')
        figure=cutout(paints[person],(w-22,round(h*.43)),scaled);out.alpha_composite(figure,((w-figure.width)//2,round(h*.37)))
        draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((10,h-81,w-11,h-15),radius=7,fill='#f3ead2',outline='#c8ad72')
        for n,line in enumerate(subtitle.split(' · ')):fit_text(line,(13,h-78+n*28,w-26,28),15,ink)
    else:
        scene=ImageOps.fit(paints[backdrop].convert('RGBA'),(w-10,h-10),method=Image.Resampling.LANCZOS,centering=(.5,.42))
        out.alpha_composite(scene,(5,5));draw=ImageDraw.Draw(out)
        # A solid paper caption column gives stable text contrast and does
        # not depend on the previous campaign illustration's Alpha.
        right=round(w*.59);draw.rounded_rectangle((8,8,right,h-9),radius=7,fill='#f3ead2',outline='#c8ad72')
        fit_text('灵葫大作战',(12,11,right-16,22),14,ink)
        fit_text(label,(12,round(h*.29),right-16,36),25,ink)
        lines=subtitle.split(' · ')
        if h>=140:
            for n,line in enumerate(lines):fit_text(line,(12,round(h*.61)+n*20,right-16,20),12,ink)
        else:fit_text(' · '.join(lines),(12,h-39,right-16,23),11,ink)
        figure=cutout(paints[person],(round(w*.40),h-18),scaled);out.alpha_composite(figure,(w-9-figure.width,h-9-figure.height))
    return out
