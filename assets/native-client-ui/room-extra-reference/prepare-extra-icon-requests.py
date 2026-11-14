"""Record independent original UI portrait requests; never call paid services."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGNS = [
    ('67', '玉墨面师', 'a round pale jade mask sage with broad ink-green eyebrows, a folded ivory scholar cap, warm bronze cheeks and a tiny bamboo-scroll collar; no skull, no horror'),
    ('69', '苔盏灵蛙', 'a plump moss-jade toad spirit with one large warm amber eye and one smaller curious eye, a cream throat, short leaf eyebrows and a tiny gold dew-drop brow ornament'),
    ('72', '青崖甲卫', 'a friendly blue-gray stone guardian with a rounded square face, narrow gold eyes, a dark jade forehead plate and small smooth cloud-carved helmet wings'),
    ('73', '铜铃渡客', 'a weathered but cute one-eyed river ferryman, warm tan face, a small ivory eye patch, broad bamboo rain hat, one dark brown moustache curl and a tiny copper bell at his collar'),
    ('75', '松潮长髯', 'an elderly broad-faced teal-bearded tide warden with two sweeping pale jade eyebrows, thick turquoise moustache and beard, a small ivory crane-shaped head crest and a calm smile'),
    ('77', '瓷骨灯灵', 'a little ivory porcelain lantern spirit with a simple rounded porcelain face, dark jade eye hollows shaped like gentle crescent moons, small smiling mouth and two tiny warm amber cracks; not a human skull'),
    ('78', '朱炉卜者', 'a small round-faced diviner beneath a deep cinnabar hood with gold cloud trim, luminous pale blue eyes, a visible jade-blue nose and a small round incense censer medallion at the throat'),
    ('79', '赤陶面灵', 'a cheerful red terracotta guardian mask with a broad circular forehead, gold dot eyebrows, small dark jade eyes, an open ivory smile and short clay cloud curls at the temples'),
    ('81', '雪玉鸮灵', 'a snow-ivory owl oracle with a wide round heart-shaped face disk, dark plum eyes, pale jade feather brows, a little amber beak and a small gold star on the forehead'),
    ('85', '夜云守星', 'a mysterious but friendly night-cloud keeper with a dark indigo face, two warm gold star-like eyes, a soft jade-edged cloud hood, tiny ivory moon nose and a calm subtle smile'),
    ('117', '月瓣小仙', 'a peach-ivory flower fairy with a round young adult face, lavender almond eyes, short silver hair, three pale jade moon-petal hair ornaments on the left and a warm ivory high collar'),
    ('118', '古玉龟卜', 'an ancient jade turtle oracle with a rounded olive turtle face, warm brown eyes, small folded ivory brow scales, a bronze shell rim behind the head and a short cream goatee'),
    ('119', '霜晶角灵', 'a cute frost-crystal stag spirit with a light blue-gray rounded deer face, two short branching pale jade antlers fully visible, dark violet eyes and a tiny snow-white forehead diamond'),
    ('124', '丹岩小狮', 'a round cinnabar stone lion cub spirit with a broad ruby nose, warm golden eyes, ivory cheek swirls, a short sculpted red-orange cloud mane and a gentle grin'),
    ('125', '桂金鹏灵', 'a small round gold-and-ivory mythical bird spirit with a short jade beak, two warm brown almond eyes, a golden osmanthus leaf crest and soft peach cheek feathers'),
    ('xxm', '竹叶符使', 'a slim-faced young adult talisman runner with warm brown skin, dark brown swept hair tied with a green leaf ribbon, lively amber eyes, one small eyebrow scar and a jade-and-cream collar'),
    ('zjl', '朱仪仙翁', 'a dignified but cute adult opera immortal with an ivory beard split into two short curls, a warm peach square face, expressive copper eyes and a compact cinnabar-and-gold ceremonial cloud crown'),
]


def main():
    source = json.loads((HERE / 'manifest.json').read_bytes())
    resources = {r['nativePath']: r for r in source['resources']}
    refs = ['references/image/01-mail-event.png', 'references/image/team-ui-v2.png']
    requests = []
    for key, name, design in DESIGNS:
        native_path = f'object/ui/room/char/icon_{key}.img'
        prompt = (
            'Create ONE new original Daoist Q-style game UI head portrait, isolated on a genuinely transparent background. '
            'The two attached images are visual style references only: our detailed hand-painted jade-green, warm gold and ivory Daoist Q fantasy game interface. '
            'Do not copy their characters, faces, composition or words. This new portrait is for an independent 55x55 pixel UI image slot; it is not an animation or a full character sheet. '
            'Subject: '+design+'. '
            'Front three-quarter bust: show the complete head silhouette, hairstyle or head ornament, neck and a little collar only. Large expressive face, short cute proportions, rounded painted shapes, restrained rich colors, clean soft shading and crisp readable silhouette. '
            'Keep all head ornaments safely inside the square with generous fully transparent margins; face centered at approximately 52 percent canvas height. Simple lighting, no effects, no particles, no floating decorations. '
            'No border, no frame, no backdrop, no labels, no text, no numbers, no logo, no watermark, no full body, no weapons, no hands, no scenery, no floor, no cast shadow or checkerboard. '
            'True RGBA transparent cutout around the whole subject. A single original identity, not variants of a reused face and not a grid. '
            'This is project-authored original UI artwork; do not resemble a known licensed character or recreate QQTang art.'
        )
        requests.append({'slotKey': key, 'projectUiIdentityName': name, 'sourceNativePath': native_path,
            'sourceSha256': resources[native_path]['sourceSha256'],
            'sourceNamespace': 'Numeric filename selected by uiGame PVEBossInfo.m_iImageID; nonnumeric orphan aliases have no established runtime role bridge',
            'sourceRoleId': None, 'worldModelBindingVerified': False,
            'appearanceAllocation': 'Independent project-authored UI portrait identity at this stable native image path, not recovered original NPC identity',
            'submitted': {'prompt': prompt, 'referenced_image_paths': [str(ROOT / p) for p in refs], 'transparent_background': True},
            'referenceImages': [{'file': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest(), 'role': 'user canonical style only'} for p in refs],
            'configuredTarget': json.loads((ROOT / 'config/image-generation.json').read_bytes()),
            'actualSubmittedModel': None, 'actualSubmittedQuality': None, 'actualReturnedModel': None, 'actualReturnedQuality': None,
            'route': 'host builtin image_gen', 'paidApiInvoked': False,
            'plannedOutput': f'assets/native-client-ui/room-extra-reference/extra-icons/icon-{key}-master.png',
            'visualAccepted': False, 'nativeRuntimeVerified': False})
    previous_path = HERE / 'extra-icon-generation-requests.json'
    prepared_at = json.loads(previous_path.read_bytes())['preparedAtUtc'] if previous_path.exists() else datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = {'schemaVersion': 1, 'preparedAtUtc': prepared_at,
              'updatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scopeCorrection': 'cbz and xz were not generated: exact uiGame role ID10/11 alias evidence allows existing Star Formation and Cloud Tortoise identities',
              'sourceReferences': {'file': 'assets/native-client-ui/room-extra-reference/manifest.json', 'sha256': hashlib.sha256((HERE / 'manifest.json').read_bytes()).hexdigest()},
              'requests': requests}
    (HERE / 'extra-icon-generation-requests.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'independentPortraitRequests': len(requests)}))


if __name__ == '__main__':
    main()
