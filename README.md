# 灵葫大作战

正式游戏名采用 **《灵葫大作战》**，口号“灵葫聚友 · 泡泡争锋”。“灵葫”承接原创道家Q版角色与法器，“大作战”体现泡泡、走位、道具和多人竞技；命名记录见 [GAME_IDENTITY_20261028.md](docs/GAME_IDENTITY_20261028.md)。现有工程目录和GitHub仓库地址沿用，历史QQ堂研究、原始数据名与来源记录保持可追溯。

命名和新字标已保存至独立公开开发分支`codex/linghu-brand-20261028`，该固定小批71项远端测试及语法/基线构建通过，范围见 [BRAND_PUBLICATION_20261028.md](docs/BRAND_PUBLICATION_20261028.md)。其余新美术仍在本地生产，不能把此分支当作全部美术已上传。当前库存候选见 [护罩与仙驾](assets/items/surroundings/README.md)，角色新整腿/整臂仅静态候选与六相位缺件分析，完整动作未完成。

公开仓库：[luhailong-java/qqtang-daoist-remake](https://github.com/luhailong-java/qqtang-daoist-remake)。当前为开发中的完整工程与美术制作资料，尚未达到完整游戏全部美术完成及终验标准。

目标是承接腾讯《QQ堂》的玩法、规则、操作、流程及逐张地图几何，UI和人物改用我们自己的原创道家Q版设计。最新合同为 [USER_REQUIREMENTS_LOCK_20261026.md](docs/USER_REQUIREMENTS_LOCK_20261026.md)：原版地图尺寸、行列、格子、建筑占位、道路、障碍、出生点、碰撞和角色相对尺度不能自行更改。

本项目从零编写浏览器客户端和本地服务端。现已接入社区来源地图的原始三层、占地、出生点和地图人数限制，并用自有道家Q版候选素材替换部分地图。社区来源的腾讯原版身份、目标历史版本、完整规则与美术仍未通过终验，当前不是完整游戏成品。

## 运行方式

需要 **Node.js 22+**，无npm依赖。在项目目录运行：

```powershell
node scripts/serve.mjs
```

打开 <http://127.0.0.1:4387>。同一电脑可以在多个标签页建立独立本地身份、进入同一房间联机。席位上限随地图确定，例如中国城01为四人；界面的其余席位显示不适用。HTTP请求与SSE快照连接自有权威服务端，客户端发送操作，服务端处理移动、碰撞、糖泡和胜负。详细协议及权限见 [NETWORK_API.md](docs/NETWORK_API.md)。

身份保存在每标签的 `sessionStorage`；房间、会话和对局存于服务内存，重启清空。默认仅监听回环地址，不需要QQ账号或密码；局域网、互联网和持久账号未交付。关闭终端或Ctrl+C停止服务。本版必须通过HTTP运行，不能双击 `file://` 页面游玩。

`node scripts/build.mjs` 用于整理运行包；包内须包含服务端、启动脚本、客户端与当前采用资源，在包目录同样运行上述服务命令。旧离线入口、旧截图和旧压缩包不能作为本轮达标交付。

当前地图美术可在 <http://127.0.0.1:4387/maps.html> 按主题、名称或编号浏览。预览从真实源场景绘制新画候选，未制作的元素保留缺失提示；可切换占地检查，不把预览覆盖当成正式验收。

## 当前范围与未完成项

已有本地身份、频道／大厅、创建与加入房间、4×2八席、准备、队伍和配置、房间聊天、对局、结算回房等技术实现。已有普通竞技、比武、抢包山、热血足球、推箱子、合作探险六个规则分支；这些分支仍须逐项对照原版行为、参数与地图，不能以自定复活、速度、得分或波次填补资料缺口。商城只是本地试穿，没有Q币支付或真实商品交易。

旧 `15×13` 随机布局及 `courtyard/town/factory` 自定摆放不符合逐图还原要求。现已静态导出社区修改后客户端样本的377张map、381目录项与721元素，逐图重建字节哈希一致；样本的腾讯原始身份与目标版本仍未确认，未据此签署地图美术或机制已一致。每图必须核对原始ID／名称、来源、哈希、像素／格子规格、行列、分层、建筑／障碍／出生点与碰撞，再以同坐标新画法替换。未知项记“待核实”，不能用放大截图、重新摆箱或修改显示比例代替。见 [QQTANG_MAP_DIMENSION_EVIDENCE.md](docs/QQTANG_MAP_DIMENSION_EVIDENCE.md)。

人物采用image现有的金发带Q道童、月影少女、山岳守卫、莲花医者，显示名为道童、月影、山岳、莲花。四张身份原图保留，运行时使用可追溯的1024像素等比导出，解码内存由256MiB降为16MiB。山岳、莲花已有候选方向跑步／受击帧接入；道童、月影的新动作仍在逐方向制作。缺失动作使用明确的静态回退。外观与玩法属性分开，不因外观新增技能或改变碰撞；全部动作、脚底和地图相对尺度仍需终验。见 [OWN_CHARACTER_ADOPTION.md](docs/OWN_CHARACTER_ADOPTION.md)、[CHARACTER_MOTION_ADOPTION.md](docs/CHARACTER_MOTION_ADOPTION.md)。

地图已核验生产账为 [assets/maps/production-index.json](assets/maps/production-index.json)，区分源参考、原创候选、待制作和验收状态。2026-10-28新增在制稿的轻量快照另见 [ART_PRODUCTION_STATUS_20261028.json](docs/ART_PRODUCTION_STATUS_20261028.json)，在全量核验恢复前不冒充已验证运行清单。中国城01的17类候选已覆盖其339个场景对象；画布使用600×520逻辑尺寸、1200×1040物理像素，绘制密度不改变地图坐标。地图美术按当前地图按需解码。见 [SOURCE_MAP_ART_RENDERING.md](docs/SOURCE_MAP_ART_RENDERING.md)。UI已有窗框、按钮、16个语义图标及16种控件素材接入CSS；切片和状态不等于全部页面已验收。

二进制地图属性表另找到52项，合计773项；旧721项共享字段逐项零差异，先前27个未知编号的核心定义均找到。773项均已有首轮候选，比例／接缝／透明／锚点与运行验收继续，accepted仍为0；未直接覆盖旧运行数据，两项非序列化字段保持未知。见 [二进制补充证据](docs/BINARY_MAP_PROPERTY_SUPPLEMENT_20261028.md)。

物品来源目录现有2,945条记录；其中32个消耗道具、80个技能书已有首轮自有风格图标，见 [assets/items/README.md](assets/items/README.md)及`assets/items/skills/`。20个源角色槽位已有20个自有静态身份映射，运行层仍为四位；角色动作、变身、怪物、特效、其余装扮与完整UI继续制作。当前按人类授权暂停本机重型验收，远端生图继续；状态见 [LOCAL_RESOURCE_WINDOW_20261028.md](docs/LOCAL_RESOURCE_WINDOW_20261028.md)。

四人物、六模式技术分支和已有流程不等于原版全角色、全模式、全部地图／关卡或机制精确一致。旧“道趣泡泡”单人稿、v0.2原版四角色重绘和自定义地图试稿均不能作为最新要求已完成的证据。

## 文件与来源

| 路径 | 用途 |
|---|---|
| `src/app.js`、`src/styles.css` | 大厅、八席房间、对局界面与显示适配 |
| `src/game.js` | 规则引擎；待按原版机制及逐图数据持续校核 |
| `server/app.mjs`、`scripts/serve.mjs` | 自有本地HTTP／SSE服务与启动入口 |
| `assets/art.json` | 当前素材入口、源矩形与使用范围，以实际接入清单为准 |
| `assets/characters/daoist-child.png`、`moon-shadow.png`、`mountain-guardian.png`、`lotus-healer.png` | image四自有静态人物原样复制；各有`.source.json` |
| `assets/ui/qdao-ui-kit-v3.png` | 新生成UI皮肤母图及逐图记录；切片与接入按当前制作账推进 |
| `references/image/` | 两张UI风格参考副本与根规则、策略、配置快照 |
| `references/qqtang-original/` | 历史截图与资料来源，负责功能、结构和尺度取证，不直接作运行时素材 |
| `docs/USER_REQUIREMENTS_LOCK_20261026.md` | 最新需求的固定边界 |
| `docs/UI_SPEC.md`、`docs/REFERENCE_AUDIT.md` | 当前合同、素材使用与证据边界 |
| `docs/VALIDATION.md` | 当前版本验证状态、未完成项及限制，由最终验收更新 |
| `docs/ART_COMPLETION_CHECKLIST.md` | 完整游戏美术的complete／pending／blocked清单，不以六模式小样替代全范围 |

人物直接复用与风格参考分别登记。自有四人物来自image的 `q_daoist_character_pack_4096/`；4096是历史兼容导出画布，不等于原生4K生成细节。本次复用不产生新的模型生成，缺失的旧图模型／质量证据保持未确认，不按当前配置回填。

风格来自实际查看的 `designs/mail-ui-v1/01-mail-event.png` 与 `designs/team-ui-v2/team-ui-v2.png`：玉绿、象牙米白纸绢、暖金细边、圆润云纹、高清手绘和大头短身。两张风格副本不作运行时素材；直接复用的人物是另行列出的四张PNG。新项目实际人物采用路径及每张来源链以 `docs/REFERENCE_AUDIT.md` 为准。

## 仓库对应与验证

本地项目为 `D:\work\qqtang-ui`，image参考仓库为 `D:\work\image`。用户于2026-10-27授权公开上传，已创建独立Git仓库与公开远端 [luhailong-java/qqtang-daoist-remake](https://github.com/luhailong-java/qqtang-daoist-remake)；首批文件范围和核验说明见 [GITHUB_PUBLICATION.md](docs/GITHUB_PUBLICATION.md)。原版研究中的社区工程只是线索，没有克隆其工程。

image的历史GitHub／素材来源为 [luhailong-cpp/image](https://github.com/luhailong-cpp/image)，当前本地origin为 [Azure Repos image](https://luyuacpp.visualstudio.com/image/_git/image)，依据本地文档和只读配置核对，未在线验证同步；二者不是本项目远端。关联记录在image的 `designs/qqtang-ui-20261026/README.md` 与 `q_daoist_character_pack_4096/README.md` 的“项目关联”。

image要求的 `qdao_ui_redesign_v5/UI_SPEC.md` 当前缺失，未从旧Git恢复；已读现存根规则、邮件与组队专项说明。每次新生图前重读适用规则和配置，透明处理、裁显、缩放与模型生成分别记录。

`node --test tests/*.test.mjs` 执行规则、联网、源文件解析、源地图运行接口、地图美术和来源清单检查。测试仅确认其断言范围，不能替代原版认证和实机终验。2026-10-28已实际打开当前登录页，旧浏览器禁用已解除；此后本机重型验收按人类授权暂停，尚未取得时段交还。最新测试结果见 [VALIDATION.md](docs/VALIDATION.md)，完整美术缺口见制作账。历史v0.2截图和压缩包不代表当前版本。
