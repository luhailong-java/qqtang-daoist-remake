# water 原创图元候选

2026-10-26：32/32 条定义有候选，来自 32 幅不同源画面；6 张内置 image_gen 母图，0 条显式源画面别名。正式几何、锚点和游戏验收通过 0 条。

所有地图坐标、footprint、GridAttr 和源 offset 保留原值。每件导出画布为原始 frame 的 4 倍，只做裁切、等比适配和透明画布放置，不代表模型原生 4 倍细节。

每次实际附上 image 邮件/组队两主图及本批结构联系表。逐图记录保存配置目标、实际参数、返回文件、引用 SHA256 和 UTC 时间；宿主没有披露实际型号/质量，均为 null。

## 文件

- art.json：逐件文件、原始参数、裁切坐标与待验项。
- props-*-v1.png.generation.json：每次独立生成记录。
- pieces/*.png.provenance.json：每件派生来源与实际尺寸。
- references/：带元素 ID、原始 frame 尺寸和占地的结构参考，仅供取证。
- qa.json：身份/透明/尺寸/元数据验证和完整未通过点。
- candidate-contact.png：当前候选检查联系表，不是游戏内预览。

## 母图原生尺寸

| 母图 | 实际原生尺寸 | 记录 |
|---|---|---|
| props-a-v1.png | 1536×1024 | props-a-v1.png.generation.json |
| props-b-v1.png | 1536×1024 | props-b-v1.png.generation.json |
| props-c-v1.png | 1536×1024 | props-c-v1.png.generation.json |
| props-d-v1.png | 1536×1024 | props-d-v1.png.generation.json |
| props-e-v1.png | 1536×1024 | props-e-v1.png.generation.json |
| props-f-v1.png | 1536×1024 | props-f-v1.png.generation.json |

## 尚未通过

| ID | 检查 | 数值 | 门槛 | 文件 |
|---|---|---:|---:|---|
| 5002 | visible-aspect-deviation | 0.101 | 0.1 | 5002-water-v2-crop.png |
| 5011 | visible-aspect-deviation | 0.201 | 0.1 | 5011-water-v1.png |
| 5013 | visible-aspect-deviation | 0.121 | 0.1 | 5013-water-v1.png |
| 5020 | visible-aspect-deviation | 0.108 | 0.1 | 5020-water-v1.png |
| 5037 | visible-aspect-deviation | 0.110 | 0.1 | 5037-water-v1.png |
| 5037 | visible-horizontal-plank-count | 4 | 5 | 5037-water-v1.png |

宽高比不超阈值也不等于内部区界、连接口、占地/轮廓与源图匹配已经通过。相邻接缝、重复边、源锚点及实际落位均待验。

源画面别名：无；每幅源画面均独立制作。

本批没有浏览器或游戏内截图验收，没有修改其他族、全局生产统计或共享 Git。
