"""Complete112 native shop extras from own UI/paint and verified role allocation.

No original color/text pixels or old glyph alpha are copied. Structural masks
remain source-exact where declared; cosmetic glyph/illustration alpha is rebuilt.
"""
from functools import lru_cache
from pathlib import Path
import math
import json
import hashlib
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'assets/native-client-ui/shop-extra-reference'
RENDERER_PREFIX = 'shopextra-'
REFERENCE_MANIFEST = 'assets/native-client-ui/shop-extra-reference/manifest.json'
PAINT_INPUTS = {'shopextra-chest': 'assets/ui/semantic-extra/warehouse.png', 'shopextra-envelope': 'assets/ui/semantic-extra/private-chat.png', 'shopextra-hammer': 'assets/items/platform/icons/9013-cloud-gold-hammer.png', 'shopextra-role-9': 'assets/characters/portraits-candidates/daoist-child-256.png', 'shopextra-role-22': 'assets/characters/portraits-candidates/moon-shadow-256.png', 'shopextra-role-1': 'assets/characters/portraits-candidates/mountain-guardian-256.png', 'shopextra-role-2': 'assets/characters/portraits-candidates/lotus-healer-256.png', 'shopextra-role-3': 'assets/characters/portraits-candidates/01_ice_sword_girl-256.png', 'shopextra-role-4': 'assets/characters/portraits-candidates/02_fire_talisman_boy-256.png', 'shopextra-role-5': 'assets/characters/portraits-candidates/05_celestial_musician_girl-256.png', 'shopextra-role-6': 'assets/characters/portraits-candidates/06_thunder_caster_boy-256.png', 'shopextra-role-7': 'assets/characters/portraits-candidates/08_alchemy_prodigy_boy-256.png', 'shopextra-role-8': 'assets/characters/portraits-candidates/09_bamboo_archer_girl-256.png', 'shopextra-role-18': 'assets/characters/portraits-candidates/10_crimson_spear_girl-256.png', 'shopextra-role-19': 'assets/characters/portraits-candidates/14_short_hair_snow_summoner_girl-256.png', 'shopextra-role-20': 'assets/characters/portraits-candidates/15_water_dragon_scholar_boy-256.png', 'shopextra-role-21': 'assets/characters/portraits-candidates/17_ghost_script_calligrapher_boy-256.png', 'shopextra-role-13': 'assets/characters/portraits-candidates/pine-cloud-elder-256.png', 'shopextra-role-14': 'assets/characters/portraits-candidates/jade-craft-artisan-256.png', 'shopextra-role-15': 'assets/characters/portraits-candidates/paper-kite-wanderer-256.png', 'shopextra-role-16': 'assets/characters/portraits-candidates/cinnabar-seal-keeper-256.png'}
REFERENCE_INPUTS = ['assets/native-client-ui/shop-extra-reference/dynamic-layout-evidence.json', 'assets/native-client-ui/room-extra-reference/roster-mapping-audit.json', 'assets/native-client-ui/shop-extra-reference/header-currency-evidence.json']
SPEC_ROWS = [('object/ui/shop/advert.img', 'shopextra-advert', 'advert', None, 'source', 1), ('object/ui/shop/breakEgg/btn_close.img', 'shopextra-breakegg-btn-close', 'button3', '关闭', 'source', 3), ('object/ui/shop/breakEgg/btn_hammerFrame1.img', 'shopextra-breakegg-btn-hammerframe1', 'hammer-slot', '铁锤', 'source', 4), ('object/ui/shop/breakEgg/btn_hammerFrame2.img', 'shopextra-breakegg-btn-hammerframe2', 'hammer-slot', '银锤', 'source', 4), ('object/ui/shop/breakEgg/btn_hammerFrame3.img', 'shopextra-breakegg-btn-hammerframe3', 'hammer-slot', '金锤', 'source', 4), ('object/ui/shop/breakEgg/dlg_breakEgg.img', 'shopextra-breakegg-dlg-breakegg', 'egg-panel', None, 'source', 1), ('object/ui/shop/breakEgg/failed.img', 'shopextra-breakegg-failed', 'egg-failure', None, 'source', 1), ('object/ui/shop/breakEgg/success.img', 'shopextra-breakegg-success', 'egg-success', None, 'source', 1), ('object/ui/shop/breakEgg/title.img', 'shopextra-breakegg-title', 'egg-title', '惊喜砸彩蛋', 'redraw', 8), ('object/ui/shop/btn_addQB.img', 'shopextra-btn-addqb', 'button4', '账户充值', 'source', 4), ('object/ui/shop/btn_depositQB.img', 'shopextra-btn-depositqb', 'stack3', 'Q币\n充值', 'source', 3), ('object/ui/shop/btn_joinMember.img', 'shopextra-btn-joinmember', 'stack3', '开通\n会员', 'source', 3), ('object/ui/shop/charIcon/bbl.img', 'shopextra-charicon-bbl', 'character-banner', '5', 'source', 1), ('object/ui/shop/charIcon/BOY.img', 'shopextra-charicon-boy', 'character-banner', '9', 'source', 1), ('object/ui/shop/charIcon/cl.img', 'shopextra-charicon-cl', 'character-banner', '4', 'source', 1), ('object/ui/shop/charIcon/ge.img', 'shopextra-charicon-ge', 'character-banner', '20', 'source', 1), ('object/ui/shop/charIcon/GIRL.img', 'shopextra-charicon-girl', 'character-banner', '22', 'source', 1), ('object/ui/shop/charIcon/hwz.img', 'shopextra-charicon-hwz', 'character-banner', '8', 'source', 1), ('object/ui/shop/charIcon/hy.img', 'shopextra-charicon-hy', 'character-banner', '6', 'source', 1), ('object/ui/shop/charIcon/kl.img', 'shopextra-charicon-kl', 'character-banner', '13', 'source', 1), ('object/ui/shop/charIcon/ld.img', 'shopextra-charicon-ld', 'character-banner', '19', 'source', 1), ('object/ui/shop/charIcon/mly.img', 'shopextra-charicon-mly', 'character-banner', '7', 'source', 1), ('object/ui/shop/charIcon/nz.img', 'shopextra-charicon-nz', 'character-banner', '14', 'source', 1), ('object/ui/shop/charIcon/tb.img', 'shopextra-charicon-tb', 'character-banner', '21', 'source', 1), ('object/ui/shop/charIcon/tt.img', 'shopextra-charicon-tt', 'character-banner', '2', 'source', 1), ('object/ui/shop/charIcon/wll.img', 'shopextra-charicon-wll', 'character-banner', '15', 'source', 1), ('object/ui/shop/charIcon/xq.img', 'shopextra-charicon-xq', 'character-banner', '3', 'source', 1), ('object/ui/shop/charIcon/xwk.img', 'shopextra-charicon-xwk', 'character-banner', '1', 'source', 1), ('object/ui/shop/charIcon/yd.img', 'shopextra-charicon-yd', 'character-banner', '18', 'source', 1), ('object/ui/shop/charIcon/yy.img', 'shopextra-charicon-yy', 'character-banner', '16', 'source', 1), ('object/ui/shop/dlg_buy.img', 'shopextra-dlg-buy', 'buy-panel', None, 'source', 1), ('object/ui/shop/dlg_donate.img', 'shopextra-dlg-donate', 'donate-panel', None, 'source', 1), ('object/ui/shop/dlg_luckResult.img', 'shopextra-dlg-luckresult', 'luck-result', None, 'source', 1), ('object/ui/shop/dlg_repair.img', 'shopextra-dlg-repair', 'repair-panel', None, 'source', 1), ('object/ui/shop/equiped.img', 'shopextra-equiped', 'glyph', '已装备', 'redraw', 1), ('object/ui/shop/forged.img', 'shopextra-forged', 'hammer-icon', None, 'redraw', 1), ('object/ui/shop/img_itemTag.img', 'shopextra-img-itemtag', 'item-tag', None, 'source', 1), ('object/ui/shop/img_recycler.img', 'shopextra-img-recycler', 'recycler-panel', None, 'source', 1), ('object/ui/shop/img_ware.img', 'shopextra-img-ware', 'ware-row', None, 'source', 1), ('object/ui/shop/img_wareFrame.img', 'shopextra-img-wareframe', 'ware-frame', None, 'source', 1), ('object/ui/shop/lightIcon/dlg_back.img', 'shopextra-lighticon-dlg-back', 'category-icon', 'back', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_bg.img', 'shopextra-lighticon-dlg-bg', 'category-icon', 'bg', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_bomb.img', 'shopextra-lighticon-dlg-bomb', 'category-icon', 'bomb', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_cap.img', 'shopextra-lighticon-dlg-cap', 'category-icon', 'cap', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_cloth.img', 'shopextra-lighticon-dlg-cloth', 'category-icon', 'cloth', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_face.img', 'shopextra-lighticon-dlg-face', 'category-icon', 'face', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_foot.img', 'shopextra-lighticon-dlg-foot', 'category-icon', 'foot', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_huanying.img', 'shopextra-lighticon-dlg-huanying', 'category-icon', 'huanying', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_namecard.img', 'shopextra-lighticon-dlg-namecard', 'category-icon', 'namecard', 'redraw', 1), ('object/ui/shop/lightIcon/dlg_pet.img', 'shopextra-lighticon-dlg-pet', 'category-icon', 'pet', 'redraw', 1), ('object/ui/shop/luckyStar/btn_startLuck.img', 'shopextra-luckystar-btn-startluck', 'lucky-button', '开始', 'redraw', 4), ('object/ui/shop/luckyStar/btn_stopLuck.img', 'shopextra-luckystar-btn-stopluck', 'lucky-button', '停止', 'redraw', 4), ('object/ui/shop/luckyStar/frame.img', 'shopextra-luckystar-frame', 'lucky-frame', None, 'source', 1), ('object/ui/shop/luckyStar/img_light.img', 'shopextra-luckystar-img-light', 'lucky-lights', None, 'source', 7), ('object/ui/shop/luckyStar/img_lightback.img', 'shopextra-luckystar-img-lightback', 'lucky-lights', None, 'source', 1), ('object/ui/shop/luckyStar/img_luckyStar.img', 'shopextra-luckystar-img-luckystar', 'lucky-machine', None, 'redraw', 1), ('object/ui/shop/luckyStar/tip.img', 'shopextra-luckystar-tip', 'lucky-tip', None, 'redraw', 1), ('object/ui/shop/luckyStar/tip_luckyStar.img', 'shopextra-luckystar-tip-luckystar', 'lucky-small-tip', None, 'source', 1), ('object/ui/shop/rad_QB.img', 'shopextra-rad-qb', 'currency-radio', 'Q币专区', 'source', 2), ('object/ui/shop/rad_TangB.img', 'shopextra-rad-tangb', 'currency-radio', '灵币专区', 'source', 2), ('object/ui/shop/rolename/rolename1.img', 'shopextra-rolename-rolename1', 'role-name', '山岳', 'redraw', 1), ('object/ui/shop/rolename/rolename13.img', 'shopextra-rolename-rolename13', 'role-name', '松翁', 'redraw', 1), ('object/ui/shop/rolename/rolename14.img', 'shopextra-rolename-rolename14', 'role-name', '玉匠', 'redraw', 1), ('object/ui/shop/rolename/rolename15.img', 'shopextra-rolename-rolename15', 'role-name', '纸鸢', 'redraw', 1), ('object/ui/shop/rolename/rolename16.img', 'shopextra-rolename-rolename16', 'role-name', '赤砂', 'redraw', 1), ('object/ui/shop/rolename/rolename18.img', 'shopextra-rolename-rolename18', 'role-name', '赤枪', 'redraw', 1), ('object/ui/shop/rolename/rolename19.img', 'shopextra-rolename-rolename19', 'role-name', '唤雪', 'redraw', 1), ('object/ui/shop/rolename/rolename2.img', 'shopextra-rolename-rolename2', 'role-name', '莲花', 'redraw', 1), ('object/ui/shop/rolename/rolename20.img', 'shopextra-rolename-rolename20', 'role-name', '水龙', 'redraw', 1), ('object/ui/shop/rolename/rolename21.img', 'shopextra-rolename-rolename21', 'role-name', '灵篆', 'redraw', 1), ('object/ui/shop/rolename/rolename22.img', 'shopextra-rolename-rolename22', 'role-name', '月影', 'redraw', 1), ('object/ui/shop/rolename/rolename3.img', 'shopextra-rolename-rolename3', 'role-name', '冰剑', 'redraw', 1), ('object/ui/shop/rolename/rolename4.img', 'shopextra-rolename-rolename4', 'role-name', '火符', 'redraw', 1), ('object/ui/shop/rolename/rolename5.img', 'shopextra-rolename-rolename5', 'role-name', '天音', 'redraw', 1), ('object/ui/shop/rolename/rolename6.img', 'shopextra-rolename-rolename6', 'role-name', '雷法', 'redraw', 1), ('object/ui/shop/rolename/rolename7.img', 'shopextra-rolename-rolename7', 'role-name', '炼丹', 'redraw', 1), ('object/ui/shop/rolename/rolename8.img', 'shopextra-rolename-rolename8', 'role-name', '竹弓', 'redraw', 1), ('object/ui/shop/rolename/rolename9.img', 'shopextra-rolename-rolename9', 'role-name', '道童', 'redraw', 1), ('object/ui/shop/secrecyValidate/btn_cancel.img', 'shopextra-secrecyvalidate-btn-cancel', 'button4', '取消', 'source', 4), ('object/ui/shop/secrecyValidate/btn_forward.img', 'shopextra-secrecyvalidate-btn-forward', 'button4', '上一步', 'source', 4), ('object/ui/shop/secrecyValidate/btn_next.img', 'shopextra-secrecyvalidate-btn-next', 'button4', '下一步', 'source', 4), ('object/ui/shop/secrecyValidate/btn_ratio.img', 'shopextra-secrecyvalidate-btn-ratio', 'security-radio', None, 'source', 4), ('object/ui/shop/secrecyValidate/dlg_DefaultSecrecyValidate.img', 'shopextra-secrecyvalidate-dlg-defaultsecrecyvalidate', 'security-panel', None, 'source', 1), ('object/ui/shop/secrecyValidate/txt_long.img', 'shopextra-secrecyvalidate-txt-long', 'edit-paper', None, 'source', 1), ('object/ui/shop/secrecyValidate/txt_small.img', 'shopextra-secrecyvalidate-txt-small', 'edit-paper', None, 'source', 1), ('object/ui/shop/tab_char.img', 'shopextra-tab-char', 'tab-dark-paper', '角色', 'source', 2), ('object/ui/shop/tab_itemChar.img', 'shopextra-tab-itemchar', 'tab-paper-jade', '角色', 'source', 2), ('object/ui/shop/tab_itemPet.img', 'shopextra-tab-itempet', 'tab-dark-paper', '宠物', 'source', 2), ('object/ui/shop/tab_itemZizuan.img', 'shopextra-tab-itemzizuan', 'tab-dark-paper', None, 'source', 2), ('object/ui/shop/tab_sub.img', 'shopextra-tab-sub', 'tab-paper-jade', None, 'source', 2), ('object/ui/shop/ware/originPrice.img', 'shopextra-ware-originprice', 'glyph', '原价:', 'redraw', 1), ('object/ui/shop/ware/rebatePrice.img', 'shopextra-ware-rebateprice', 'glyph', '折后:', 'redraw', 1), ('object/ui/shop/wareAttr/0.img', 'shopextra-wareattr-0', 'digit', '0', 'redraw', 1), ('object/ui/shop/wareAttr/1.img', 'shopextra-wareattr-1', 'digit', '1', 'redraw', 1), ('object/ui/shop/wareAttr/2.img', 'shopextra-wareattr-2', 'digit', '2', 'redraw', 1), ('object/ui/shop/wareAttr/3.img', 'shopextra-wareattr-3', 'digit', '3', 'redraw', 1), ('object/ui/shop/wareAttr/4.img', 'shopextra-wareattr-4', 'digit', '4', 'redraw', 1), ('object/ui/shop/wareAttr/5.img', 'shopextra-wareattr-5', 'digit', '5', 'redraw', 1), ('object/ui/shop/wareAttr/6.img', 'shopextra-wareattr-6', 'digit', '6', 'redraw', 1), ('object/ui/shop/wareAttr/7.img', 'shopextra-wareattr-7', 'digit', '7', 'redraw', 1), ('object/ui/shop/wareAttr/8.img', 'shopextra-wareattr-8', 'digit', '8', 'redraw', 1), ('object/ui/shop/wareAttr/9.img', 'shopextra-wareattr-9', 'digit', '9', 'redraw', 1), ('object/ui/shop/wareAttr/bg_rebate.img', 'shopextra-wareattr-bg-rebate', 'badge', None, 'redraw', 1), ('object/ui/shop/wareAttr/free.img', 'shopextra-wareattr-free', 'badge', '免费', 'redraw', 1), ('object/ui/shop/wareAttr/hot.img', 'shopextra-wareattr-hot', 'badge', '热销', 'redraw', 1), ('object/ui/shop/wareAttr/member.img', 'shopextra-wareattr-member', 'badge', '会员', 'redraw', 1), ('object/ui/shop/wareAttr/memberPic.img', 'shopextra-wareattr-memberpic', 'glyph', '会员:', 'redraw', 1), ('object/ui/shop/wareAttr/new.img', 'shopextra-wareattr-new', 'badge', '新品', 'redraw', 1), ('object/ui/shop/wareAttr/numberlimited.img', 'shopextra-wareattr-numberlimited', 'badge', '限量', 'redraw', 1), ('object/ui/shop/wareAttr/point.img', 'shopextra-wareattr-point', 'point', '·', 'redraw', 1), ('object/ui/shop/wareAttr/timelimited.img', 'shopextra-wareattr-timelimited', 'badge', '限时', 'redraw', 1), ('object/ui/shop/wareAttr/zhe.img', 'shopextra-wareattr-zhe', 'glyph', '折', 'redraw', 1)]
PATHS = {path: (kind, label) for path, kind, family, label, alpha, count in SPEC_ROWS}
SPECS = {kind: {'nativePath':path, 'family':family, 'label':label, 'alpha':alpha, 'count':count}
         for path, kind, family, label, alpha, count in SPEC_ROWS}
STRUCTURAL_ALPHA_INPUTS = {
    f'{kind}-{index:02}': f"{REFERENCE}/source/{path.removeprefix('object/ui/').removesuffix('.img').replace('/', '__')}-{index:02}.png"
    for path, kind, family, label, alpha, count in SPEC_ROWS if alpha == 'source' for index in range(count)
}
VISUAL_MAPPING_ASSUMPTIONS = [
    'Exactly112 remaining native shop paths,168 original positions; existing20 shop controls are excluded.',
    'Character banners and role labels use the shared18-entry sourceRoleId/native alias/project portrait contract; no filename identity guesses or reused placeholder role.',
    'Text-only digits/role names, small category glyphs, promo badges, eight egg-title phases and cosmetic lucky-machine art rebuild whole-frame alpha to remove legacy glyph/person/bear silhouettes. Functional crop sizes/offsets/modes remain exact.',
    'Source-alpha policies retain exact structural planes, including lucky bulb positions, frame glows, input fields, radio holes and dialogs; alpha-redraw rows are separate documented cosmetic exceptions.',
    'Q币 source payment category is retained because underlying payment callbacks/URL/values are unchanged. TangB/QQ糖币 is 灵币; 酷比宝石 is 灵玉. QQTTicket variable does not override original displayed gemstone identity.',
    'Source8 egg title and7 bulb positions retain distinct stored slots; timing, loops, active bindings, live text width and final visuals remain unverified.',
]

@lru_cache(maxsize=168)
def source_alpha(kind,index):
    with Image.open(ROOT / STRUCTURAL_ALPHA_INPUTS[f'{kind}-{index:02}']) as picture:
        return picture.getchannel('A').copy()

@lru_cache(maxsize=1)
def role_entries():
    data=json.loads((ROOT/'assets/native-client-ui/room-extra-reference/roster-mapping-audit.json').read_bytes())
    entries={entry['sourceRoleId']:entry for entry in data['entries']}
    if len(entries)!=18:
        raise ValueError('Shared role allocation changed')
    for role_id, entry in entries.items():
        picture = entry['portrait']
        if (PAINT_INPUTS[f'shopextra-role-{role_id}'] != picture['file'] or
                hashlib.sha256((ROOT / picture['file']).read_bytes()).hexdigest() != picture['sha256']):
            raise ValueError('Shared project portrait allocation changed')
    return entries


def render(kind, label, index, size, paints, font_path, nine_slice, scaled):
    spec = SPECS[kind]
    family = spec['family']
    if not 0 <= index < spec['count']:
        raise ValueError('Native shop-extra source frame index differs')
    ink, jade, gold, pale = '#254e40', '#234b3c', '#c8ad72', '#fff3d5'
    state = ('normal', 'disabled', 'hover', 'pressed')[index] if spec['count'] == 4 else 'normal'

    def paint(name):
        if name in paints:
            return paints[name]
        with Image.open(ROOT / PAINT_INPUTS[name]) as picture:
            return picture.convert('RGBA')

    def base(color=jade):
        return Image.new('RGBA', size, color)

    def label_at(out, pos, text, fs=12, fill=pale, anchor='mm', edge=False):
        font = ImageFont.truetype(str(font_path), fs)
        ImageDraw.Draw(out).text(pos, text, font=font, fill=fill, anchor=anchor,
                                 stroke_width=1 if edge else 0, stroke_fill=ink)

    def fit_text(canvas_size, text, maximum=13, fill=pale, edge=True):
        # Own font rasterization, whole native frame. No old glyph alpha is reused.
        factor = 4
        out = Image.new('RGBA', (canvas_size[0] * factor, canvas_size[1] * factor))
        draw = ImageDraw.Draw(out)
        stroke = factor if edge else 0
        for fs in range(maximum, 4, -1):
            font = ImageFont.truetype(str(font_path), fs * factor)
            box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
            if box[2] - box[0] <= (canvas_size[0] - 1) * factor and box[3] - box[1] <= (canvas_size[1] - 1) * factor:
                break
        box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
        origin = ((out.width - box[2] + box[0]) // 2 - box[0], (out.height - box[3] + box[1]) // 2 - box[1])
        draw.text(origin, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=ink)
        return scaled(out, canvas_size)

    def panel():
        out = base('#f3ead2')
        out.alpha_composite(nine_slice(scaled(paints['panel'], (132, 124)), size, 18))
        return out

    def well(out, rect, light=False):
        ImageDraw.Draw(out).rounded_rectangle(rect, radius=4,
            fill='#fff8e6' if light else '#203f35', outline=gold)

    def button(style=None):
        chosen = style or state
        out = base()
        texture = paints['normal' if chosen == 'disabled' else chosen]
        out.alpha_composite(nine_slice(texture, size, 42))
        if chosen == 'disabled':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.05)).enhance(0.8)
        return out

    if family == 'character-banner':
        role_id = int(label)
        entry = role_entries()[role_id]
        if entry['nativeAlias'] != Path(spec['nativePath']).stem.lower():
            raise ValueError('Native shop character alias differs from confirmed role contract')
        out = base()
        out.alpha_composite(scaled(paints['normal'].crop((90, 35, 400, 110)), size))
        portrait_source = paint(f'shopextra-role-{role_id}')
        if portrait_source.size != (256, 256):
            raise ValueError('Confirmed project portrait canvas changed')
        portrait = scaled(portrait_source.crop((0, 72, 256, 216)), (73, 41))
        # Explicit own-portrait facial ROI, uniformly reduced then clipped to
        # the original116x35 banner. It is not a world attachment or source-role
        # recognition based on a filename.
        out.alpha_composite(portrait, (42, -2))
        ImageDraw.Draw(out).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        label_at(out, (22, size[1] // 2), entry['uiShortName'], 12, edge=True)
    elif family in ('role-name', 'glyph', 'digit'):
        if family == 'role-name':
            role_id = int(Path(spec['nativePath']).stem.removeprefix('rolename'))
            if role_entries()[role_id]['uiShortName'] != label:
                raise ValueError('Role short name differs from the confirmed allocation')
        maximum = 14 if family == 'digit' else 13 if family == 'role-name' else 11
        out = fit_text(size, label, maximum, fill=pale, edge=True)
    elif family == 'point':
        out = Image.new('RGBA', size)
        ImageDraw.Draw(out).ellipse((2, 2, size[0] - 3, size[1] - 2), fill=pale, outline=gold)
    elif family in ('button3', 'button4', 'stack3'):
        style = ('normal', 'hover', 'pressed')[index] if family in ('button3', 'stack3') else state
        out = button(style)
        if family == 'stack3':
            draw = ImageDraw.Draw(out)
            font = ImageFont.truetype(str(font_path), 13)
            draw.multiline_text((size[0] // 2, size[1] // 2), label, font=font,
                fill=pale, anchor='mm', align='center', spacing=1, stroke_width=1, stroke_fill=ink)
        else:
            label_at(out, (size[0] // 2, size[1] // 2 + (style == 'pressed')), label, 13,
                     fill='#d4d6cf' if style == 'disabled' else pale, edge=True)
    elif family == 'hammer-slot':
        out = panel()
        overlay = '#344e44' if state == 'disabled' else '#3e6653' if state == 'hover' else jade
        ImageDraw.Draw(out).rounded_rectangle((6, 6, size[0] - 7, size[1] - 7), radius=5, fill=overlay, outline=gold)
        # The live hammer image/count are separate children. Never bake an
        # owned hammer or a fake count into an empty functional slot.
        ImageDraw.Draw(out).rectangle((11, 17, size[0] - 12, size[1] - 12), fill='#203f35', outline='#799172')
        if state == 'disabled':
            out = ImageEnhance.Brightness(ImageEnhance.Color(out).enhance(0.02)).enhance(0.78)
    elif family == 'egg-panel':
        out = panel()
        label_at(out, (size[0] // 2, 40), '惊喜砸彩蛋', 22, fill=ink)
        well(out, (16, 75, size[0] - 17, 224))
        # Explicit yellow description24,90,302,60 and white hammerCnt children.
        for x in (17, 106, 195):
            well(out, (x, 230, x + 82, 308))
        well(out, (149, 133, 235, 216))
    elif family == 'egg-title':
        out = Image.new('RGBA', size)
        # Eight distinct title-gloss samples; raw slot order is preserved,
        # native durations and state labels are not invented.
        ribbon = nine_slice(paints['normal'], (size[0] - 12, size[1] - 14), 42)
        out.alpha_composite(ribbon, (6, 7))
        title = fit_text((size[0] - 45, size[1] - 24), label, 25, fill=pale)
        out.alpha_composite(title, (22, 12))
        draw = ImageDraw.Draw(out)
        x = 20 + index * (size[0] - 40) // 7
        draw.line((x, 8, x, 20), fill='#fffbd6', width=2)
        draw.line((x - 5, 14, x + 5, 14), fill='#fffbd6', width=2)
        draw.ellipse((size[0] - 26, 58 - index % 3, size[0] - 22, 62 - index % 3), fill=gold)
    elif family in ('egg-failure', 'egg-success'):
        out = base('#607f65' if family == 'egg-failure' else '#e1c27e')
        # Exact native particle alpha is kept; color is repainted with own
        # jade/gold material, not copied from the legacy pebble/ribbon pixels.
        if family == 'egg-failure':
            out.alpha_composite(scaled(paints['normal'].crop((90, 35, 400, 110)), size))
        else:
            draw = ImageDraw.Draw(out)
            for y in range(size[1]):
                draw.line((0, y, size[0] - 1, y), fill='#fff1bd' if y % 16 < 5 else '#dfc17d')
    elif family in ('buy-panel', 'donate-panel', 'repair-panel', 'luck-result'):
        out = panel()
        if family == 'buy-panel':
            well(out, (27, 23, 296, 58))
            well(out, (27, 61, 296, 181))
            for y in (186, 246, 305):
                well(out, (27, y - 8, 256, y + 17))
                label_at(out, (37, y + 4), '价格:', 11, anchor='lm')
            # These source QB/QD shortfall hints are explicitly blue. Keep
            # their whole text rectangles light and do not bake replacement text.
            well(out, (20, 212, 276, 234), light=True)
            well(out, (20, 270, 276, 292), light=True)
        elif family == 'donate-panel':
            label_at(out, (size[0] // 2, 35), '赠送物品', 16, fill=ink)
            label_at(out, (36, 88), '商品现价:', 11, fill=ink, anchor='lm')
            well(out, (105, 76, 215, 100), light=True)
            label_at(out, (36, 112), '受赠人:', 11, fill=ink, anchor='lm')
            well(out, (106, 102, 215, 123))
            well(out, (20, 126, 278, 148), light=True)
            well(out, (232, 71, 300, 139))
            well(out, (213, 138, 317, 162))
            label_at(out, (40, 177), '赠送留言:', 11, fill=ink, anchor='lm')
            well(out, (37, 186, 288, 279))
        elif family == 'repair-panel':
            well(out, (29, 39, 297, 66))
            well(out, (29, 74, 297, 205))
            well(out, (29, 216, 297, 244))
            well(out, (29, 260, 297, 289))
            label_at(out, (40, 231), '数量:', 11, anchor='lm')
            label_at(out, (40, 275), '价格:', 11, anchor='lm')
        else:
            label_at(out, (size[0] // 2, 46), '恭喜！', 26, fill=ink)
            well(out, (23, 76, size[0] - 24, size[1] - 72))
    elif family == 'recycler-panel':
        out = panel()
        label_at(out, (19, 22), '收藏柜', 14, fill=ink, anchor='lm')
        well(out, (18, 43, size[0] - 18, 316), light=True)
        label_at(out, (100, 65), '道具名称', 12, fill=ink)
        # Ten native item rows start30,80 and keep a dark caption background.
        for y in range(80, 301, 22):
            well(out, (29, y - 1, 172, y + 20))
        ImageDraw.Draw(out).line((197, 83, 197, 294), fill=gold, width=2)
    elif family == 'ware-row':
        out = base('#24483c')
        well(out, (0, 0, 68, size[1] - 1))
        ImageDraw.Draw(out).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
    elif family in ('ware-frame', 'lucky-frame', 'item-tag'):
        out = base('#d9bd73' if family != 'item-tag' else '#84a76c')
        ImageDraw.Draw(out).rounded_rectangle((1, 1, size[0] - 2, size[1] - 2), radius=5,
                                               fill='#c8ad72', outline='#fff4cb', width=2)
    elif family == 'hammer-icon':
        out = Image.new('RGBA', size)
        symbol = scaled(paint('shopextra-hammer'), size)
        out.alpha_composite(symbol)
    elif family == 'category-icon':
        out = Image.new('RGBA', size)
        d = ImageDraw.Draw(out)
        w, h = size
        if label == 'back':
            d.ellipse((0, 1, w // 2, h - 2), fill='#b0d0a3', outline=gold)
            d.ellipse((w // 2, 1, w - 1, h - 2), fill='#b0d0a3', outline=gold)
            d.ellipse((w // 2 - 1, h // 2 - 2, w // 2 + 1, h // 2 + 1), fill=gold)
        elif label == 'bg':
            d.ellipse((w - 7, 0, w - 3, 4), fill=gold)
            d.polygon(((0, h - 1), (w // 3, 3), (w // 2, h - 4), (w * 3 // 4, 5), (w - 1, h - 1)), fill='#79ad7b', outline=gold)
        elif label == 'bomb':
            d.ellipse((1, 1, w - 2, h - 1), fill='#5fbfa5', outline=gold)
            d.arc((w // 2 - 2, 0, w - 1, 6), 180, 300, fill=pale)
        elif label == 'cap':
            d.polygon(((1, h - 2), (4, 2), (w - 5, 2), (w - 2, h - 2)), fill=jade, outline=gold)
            d.ellipse((w // 2 - 1, 2, w // 2 + 1, 4), fill=pale)
        elif label == 'cloth':
            d.polygon(((w // 3, 0), (w * 2 // 3, 0), (w - 1, 4), (w - 4, 7), (w * 2 // 3, 5),
                       (w * 2 // 3, h - 1), (w // 3, h - 1), (w // 3, 5), (3, 7), (0, 4)), fill=jade, outline=gold)
            d.line((w // 2, 2, w // 2, h - 2), fill=pale)
        elif label == 'face':
            d.ellipse((1, 0, w - 2, h - 1), fill='#ffe1ac', outline=gold)
            d.point((w // 3, h // 2), fill=ink);d.point((w * 2 // 3, h // 2), fill=ink)
            d.arc((3, h // 2, w - 3, h - 2), 0, 180, fill=ink)
        elif label == 'foot':
            d.polygon(((3, 0), (9, 0), (9, h - 5), (w - 1, h - 5), (w - 1, h - 1), (2, h - 1)), fill=jade, outline=gold)
        elif label == 'huanying':
            for x, y, r in ((4, 4, 3), (12, 9, 3), (5, h - 4, 2)):
                d.polygon(((x, y - r), (x + r, y), (x, y + r), (x - r, y)), fill=gold)
        elif label == 'namecard':
            d.rectangle((0, 1, w - 1, h - 2), fill=jade, outline=gold)
            d.ellipse((2, 3, 6, 8), fill=pale)
            d.line((8, 4, w - 3, 4), fill=pale);d.line((8, 7, w - 3, 7), fill=pale)
        elif label == 'pet':
            d.ellipse((0, 0, 6, 6), fill='#bbd39f', outline=gold)
            d.ellipse((w - 7, 0, w - 1, 6), fill='#bbd39f', outline=gold)
            d.ellipse((2, 3, w - 3, h - 1), fill='#bbd39f', outline=gold)
            d.point((6, 8), fill=ink);d.point((w - 7, 8), fill=ink)
        else:
            raise ValueError('Unknown source-observed small category symbol')
    elif family == 'lucky-button':
        out = Image.new('RGBA', size)
        layer = button()
        # Replace the old bear-head cosmetic silhouette with an own scroll seal.
        mask = Image.new('L', size)
        ImageDraw.Draw(mask).rounded_rectangle((2, 3, size[0] - 3, size[1] - 3), radius=14, fill=255)
        layer.putalpha(mask)
        out.alpha_composite(layer)
        label_at(out, (size[0] // 2, size[1] // 2), label, 17, edge=True)
    elif family == 'lucky-lights':
        # Exact sparse alpha encodes bulb positions and the7 cropped phases.
        # Native source crops/offsets remain independent, never stretch a phase.
        out = base('#8fe0b0')
        ImageDraw.Draw(out).line((0, 1, size[0] - 1, 1), fill='#fffbd0', width=2)
    elif family == 'lucky-machine':
        out = panel()
        label_at(out, (108, 32), '福缘宝阁', 24, fill=ink)
        # bkimagepos(-15,-52)+raw frame offset(10,5) gives(-5,-47).
        # item children13/88/163,63 -> raw18/93/168,110.
        for x in (16, 91, 166):
            well(out, (x, 106, x + 69, 178))
        symbol = scaled(paint('shopextra-chest'), (95, 95))
        out.alpha_composite(symbol, (291, 49))
        # Start/stop share parent rect309,108,75,65 -> raw314,155.
        well(out, (311, 152, 391, 222))
    elif family == 'lucky-tip':
        out = Image.new('RGBA', size)
        tile = nine_slice(paints['normal'], (size[0] - 14, 80), 42)
        out.alpha_composite(tile, (7, 5))
        label_at(out, (119, 29), '福缘宝阁', 22, edge=True)
        label_at(out, (285, 29), '只要10币，随机道具！', 13, edge=True)
        label_at(out, (250, 58), '道友来试试今日手气吧！', 13, edge=True)
        symbol = scaled(paint('shopextra-chest'), (133, 133))
        out.alpha_composite(symbol, (264, 82))
        # The source raster explicitly says10币; currency type/fee execution
        # is not inferred from variable names or altered by this art candidate.
    elif family == 'lucky-small-tip':
        out = panel()
        label_at(out, (size[0] // 2, 18), '福缘好礼', 14, fill=ink)
        label_at(out, (size[0] // 2, 38), '道友试试手气吧！', 12, fill=ink)
    elif family == 'currency-radio':
        out = button('normal' if index == 0 else 'hover')
        label_at(out, (size[0] // 2, size[1] // 2), label, 13, edge=True)
    elif family == 'security-radio':
        out = base('#b8ccb0' if index == 1 else '#fff3d5')
        ImageDraw.Draw(out).ellipse((0, 0, size[0] - 1, size[1] - 1), outline=gold)
        # Source raw0 has a colored hollow center, not an alpha hole.
        # Its RGB distinction must be rebuilt as well as its alpha retained.
        if index == 0:
            ImageDraw.Draw(out).ellipse((3, 3, size[0] - 4, size[1] - 4), fill=jade)
        elif index == 2:
            ImageDraw.Draw(out).ellipse((1, 1, size[0] - 2, size[1] - 2), outline='#fffbd0')
    elif family == 'security-panel':
        out = panel()
        well(out, (16, 33, size[0] - 17, size[1] - 39), light=True)
        # Source prompt labels are dark/blue, genericTEditNum is black. No
        # secret answer, account value or source-protocol text is baked here.
    elif family == 'edit-paper':
        out = base('#fff8e6')
        ImageDraw.Draw(out).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=gold)
    elif family in ('tab-dark-paper', 'tab-paper-jade'):
        paper = index == 1 if family == 'tab-dark-paper' else index == 0
        out = panel() if paper else button('normal')
        if label:
            label_at(out, (size[0] // 2, size[1] // 2), label, 12, fill=ink if paper else pale)
    elif family == 'badge':
        out = Image.new('RGBA', size)
        d = ImageDraw.Draw(out)
        cx, cy = size[0] // 2, size[1] // 2
        radius = min(size) // 2 - 2
        d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=jade, outline=gold, width=2)
        for x in (cx - radius + 4, cx, cx + radius - 4):
            d.ellipse((x - 4, cy - radius - 1, x + 4, cy - radius + 7), fill='#719d72', outline=gold)
        if label:
            label_at(out, (cx, cy + 2), label, 11 if size[0] <= 45 else 13, edge=True)
    elif family == 'advert':
        out = panel()
        symbol = scaled(paint('shopextra-chest'), (139, 139))
        out.alpha_composite(symbol, (size[0] - 151, 12))
        label_at(out, (125, 59), '灵葫宝阁', 28, fill=ink)
        label_at(out, (124, 103), '服饰 · 灵器 · 仙宠', 15, fill=ink)
    else:
        raise ValueError(f'Unknown shop-extra family {family}')
    if spec['alpha'] == 'source':
        opacity = source_alpha(kind, index)
        if opacity.size != size:
            raise ValueError('Native shop-extra structural alpha dimensions differ')
        out.putalpha(opacity)
    return out
