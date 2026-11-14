# 原生宠物控件候选

本组交付 `object/ui/pet` 全部 **23 件 IMG、67 个原生状态位置**：13 个四态按钮、4 个单态面板、5 个双态情绪气泡和1个进度条。已导出原生像素并回读复验；未安装到用户目录，未运行原客户端，未操作 Git。新画面仍待用户视觉确认，原程序运行中的文字、裁切、表情相位与状态对应仍待验。本组不代表宠物生物动画或整款游戏美术完成。

- [原生候选总览](candidate/contact-native.png)
- [五种表情的十个原生状态](candidate/emotions-native.png)
- [深玉/米白底透明边诊断](candidate/emotions-edge-diagnostic.png) · [边缘RGBA量化](edge-evidence.json)
- [原生来源图](source-contact.png) · [表情来源放大对照](face-source-detail.png)
- [来源合同](manifest.json) · [候选清单](candidate-manifest.json) · [文字颜色与最终像素证据](palette-evidence.json)

来源是锁定的 `QQTang-Local-v1.3.4.zip` 内 `object.pkg`，归档 SHA-256 为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。源图仅用于布局、状态和功能参考。`uiMain.pyc`、`uiSelRoom.pyc` 使用有界静态常量解析器读取，未导入或执行客户端字节码。每件资源的压缩及解包 SHA、包目录项、原始 DIMG 头、逐帧模式、尺寸和偏移见来源合同。

画稿与转换：

- 按钮和面板复用项目自有玉绿金边手绘套件，沿用两张用户指定风格参考。按钮保留原槽位顺序、原文字及每个槽位观察到的折叠箭头方向；没有改原回调或状态方案。
- `dlg_pet` 按原声明画布 `257×290` 排布，依原栅格偏移裁切 `(2,2,253,287)` 得 `251×285`。名字输入、宠物预览、等级、两条进度和数值的坐标承接原子控件。右侧数值控件声明宽度延伸到原背景栅格之外；本批不更改原声明，超出背景部分的实际运行裁切仍待验。
- 食品面板维持原4列3行。翻页图16态、食品格面板1态、进度条1态，共18处功能 Alpha 在最终原生解码后逐字节等于来源。宠物预览、食品物品图、数量文字、工具提示以及共用关闭/左右按钮继续由各自的原资源或动态控件提供。
- 名称、成长值、体力、技能及食品数量显式使用 `lightColor`，等级显式使用 `darkColor`。证据包含相邻 `LOAD_NAME→STORE_NAME` 原指令及 `uiMain` 全局字面量，未把未提取到的 `drawcolor` 当成默认黑字。7处最终原生背景采样达到本批选择的4.5对比阈值；食品动态图可能覆盖数量底，仍需运行核验。

五张表情分别通过宿主内置 `image_gen` 生成，实际文件均为 `1254×1254 RGBA`，五张母图哈希不同，十个原生导出帧哈希也各不相同。按源观察分别保留忧愁、挤眼、微笑、欢喜及爱心眼表情；这些名称只是画面描述，不声称已验证具体心情数值与索引之间的运行映射。

每张母图保留原始返回文件、完整实际提示词、两张风格输入 SHA、工具返回提示、宿主返回路径、PNG尺寸、时间及 SHA。配置目标和实际参数分开记录：实际内置型号、质量未披露，均为 `null`，不把配置目标当作实际返回型号。参考 [生成请求](generation-requests.json)、[工具返回记录](tool-results.json)、[本批官方能力核对](model-capability-check.json)。

| 索引 | 自有原画与逐图来源 |
|---|---|
| face0 | [画稿](emotions/face0-master.png) · [来源记录](emotions/face0-master.png.generation.json) |
| face1 | [画稿](emotions/face1-master.png) · [来源记录](emotions/face1-master.png.generation.json) |
| face2 | [画稿](emotions/face2-master.png) · [来源记录](emotions/face2-master.png.generation.json) |
| face3 | [画稿](emotions/face3-master.png) · [来源记录](emotions/face3-master.png.generation.json) |
| face4 | [画稿](emotions/face4-master.png) · [来源记录](emotions/face4-master.png.generation.json) |

表情装帧以母图 Alpha≥8 的可见框外扩1px，框外最大 Alpha≤7，仅裁去宿主透明输出的外围低 Alpha 尘点；主体透明通道保留。先预乘 Alpha 等比缩放，统一注册在两态原生窗口的逻辑交集：face0/1/3/4为 `34×33` 逻辑画布中的 `(0,1,34,33)`，face2为 `(0,0,34,33)`。两态共用同一缩放和位置，再按各自原始偏移/尺寸切出，避免第二态裁掉脸圈或分别缩放造成抖动；最终原生回读的两态还原偏移后 Alpha 逐字节相等，可见主体裁损为0。逐张裁框、逻辑交集及排除 Alpha 上限记录在候选清单的 `emotionPacking`。第二态为自有画稿亮度 `1.10` 材质变化，并按原第二态的 `34×32/y=1` 或 `34×33/y=0` 几何导出。来源两态有亮度、边缘及细小像素差，本批**没有证实逐像素表情相位一致**，没有把材质派生声称为另一张模型原画，也未新增时序。

透明边另按 `G≥150、G-R>80、G-B>80、Alpha≥8` 检查：母图 face0/face1 各有1点 Alpha=8，其他母图为0；最终10个原生帧全部为0。低 Alpha RGB 的存在与正确 Alpha 合成后的可见结果分开记录，不因文件是 RGBA 就宣称边缘干净。深玉及米白底诊断使用实际原生解码 PNG 做精确 Alpha 合成再近邻放大4倍，图像仍待视觉验收。

独立复验命令，在仓库根目录执行：

```powershell
python assets/native-client-ui/pet-controls-reference/decode-references.py
python assets/native-client-ui/pet-controls-reference/verify-renderer.py
python assets/native-client-ui/pet-controls-reference/verify-renderer.py --check
python assets/native-client-ui/pet-controls-reference/check-emotion-edges.py --check
```

`--controls-only` 可仅导出不含 face 的18件/57态；冻结全量清单时应执行上面的无此选项命令。生成请求准备器及返回文件导入器只记录请求或复制已实际返回的 PNG，不调用付费 API。生成工具不可用时不以重复图冒充缺失画稿。

主构建接入键可使用 `pet-controls`，模块为 `scripts/native-ui-pet-controls-art.py`。所有 `kind` 均以 `pet-` 开头，兼容主构建器现有前缀分派；`PAINT_INPUTS` 为5张独立表情原画，`ART_GENERATION_RECORDS` 为这5张画稿的逐图生成记录，`FONT_INPUTS` 为符号字库，`STRUCTURAL_ALPHA_INPUTS` 为18个精确来源 Alpha。原生构建本身不调用图像模型，上游5张新增模型画稿单独记入来源。独立编码文件位于 `candidate/patch/object/ui/pet/`，应由协调者合入同一 `object.pkg` 包批次，而非单独覆盖已有包。

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收继续待完成。
