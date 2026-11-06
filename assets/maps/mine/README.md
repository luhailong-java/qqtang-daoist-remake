# 矿洞族原创图元候选

2026-10-26：70 条定义已形成候选，来自 68 幅不同源画面；11 张内置 image_gen 母图，2 条源画面别名。正式几何、锚点和游戏验收通过 0 条。

所有地图坐标、footprint、GridAttr 与源 offset 保持原值。每件导出画布是原始 frame 的 4 倍；操作只有裁切、等比适配和透明画布放置，不代表模型原生 4 倍细节。

每次实际附上 image 邮件/组队两主图及对应结构联系表。逐图记录保存配置目标、实际参数、工具输出、引用 SHA256 和 UTC 时间；宿主没有披露实际型号/质量，均为 null。

## 文件

- art.json：70 条定义的逐件文件、原始参数、裁切坐标与未通过点。
- props-[a-k]-v1.png.generation.json：11 次独立生成记录。
- pieces/*.png.provenance.json：每件派生来源。
- references/：结构参考联系表，包含元素 ID、原始 frame 尺寸与占地；不作为运行时原创素材。
- qa.json：完整校验数值与未通过状态。

## 母图原生尺寸

| 母图 | 实际原生尺寸 | 生成记录 |
|---|---|---|
| props-a-v1.png | 1536×1024 | props-a-v1.png.generation.json |
| props-b-v1.png | 1536×1024 | props-b-v1.png.generation.json |
| props-c-v1.png | 1536×1024 | props-c-v1.png.generation.json |
| props-d-v1.png | 1254×1254 | props-d-v1.png.generation.json |
| props-e-v1.png | 1254×1254 | props-e-v1.png.generation.json |
| props-f-v1.png | 1536×1024 | props-f-v1.png.generation.json |
| props-g-v1.png | 1536×1024 | props-g-v1.png.generation.json |
| props-h-v1.png | 1536×1024 | props-h-v1.png.generation.json |
| props-i-v1.png | 1086×1448 | props-i-v1.png.generation.json |
| props-j-v1.png | 1254×1254 | props-j-v1.png.generation.json |
| props-k-v1.png | 1254×1254 | props-k-v1.png.generation.json |

## 尚未通过

| ID | 检查 | 数值 | 门槛 | 文件 |
|---|---|---:|---:|---|
| 4007 | visible-aspect-deviation | 0.118 | 0.1 | 4007-mine-v1.png |
| 4027 | visible-aspect-deviation | 0.121 | 0.1 | 4027-mine-v1.png |
| 4048 | visible-aspect-deviation | 0.112 | 0.1 | 4048-mine-v1.png |
| 4049 | visible-aspect-deviation | 0.142 | 0.1 | 4049-mine-v1.png |
| 4050 | visible-aspect-deviation | 0.112 | 0.1 | 4050-mine-v1.png |
| 4052 | visible-aspect-deviation | 0.136 | 0.1 | 4052-mine-v1.png |
| 4071 | visible-aspect-deviation | 0.152 | 0.1 | 4071-mine-v2-crop.png |
| 4072 | visible-aspect-deviation | 0.148 | 0.1 | 4072-mine-v1.png |
| 4079 | visible-aspect-deviation | 0.154 | 0.1 | 4079-mine-v1.png |
| 4082 | visible-aspect-deviation | 0.343 | 0.1 | 4082-mine-v1.png |
| 4084 | visible-aspect-deviation | 0.191 | 0.1 | 4084-mine-v1.png |

宽高比数值不超阈值也不代表内部区界、出口/连接口、图元占地已经通过。地砖纹样和坑壁区域还需按源位置匹配，重复/相邻接缝、墙柱连接、特殊复合结构内部区域以及锚点均未通过。

4017 复用 4014，4023 复用 4019；仅因源画面 SHA256 相同，不计作新增独立绘制。保留各自原始 offset、GridAttr、footprint 和待验状态。

本批没有浏览器或游戏内截图验收。没有修改 town、snow、全局统计或共享 Git。
