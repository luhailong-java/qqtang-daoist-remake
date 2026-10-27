# 自有道家 Q 版人物已接入记录

2026-10-26。依据 `USER_REQUIREMENTS_LOCK_20261026.md`，人物使用我们自己的名字、脸型、发型、服装、轮廓和身份。此轮实际将四张 image 现存透明 PNG 复制至运行素材目录并接入；没有新生图、AI 修图、缩放导出或像素改写，没有改地图数据与对战规则。

## 采用映射

内部旧 ID 仅用于存档及网络协议兼容，不再作为展示姓名。既有四槽位的容量、威力、速度及上限保持原值；原创外观与玩法数值分开。

| 展示名／身份 | 兼容槽位 ID | 新项目正式 PNG | image 内源 PNG |
|---|---|---|---|
| 道童／金发带道童 | `maomao` | `assets/characters/daoist-child.png` | `q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png` |
| 月影／月影少女 | `asha` | `assets/characters/moon-shadow.png` | `q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png` |
| 山岳／山岳守卫 | `wukong` | `assets/characters/mountain-guardian.png` | `q_daoist_character_pack_4096/04_mountain_guardian_boy_transparent_4096.png` |
| 莲花／莲花医者 | `titan` | `assets/characters/lotus-healer.png` | `q_daoist_character_pack_4096/03_lotus_healer_girl_transparent_4096.png` |

四个目标文件均与对应源文件逐字节 SHA-256 一致。逐图源记录为同路径的 `<文件名>.source.json`，含哈希、源路径、4096×4096 画布、RGBA、Alpha 极值及包围框。

## 实际接入

- `src/game.js` 的 `CHARACTERS` 改为四位自有人物名字、身份及外观描述；默认 AI 名称同样改为自有名字。其余数值、地图、逻辑不改。
- `assets/art.json` 前四项使用四张独立 PNG。`src/art.js` 现支持独立文件和共享图集混用；每张按现有 Alpha 包围框作 SVG／Canvas 等比例裁显。源文件没有离线裁切或重采样，显示槽位大小不变。
- 登录选角、角色页、房间、头像、对战与结算使用同一素材入口。用户界面不再显示“原版角色重绘”，AI 显示名从自有角色元数据取得，不沿用服务器旧会话里的原版名。
- `assets/qqtang-characters-v2.png` 的四个旧角色分区（索引0–3）停止运行时引用；仅怪物、包子分区（索引4–5）暂留。旧图的历史生成记录没有篡改为本次自有角色来源。
- 角色页文案明确为自有身份与属性槽位映射，不把原创角色当作原版角色换衣服。

## 图片质量与来源边界

四张均完整解码为4096×4096 RGBA，含0–255真实Alpha。4096是历史兼容导出画布，不是本次或历史已确认的原生4K细节。现存人物包README仅称原生图“通常1254×1254”，四张逐图原生尺寸、模型、质量回执缺失，均保留未确认，未用当前默认配置回填旧图来源。

已经实际查看四张源图和两张指定主参考，人物符合大头短身、手绘玉绿／米白／暖金方向，身份彼此不同。细微洋红边沿沿用原图，未擅自去边或重绘。本轮为静态人物接入，不是八方向动画、战斗动作或全游戏美术全部完成。

## 读取与核对

已实际阅读最新需求锁定、`OWN_CHARACTER_SOURCE_CANDIDATES.md`、image根`AGENTS.md`、人物包README及manifest根字段、美术定调、邮件现存UI规范；已实际查看邮件和组队主参考及四张原图。根规则指定的`qdao_ui_redesign_v5/UI_SPEC.md`仍缺失，本次未恢复。

本轮没有改 image 仓库文件、共享 Git、地图、碰撞、出生点或玩法参数。独立 PNG 的源/目标哈希、透明通道与新运行引用已完成本地核对；角色页、头像及对战的最终浏览器显示验证由项目总验收记录补充。
