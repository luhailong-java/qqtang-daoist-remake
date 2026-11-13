# 《灵葫大作战》道家 Q 版美术进度 · 2026-11-13

这轮补绘了道童西、南向步行、三组地图机关及 18 件库存图。触屏方向按钮改用玉纹金边图标；持有护盾的存活角色显示自有护体泡光。移动、道具和地图规则没有修改。

本地《QQ堂》静态参考是与社区 v1.3.4 发行包逐字节相符的 QQTang-Local 样本。它用于核对资源号、方向、原帧和尺寸。腾讯未修改的目标客户端仍未核实，原动作时序和挂点继续待核验。 [QQ堂来源与使用范围](QQTANG_REFERENCE_SOURCE.md)

| 内容 | 本轮改动 | 人工审核 |
| --- | --- | --- |
| 道童步行 | 西向 f12–17、南向 f18–23，各 6 张原创透明图。结合此前东、北向，道童四个方向均有步行候选。 | [西向](../assets/characters/motion-continuation-20261113/daoist-child-west/review-light-dark.png) · [南向](../assets/characters/motion-continuation-20261113/daoist-child-south/review-light-dark.png) |
| 地图机关 | 17033、17037、17038 各 6 帧，保留 40×40 原逻辑格及 `[0,0]` 源偏移。提供 40 和 160 像素导出。 | [逐帧对照](MAP_GRATE_ANIMATION_REVIEW_20261113.md) |
| 灵翼 | `fpack` 库存编号 25、26、27、111、133、147。 | [小尺寸预览](../assets/items/wing-adornments/spirit-wings-a/contact-mobile-32-48-64.png) · [来源与偏差](../assets/items/wing-adornments/spirit-wings-a/README.md) |
| 勋章 | `frame` 库存编号 2398–2403，分别对应雪花、灯笼、四叶草、利剑、龙舟、神盾。原图均为 56×53，输出为 256×256 透明图。 | [双底预览](../assets/items/profile-frames/elemental-medals/contact-32-48-64-256.png) · [来源](../assets/items/profile-frames/elemental-medals/source-contract.json) |
| 风物背景 | `bg` 库存编号 1、2、3、4、7、55，涵盖四季、云海、林径。输出为无边框的 256×256 满幅缩略图。 | [小尺寸预览](../assets/items/scenic-backgrounds/four-seasons-a/contact-mobile-32-48-64.png) · [来源](../assets/items/scenic-backgrounds/four-seasons-a/README.md) |
| 触屏方向 | 上、左、下、右四枚原创方向图，128 像素透明导出，按原控件顺序以 26 像素显示。 | [双底预览](../assets/ui/touch-icons-20261113/contact-20-24-32-128.png) |

库存图、角色新动作和地图序列已加入本地服务的 `/art.html`，当前用于人工审核。勋章在 32 像素下剑身偏细，部分灵翼的轮廓宽高比和原参考有差异；道童需要连看支撑脚、衣摆和头顶衔接，机关需要看整图接缝。库存图不代表已做好佩戴、边框展示或实景背景。

触屏四键原有的触控面积、方向值、按住移动和辅助名称均保留。护体泡光复用项目现有 `magic3` 第 2 帧，只在存活、未被困且当前持有护盾时绘制。道具拾取图仍单独使用原接入的自有盾牌。画面跟随已有状态，未借用无敌计时，也没有赋予 `magic3` 未经证实的原版挂点或时长。当前圆形效果的尺寸、人物遮挡和小屏观感待实机审核。 [护体泡光](../assets/effects/states/protection-bubble/02.png)

勋章及触屏图均由内置图像生成产出。实际模型和质量未披露；按图记录了母图、参考文件、调用和导出。 [勋章提示词](../assets/items/profile-frames/elemental-medals/elemental-medals-v1.prompt.txt) · [方向图标提示词](../assets/ui/touch-icons-20261113/jade-touch-v1.prompt.txt)

2,945 个源物品 ID 中已有 577 个至少有一张候选图，尚缺 2,368 个。45 个地图多帧定义中有 28 个候选序列，覆盖 134 个源位置，尚缺 17 组。整款美术仍在制作，其余角色与怪物动作、装扮世界帧、完整 UI 状态及手游实机终验仍待完成。 [本轮可核对缺口](ART_PROGRESS_20261113.json)
