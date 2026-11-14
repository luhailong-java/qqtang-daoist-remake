# 玉龙迎云入场特效

源物品 1658「神龙入场」对应社区客户端的 `object/enter/enter32_stand.img` 和库存 `res/uiRes/icon/enter/enter32.img`。世界成员六个位置均为不同的 100×100 不透明图，原偏移均为 (0, 0)，声明一个方向。库存源图为 56×53。见[源记录](source-contract.json)。

按源位置重画星空、窄光柱、宽光柱和金白龙影、暖色显形、青玉龙、青玉亮边。六个位置各导出一张 400×400 RGBA，保留原先的方形不透明画面。为保持星空连续，各相位使用同一张原创星空，按位置叠加独立的透明光柱和玉龙图层。光柱纵向铺满原画幅，龙身按等比放置。第 04 张另等比派生 256×256 库存候选，覆盖 71 个 enter 源 ID 中的一项。见[世界清单](world-art.json)和[库存清单](art.json)。

两次内置 imagegen 分别返回 1254×1254 的 RGB 星空和 1536×1024 的 RGBA 光柱／龙图。实际模型和质量字段未披露。见[星空生成记录](entry-background.png.generation.json)、[图层生成记录](entry-layers.png.generation.json)和[裁口](selection.json)。

逐像素重放通过。透明图层裁口边缘的最大 alpha 为 1。四种龙图层的两个中空测点 alpha 为 0–1，合成后显示后方星空或光柱。两条光柱的上下边中心均有可见像素。04 和 05 在 32 px 下主要靠光柱宽度区分，龙身高光变化较细微。见[源图、候选及小尺寸对照](contact-source-candidate-mobile.png)和[检查记录](verification.json)。

画面待用户审核。原播放帧时长、层级和实际入场触发点待验证，候选未接入游戏运行。

```powershell
python -B assets/items/entry-effects/world-1658/effect.py
```
