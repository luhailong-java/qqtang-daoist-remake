# 自有角色全库存与候选复用

核实日期：2026-10-26。image 素材库：`D:\work\image`；新项目：`D:\work\qqtang-ui`。

本次只检查现存 `q_daoist_character_pack_4096/` 及可证实的项目采用记录，没有全盘检索、下载、生图、恢复旧 Git 或修改 image。当前四位角色代码、现有采用文件及其他制作窗口成果均未改动。

## 已完成的库存工作

现存包共 **15 张 PNG、15 个不同身份**，没有额外未列入 manifest 的 PNG。15 张均已完整解码，PNG 签名正确、不是 LFS 指针，均为 **4096×4096 RGBA、真实 Alpha 0–255**，当前 SHA-256 与包内 manifest 完全一致。此处 15 是现存自有静态库存数，不是腾讯《QQ堂》全角色或本项目最终角色分母。

已采用的 00 金发带 Q 道童、07 月影少女、04 山岳守卫、03 莲花医者保持原状，详见 `OWN_CHARACTER_ADOPTION.md` 与 `OWN_CHARACTER_SOURCE_CANDIDATES.md`。另外 **11 张静态 master 已原样复制**到 `assets/characters/roster-candidates/<角色ID>/master.png`，各有 `source.json`，合计 101,213,002 字节；复制后逐张 SHA 与源一致。

11 位全部保留 `candidate_static_master_pending_roster_acceptance` 状态。未加入 `assets/art.json`、角色选择代码或玩法参数；未导入动作。不因为持弓、枪、药瓶、符牌等外观增加技能或改变速度、威力、容量、碰撞与地图尺度。

## 完整自有候选阵容建议

以现存 15 个身份组成一个待审的自有阵容：道童、月影、山岳、莲花，加上冰剑、火符、天音、雷法、炼丹、竹弓、赤枪、唤雪、水龙、灵篆、星阵。沿用每位自身发型、脸部特点、服饰与身份，不以毛毛、阿莎、悟空、泰坦或其他腾讯人物作为换衣模板。原版玩法属性如何映射，必须在完整原版角色规则取证后另行登记；本清单不给未知槽位自定属性。

从已实看的 PNG 可辨其职业、主色、发型、眼色和道具，适合继续作原创选角 master。**这些角色仍偏统一幼龄圆眼脸型**：火符、雷法、炼丹、灵篆等棕发少年尤其接近，冰剑、天音、莲花、星阵也有相近的束发与幼脸模板。本库存不将服装、法器不同等同于完整脸型／年龄／体态差异终验通过。后续如需扩展到全角色，先在本阵容的脸型、眉眼、年龄感与体态矩阵中确认独立识别，再安排必要新作；不按腾讯角色脸型推导。

## 本次新增的 11 位静态候选

下表源文件均位于 image 的 `q_daoist_character_pack_4096/`。新项目目标均位于 `assets/characters/roster-candidates/<ID>/`，`master.png` 是原字节副本，`source.json` 记录源路径、manifest、哈希、Alpha、历史证据缺口及候选状态。

| ID／现有身份 | 实看身份特征与待核项 | image 源 PNG | 新项目目标目录 |
|---|---|---|---|
| `01_ice_sword_girl` 冰剑少女 | 深棕长发高髻、蓝灰眼、蓝白裙袍、冰晶剑与蓝符；与其他高髻少女的幼脸差异待阵容对照 | `01_ice_sword_girl_transparent_4096.png` | `assets/characters/roster-candidates/01_ice_sword_girl/` |
| `02_fire_talisman_boy` 火符少年 | 棕发小马尾、粗眉、红金黑符袍、成扇火符与铜铃；与炼丹／雷法眉眼接近 | `02_fire_talisman_boy_transparent_4096.png` | `assets/characters/roster-candidates/02_fire_talisman_boy/` |
| `05_celestial_musician_girl` 天音少女 | 紫发高髻、紫眼、紫白长袍、琴与长飘带；琴和长发轮廓清楚 | `05_celestial_musician_girl_transparent_4096.png` | `assets/characters/roster-candidates/05_celestial_musician_girl/` |
| `06_thunder_caster_boy` 雷法少年 | 深棕短发小髻、太极额饰、黄白深蓝道袍、金色法器与黄符；少年脸部识别待加强 | `06_thunder_caster_boy_transparent_4096.png` | `assets/characters/roster-candidates/06_thunder_caster_boy/` |
| `08_alchemy_prodigy_boy` 炼丹童子 | 棕发小髻、橙金玉绿袍、掌托小炉、药瓶与卷轴药篓；不能因药篓自设容量数值 | `08_alchemy_prodigy_boy_transparent_4096.png` | `assets/characters/roster-candidates/08_alchemy_prodigy_boy/` |
| `09_bamboo_archer_girl` 竹弓少女 | 棕发高马尾、绿眼、叶饰、绿白短装、竹弓箭筒；发尾与拉弓姿态占宽较大 | `09_bamboo_archer_girl_transparent_4096.png` | `assets/characters/roster-candidates/09_bamboo_archer_girl/` |
| `10_crimson_spear_girl` 赤枪少女 | 双髻长尾、红金白裙甲、赤枪与长红绸；动态抬腿为静态画姿，不能当成跑步序列 | `10_crimson_spear_girl_transparent_4096.png` | `assets/characters/roster-candidates/10_crimson_spear_girl/` |
| `14_short_hair_snow_summoner_girl` 唤雪少女 | 银白短发、狐耳、紫眼、白紫毛领、雪晶及怀抱白色小兽；与月影同为银发但耳形／服装／道具不同，小兽未拆为独立宠物素材 | `14_short_hair_snow_summoner_girl_transparent_4096.png` | `assets/characters/roster-candidates/14_short_hair_snow_summoner_girl/` |
| `15_water_dragon_scholar_boy` 水龙书生 | 深蓝发髻、蓝眼、蓝白长袍、青玉佩及水龙折扇；长袍、扇面与玉佩需保持身份 | `15_water_dragon_scholar_boy_transparent_4096.png` | `assets/characters/roster-candidates/15_water_dragon_scholar_boy/` |
| `17_ghost_script_calligrapher_boy` 灵篆书生 | 棕发髻、额心青印、黑金青绿长袍、大笔与卷轴、两只青色小灵；小灵与卷轴尚未分层 | `17_ghost_script_calligrapher_boy_transparent_4096.png` | `assets/characters/roster-candidates/17_ghost_script_calligrapher_boy/` |
| `20_star_formation_master_girl` 星阵少女 | 棕发高髻、红星冠、黑金红长袍、星盘和星牌；牌面与衣饰细节密集，缩小辨识待目标分辨率核验 | `20_star_formation_master_girl_transparent_4096.png` | `assets/characters/roster-candidates/20_star_formation_master_girl/` |

以上 11 张已经逐张实际查看；前次已实看 00／03／04／07，以及邮件、组队两张主参考。查看器将 4096 图显示为 1600 预览；文件尺寸以 Pillow 完整解码为准。未将预览尺寸写成原图尺寸。

## 逐图文件核验

所有行均为 4096×4096 RGBA、Alpha 极值 `[0,255]`、PNG 签名 `89504e470d0a1a0a`、LFS 指针检查为 false、manifest 哈希匹配为 true。包围框为 Alpha 大于零的 `[左,上,右开,下开]`；它不是客户端碰撞体或正式角色根点。

| ID | 字节数 | Alpha 包围框 | SHA-256（源与候选副本相同） |
|---|---:|---|---|
| 01 | 8,013,428 | `[329,240,3764,3859]` | `2c25b13134fdf91fbcead12c82840cafcb1fcc74855891c5c24964cde33f22ef` |
| 02 | 8,809,819 | `[577,240,3519,3859]` | `8df2760a5a80eb54ea21558abace8bcbaeca7f7ae6f64de022b6a8b1919c854a` |
| 05 | 8,659,965 | `[665,240,3431,3859]` | `f8cd360988a1d5d9b6aebb81d9868b5d4692aa520d7fcae1af9d525bf70e12f8` |
| 06 | 8,588,401 | `[744,241,3349,3859]` | `abdfbe1fdc243ea6360a5d588f9ff1294fa2f0d43876d8b63aa452ec4889cd31` |
| 08 | 8,865,306 | `[610,240,3483,3859]` | `fcbf04089dbc229887d9c18b2b21e9dfb7997c5ec28c086e45db2d78e9bef82e` |
| 09 | 9,550,415 | `[270,240,3823,3859]` | `c7ba2937630b589f16c0581f76421f20eccb19599aba6b47cca748de450447dd` |
| 10 | 10,805,742 | `[244,240,3849,3859]` | `ea068eb40dbd372b108d2e7d041c8e270e898f8ae979ce039873a08e49a0260f` |
| 14 | 7,666,414 | `[678,240,3415,3859]` | `834fbe56bc3de4aa8a241d7e12a9725095cfcf486b98066876a8e70fa343c2a8` |
| 15 | 9,000,643 | `[450,240,3643,3859]` | `c3b96a88c2fdebb36951c8b47d3b1860b0e5895ae775bb360beb036bb393de70` |
| 17 | 9,763,399 | `[427,240,3669,3859]` | `34d13fe2558dee7ab8403180a7cd4c26e95b0b9795181053057b5759c69a5614` |
| 20 | 11,489,470 | `[440,240,3656,3859]` | `4a5de67ffb880a852554d460c709f7179bffd3706fa7bf825767e5369e9bd3e5` |

四位已采用角色的源文件也在本次重新完成解码与哈希核验；其 SHA 与 `OWN_CHARACTER_SOURCE_CANDIDATES.md` 一致。没有为了本表重新处理或覆盖四位已采用图。

## 来源链的可证实部分

现存人物包 README 把这些路径列为正式透明输出；manifest 为 `qdao.portraits.v6`、`status: static_art_only`、`engine_integration: false`。本次 11 位的 `creation_method` 均记为 `individual built-in image_gen redraw + skill cleanup`，逐图记录指向 `records/<完整 PNG stem>.json`。每张 candidate 的 `source.json` 保留了这两个声明及当前源哈希，未把静态包声明升级成游戏接入验收。

**11 个声明的逐图 record 当前均缺失**，人物包 `records/` 目录缺失。因此原图生成时间、原生生成尺寸、当时配置目标、实际提交／返回模型及质量全部保持未确认或 null。README 的“原生通常 1254×1254”只作历史概括；4096 明确是等比兼容导出画布，不能登记为原生 4K。当前配置不能给旧图倒填实际型号。复制未调用任何生成入口，不产生新的生图记录。

交接文档曾指向 v9 人物差异化及节庆最终验收，它们当前缺失，不能凭旧文字确认现存 15 图都是后续 v9／节庆最终版本。本次采用证据只到现存 PNG 与现存包 README／manifest 一致。没有从 Git、快照或已删除目录恢复来源。

## 旧清单中缺失的项

manifest／README 历史列 24 路径，当前实际 15 张，以下 **9 个路径不存在**。前 8 项是未在本现存包取得的身份，最后一项是道童兼容别名，不能把缺失别名算成一个新角色。历史 manifest 的预期 SHA 不是取得实物或验收的证据。

| ID／身份 | 缺失 PNG（image 的 `q_daoist_character_pack_4096/` 下） | 本次处理 |
|---|---|---|
| 11 玉拳少年 | `11_jade_fist_flat_top_boy_transparent_4096.png` | pending；未复制、未恢复 |
| 12 铁刀少年 | `12_iron_saber_flat_top_boy_transparent_4096.png` | pending；未复制、未恢复 |
| 13 风刃少女 | `13_short_hair_wind_blade_girl_transparent_4096.png` | pending；未复制、未恢复 |
| 16 金铃舞者 | `16_golden_bell_dancer_girl_transparent_4096.png` | pending；未复制、未恢复 |
| 18 沙海日轮少女 | `18_desert_sun_monk_girl_transparent_4096.png` | pending；未复制、未恢复 |
| 19 御兽少年 | `19_spirit_beast_tamer_boy_transparent_4096.png` | pending；未复制、未恢复 |
| 21 厨道童子 | `21_lidazui_hair_cook_boy_transparent_4096.png` | pending；未复制、未恢复 |
| 22 执刀小侍 | `22_lidazui_hair_waiter_saber_boy_transparent_4096.png` | pending；未复制、未恢复 |
| 道童重复别名 | `q_daoist_topright_character_full_uncropped_transparent_4096.png` | 缺失；不补副本，不计独立角色 |

## 尚未完成的角色美术

- 候选 11 位的本项目最终身份采用、与完整原版角色槽位的属性映射仍待做；现存阵容不自动等于原版全部角色覆盖。
- 15 位整体仍需脸型／年龄／体态差异矩阵及目标背景审查，部分透明边可见细微洋红残色；本次原样保留，没有用清边或裁切冒充新作。
- 人物朝向、待机、移动、放泡、困泡、营救、淘汰、复活、胜负、表情、持物和装扮挂点，未因本次静态库存而完成。未审计或复制对应动作集，不据历史目录数量推定可用动画。
- 选角／头像／房间／战斗的目标尺寸、角色相对地图比例、脚底锚点、遮挡、内存和加载性能仍需实际实现与运行核验。Alpha 包围框不是缩放合同，不允许据此改变原版相对尺度。
- image 项目关联章节目前只记录已采用四位。本次候选导入不是正式采用；候选转正时再同步实际使用位置，不提前把候选登记为运行时已复用。

完整游戏美术继续按 `ART_COMPLETION_CHECKLIST.md` 推进。本次可标完成的是“现存 15 张自有静态库存核验”和“11 张候选副本与逐图源记录”，不能把全角色、全动作或完整游戏美术标完成。

## 本次实际读取

- image 根 `AGENTS.md`；前次已实际读取的根 `README.md` 接手说明、`docs/QDAO_ART_DIRECTION.md` 与 `docs/WUXING_QITAN_HANDOFF.md` 人物／静态包／客户端边界段落继续适用。
- 本次完整读取现存 `q_daoist_character_pack_4096/README.md`（含最新四位项目关联）及 `manifest.json`，逐项比对包内所有 24 条目录声明和 15 张实际 PNG。
- 新项目 `README.md`、`docs/USER_REQUIREMENTS_LOCK_20261026.md` 固定边界，`docs/ART_COMPLETION_CHECKLIST.md` 库存／角色与验收条目，以及已采用道童的 `.source.json` 格式与证据边界。
- 本次检查的 `D:\AGENTS.md`、`D:\work\AGENTS.md`、新项目根／assets／assets/characters／docs 下 `AGENTS.md` 均未发现现存文件；未凭空继承 image 的共享 Git 流程给新项目。
