# 五阶披风源合同与候选边界

本批只处理 `npack` 中目录描述明确的一组 2005 赛事五阶披风：148 羽林披风→青岚羽林披、149 骁骑披风→紫雾骁风披、150 冥袭披风→玄霜夜行披、151 影羽披风→金霞影羽披、152 太御披风→朱金太御披。完整小族不等于全部 197 件背饰，更不等于全游戏完成。最终选用文件以本族独立清单和交付索引为准；生成失败与重试均保留。

唯一物品输出目录是 `assets/items/back-adornments/honor-capes/`。不修改头饰全族采用清单、其他物品资产、运行时接线或 Git。目录下的源 PNG、相位板和剪裁编辑输入都是 reference-only，不能进入运行时素材。

## 可核源链

固定输入 `.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip`，SHA256 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。它是社区修改样本，不将其版本或美术真实性冒称为已验证的腾讯原版。

按 `references/qqtang-item-data/catalog.json` 的 `installed_files` 取精确 member，而非从源 ID 猜资源号。member 前缀为 `QQTang-Local/runtime/client-patched/`，五件资源号分别 19–23；世界输入为 `object/npack/npack{resource}_{stand,walk}.img`，库存输入为 `res/uiRes/icon/npack/npack{resource}.img`。

只静态读取 ZIP 字节并调用项目可信 `scripts/inspect-reference-dimg.py` 解码；不执行客户端。世界每件 stand/walk 文件字节一致，每个文件 12 个源位置、12 个独立 raster，头部声明 4 directions。按每次至多 6 个明确位置恢复源 PNG。精确 member、源 IMG/编码像素/解码 RGBA/PNG SHA、原始记录、源尺寸及 rawOffset 全部在 `references/{ID}/source-contract.json` 与各 `.source.json`。

源位置集合是 0–11，表示文件记录次序；未经证明的 cardinal、时间间隔、循环、方向块语义、原生挂点均保持 null/unknown。stand/walk 字节相同不证明二者时序相同。不得把本批 60 张新世界 raster 膨胀计成 120 张独立原画。

## 实际观察到的姿态

- 0–2 是细窄 L 形侧披层：上方领带向右延伸，左侧垂下或向左鼓动；大部分中央是被不可见角色遮挡后的透明空隙。
- 3–5 是短披风外面：三片主要下摆，静止、向左鼓动、向右鼓动。
- 6–8 是实际源图的另一侧细窄层：领带向左延伸，右侧垂下或鼓动；逐帧重画，不用程序镜像充数。
- 9–11 是内衬一面：中央内衬与两侧翻折，静止及左右鼓动；不能把外侧中央绣纹又贴在内衬中央。

以上是图像形状描述，不是确认后的前后左右方向名或播放时序。所有源板、五件源库存与新身份/风格引用都实际以文件图像查看。150 的源位置 3 存在不明白色边绘，原样保留在 reference-only 源图，不编造其粒子/运动效果语义；自己的物理披风候选不加散点来凑包络，仍保留其源逻辑画幅与 rawOffset。

库存源图含蓝色椭圆 UI 台底。完整源图原样保留，另作物理披风 reference 裁口：148/149/150 `[0,0,26,18]`，151 `[0,0,31,23]`，152 `[0,0,38,25]`。新库存候选明确只绘物理披风，不把 UI 台底当衣物。独立 native-density 库存变体保留原库存画幅和 rawOffset，并明确标记省略该非物理台底。

## 制作与技术门槛

新图采用本项目道家 Q 身份：绿色、紫灰、钴蓝、琥珀金、朱红金五档短肩披；库存身份来自 builtin 原画，世界相位以同件身份延续。自有人物 `assets/characters/runtime/daoist-child.png` 以及两张主 style `references/image/01-mail-event.png`、`references/image/team-ui-v2.png` 已查看；它们提供材质风格，不提供披风方向/时序。后续各六相位批次引用已生成的对应库存身份，精确 refs 顺序与角色逐次封存在 submission/generation 元数据。

只调用内置 `image_gen.imagegen`。项目配置目标为本轮已核对的 `gpt-image-2.6-sunburst / high`，内置工具没有模型或质量选择器，`actualModel`/`actualQuality` 始终 null。每次实际调用前把 `functions.store` 的完整字符串直接 JSON 转义封存，CRLF 原样参与 UTF-8 SHA；promptFile SHA 按原始文件 bytes 计算，不用 Python universal-newline read 重构实际提交。实际参数、refs/SHA、tool 返回字段、hostSource、未经改写的 PNG 与原生尺寸都保留。

生成不合格时用真实 AI 重画/编辑并保留旧 take，不用代码绘制披风、非等比拉伸、程序镜像或颗粒填包络。母图按实际 extent 与未切到可见 alpha 的裁口导出。技术比例按 alpha≥16 的物理可见包络相对源包络偏差 ≤10%；边界门槛不能替代人工视觉审核。母图可能保留低 alpha 抗锯齿残留，必须通过浅/深底预览复核，不把技术通过等同于视觉 PASS。

世界输出仅 crop、等比 premultiplied-alpha LANCZOS 缩放，源 logical canvas×4，源 rawOffset 原数值保留。注册位置为源 alpha 包络 X 居中/Y 底对齐，属于候选导出约定；不冒称原生挂点已复现。库存另外提供归一 256 图及原库存画幅×4 变体。

本批所有新候选的 `visualAccepted`、`geometryAccepted`、`accepted`、`runtimeAdopted`、`completeAnimationAccepted` 均保持 false，`userReviewStatus` 为 pending。不把文件覆盖、比例或 SHA 校验冒称时序、挂点、实机或完整游戏通过。禁止 GUI/CUA/sky/替代 GUI；视觉、实速、穿戴挂点与完整动作由用户另行审核。
