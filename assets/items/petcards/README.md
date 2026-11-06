# 自有仙灵与原创宠物静态卡面

2026-10-28：源 catalog 的petcard类48/48条已有256×256 RGBA静态候选。A—H八张首稿母图覆盖48项，I为28015的单件AI编辑。全部visualAccepted:false、runtimeAdopted:false，不代表宠物实体、动作、技能特效或整游戏美术验收完成。

art.json保留原ID、category、sourceName、sourceDescription、真实文件哈希、源图和裁切来源。自有外观projectIdentity / projectDisplayName另列，不改源能力数值。4334/4335保留10格/20格及旧版本限制；28044源明确“无效的宠物”，保留sourceExplicitInvalid:true，卡面用锁印，没有启用或编造天赋。28042源无明确天赋，卡面没有能力徽章。

内置image_gen实际附源功能图、两张指定主风格及自有成图。入口最多5张本地参考，因此把既有items-a和petcards-a等比组成references/item-and-pet-finish.png，作为来源明确的风格参考板，不是新画或正式素材。逐图generation区分Sunburst/max目标与未披露的实际型号/质量null。裁切和等比缩放不是模型生成。未新增付费路线，未操作Git。

实际采用image外观共9个：新仙气包04桂灯童、02绛铃、14绯耳灵、16露华灵、07苍嶂麟、06汐螺、12月弦师；新包没有同身份时用旧原创包13芽铃童、11霞角鹿。逐个实际看PNG并读receipt、最新review、portrait裁切和历史generation，原哈希及历史null保留在references/canon/。精确image相对路径、实际采用ID和目标PNG见adoption-index.json，prepared与used区分。这是本项目新外观选择，不是腾讯历史ID映射，也不引入MMO属性。

21/22及38/39用本项目道童/月影替代QQ企鹅，参考裁切来自references/own-four-characters-contact.png。猪、犬、龙、猫、熊猫、婴童、蝎、牛、驼、蝠等无合适同物种现存参考时绘制独立原创外观；同身份的能力变体保持特征。

首轮必要修正：C/D/G按实际两行间隙切片；H按各列间隙调整，去掉4334/4335上方混入的上一行金边并补全28044锁印。实际看最终256PNG，10/20清楚、锁印完整。28015 I实际编辑原C切片，双积分徽章3星纠正为2星，目视母图和最终256确认；editOf链保留。详见QA_NOTES.md，这些局部观察不等于整包通过。

仍需完整功能徽章复核、64px阅读性、alpha弱边缘、框板一致性及游戏内接入。重型本机时段尚未交还，未跑全族扫描、整包QA、编译、测试或实机；目前只有单批必要落盘和局部目视。

## 项目关联

- 项目：QQ堂道家Q版独立复刻；GitHub：https://github.com/luhailong-java/qqtang-daoist-remake 。本轮卡面未提交/上传。
- image仓库origin：https://luyuacpp.visualstudio.com/image/_git/image ；image的GitHub地址待确认。
- 风格参考：designs/mail-ui-v1/01-mail-event.png、designs/team-ui-v2/team-ui-v2.png。仙灵改造使用来源见adoption-index.json，不是直接客户端接入。
- 新项目实际位置：assets/items/petcards/；核实日期2026-10-28。image目录关联由协调者统一更新，本窗口不改共享Git。
