# 原创道家 Q 版角色候选来源核验

核实日期：2026-10-26。范围：只读核验本机 `D:\work\image` 现存素材。本次未生成图片、未复制素材、未修改运行代码，也未操作 image 的共享 Git。

## 本次边界

人物使用我们自己的道家 Q 版身份、发型、服装和法器，不按腾讯《QQ堂》的毛毛、阿莎、悟空、泰坦重绘。玩法与地图的尺寸、格子、建筑占位、碰撞及规则由本项目另行取证与实施；人物替换不能改变这些数据。

下列“平衡、灵巧、威力、容量”只对应现有四个展示槽位，不制定数值，不添加职业技能，也不据外观推定原版属性。

## 推荐四位

四张均来自现存 `q_daoist_character_pack_4096/`，实际查看了 PNG，并与两张指定 UI 主参考比对。整体为大头短身、细腻手绘、米白与暖金材质，人物通过发型、眉眼、配色、轮廓与道具区分。该选择是当前可用来源候选，不冒称已获得本项目最终选角验收。

| 展示槽位 | 现有名字与身份 | image 内现存 PNG（仓库相对路径） | 实际观察与采用证据 |
|---|---|---|---|
| 平衡 | 金发带 Q 道童 | `q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png` | 短刺棕发、金发带、圆眼笑脸、玉绿背心、米白袍裤、太极金葫芦。人物包 README 列为正式透明输出；manifest 标记 `approved Q hero compatibility export`。与邮件、组队主参考中的自有道童身份一致。 |
| 灵巧 | 月影少女 | `q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png` | 银色短发、紫瞳、月形发饰、蓝色围巾、双弯刃，与道童轮廓和服装不同。人物包 README 与 manifest 的 07 条目可对应；现存动作 manifest 另记录 `formalAccepted: true`，范围仅为该动作包离线美术交付。 |
| 威力 | 山岳守卫 | `q_daoist_character_pack_4096/04_mountain_guardian_boy_transparent_4096.png` | 棕发小马尾、较浓眉、额心金饰、木珠、金绿甲衣、环首法杖和圆盾。人物包 README 与 manifest 的 04 条目可对应；2026-10-01 动作 TASK 明确把这张 PNG 指为身份画像，IDENTITY_NOTES 与实际图一致，当前 README/STATUS 记录其动作离线完成。 |
| 容量 | 莲花医者 | `q_daoist_character_pack_4096/03_lotus_healer_girl_transparent_4096.png` | 高束棕发、莲花金冠与粉穗、粉白长衣、莲灯和药瓶。人物包 README 与 manifest 的 03 条目可对应。现存动作交接仍标候选待用户及客户端审查，不能把动作状态算作已接入游戏。 |

上述静态 PNG 可在用户已授权的自有素材复用范围内复制到新项目作选角、头像或静态角色展示。透明图技术可用不代表动作、锚点、脚底、碰撞与客户端适配已经验收。实际复制与接入位置待本项目实施记录，本次没有导入。

## 实测文件规格与 SHA-256

使用本机 Pillow 逐张完整解码。四张的 PNG 签名均为 `89504e470d0a1a0a`，文件不是 Git LFS 指针；均为 **4096×4096、RGBA，Alpha 极值 0–255**，包含真实透明像素。当前 SHA、画布与 Alpha 包围框全部与人物包现存 manifest 一致。包围框采用左、上、右开、下开坐标。

| ID | 文件字节数 | Alpha > 0 包围框 | 当前 SHA-256 |
|---|---:|---|---|
| 00 | 6,938,313 | `[783,239,3309,3861]` | `0e68fc89ad535b6f93fd3e6a724d3499de45d8c105d32902506e673d358d0155` |
| 07 | 8,412,923 | `[499,240,3594,3859]` | `8ccc7e9118ed1ca608a407687e5a76cf392b1f694ef7737ccc28536caae84bfc` |
| 04 | 8,601,316 | `[649,240,3444,3859]` | `371bb4d303cc5bde21e73eb4ddba277aebee06b5ad65d81301ea828804263521` |
| 03 | 9,081,265 | `[570,240,3526,3859]` | `eac7887f4c24cfa55da236ae0ddb915ee2f6e14bad135c7858ec0ec99f8d9354` |

**原生尺寸与模型来源的边界：** 4096 是导出兼容画布，不是原生 4K 生成细节。人物包 README 记载原生图“通常 1254×1254”，并经色键清理、脚底对齐和等比导出；由于下列逐图原始记录不在当前磁盘，不能据“通常”把四张逐图原生尺寸确认为 1254。四张逐图实际生成型号、质量、提交参数及返回值均未确认。本次没有新生图，不套用当前配置给旧图补记实际型号。

manifest 为 00 指向 `qdao_asset_refresh_v6/hero_compat_manifest.json`，03/04/07 指向人物包 `records/<角色文件 stem>.json`；上述记录路径实查缺失。03/04/07 的 manifest 方法仅能确认历史文字记录为 `individual built-in image_gen redraw + skill cleanup`，不能替代缺失的逐图模型回执。

## 实际读取与查看

已读取的关键文字：

- image 根 `AGENTS.md`、`README.md` 的接手与当前入口说明。
- `docs/QDAO_ART_DIRECTION.md`；`docs/WUXING_QITAN_HANDOFF.md` 的接手入口、人物 v9 取代 v6、静态人物、风格及尺寸、客户端边界段落。
- `q_daoist_character_pack_4096/README.md`、`manifest.json` 的根字段和四个候选条目。
- `qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy/` 下 `TASK.md`、`README.md`、`IDENTITY_NOTES.md`、`STATUS.md`。
- 03 的 `MERGE_HANDOFF.md` 中当前状态、预览来源、客户端边界段落；00/03/07 的动作 manifest 状态与顶层字段。未把巨型逐帧清单读取声称为全量动作验收。

已实际查看的图片：

- `designs/mail-ui-v1/01-mail-event.png`
- `designs/team-ui-v2/team-ui-v2.png`
- 本文四张候选 PNG。

## 缺失与待核实

- `qdao_character_diversity_v9/` 与 `qdao_festival_refinement_20260910/` 当前缺失。交接文档称 v9 人物及节庆验收取代旧 v6，但本机无法核实其完整当前采用链。本文只证明四张现存 PNG 的身份、可解码性与现存 manifest 一致，不宣称恢复了这些后续版本。
- 人物包 `records/` 和 00 的兼容来源 manifest 当前缺失。未从 Git、旧快照或已删除目录补回。
- `qdao_original_roster_v14_hd/README.md` 与 `action-remake-20261001/README.md` 当前缺失；不能凭目录名把所有动作统一称为正式已验收。
- 静态包 README 和 manifest 历史上列 24 张；本机该目录当前只见 15 张 PNG。本文只使用实际存在且已核验的四张，不据旧清单宣称 24 张齐全。
- 四张画面个别透明轮廓可见细微洋红边缘，缩小显示时需在新项目目标背景上再做视觉核验。未对原素材改色、去边或 AI 修图。
- 完整逐图原生尺寸、实际模型质量证据，以及新项目最终选角、目标显示尺寸、动作与客户端验收仍待后续实施。当前不需要新增付费路线。
