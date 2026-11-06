# QQ堂原版地图几何证据与缺口

核实日期：2026-10-26。范围：只读核对公开资料和源码，不下载或运行 EXE、不克隆社区工程、不修改游戏代码或共享 Git。

## 当前结论

用户要求以腾讯已下线《QQ堂》的玩法、地图结构和地图尺寸为准，UI、人物及地图表面美术换为本项目自己的道家 Q 版风格。这里的“尺寸相同”包括行列数、格距、逻辑像素、建筑占地、障碍、碰撞、出生点及特殊格坐标；不能仅让两张截图看起来相似。

**已取得并核验社区 v1.3.4 修改后客户端中的 377 张地图数据；尚未确认它们是未改动的腾讯原版文件，尚不能签署任何一张重制地图“与腾讯原版完全一致”。** 本任务自行编写的只读解析器已完整读取 377 张 `.map`，保留全部三层、坐标表和逐文件哈希；没有执行包内 Python、EXE 或 DLL。数据、来源和差异见 `../references/qqtang-map-data/index.json`。

已读的社区恢复项目提供了可追踪的逆向解析依据：其竞技 `.map` 解析器的 v3 分支使用 15 列 × 13 行，v4 分支从文件头读取宽高，战斗格距常量为 40 像素。本次实测 188 张为 v3、189 张为 v4；327 张为 15×13，另 50 张有 40×40、40×17、20×30 等宽高，**不能把所有地图统一设为 15×13**。40 像素仍是社区实现依据，未升级为腾讯官方规格。条件成立时，v3 逻辑格区可计算为 600×520 像素；该乘积不是已核实的整屏分辨率、地图美术外框尺寸或任意具体地图验收值。

本地已有 courtyard、town、factory 三张 15×13 自定义试稿不具有原图、原文件、原地图 ID 和逐格映射证明。它们只能保留为试稿，不能作为此次原版地图交付或尺寸证据。截图文件的 620×465、600×450 等尺寸也不能作为原游戏画布或格距。

## 已实际阅读的本地资料

- `docs/QQTANG_ORIGINAL_RESEARCH.md`：记录官方站点访问缺口、历史 UI 参考及社区来源的性质；其内容没有给出经过原文件验证的地图尺寸。
- `references/qqtang-original/source.json`：历史参考图文件、来源、尺寸和哈希记录；这些图有跨版本、裁切、水印和标注差异，不能替代逻辑地图数据。

## 证据等级与固定版本

主要技术资料来自 [kuuhaku1314/qqtang](https://github.com/kuuhaku1314/qqtang)，是项目作者对其自身恢复实现的一手资料，**不是腾讯公开的原始源码**。核对时固定到提交 [`4b3a245fd985cabd4abd68ade6c282cc163d9edb`](https://github.com/kuuhaku1314/qqtang/commit/4b3a245fd985cabd4abd68ade6c282cc163d9edb)；后续 `main` 更新不能自动改变本次结论。

| 编号 | 可核验事实 | 直接来源与行范围 | 使用边界 |
|---|---|---|---|
| E01 | 仓库提供恢复服务端、协议/规则实现、兼容补丁和构建脚本；原客户端不纳入仓库，原客户端也不属于其源码许可范围。 | [README-DEV.md L1–14](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/README-DEV.md#L1-L14) | 不能把仓库 clone 或源码可读当成已取得原客户端或原地图。 |
| E02 | 兼容说明要求自行放入原客户端，写明目标可执行文件版本为 `5.2.1.201`。 | [client/original/README.md L1–18](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/client/original/README.md#L1-L18) | 这是社区补丁兼容版本；本项目用户尚未指定历史版本，不能默认所有年代地图都与它一致。 |
| E03 | 地图目录从客户端根的 `map` 读取，目录索引文件为 `mapDesc.py`，按 GBK 解码；元素定义来自 `object/mapElem/mapElem.py`。 | [catalog.go L340–375](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L340-L375) | 需取得索引、元素定义与实际 `.map` 文件，名称列表自身不是布局。 |
| E04 | 解析器按索引对应文件读取 `.map` 字节，并计算地图文件 MD5；规则编号来自 bytes `[4,8)` 的小端 uint32。 | [catalog.go L476–501](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L476-L501) | 此处只有算法，没有本项目实际原图文件的 MD5。不得填造哈希或凭目录名认定模式。 |
| E05 | 文件版本读取 bytes `[0,4)`，小端 uint32；v3 使用 12 字节头、15 列 × 13 行默认几何；v4 使用 20 字节头，宽为 bytes `[12,16)`、高为 bytes `[16,20)` 的小端 uint32。其余版本报错。 | [catalog.go L535–577](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L535-L577) | v3 的 15×13 是该逆向解析器的分支规则，不是具体地图的原件证明。v4 必须逐文件读取，不能强制 15×13。 |
| E06 | 解析器假定 3 层 tile 数据，每格每层 4 字节；墙内物品表偏移为 `headerSize + 3 × width × height × 4`。 | [catalog.go L535–552](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L535-L552) | 分层数据需要完整保留，不能只输出一张扁平缩放图。 |
| E07 | 墙内物品规则后依次解析隐藏物品格、出生组 A、出生组 B、目标格；若有未解析尾字节则报错。 | [catalog.go L497–524](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L497-L524) | 不能按空地猜出生点或目标点；需要保留文件中的顺序和坐标。 |
| E08 | 坐标表先读取小端 uint32 个数，每项 4 字节，先小端 uint16 行、后小端 uint16 列，并校验边界和重复项。 | [catalog.go L636–660](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L636-L660) | 数据导入时需保留 row/col 顺序，不可将 x/y 直接互换。 |
| E09 | 碰撞投影读取前两层 tile，每层 `width × height × 4` 字节，以 `row × width + col` 索引；每格读小端 32 位数据后转有符号值。 | [competitive_battlefield.go L201–251](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L201-L251) | 仅有宽高不能复现障碍和碰撞；须取得两层实例及元素定义。 |
| E10 | 元素定义解析了宽高及每格 `GridAttr`，将建筑/物件占地逐格投影到地图，越界时报错。 | [competitive_battlefield.go L94–125](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L94-L125)、[L163–182](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L163-L182)、[L251–301](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L251-L301) | 原建筑可重绘表面，但占地、可通行方向、耐久等不能自行设定。不能用一个 solid 布尔值概括全部原行为。 |
| E11 | 该实现注释称原客户端使用 40 像素格；战斗核心 `CellSizePixels = 40`，坐标转换使用格坐标乘格距并加半格。 | [competitive_battlefield.go L24–29](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L24-L29)、[battleengine/types.go L14–20](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/types.go#L14-L20)、[L199–210](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/types.go#L199-L210) | 已确认社区实现常量；待以目标版本原客户端/原数据交叉核对。40 像素逻辑格距不等于每张建筑贴图的纹理边长。 |
| E12 | 该竞技目录分支跳过 `rand`、`pve`、`practice` 家族。 | [catalog.go L376–390](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog.go#L376-L390) | 不能把此解析分支直接宣称覆盖全部探险、练习或其他原版地图。 |

上表字节区间为零基、左闭右开。15×40=600、13×40=520 是基于 E05 和 E11 的**条件计算**，没有把未知地图尺寸补为 600×520。

## 原地图文件与来源检查

截至本次核对，社区修改后客户端的文件来源 URL、ZIP 和逐文件 SHA-256、目录 ID、三层格值及元素字面量已记录；未建立腾讯原始安装包的签名/哈希链。每张社区样本的格值可以准确比较，但不能把此结论等同于腾讯原件身份确认。逻辑像素格距、渲染偏移含义、目标历史版本与完整运行碰撞还需交叉核实。

| 来源/入口 | 本次实际状态 | 版本/哈希/签名与可用性 |
|---|---|---|
| [腾讯原站](https://qqtang.qq.com/) | 网页读取入口未能访问。 | 未取得可核验下载清单、地图清单、安装包哈希或腾讯数字签名。失败仅说明本次入口未读取成功。 |
| [历史原站下载入口](http://qqtang.qq.com/new/download.htm)（[52PK 历史 FAQ 所留外链](https://qqtang.52pk.com/data/xinshou/FAQ.htm)） | FAQ 可读并指向此官方域名；HTTP/HTTPS 下载页本次网页读取均未成功。 | FAQ 是转存线索，未取得官方页正文、包名、签名、哈希；没有下载 EXE。 |
| [另一原站下载候选页](https://qqtang.qq.com/download.shtml) | 网页读取入口未能访问；未据此猜测安装包名称或下载地址。 | 待核实；该路径也不应视为已证实的官方历史入口。 |
| [社区固定提交完整文件树 API](https://api.github.com/repos/kuuhaku1314/qqtang/git/trees/4b3a245fd985cabd4abd68ade6c282cc163d9edb?recursive=1) | 可访问；该树中的 `.map` 文件数量为 0；`client/original` 只有说明。 | 不是原地图资源库；其 `.map` 解析测试和代码不能替代原地图实例。 |
| [社区 v1.3.4 发行页](https://github.com/kuuhaku1314/qqtang/releases/tag/v1.3.4)、[发行元数据 API](https://api.github.com/repos/kuuhaku1314/qqtang/releases/latest)、[QQTang-Local.zip 入口](https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip) | 已下载 288,298,460 字节并重新计算 SHA-256；仅抽取数据，未运行客户端。发布时间元数据为 `2026-10-22T22:39:25Z`。 | 下载文件 SHA-256 为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`，与平台元数据严格相同。这证明取得同一份**社区发行 ZIP**；不是腾讯原始客户端签名或未修改证明。每图哈希另列导出索引。 |
| [QQ堂怀念版](https://qqt.95hyc.cn/) | 网页可访问。作者页面明确说明其为演示网页，未实现真实放泡玩法，素材为玩家收集。 | 可以作为历史画面线索；不作为原碰撞、建筑占地和地图几何验收依据。 |
| [QQTPVE 原作者仓库](https://github.com/atxxfs/QQTPVE) | 页面可访问，当前 `main` 文件树只有 README。 | 不是腾讯源码，未发现可核验原地图文件；不以复刻版本自有数据认定原版。 |
| [老玩家素材库线索](http://qqqt.ysepan.com/) | 怀念版首页的素材按钮指向此地址；本次 HTTP/HTTPS 网页读取均未成功。 | 未取得文件清单、来源链、版本和哈希；没有据此下载任何包。 |

### 社区测试中的地图哈希线索

[catalog_test.go L784–813](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/catalog_test.go#L784-L813) 的可选运行时测试预期探险地图 ID `1601` 的 MD5 为 `AD8C5668C199C5521616A7D2D1829DDC`。本次静态目录将 ID 1601 对应到 `pve01_8.map`，实际重新计算 MD5 与之精确相同；SHA-256 为 `289c25de8cd5a9a8d7c6366febacf798c8b6d9dbeedb84dcb659f60b0bfcbabc`。该文件头为 v4、40×17，而目录声明为 15×13。没有运行社区测试或客户端；MD5 一致仅表明与该社区预期样本一致，不证明腾讯原始身份，也不证明其他版本不变。源码单元测试中临时创建的 15×13 数据不作为原地图证据。

## 2026-10-26 本地数据导出与校验

- 输入清单：`.artifacts/reference-inputs/extracted-data-manifest.json`；377 张 `.map` 均逐个匹配抽取清单中的字节数和 SHA-256，解析无拒绝且无尾数据。
- 输出：`references/qqtang-map-data/catalog.json`、`elements.json`、`index.json`、`maps/*.json`；每张 JSON 中保留未知头部字、三个有符号图层、坐标表、概率原始 float32 bits、来源与分段偏移。
- `mapDesc.py`（48,965 字节）SHA-256 为 `342c91fb1b7f76116191ebc09eec6b00833e7492350b38163c4064cc1a578f8d`；按 GB18030 严格解码，AST 只取 `mapDesc` 字面量，得到 381 条、无重复 ID。
- `mapElem.py`（99,032 字节）SHA-256 为 `6bbc353501dcaadb5af4d8007dc250b3532a7abb603a7a98f6eb74beea6b314f`；UTF-8 严格解码，AST 静态读取 722 个类/721 条元素及继承字面量；注册 ID、size 与 GridAttr 长度校验零问题。末尾类名注册映射只按 AST Name 解析，未执行文件。
- 50 张实际尺寸与目录元数据不一致，全部保留差异并采用文件头实际宽高；`rand.map` 目录占位无文件；10 张文件没有目录记录；22 张地图用到 `mapElem.py` 未定义的正元素 ID。所有缺项均进入索引，没有猜造元素或碰撞。
- 已运行 11 项二进制解析器测试与 4 项静态导出/数据完整性测试；后者逐图由 JSON 在内存重建全部字节，377 张 SHA-256 和 MD5 均与输入相同。此校验确认导出无字节信息丢失，不等于原版游戏行为验收。

## 中国城01原像素参考取证

本地包内 `data/object.idx`（176,711 字节，SHA-256 `7f26487ceef121ab4352fab8d26051ddb88c8db8fc591c4ac4f267ac5c6e355e`）与 `data/object.pkg`（35,553,570 字节，SHA-256 `3f5a8dfe0f629bd8bbd02ea81226f69be968e1e4c5d737ac78439a7221c1188a`）均与社区发行清单匹配。索引 3,482 条完整读取；所用资源按包偏移解压独立 zlib 流，严格核对边界、EOF、解压长度和 QQF/DIMG 签名。没有运行被检查代码。

目录 ID 201 明确将中国城01关联到 `town01_4.map` 与 `town01_4.img`。后者 SHA-256 `3aafd617d51a436c8db8e4449292f9346f271f9fdbcf327d12b76ad995e11f49`，实际首帧为 **150×125**；其 DIMG 声明画布字段为未初始化值 `0xCCCCCCCC`，只解码有界 frame，不据此猜地图像素尺寸。`references/qqtang-map-data/visual-reference/town01_4-thumbnail-frame.png` 保留原帧；`town01_4-thumbnail-4x-inspection.png` 是最近邻 4 倍检查图，**600×500 不是原地图逻辑尺寸**。

同目录还有 17 个建筑/地面候选资源的原帧和 `town01-building-candidates-contact-sheet.png`，均已实际查看。`3000+N → town/elemN_stand.img` 只记录为文件名和类别推断，尚无客户端查找表证明。原始 DIMG canvas/frame offset、mapElem 占地和 offset 分开保留到 `visual-reference/manifest.json`；没有猜锚点或重拼整图，也没有复制这些原像素到游戏运行资源。解码与索引另有 4 项已知像素/边界测试通过。

## 本项目几何锁定规则

1. 一张图的正式制作以“目标历史版本 + 原地图 ID + 原文件路径 + 文件 SHA-256 + 来源证据”为起点；未取得时维持 `待核实`。
2. 逐文件读取格式版本、行列、逻辑格距、3 层格值、元素定义/占地、出生与目标格；输出可逐格比较的清单。v4 不套用 v3 默认宽高。
3. 核对建筑贴图锚点、覆盖范围与底部碰撞占地；重新绘制道家 Q 版外观时保留原坐标/占地关系。高清导出倍率另记，不能改变逻辑格距或将放大当原生尺寸证据。
4. 验收比较原文件与新项目导入数据：行列、格距、分层元素 ID 映射、格级碰撞/方向属性、耐久/特殊格、出生组/目标格及建筑占地必须一致；显示缩放与 UI 排版单独验收。
5. 原件缺失期间可继续原创 UI、角色定调、界面状态和数据导入接口，但不发布自行排布地图为原版复刻成品，也不从截图拉伸或凭视觉数格补造待核实值。

## 尚未完成的具体事项

- 核实用户所指原版的历史版本；当前只能将 `5.2.1.201` 记录为社区兼容线索。
- 找到可公开核验的原客户端或原地图独立文件来源，并验证出处、版本、签名/哈希链。本轮不要求用户重复提供其已说明没有的文件。
- 已取得社区 `map/mapDesc.py`、377 张 `.map` 和 `object/mapElem/mapElem.py` 并保留数据；继续核实腾讯原始来源、缺失元素及相应贴图/锚点含义。不能将社区文件的哈希写为腾讯原件认证。
- 对每张目标地图建立原数据到道家 Q 版资源的对应清单并逐格验收。任何地图尚未达到此阶段。

后续有原件证据时补充本文件；不得倒改本次未知项为此前已验证。
