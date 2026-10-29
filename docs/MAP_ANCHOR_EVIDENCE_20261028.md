# 地图像素锚点静态取证（2026-10-28）

本轮只读核对固定社区主源、现有自有渲染、五个明确资源头及已知原生地址的小段字节。结论分成“当前代码事实”“本包原生字节事实”和“尚未闭合的绘制关系”。没有地图通过原版几何验收；`geometryAccepted` 保持 false。用户合同仍为 [USER_REQUIREMENTS_LOCK_20261026.md](USER_REQUIREMENTS_LOCK_20261026.md) 与 [UI_SPEC.md](UI_SPEC.md)。

## 当前代码实际公式

实际读取的 [src/map-art.js](../src/map-art.js) 第 61 行是：

```js
x = object.x * 40 - offset[0]
y = object.y * 40 - offset[1]
```

没有额外 `+40`，没有地面特殊分支。第 62 行以 `art.worldFrameWidth/worldFrameHeight` 绘制；第 63 行按完整占地底边排序；第 105 行直接 `drawImage`。`DIMG frameOffset` 不参与这条调用。[src/original-maps.js](../src/original-maps.js) 第 63 行把 `element.imageOffset` 原样复制到实例，没有预先归一化、加帧偏移或加一格。渲染文件自己仍标 `candidate-awaiting-original-client-render-comparison`。

因此，offset 为 `[0,0]` 的 3001/3002 地面在当前代码中不会因为“普遍加 40”而移一格。禁止为修复一个当前不存在的 `+40` 改动源图格值。现有公式能否直接作用于已裁出的原帧，仍需下述显示链证据。

## 来源固定与本轮边界

- 社区恢复仓库固定为 [`4b3a245fd985cabd4abd68ade6c282cc163d9edb`](https://github.com/kuuhaku1314/qqtang/commit/4b3a245fd985cabd4abd68ade6c282cc163d9edb)，不是腾讯公开原始源码。已通过 GitHub 连接器读取六份主源；具体 blob SHA、行号、摘录及十三项检索回执保存到 [pinned-source-excerpts.json](../references/qqtang-map-data/anchor-evidence/pinned-source-excerpts.json)。检索没有找到显式 `mapElem_offset` 地图绘制实现，但检索无结果不能证明所有来源都不存在该实现。
- 固定本机包为 `.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip`，既有 SHA256 为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。本轮核对路径、大小及选中成员信息，未重新哈希整个 288,298,460 字节包。成员为 `QQTang-Local/runtime/client-patched/Client.exe`，13,860,864 字节、CRC32 `04f986c5`，PE32/i386、ImageBase `0x400000`。这些是社区补丁包身份，不能证明未改版腾讯身份或用户目标历史版本。
- 原生读取从主源给出的 `005d80e1`、`005d839c`、`0060c518`、`005eee71` 起，只沿实际解码出的 direct call/jump、一个构造器写入的表地址及明确表槽取小段。含下文两项定向补证，累计 **6,549 代码字节、112 静态数据字节**；每段保留 VA、RVA、fileOffset、长度、SHA256、原字节、来源链和解码文本。见 [native-windows.json](../references/qqtang-map-data/anchor-evidence/native-windows.json)、[native-data.json](../references/qqtang-map-data/anchor-evidence/native-data.json)。没有全程序反汇编扫描、猜测 xref 或安装工具。
- 使用已安装 LLVM 对临时 COFF 数据包装中的选中片段静态解码，包装随后删除；没有编译、链接、执行或完整导出客户端。窗口末尾、相邻函数、填充值和跳转表可能被反汇编器显示为指令；报告只引用下文明确地址，不把邻接字节当成已识别函数。多数窗口没有预先证明函数结束边界。
- 遵守 [LOCAL_RESOURCE_WINDOW_20261028.md](LOCAL_RESOURCE_WINDOW_20261028.md)：没有测试、构建、浏览器、模拟器、全量 PNG/alpha 解码或 QA、新生图、运行清单改写、Git 操作。只在本报告和 `references/qqtang-map-data/anchor-evidence/` 写入证据。

## 40 像素格距：本包已有独立字节支持

主源 [competitive_battlefield.go L24–29](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L24-L29) 声明 40 像素格；[types.go L202–210](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/types.go#L202-L210) 的社区实现使用 `col/row*40+20` 取中心、除 40 换格。这本身仍是社区实现。

本轮另按 [pickup.go L164–167](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/pickup.go#L164-L167) 给出的原生 `0060c518` 地址核对本包字节：[window-0060c518.txt](../references/qqtang-map-data/anchor-evidence/window-0060c518.txt) 中，`60c530/60c536` 读取 actor `+0x33c/+0x338`，`60c541/60c54d` 两次压入 `0x28`，`60c545/60c551` 两次 `idiv ecx`，随后 `60c55a` 调用查格路径 `005dbd54`。因此“这个固定社区包中的该原生路径按 40 换格”已有字节支持，不再只依赖自有测试或变量名。

这不证明整屏分辨率、地图美术外框、摄像机原点、未改版腾讯身份或所有特殊地图投影。15×13 的逻辑格区域按此格距为 600×520；不能由此宣称任意地图整图像素尺寸已验收。

## 原生地图对象的偏移入点：已看到属性对被减去

[competitive_battlefield.go L227–232、L260–264](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L227-L264) 给出正锚点安装地址。实际 [window-005d80e1.txt](../references/qqtang-map-data/anchor-evidence/window-005d80e1.txt) 的 `5d82f4/5d833b` 调用对象 vtable `+0x20`，随后 `5d8343` 调用 `005d839c`。对象安装保留行列与完整 size，不使用贴图偏移改占地。`005d839c` 代码与逐格展开、写对象指针的主源描述相符。

短调用链还有以下可核对事实：

| 原生位置 | 实际字节行为 | 解释边界 |
|---|---|---|
| `005f532d` 默认分支、静态 `0x7f6a50` | 将明确字符串 `CMapElem` 传给类工厂 `005f52ea` | 证明默认类名参数；未完整恢复运行时注册链及所有派生类。 |
| 构造器 `005eec60`、静态 `0x7a369c` | 写入表地址；表 `+0x20` 为 `005ef073` | 表来自具体指令，未凭地址范围搜索。 |
| `005ef073` | 验界后将两个有符号 16 位格参数保存到 object `+0x08/+0x0a` | 是格坐标保存；没有 `+40` 或贴图偏移。 |
| `005eee22` | 按元素 ID 经 `005c3b44` 取指针，放到 object `+0x14` | 后续称此指针为“属性指针”；其加载/分配布局尚未全链追完。 |
| `005eee71` 状态 1/2 | 将格坐标乘 40，减去属性指针 `+0x08/+0x0a` 的有符号 16 位值，再加固定 `8/21`，调用 `0040c900` | 已证明调用参数，不等同于最终原帧左上角。 |
| `0040c900 → 00582b70` | 至少将这两个实参保存到显示对象 `+0x08/+0x0c`；后续又涉及全局量 `0x8037b0` | 显示坐标空间/全局量含义未确定。 |
| `005ef003 → 004053a8 → 00583ac0` | 选状态显示对象后逐层转调 | 未闭合到具体 DIMG 帧的最终光栅位置。 |

最关键片段在 [window-005eee71.txt](../references/qqtang-map-data/anchor-evidence/window-005eee71.txt) 的 `5eefb7–5eefe2`（状态 1），状态 2 的 `5eef22–5eef4d` 重复相同算式。以 `R=object+0x08`、`C=object+0x0a`、`P=object+0x14` 表示原始读取，不先给未知字段补名字：

```text
arg1 = C * 40 - sign16(P + 0x08) + 8
arg2 = R * 40 - sign16(P + 0x0a) + 21
call 0x0040c900(arg1, arg2)
```

`P+0x08/+0x0a` 与 `mapElem.prop` 记录头中 offset 的有符号 16 位位置吻合；此前 721 个共同定义与 Python 字面量 offset 全相等，本轮五个具体记录再次从原始头核对相等。但 **native 属性表加载到 P 的布局转换尚未完全追完**，所以“该属性对就是外部表 raw offset、且没有中间变换”仍作为很强的可检验关联保存，未当作已完全闭合证明。

固定 `+8/+21` 不能直接命名为“地图原点”或随手删/加到自有画布。它们可能属于原客户端显示/场景坐标；本轮未证明其与视口、摄像机、后续全局变换的关系。当前自有画布若从 `(0,0)` 表示地图区域，去掉共同平移可能合理，但此处仍不能签通过。

## DIMG 偏移、像素范围和包偏移分别保留

主源 [dimg.go L155–205](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/itemcatalog/dimg.go#L155-L205) 在 frame header `+4/+8` 按有符号 32 位读 x/y；独立本地读取器同样保存为 `frameOffset`。主源的 [DecodeDIMG L72–103](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/itemcatalog/dimg.go#L72-L103) 把 frameOffset 加到声明画布中，`DecodeDIMGFrame` 则只返回原帧。它是 GM/UI 图标预览路径，不能证明 CMapElem 绘制也用同一加法。主源 [item_images.go L186–190](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/server/gm/item_images.go#L186-L190) 也明确提示声明画布并非可靠 UI 边界。

本轮只对下列五个精确 `object.pkg` 流做有界读取，累计 **8,974 压缩字节**，核对各压缩流和完整 DIMG 的既有哈希、首 68 字节与对应 24 字节属性头，未解码像素。记录和脚本见 [local-anchor-samples.json](../references/qqtang-map-data/anchor-evidence/local-anchor-samples.json)。

| 元素 | 格占地 | 原帧尺寸 | mapElem raw offset | DIMG 第 0 帧 offset | 对本轮问题的价值 |
|---|---:|---:|---:|---:|---|
| 3001 | 1×1 | 40×40 | `[0,0]` | `[0,0]` | 一格纹理与 40 格距相容；无法区分帧偏移正负。 |
| 3002 | 1×1 | 40×40 | `[0,0]` | `[0,0]` | 同上；当前公式没有移一格。 |
| 3019 | 4×2 | 161×110 | `[0,30]` | `[0,17]` | 有效区分候选：在锚点 `(0,0)`，当前 y 为 `-30`，假设加帧偏移为 `-13`，假设减帧偏移为 `-47`；三者尚未选定。 |
| 3050 | 1×1 | 43×101 | `[1,60]` | `[0,0]` | 原帧远高于占地；不能用尺寸重心或 40×40 拉伸替代原锚点。声明四帧，单帧不能作完整状态交付。 |
| 11007 | 13×1 | 520×40 | `[0,0]` | `[0,0]` | 520÷13=40，另一个独立资源相对尺度支持；不证明画面原点。 |

这些 ID 与资源路径的关联仍继承生产索引的“数值前缀/文件后缀候选”边界；本轮发现的原生资源编码（`005ef283`）尚未完整追到包路径查找，不能把关联自动转正。

`visibleBoundingBox` 是此前像素解码得到的帧内可见范围，本轮仅复用 JSON。`recordOffset/packageOffset/pixelDataOffset` 是文件字节位置；`mapElem offset` 是属性对；`frameOffset` 是图像帧字段；四类数值不得相加。地图缩略图 `town01_4.img` 原帧 150×125 以及曾生成的 4 倍检查图也不参与本次地图像素尺寸证明。

## 当前判定与可检验下一步

| 项目 | 状态 |
|---|---|
| 自有 renderer 实际使用 `anchor*40-mapElem.imageOffset`、无普遍 `+40` | 已直接确认代码事实。 |
| 固定社区包中的原生坐标换格采用除 40；资源存在 40×40/13×40 对应 | 已确认本包字节/资源事实；腾讯目标版本身份仍未知。 |
| 原生地图相关调用先乘 40、减属性有符号对，再加 `[8,21]` | 已确认明确地址的调用参数。 |
| 属性对与序列化 mapElem raw offset 的完整加载对应 | 有强关联，加载链未完全闭合，保留候选。 |
| `[8,21]` 的坐标空间、摄像机/视口归一化 | unknown。 |
| DIMG frameOffset 到最终地图像素的符号、是否应用及是否另有层内变换 | unknown；当前 renderer 不使用它。 |
| 原生普通/破坏/移动/派生元素是否共用相同公式、层间/角色排序 | unknown，未由这几个地址推广。 |
| 原版目标历史版本、未改版腾讯身份、逐地图 1:1 几何验收 | 未通过。 |

最小后续证据应沿已经明确的 `00583ac0 → 00403cb5` 绘制调用和原生属性表装载继续做有界静态核对，或在用户允许的验收时段用有版本身份的原版画面/坐标回执对照。优先选择 3019 这种非零 DIMG offset 元素，同时以 3001/3002 校验共同原点，不能只看所有偏移为零的地面后宣布公式正确。若取得实际显示坐标，还须分开记录场景显示对象坐标、帧内光栅坐标与最终屏幕像素。

本轮没有修改 `src`、生产索引、当前美术、运行清单或其他窗口记录，也没有用自有测试通过代替原版证据。

## 定向补证一：3019 的两处数值与原生层绘制

本节沿已有地址新增读取 2,233 代码字节；没有扩大到全程序搜索，也没有新解码图片。3019 的原始头和现有 alpha 元数据直接来自前述五件样本及 [character-scale-evidence.json](../references/qqtang-map-data/anchor-evidence/character-scale-evidence.json)：

- 占地 4×2 格，在 40 格距下为 160×80；原帧 161×110，声明尺寸 161×110，已记录帧内 `visibleBoundingBox=[0,0,161,110]`。
- DIMG 文件头 byte `24/28` 的未命名有符号 pair 是 `[0,17]`；第 0 帧头（文件 byte `44/48`）也是 `[0,17]`。**两处数值相等不证明两次平移，也不证明它们语义相同。** 本地读取器仍把文件头的两项保留为 unknown。
- 所保留 PNG 是直接解码的 tight frame，未把 frameOffset 放入画布；已有 bbox 从 y=0 到 y=110，不能说它已经含 17 行顶部全透明 padding。若将帧放到同样高 110 的声明画布并再加 y=17，会延伸到 127；因此声明尺寸也不能直接当作已组合完整边界。
- 当前候选在锚点零处的底边为 `110-30=80`，恰与 2 格占地高 `2*40=80` 相等；额外加 17 会变为 97。这是有用的几何相容线索，但帧外框/alpha 底边不是已证物理脚底，不能以此替代原生装载与绘制证明。
- 像素中出现接近某个“脚底/地面线”的轮廓最多是线索。此处没有新测像素或用物理脚底选择锚点公式。

原生 setter 的后半段现已看到返回：[window-00582b70.txt](../references/qqtang-map-data/anchor-evidence/window-00582b70.txt) 与 [window-00582ba0.txt](../references/qqtang-map-data/anchor-evidence/window-00582ba0.txt) 组合表明 `00582b70`：

```text
display[+0x08] = arg1
display[+0x0c] = arg2
display[+0x10] = arg1 - global[0x8037b0]
display[+0x14] = arg2 - global[0x8037b4]
return
```

这一步没有读取 DIMG 帧。两个 global 的意义/运行值仍未取得。

继续沿 `005ef003 → 004053a8 → 00583ac0 → 00403cb5 → 00583340` 的明确调用，读到完整的这一层绘制函数及终点 `005838fa`。其中 `00583492` 经 `00407ae5 → 00480970` 取出按两个索引选择的运行时记录 F；`005834ab/005834b1` 读取 `F[0]/F[4]`。再经已解码的 Point 构造 `005854a0`、相减 `005854e0` 和复制 `00585460`，形成：

```text
delta = Point(layer[+0x2c], layer[+0x30]) - Point(F[0], F[4])
```

`00583601–00583648` 将 delta 以负 X 及该绘制链 Y 轴约定送入顶点平移。后面还组合图层旋转/缩放与 `display[+0x10/+0x14]`，最后 `005838ee` 调用渲染接口槽 `+0x118`。具体字节见 [window-00583340.txt](../references/qqtang-map-data/anchor-evidence/window-00583340.txt)、[window-005834be.txt](../references/qqtang-map-data/anchor-evidence/window-005834be.txt)、[window-00585460.txt](../references/qqtang-map-data/anchor-evidence/window-00585460.txt)。因此这条 generic 层绘制链**确实使用运行时 frame-like pair**，不能概括成“原生显示完全忽略帧偏移”。

仍不能由此给 3019 选择 `-13`：没有追完 **DIMG 装载时 F 的字段赋值**。F 的 pair 可能直接保留原帧 offset，也可能先减文件头 pair 或做其他归一化；3019 两个 pair 恰好相等，单图尤其无法区分。具体 map fastpath 是否沿完全相同的记录/变换、图层默认位移及缩放值也未验证。条件为“Fpair 就是 raw frameOffset、图层位移与额外变换为零、共同显示原点已归一化”时，正向加 frameOffset 才是这个局部运算支持的候选；这些条件尚未同时证明。**不在 renderer 上硬加 raw 17，不重复叠加 header pair 与 frame pair，组合公式保持 unknown。**

## 定向补证二：当前角色画布、alpha 范围与 40 格距

实际读了 `src/game.js`、`src/app.js`、`src/art.js`、`src/character-motion.js`，没有根据旧文档猜倍率。输入快照、元数据和算术保存在 [character-scale-evidence.json](../references/qqtang-map-data/anchor-evidence/character-scale-evidence.json)，复算脚本 [capture-character-scale.py](../references/qqtang-map-data/anchor-evidence/capture-character-scale.py) 不读图片。

`src/game.js` 第 65/89 行保存源地图宽高、人物格坐标及 sprite 索引；实际显示在 **`src/app.js` 第 123 行起的 paintBoard**：源地图 `cell=40`、`unit=40/64=0.625`，人物绘制放入 `ctx.scale(unit,unit)`。`density=2` 仅使地图和人物共同用双倍后备像素，不改变人物/格子的相对比例；CSS 等比呈现再共同缩放。

### 静态回退实际按 alpha 裁区绘制

`src/app.js` 第 165 行请求 `drawSprite(...,82,90)`；`src/art.js` 第 7 行先从 `assets/art.json` 的 alpha 包围框裁区取图，再 `min(82/cropWidth,90/cropHeight)` 等比装入该框。它**没有把完整 1024×1024 画布画成 82×90**。四人的已存运行图 canvas 都是 1024×1024；按当前已记录裁区计算：

| 人物 | 已存 alpha 裁区大小 | 裁区高/原画布高 | 最终裁区逻辑尺寸 | 相对 40 格的高度 |
|---|---:|---:|---:|---:|
| 道童 | 633×907 | 88.5742% | 39.2572×56.25 | 1.40625 格 |
| 月影 | 775×906 | 88.4766% | 48.1167×56.25 | 1.40625 格 |
| 山岳 | 701×906 | 88.4766% | 43.5224×56.25 | 1.40625 格 |
| 莲花 | 740×906 | 88.4766% | 45.9437×56.25 | 1.40625 格 |

这些是已有 `runtime/*.png.provenance.json` 的 visibleBounds 与当前代码的确定算术，本轮未重测 alpha。道童图的 1024 全画布如果按同一倍率假想保留，会约为 63.5061×63.5061 逻辑像素，但该全画布实际没有被此分支绘制，不能把这个换算当成 drawImage 的目标矩形。当前静态裁区顶边是格 y−16.875、底边是格 y+39.375；这是裁区边界，不是已认证的原版脚底。

### 跑步分支的完整画布是 68.75，不是 40

`src/app.js` 第 164 行在非预览、非困泡、最近移动小于 190ms 时尝试 `drawCharacterMotion(...,110,...)`；`src/character-motion.js` 第 135/136 行按 `size/frame.canvas[0]` 计算锚点，并把**完整 canvas** 画成 size×size。因此运行清单画布 256×256，在源地图中显示为：

```text
full motion canvas = 110 × (40/64) = 68.75 × 68.75 logical pixels
full motion canvas per grid = 1.71875 × 1.71875 cells
256 frame pixel → map logical pixel = 68.75/256 = 0.2685546875
world root = (col*40+20, row*40+36.875)
```

68.75 是包含透明留边的完整 canvas，不是可见人物高度。现有 E01 小 JSON 中，山岳源 1024 图 alpha>8 的高度为 923，莲花为 883；原样全画布缩小的元数据投影给出约 **61.9690** 和 **59.2834** 逻辑像素可见高度，分别约 1.5492、1.4821 格。由于 256 输出经 LANCZOS、阈值边缘可能变动，这是源 alpha 比例投影，本轮没有把它冒充新测输出 bbox，也没有推广到其他所有帧。相应 clip anchor 本身仍是 historical/provisional，不能把 root 自动视为已标定脚底。

当前 `assets/characters/motion/manifest.json` 中：山岳/莲花有 `client_candidate` 的 run/hit；**道童和月影 `adoptionStatus=missing`、clips 为空**。所以当前 source-map 道童即使移动，动画尝试也返回 false，实际用上述静态 56.25 高回退。`motion-generated/daoist-child/` 的新候选和原生参考目录存在，不表示这份运行清单已采用它们。

### 原角色 9 的 100 画布与约 55 高只作有限比较

只读取现存 `native-role9-evidence/group0-six-phase-board.json` 的六个已记录原始 layer offset/size，没有新解任何层 PNG。hair/face/cloth/leg/body/foot 六层矩形在原 100×100 平面上的并集：第 0–4 相位均为 `[31,26,66,81]`，35×55；第 5 相位为 `[32,26,67,80]`，35×54。该 JSON 的 E 朝向来自既有实际图像观察；叠层顺序仍标为诊断选择，head1 未包含。

**矩形并集不是精确 alpha 并集**：它是可见像素范围的上界，层内还可能有透明像素。100×100 是源资源画布，也未证明原客户端将完整画布以 100 屏幕像素、或将这些层以 1:1 显示。若暂作原生无额外缩放假设，54–55 源像素约 1.35–1.375 格；当前道童静态 56.25 高相对上界仅约高 2.27%–4.17%，没有从这组数据看到数量级的尺度失配。宽度约 39.257 对 35 约大 12.16%，但原生 alpha 宽度、完整装饰/遮挡和实际显示变换未核实，不能据此判精确通过或直接把原创人物按某个比率缩小。

同理，拿 68.75 的“完整动作画布”直接除以 55 的“原生层矩形并集高度”会混淆透明画布与可见范围；拿 256、100 或 1024 这三个导出画布尺寸直接比较也无效。当前结论仍是：**明确了现有显示倍率及运行采用状态，原版人物/地图的相对尺度验收尚未完成。**
