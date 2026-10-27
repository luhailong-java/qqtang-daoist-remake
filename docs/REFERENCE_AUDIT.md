# QQ堂·道家Q版重制 · 参考来源与采用核查

核实日期：2026-10-26。新项目本地目录：`D:\work\qqtang-ui`；美术参考仓库：`D:\work\image`。

用户最新要求是腾讯已停运《QQ堂》原版玩法、机制、操作、流程与逐图几何保持一致，UI和人物采用我们自己的原创道家Q版设计，见 `docs/USER_REQUIREMENTS_LOCK_20261026.md`。用户没有现成客户端、源码或GitHub，已选择从零编写自己的客户端与本地服务端，不接腾讯原协议。当前名为“QQ堂·道家Q版重制”，没有克隆第三方工程、初始化Git或设置远端。旧“道趣泡泡”方案、原版四角色重绘、自定15×13随机图和旧验证均不能作为最新合同已完成的证据。社区发布ZIP已经协调者核对摘要并静态导出地图数据，身份仍为社区修改后客户端，不能冒称腾讯原始安装包或已完成原版地图接入／美术验收。

## 实际读取的文件

以下路径均相对 `image` 仓库根目录；本记录保留阅读范围，不能替代相应文件的当前内容。

| 文件 | 本次用途与读取范围 |
|---|---|
| `AGENTS.md` | 全文；优先参考图、道家 Q 版风格、逐图来源、素材保留及共享 Git 边界 |
| `README.md` | 全文；接手说明、交接入口、LFS 要求及仓库对应关系 |
| `docs/WUXING_QITAN_HANDOFF.md` | 全文；区分历史交付、当前采用和客户端／线上验收边界 |
| `docs/QDAO_ART_DIRECTION.md` | 全文；人物比例、配色、画法及原创外观要求 |
| `docs/IMAGE_MODEL_POLICY.md` | 全文；内置入口优先、配置目标与实际参数／返回证据分开记录 |
| `config/image-generation.json` | 全文；读取当次生成配置目标；不据此认定实际返回型号 |
| `designs/README.md` | 全文；核对确认成图入口与历史路径说明 |
| `designs/mail-ui-v1/README.md` | 现存正文至本地预览与验收部分；了解整屏设计与原生交互实现分离 |
| `designs/mail-ui-v1/UI_SPEC.md` | 全文；纸面、主次按钮、装饰、原生文字和响应布局原则 |
| `designs/team-ui-v2/README.md` | 全文；双栏层级、成员状态、字号、间距与交互边界 |
| `designs/team-ui-v2/unity-slices/README.md` | 全文；透明通道、九宫格、原生文字和资源规格说明 |
| `designs/team-ui-v2/source/generation.json` | 全文；组队主参考原始生成来源与尺寸证据 |
| `designs/team-ui-v2/exact-20261017/visual-difference-list.json` | 全文；确认该次加工记录仍为 `completed=false` |
| `designs/team-ui-v2/exact-20261017/source-record.json` | 文件前 95 行；确认此批为既有原稿加工，未作新模型生成；未将其当作完成验收 |
| `designs/team-ui-v2/asset-manifest.json` | 文件前 75 行；核对现存交互预览的素材来源表达方式 |
| `designs/gameplay-ui/README.md` | 全文；任务、背包、活动和帮会成图的交付与业务边界 |
| `designs/battle-patrol-jewelry-ui-20261021/README.md` | 全文；同风格战斗页与逐图记录方式 |
| `designs/ui-completion-20261021/README.md` | 全文；选服、排行、活动及 HUD 整屏交付说明 |
| `designs/ui-completion-20261021/requirements/07-team-hud.md` | 已查阅功能、现状入口、共用栏和组队行为部分；仅辨别业务归属，不作为本项目业务合同 |
| `designs/main-hud-20261021/ARTWORK.md` | 全文；图标透明边距、来源链、原生尺寸和派生处理说明 |
| `docs/AI_DESIGN_TOOLS_SETUP.md` | 文件前 90 行；移机、内置入口、外部 API 凭证与依赖边界 |

新建项目开始时没有既存的 `AGENTS.md`、`README.md`、需求、技术或资源合同可供继承；本次项目文档由制作流程另行建立。已读取前稿 `README.md` 和 `docs/UI_SPEC.md`，纠正后重新编写这两份当前合同。核查时 `D:\AGENTS.md` 与 `D:\work\AGENTS.md` 均未发现，未从不存在的文件推断规则。

本轮纠正还实际全文读取 `docs/QQTANG_ORIGINAL_RESEARCH.md`、`docs/NETWORK_API.md` 和 `src/game.js`，核对证据等级、自有协议及六个模式的真实实现；读取 `assets/art.json` 与 `assets/atlas.json` 核对资源采用索引，并解析 `references/qqtang-original/source.json` 的来源 URL、哈希、下载与实看字段。原版研究是对历史转存资料的核查，没有取得可读的腾讯官方原版技术规范；不可读官方链接不能算已读官方正文。

最新修订又实际读取 `docs/USER_REQUIREMENTS_LOCK_20261026.md`、`docs/OWN_CHARACTER_SOURCE_CANDIDATES.md`、`docs/QQTANG_MAP_DIMENSION_EVIDENCE.md` 及image的 `q_daoist_character_pack_4096/README.md`。当前不采用先前“保留腾讯四角色身份／自行定义地图与参数”的合同；原版机制和数据未知时须继续取证，人物采用自有身份，外观与玩法属性分开映射。

## 实际图片核查

已实际查看以下两张完整原图。通过 PNG 文件签名、IHDR 尺寸和完整文件 SHA256 核实，真实图片字节已在本机，不是 Git LFS 指针。

| image 内相对路径 | 尺寸 | SHA256 |
|---|---|---|
| `designs/mail-ui-v1/01-mail-event.png` | 1931×814 | `3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2` |
| `designs/team-ui-v2/team-ui-v2.png` | 1931×814 | `5fab5229de7030ac48172cfa39bb45f612a545cee0dba6303ae6f2dcfdf38750` |

承接玉绿、青绿、象牙米白纸绢、暖金细边、圆润云纹、清晰手绘明暗与大头短身人物比例。文字与可交互状态由网页实现，不能把完整效果图中的按钮当作已实现交互。

开工检索时未发现已关联 QQ堂或泡泡竞技项目的素材目录；现存组队、战斗和 HUD 业务属于“五行奇谈”MMO，不向本项目移植其名称、五人配队、权威快照协议或回合战斗规则。本次已新增独立关联登记。

## 原版资料的当前用途

`references/qqtang-original/` 保存本轮真实下载的历史合作专区、媒体转存和社区留存图，不是当前腾讯官方发布，也不是从腾讯原客户端提取的资产。逐图来源、SHA256、原生尺寸、下载时间与实看观察在 `source.json`，历史资料的版本与精确性边界在 `docs/QQTANG_ORIGINAL_RESEARCH.md`。

本次文档复核实际查看了 `eight-seat-room-article.jpg` 与毛毛、阿莎、悟空、泰坦四张 `*-community-reference.png`：八席图可见4×2编号席位、右侧地图／角色区域，但有媒体裁剪和标注；四角色分别可见酒红短发与半眯眼、金棕短发、猴耳橙色尖发与头箍长棍、蓝青头盔与中央竖鳍。配对名字图及其他原版参考的实看记录读取 `source.json`，不凭装扮示例替代基础身份。

上述四角色图片的实看是历史取证过程，不再约束新人物脸型、发型或服装。最新要求明确使用自己的原创身份，不能继续把毛毛、阿莎、悟空、泰坦重绘当正式人物。原版截图仍供功能、建筑结构、布局与尺度核对，不直接作运行时素材；历史截图存在裁切／跨版本问题，不能代替逐图原始数据。本轮已有六模式分支也不等于原版全部模式、全部地图或全部关卡。

## 自有人物直接复用核查

2026-10-26实际查看四张自有人物PNG，并读取签名、IHDR及完整SHA256。下表源文件均为image仓库相对路径；目标为新项目相对路径。四目标文件已落盘，本次逐字节比较全部一致，属于**直接复用／原样复制**，没有新模型调用、离线缩放或改色。

| 自有身份 | image内源路径 | 新项目实际使用路径 | 源与目标相同的SHA256 |
|---|---|---|---|
| 金发带Q道童 | `q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png` | `assets/characters/daoist-child.png` | `0e68fc89ad535b6f93fd3e6a724d3499de45d8c105d32902506e673d358d0155` |
| 月影少女 | `q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png` | `assets/characters/moon-shadow.png` | `8ccc7e9118ed1ca608a407687e5a76cf392b1f694ef7737ccc28536caae84bfc` |
| 山岳守卫 | `q_daoist_character_pack_4096/04_mountain_guardian_boy_transparent_4096.png` | `assets/characters/mountain-guardian.png` | `371bb4d303cc5bde21e73eb4ddba277aebee06b5ad65d81301ea828804263521` |
| 莲花医者 | `q_daoist_character_pack_4096/03_lotus_healer_girl_transparent_4096.png` | `assets/characters/lotus-healer.png` | `eac7887f4c24cfa55da236ae0ddb915ee2f6e14bad135c7858ec0ec99f8d9354` |

四图为4096×4096 RGBA兼容导出画布，不是本次新生成，也不声称原生4K细节。历史逐图模型、质量、原生尺寸回执缺失项见候选核查，保持未确认，不用当前配置补写。四图旁的`.source.json`及 `docs/OWN_CHARACTER_ADOPTION.md`已落盘；`assets/art.json`前四项与`src/art.js`均绑定独立PNG，登录选角、头像、房间及对战共用入口，显示名道童／月影／山岳／莲花。旧内部ID仅兼容槽位，不再作为原版人物身份。原版四角色图集0–3已停用，怪物4／包子5暂留。

接入采用透明内容矩形等比裁显，不重新定义原版角色尺度或碰撞；最终客户端与目标背景边缘、脚底、动作和整体验收仍待当前版本实测，复制和静态绑定成功不等于验收完成。

## 社区地图样本取证进展

已读更新后的 `QQTANG_MAP_DIMENSION_EVIDENCE.md`与 `references/qqtang-map-data/index.json`：社区ZIP为288,298,460字节，SHA256 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`；导出377张map、381目录项及721元素，全部map由JSON重建后SHA256／MD5与样本一致。327张为15×13、50张有其他实际尺寸；50项目录尺寸与文件头不同、22图有未定义元素ID、10张文件未列目录，`rand.map`占位无实物。

这是社区样本的无损静态数据证据，源类型为`community-patched-client-data`，腾讯原件未改动性仍为未确认。导出清单不能作为原版几何／碰撞运行或全主题自有美术已通过；不能因为v3的默认行列与试稿偶同，就把随机摆放改记原版图。未执行包内Python、EXE或DLL，贴图／锚点与格距的原版对应仍须逐项核查。

## 缺失与冲突处理

- 根规则指向的 `qdao_ui_redesign_v5/UI_SPEC.md` 当前实际缺失；没有从旧 Git、快照或已删除目录恢复。依据当前明确指令、现存根规则、两张原图和上述专项规范推进。
- `designs/README.md` 中“旧邮件 PNG 缺失”的说明与当前文件不符；本次以实际存在且已核验的指定 PNG 为准，没有擅自改用其他图片。
- `designs/team-ui-v2/UI_SPEC.md`、`designs/team-ui-v2/exact-20261017/README.md` 与 `designs/main-hud-20261021/README.md` 当前未发现；分别读取现存 README／来源记录／`ARTWORK.md`，不声称缺失文件已读。
- 组队 2026-10-17 加工记录尚未完成运行验收；旧五行奇谈的浏览器或 Unity 验收均不代表本项目已验证。

## 仓库地址与证据边界

| 对象 | 地址／状态 | 本次证据 |
|---|---|---|
| QQ堂·道家Q版重制 GitHub | 未提供，待确认 | 用户明确表示没有 GitHub 地址；本次未克隆第三方工程、未初始化 Git |
| image 历史 GitHub／素材来源 | <https://github.com/luhailong-cpp/image> | image 根 `README.md` 的“仓库对应关系”；本次未对该远端在线核验 |
| image 当前本地 origin | <https://luyuacpp.visualstudio.com/image/_git/image> | 本次只读 `git remote -v`，fetch 与 push 相同；未核验远端最新提交和同步状态 |

image的地址不能当作QQ堂重制项目远端。原版研究提及的社区仓库是资料线索，未克隆其工程；社区ZIP数据核查与游戏运行代码采用需分别记录，不能由本说明推定。没有操作image共享Git的HEAD、index、refs、提交或推送。

## 本次素材关联与实现位置

关联类型分别为**风格参考**与**人物直接复用**。`references/image/`内两张风格副本与规则快照不作运行时游戏资产；`assets/characters/`中的四张自有人物由image原样复制，是直接复用资产。不能再笼统声称“运行时无直接复用image图片”。当前采用状态如下：

| 新项目内路径 | 用途 |
|---|---|
| `assets/characters/daoist-child.png`、`moon-shadow.png`、`mountain-guardian.png`、`lotus-healer.png` | 四张image自有静态人物，直接复用；具体源路径和哈希见上表 |
| `assets/qqtang-characters-v2.png` | 历史1536×1024 RGBA图集；原版四角色0–3已停用，当前仅怪物4、包子5暂用 |
| `assets/qqtang-world-v2.png` | 1672×941 RGB气氛试稿，不能作为原版逐图几何或建筑占位已完成的证据 |
| `assets/game-atlas.png` | 旧试稿1774×887 RGBA，仅采用索引3–7糖泡、石块、木箱、地砖和增益葫芦；旧角色0–2停用 |
| `assets/art.json`、`src/art.js` | 当前素材入口、透明内容源矩形和采用范围，以最终同步清单为准 |
| `assets/ui/qdao-ui-kit-v3.png`及旁置generation记录 | 新生成UI皮肤母图；切片、九宫格和状态接入按制作账推进，不等于全UI已完成 |
| `src/app.js` | 大厅、房间及界面状态交互 |
| `src/game.js` | 六个独立模式的权威状态与规则引擎 |
| `src/styles.css` | 玉绿、米白、暖金控件层级和分辨率适配 |
| `server/app.mjs`、`scripts/serve.mjs` | 从零实现的本地HTTP／SSE服务与启动入口 |
| `references/image/01-mail-event.png`、`references/image/team-ui-v2.png` | 为接手移机保留的两张风格主参考副本 |
| `references/image/AGENTS.md`、`references/image/IMAGE_MODEL_POLICY.md`、`references/image/image-generation.config-snapshot.json` | 本轮采用规则与配置的文字快照；不代替新图生成前重新核对适用规则 |

历史试稿哈希保留：旧原版四角色图集 `cdaa2e278b285e99db0f284e2c060e592a33e29fe6df38a78ab4ef29b517c36a`；气氛图 `df713082592761fab54e0ff29c55094dda780064857b9a5bdc3bb5b8fee2c41f`；物件图集 `8fcae7cf975436184c59e9b7fa184b1f4495c78e9c19382b01be10c916336bf6`。哈希证明当时字节身份，不代表旧稿获得最新采用或终验。新图实际生成入口、提交参数、返回证据及处理按逐图记录，未披露的型号／质量保持未确认。

历史12项引擎、8项服务端及旧浏览器结果仅证明当时试稿技术流程，不能作为最新原版几何、机制或自有人物终验。本轮浏览器入口返回`Local browser use is disabled in Work settings`，当前无法做实机终验；可继续素材和静态核查。最终状态统一读取 `docs/VALIDATION.md`；完整美术缺口见 `docs/ART_COMPLETION_CHECKLIST.md`。默认本机回环地址、内存状态重启清空、每标签身份用sessionStorage；没有腾讯协议兼容、持久账号或互联网发布的验收证据。

旧 `hero-panorama.png`、旧预览与旧压缩包不再作为当前交付依赖，其清理或保留由最终采用清单决定。本版需要 `node scripts/serve.mjs` 启动HTTP服务，不能再按旧 `file://` 双击离线入口交付。

image关联登记为 `designs/qqtang-ui-20261026/README.md`（风格和总体关联）及 `q_daoist_character_pack_4096/README.md` 的本项目关联（四人物直接复用）。仅更新文字，不改其他项目或共享Git。
