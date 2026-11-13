# 道家 Q 版美术替换进度 · 2026-11-12

当前对局开始使用自有糖泡、爆开云火、增益道具、针、护盾、包子、普通怪物与 Boss 外观。默认资源表也指向自有画稿，四位可选角色继续使用原来的自有身份。针、护盾、包子和技术稿怪物使用本项目的临时外观映射，原生资源 ID 待核。 [运行替换与文件来源](RUNTIME_ART_REPLACEMENT_20261112.md) · [针、护盾、包子小尺寸预览](../assets/runtime/battle-props-20261112/review-mobile.png)

773 个地图元素定义已关联现有自有首帧，377 张源场景引用的正 ID 均有候选图。补齐定义前后都可解析的 352 条场景投影逐项一致。新补 17030 的六相位和四个方向的玉箭地砖各五相位，可在美术检查页逐帧看。45 个多帧元素中已有 25 个候选序列，剩余 20 个待制作。 [地图接入和几何对照](FULL_MAP_ART_COVERAGE_20261112.md) · [17030](../assets/maps/animation-continuation-20261112/17030/previews/six-phase-double-background.png) · [17134](../assets/maps/animation-continuation-20261112/17134/previews/five-phase-contact.png) · [17135](../assets/maps/animation-continuation-20261112/17135/previews/five-phase-contact.png)

| 类别 | 本批候选 | 人工审核入口 |
|---|---:|---|
| 冠帽 | 42 个库存 ID | [冠帽七批预览](HAT_INVENTORY_20261112.md) |
| 背饰 | 五阶披风、六款背包，共 11 个库存 ID，披风另有 60 张世界相位 | [披风](HONOR_CAPES_DELIVERY_20261112.md) · [背包](../assets/items/back-adornments/travel-backpacks/previews/inventory-six-light.png) |
| 糖泡装扮 | 十二星座和果香甜点，共 24 个库存 ID | [糖泡合并清单](../assets/items/bubble-skins/inventory-combined.json) |
| 口部饰品 | 六件假面库存图 | [假面双底预览](../assets/items/mouth-adornments/cloud-masquerade-a/contact-native-256.png) |
| 角色动作 | 道童、月影各 6 张东向步行候选帧 | [道童](CHARACTER_MOTION_CONTINUATION_20261112.md) · [月影](../assets/characters/motion-continuation-20261112/moon-shadow-east/README.md) |

对局和界面现使用两段原创合成配乐和 19 个声音文件，按现有游戏事件触发。声音需在浏览器解锁后播放，受音量和声音开关控制，人工听审及各设备表现待确认。 [配乐与音效来源](../assets/audio/original-v1/manifest.json)

整款美术仍在制作。2,945 个源物品 ID 中 559 个已有至少一种候选，2,386 个还没有候选图。角色与怪物完整动作、装扮佩戴和世界相位、地图动态状态、UI 全状态、原音频范围和手游实机审核仍待完成。 [最新缺口清单](ART_PROGRESS_20261112C.json)

地图候选序列共覆盖 116 个源位置。道童北向步行补出六个源位置，依据七个源层的编码匹配，重复位置 f9 共用 f6，合计五张独立图。开始、暂停、关闭、下一步四个图标已接到原控件。16 像素预览中下一步的箭柄较短，保留现有按钮文字辅助识别。 [右箭地砖预览](../assets/maps/animation-continuation-20261112/17136/previews/five-phase-contact.png) · [左箭地砖预览](../assets/maps/animation-continuation-20261112/17137/previews/five-phase-contact.png) · [道童北向](../assets/characters/motion-continuation-20261112/daoist-child-north/review-light-dark.png) · [图标预览](../assets/ui/action-icons-20261112/contact-16-20-24-32-128.png)
