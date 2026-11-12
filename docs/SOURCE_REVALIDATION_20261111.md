# 参考源恢复与版本边界复核（2026-11-11）

本记录按纽约日期记账。恢复输入的核验时间为 2026-11-12 04:33:36 UTC，后续参考比较同轮完成。仅处理本仓库的忽略研究输入，未执行归档内的 Python、EXE、DLL、启动器或客户端，未把第三方像素加入游戏运行素材。

## 固定来源与恢复结果

当前可复核的参照源仍是[社区 v1.3.4 发行 ZIP](https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip)。[发行页](https://github.com/kuuhaku1314/qqtang/releases/tag/v1.3.4)和[固定 tag 元数据](https://api.github.com/repos/kuuhaku1314/qqtang/releases/tags/v1.3.4)已重新读取。平台返回资产 `QQTang-Local.zip`、288,298,460 字节、发布时间 `2026-10-22T22:39:25Z`，digest 与仓库固定值相同。发行说明列有泡/墙体逻辑、道具、变身配置等修改；不能将这份发行物称为腾讯未修改原始客户端。

| 已恢复输入 | 字节数 | 本轮重新计算的 SHA-256 |
|---|---:|---|
| `.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip` | 288298460 | `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7` |
| `.artifacts/reference-inputs/object.pkg` | 35553570 | `3f5a8dfe0f629bd8bbd02ea81226f69be968e1e4c5d737ac78439a7221c1188a` |
| `.artifacts/reference-inputs/object.idx` | 176711 | `7f26487ceef121ab4352fab8d26051ddb88c8db8fc591c4ac4f267ac5c6e355e` |
| `.artifacts/reference-inputs/town01_4.img` | 56318 | `3aafd617d51a436c8db8e4449292f9346f271f9fdbcf327d12b76ad995e11f49` |

ZIP 通过完整字节 SHA 后，才运行本项目的 `scripts/extract-reference-data.py`。恢复了 386 个白名单数据文件，其中 377 张 `.map`；每件字节数与 SHA 均再次匹配已跟踪的 `references/qqtang-map-data/archive-extraction-manifest.json`。抽取清单自身 SHA 也完全相同：`5a3dc7d1e77f08ba534f6409a7a79797fe8d244584e0e3f1b6c1f35dc5205dcc`。既有抽取脚本保留原始 `retrievedOn` 字段；这次重新下载/恢复时间由本记录和忽略目录中的本轮验证报告单独记录，没有把历史日期当本轮日期。

原格式取证文本 `format-evidence/community-dimg-format.go` 已按 README 复制到忽略输入目录，SHA `f6fec2355b4335129130feb2bcf8ea2b549608022bdad13bfd8c0175a606f161` 通过。所有下载分段、完整 ZIP、原始 pkg/idx、解码参考和重导出均位于 `.artifacts/`，不纳入公开提交。

## 与现有参考的独立比较

重导出目标为 `.artifacts/reference-inputs/reexport-20261111/`，未覆盖已跟踪参考：

- `catalog.json`、`elements.json` 与仓库现存文件逐字节一致：381 目录项、722 类/721 元素，字面量校验无问题。
- 377 地图全部原字节 SHA 与现存索引一致；三层、坐标表、尺寸、未知字段及其余 JSON 数据均相同。新 JSON 的唯一内容差异是 `/source/name` 的本机绝对输入路径从旧 `D:\work\qqtang-ui\...` 改为当前 `E:\work\qqtang-daoist-remake\...`。因此不能称为 377 JSON 逐字节相同；新索引仅有对应的 377 个 `exportedJsonSha256` 变化，除此无差异。
- 保留既有边界：188 张 v3、189 张 v4；327 张 15×13；50 张目录尺寸与实际头不一致；`rand.map` 仍缺；10 张文件仍无目录关联。没有用恢复操作改写这些未知项。
- 对恢复的 object 包重新解析全部 3,482 项索引，并逐一核对现存中国城参考中的 17 个资源压缩流 SHA 与已记录 DIMG 字段，全部一致。目录直接关联的 `town01_4.img` 元数据也一致。当前读取器新增的 4 个严格容器/后缀状态字段单独记录，不回填为旧记录原已存在的证据。
- 定向检查通过：`node --test tests/map-reference-export.test.mjs tests/map-import.test.mjs` 为 15/15；`python -B tests/dimg-reference.test.py` 为 7/7；`python -B tests/dimg-metadata-only.test.py` 为 7/7。检查的是数据/解析边界，不是全部美术或游戏实机验收。

本轮机器可读报告位于忽略输入目录：`restoration-verification-20261111.json`、`reexport-comparison-20261111.json`、`dimg-source-comparison-20261111.json`。它们供本机续作复核；公开的固定哈希和重新导出步骤仍以[地图参考说明](../references/qqtang-map-data/README.md)为准。

## 未启动世界头饰的制作优先项

只读对照 `source-state-inventory.json` 与当前三个 world 清单，得到 18 项尚未启动世界表示。对这 18 项按固定 ZIP 条目和原 SHA 静态读取全部帧结构，按尺寸/编码像素哈希分组；没有把头部声明或重复位置算作已完成美术。

最少独立 raster 的两项均为 24 原位置、12 组编码 raster：

| itemId | 源名称 | 可用证据与建议 |
|---|---|---|
| 408 | 恶魔酷比精灵 | 已有本项目 14 绯耳灵的原创身份映射。实际解码并查看 12 代表相位，侧/背/另一侧/正视及三档翼摆清楚。建议先做本项，保留既定原创身份，不沿用原酷比脸。代表 index 为 0/1/2、6/7/8、12/13/14、18/19/20。 |
| 4556 | 天国之环 | 实际解码并查看 0—11 共 12 代表相位，为不同开口/光斑位置的白色 alpha 发光环；内部几何和原生混合方式仍有限，优先级低于 408。 |

两项源 stand 容器严格完整、无未解析尾段，源 SHA 分别为 `461cc7f582406ee09ec6d81b4eae55c590a6ccb18605e565ab7de3188b630439`、`8b979392907eedeace750aa517dbf30cb4d21e6f931734a3a0c63ab1d4ffae7e`。代表图与原尺寸/原偏移/解码像素 SHA 报告在 `.artifacts/reference-inputs/head-world-scan/`，检查板为最近邻 4 倍参考，不是原生高清或新画成果。原方向 cardinal、分块顺序、逐帧时长、loop 和本项目角色头节点仍未知，未批准运行佩戴。

## 仍须外部证据锁定的范围

当前锁定的是同一份社区 v1.3.4 样本与固定研究基线 `4b3a245fd985cabd4abd68ade6c282cc163d9edb`。`5.2.1.201` 仅为社区补丁兼容版本线索。ZIP 中的资源版本表、修改版说明和哈希不能独立证明腾讯原始历史版本；本轮没有把任何一个版本号升级为用户目标版本。

用户准备的来源客户端到位后，仍须核对其实际出处、可执行文件版本/签名/哈希、资源包哈希及与本样本的逐文件关系，才能决定目标历史版本和差分范围。现有参考足以继续原创身份与已知相位的绘制、透明/尺寸/偏移检查；不足以签署原版全地图、全机制、原帧时序或整款美术已完成。
