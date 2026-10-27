# 地图原创美术生产库存

核对日期：2026-10-26。范围为已静态提取的721条地图元素定义；不等同于全部原版资源。以 `USER_REQUIREMENTS_LOCK_20261026.md` 的同坐标、同占地要求为准。

## 当前覆盖

- 元素 **721** 条，候选family **18** 组；stand候选成功解码 **721** 条。
- 去重后 **637** 个DIMG、**630** 幅可见画面；引用 **630** 张原生首个非空帧PNG（本轮family目录新增 **613** 张、复用已留存town参考 **17** 张），另有 **18** 张有限代表联系表。
- 原创已画候选 **338** 条（46.88%），待制作 **383** 条；**正式几何/锚点/游戏验收通过0条，验收覆盖0%**。
- 原图参考不计原创完成；同画面别名 **91** 条单列，不能把重复源图计为多次原创制作。

`assets/maps/production-index.json` 是完整721条逐项生产清单，含每条family/theme/size/GridAttr、使用地图、候选资源路径、原生帧尺寸、哈希、去重组、原创稿路径及待验收状态。`references/qqtang-map-data/visual-reference/families/index.json` 是同批取证索引；其中参考PNG仅供结构核对，不进入运行资源。

## 按family/theme与占地的清单

| 候选family / 主题 | 元素 | 占地分布（格） | 对应stand / 包内stand | 不同画面 | 原创候选 / 待作 | 代表联系表 |
|---|---:|---|---:|---:|---:|---|
| `desert` / 沙漠 | 43 | 11x2×4、14x2×1、1x1×15、1x2×2、1x3×3、1x4×1、1x6×2、2x1×2、2x2×2、2x3×1、2x4×2、4x3×1、5x2×1、6x2×2、7x2×2、8x2×2 | 43 / 54 | 41 | 43 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/desert/contact-sheet.png) |
| `snow` / 冰雪 | 47 | 1x1×32、1x2×2、2x1×2、2x2×9、4x2×2 | 47 / 47 | 46 | 47 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/snow/contact-sheet.png) |
| `town` / 中国城 | 38 | 15x3×1、1x1×32、1x2×3、3x2×1、4x2×1 | 38 / 39 | 38 | 38 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/town/contact-sheet.png) |
| `mine` / 矿洞 | 70 | 11x8×1、12x8×1、1x1×52、1x2×8、2x3×2、3x2×1、3x4×2、5x2×2、8x3×1 | 70 / 75 | 68 | 70 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/mine/contact-sheet.png) |
| `water` / 水面 | 32 | 15x2×1、1x1×27、2x1×1、3x2×1、4x2×1、5x2×1 | 32 / 34 | 32 | 32 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/water/contact-sheet.png) |
| `field` / 田野 | 24 | 1x1×23、3x2×1 | 24 / 25 | 24 | 6 / 18 | [查看](../references/qqtang-map-data/visual-reference/families/field/contact-sheet.png) |
| `bomb` / 炸弹场景 | 13 | 1x1×8、1x3×2、3x1×1、6x1×2 | 13 / 13 | 13 | 13 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/bomb/contact-sheet.png) |
| `bun` / 抢包山 | 27 | 1x1×18、3x3×4、4x2×1、4x3×1、5x2×2、5x4×1 | 27 / 27 | 26 | 18 / 9 | [查看](../references/qqtang-map-data/visual-reference/families/bun/contact-sheet.png) |
| `pig` / 小猪场景 | 14 | 1x1×9、2x1×2、2x2×1、3x2×1、4x3×1 | 14 / 14 | 14 | 14 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/pig/contact-sheet.png) |
| `treasure` / 寻宝 | 17 | 1x1×16、3x3×1 | 17 / 17 | 17 | 0 / 17 | [查看](../references/qqtang-map-data/visual-reference/families/treasure/contact-sheet.png) |
| `match` / 比武 | 9 | 13x1×1、15x4×1、1x1×5、1x9×2 | 9 / 9 | 9 | 9 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/match/contact-sheet.png) |
| `sculpture` / 雕塑 | 15 | 1x1×14、5x2×1 | 15 / 15 | 14 | 15 / 0 | [查看](../references/qqtang-map-data/visual-reference/families/sculpture/contact-sheet.png) |
| `machine` / 机械 | 66 | 10x1×1、15x1×2、1x1×40、1x13×1、2x1×15、2x2×1、3x1×2、3x13×1、4x1×1、5x1×1、5x2×1 | 66 / 76 | 65 | 33 / 33 | [查看](../references/qqtang-map-data/visual-reference/families/machine/contact-sheet.png) |
| `box` / 推箱子 | 66 | 1x1×65、3x3×1 | 66 / 66 | 66 | 0 / 66 | [查看](../references/qqtang-map-data/visual-reference/families/box/contact-sheet.png) |
| `practice` / 练习 | 22 | 1x1×20、3x2×1、4x2×1 | 22 / 22 | 22 | 0 / 22 | [查看](../references/qqtang-map-data/visual-reference/families/practice/contact-sheet.png) |
| `exploration` / 探险场景 | 60 | 1x1×41、1x3×2、1x4×4、1x8×1、2x2×3、3x1×3、3x3×1、4x1×4、8x1×1 | 60 / 87 | 54 | 0 / 60 | [查看](../references/qqtang-map-data/visual-reference/families/exploration/contact-sheet.png) |
| `common` / 通用场景 | 88 | 1x1×75、1x3×2、2x1×4、2x2×1、3x1×2、3x2×3、3x3×1 | 88 / 99 | 82 | 0 / 88 | [查看](../references/qqtang-map-data/visual-reference/families/common/contact-sheet.png) |
| `pve` / 探险关卡 | 70 | 11x2×4、14x2×1、1x1×43、1x2×2、1x3×3、1x4×1、1x6×2、2x1×2、2x2×3、2x3×1、2x4×2、6x2×2、7x2×2、8x2×2 | 70 / 117 | 69 | 0 / 70 | [查看](../references/qqtang-map-data/visual-reference/families/pve/contact-sheet.png) |

占地分布中的`2x1×3`表示定义占地2×1格的元素有3条，不是输出图像尺寸。包内stand数量可能大于721条所用范围；未关联的额外文件未批量导出。

## 现有原创稿与后续批次

town已存在的手绘切片仅标记为`painted-candidate-awaiting-validation`，不是原版几何或同坐标验收完成。当前依据art.json实际存在、哈希匹配且具有生成记录的文件计数；A/B源母图和切片不重复累计。

| 元素ID | 原创候选文件 | 状态 |
|---|---|---|
| 1001 | [1001-sand-ground.png](../assets/maps/desert/pieces/1001-sand-ground.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1002 | [1002-gold-brick.png](../assets/maps/desert/pieces/1002-gold-brick.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1003 | [1003-cinnabar-brick.png](../assets/maps/desert/pieces/1003-cinnabar-brick.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1004 | [1004-cloud-stone-block.png](../assets/maps/desert/pieces/1004-cloud-stone-block.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1005 | [1005-gold-fruit-planter.png](../assets/maps/desert/pieces/1005-gold-fruit-planter.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1006 | [1006-cinnabar-drum.png](../assets/maps/desert/pieces/1006-cinnabar-drum.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1007 | [1007-desert-v1.png](../assets/maps/desert/pieces/1007-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1008 | [1008-desert-v1.png](../assets/maps/desert/pieces/1008-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1009 | [1009-desert-v1.png](../assets/maps/desert/pieces/1009-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1010 | [1010-desert-v1.png](../assets/maps/desert/pieces/1010-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1011 | [1011-desert-v1.png](../assets/maps/desert/pieces/1011-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1012 | [1012-desert-source-alias-v1.png](../assets/maps/desert/pieces/1012-desert-source-alias-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1113 | [1113-desert-v1.png](../assets/maps/desert/pieces/1113-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1114 | [1114-desert-v1.png](../assets/maps/desert/pieces/1114-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1115 | [1115-desert-v1.png](../assets/maps/desert/pieces/1115-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1116 | [1116-desert-v1.png](../assets/maps/desert/pieces/1116-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1117 | [1117-desert-v1.png](../assets/maps/desert/pieces/1117-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1118 | [1118-desert-v1.png](../assets/maps/desert/pieces/1118-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1119 | [1119-desert-v1.png](../assets/maps/desert/pieces/1119-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1120 | [1120-desert-v1.png](../assets/maps/desert/pieces/1120-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1121 | [1121-desert-v1.png](../assets/maps/desert/pieces/1121-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1122 | [1122-desert-v1.png](../assets/maps/desert/pieces/1122-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1123 | [1123-desert-v1.png](../assets/maps/desert/pieces/1123-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1124 | [1124-desert-v1.png](../assets/maps/desert/pieces/1124-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1125 | [1125-desert-v1.png](../assets/maps/desert/pieces/1125-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1126 | [1126-desert-v1.png](../assets/maps/desert/pieces/1126-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1127 | [1127-desert-v1.png](../assets/maps/desert/pieces/1127-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1128 | [1128-desert-v1.png](../assets/maps/desert/pieces/1128-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1129 | [1129-desert-v1.png](../assets/maps/desert/pieces/1129-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1130 | [1130-desert-v1.png](../assets/maps/desert/pieces/1130-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1131 | [1131-desert-v1.png](../assets/maps/desert/pieces/1131-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1132 | [1132-desert-source-alias-v1.png](../assets/maps/desert/pieces/1132-desert-source-alias-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1133 | [1133-desert-v1.png](../assets/maps/desert/pieces/1133-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1134 | [1134-desert-v1.png](../assets/maps/desert/pieces/1134-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1135 | [1135-desert-v1.png](../assets/maps/desert/pieces/1135-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1136 | [1136-desert-v1.png](../assets/maps/desert/pieces/1136-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1137 | [1137-desert-v1.png](../assets/maps/desert/pieces/1137-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1138 | [1138-desert-v1.png](../assets/maps/desert/pieces/1138-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1139 | [1139-desert-v1.png](../assets/maps/desert/pieces/1139-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1140 | [1140-desert-v1.png](../assets/maps/desert/pieces/1140-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1141 | [1141-desert-v1.png](../assets/maps/desert/pieces/1141-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1142 | [1142-desert-v1.png](../assets/maps/desert/pieces/1142-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 1143 | [1143-desert-v1.png](../assets/maps/desert/pieces/1143-desert-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2001 | [2001-snow-v1.png](../assets/maps/snow/pieces/2001-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2002 | [2002-snow-v1.png](../assets/maps/snow/pieces/2002-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2003 | [2003-snow-v1.png](../assets/maps/snow/pieces/2003-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2004 | [2004-snow-v1.png](../assets/maps/snow/pieces/2004-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2005 | [2005-snow-v1.png](../assets/maps/snow/pieces/2005-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2006 | [2006-snow-v1.png](../assets/maps/snow/pieces/2006-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2007 | [2007-snow-v1.png](../assets/maps/snow/pieces/2007-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2008 | [2008-snow-v1.png](../assets/maps/snow/pieces/2008-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2011 | [2011-snow-v1.png](../assets/maps/snow/pieces/2011-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2012 | [2012-snow-v1.png](../assets/maps/snow/pieces/2012-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2013 | [2013-snow-v1.png](../assets/maps/snow/pieces/2013-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2014 | [2014-snow-v1.png](../assets/maps/snow/pieces/2014-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2015 | [2015-snow-v1.png](../assets/maps/snow/pieces/2015-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2016 | [2016-snow-v1.png](../assets/maps/snow/pieces/2016-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2017 | [2017-snow-v1.png](../assets/maps/snow/pieces/2017-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2018 | [2018-snow-v1.png](../assets/maps/snow/pieces/2018-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2019 | [2019-snow-v1.png](../assets/maps/snow/pieces/2019-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2020 | [2020-snow-v1.png](../assets/maps/snow/pieces/2020-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2021 | [2021-snow-v1.png](../assets/maps/snow/pieces/2021-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2022 | [2022-snow-v1.png](../assets/maps/snow/pieces/2022-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2023 | [2023-snow-v1.png](../assets/maps/snow/pieces/2023-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2024 | [2024-snow-v1.png](../assets/maps/snow/pieces/2024-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2025 | [2025-snow-v1.png](../assets/maps/snow/pieces/2025-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2026 | [2026-snow-v1.png](../assets/maps/snow/pieces/2026-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2027 | [2027-snow-v1.png](../assets/maps/snow/pieces/2027-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2028 | [2028-snow-v1.png](../assets/maps/snow/pieces/2028-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2029 | [2029-snow-v1.png](../assets/maps/snow/pieces/2029-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2030 | [2030-snow-v1.png](../assets/maps/snow/pieces/2030-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2031 | [2031-snow-v1.png](../assets/maps/snow/pieces/2031-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2032 | [2032-snow-v1.png](../assets/maps/snow/pieces/2032-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2033 | [2033-snow-v1.png](../assets/maps/snow/pieces/2033-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2034 | [2034-snow-v1.png](../assets/maps/snow/pieces/2034-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2035 | [2035-snow-v1.png](../assets/maps/snow/pieces/2035-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2036 | [2036-snow-v1.png](../assets/maps/snow/pieces/2036-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2037 | [2037-snow-v1.png](../assets/maps/snow/pieces/2037-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2038 | [2038-snow-v1.png](../assets/maps/snow/pieces/2038-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2039 | [2039-snow-v1.png](../assets/maps/snow/pieces/2039-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2040 | [2040-snow-v1.png](../assets/maps/snow/pieces/2040-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2041 | [2041-snow-v1.png](../assets/maps/snow/pieces/2041-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2042 | [2042-snow-v1.png](../assets/maps/snow/pieces/2042-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2043 | [2043-snow-v1.png](../assets/maps/snow/pieces/2043-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2044 | [2044-snow-v1.png](../assets/maps/snow/pieces/2044-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2045 | [2045-snow-v1.png](../assets/maps/snow/pieces/2045-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2046 | [2046-snow-v1.png](../assets/maps/snow/pieces/2046-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2047 | [2047-snow-v1.png](../assets/maps/snow/pieces/2047-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2048 | [2048-snow-v1.png](../assets/maps/snow/pieces/2048-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 2049 | [2049-snow-v1.png](../assets/maps/snow/pieces/2049-snow-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3001 | [3001-wood-floor.png](../assets/maps/town/pieces/3001-wood-floor.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3002 | [3002-pavement-light.png](../assets/maps/town/pieces/3002-pavement-light.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3003 | [3003-pavement-dark.png](../assets/maps/town/pieces/3003-pavement-dark.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3004 | [3004-drum.png](../assets/maps/town/pieces/3004-drum.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3005 | [3005-red-shrine.png](../assets/maps/town/pieces/3005-red-shrine.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3006 | [3006-taiji-courtyard-slab.png](../assets/maps/town/pieces/3006-taiji-courtyard-slab.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3007 | [3007-house-gold.png](../assets/maps/town/pieces/3007-house-gold.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3008 | [3008-house-grey.png](../assets/maps/town/pieces/3008-house-grey.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3009 | [3009-house-jade.png](../assets/maps/town/pieces/3009-house-jade.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3010 | [3010-shrub.png](../assets/maps/town/pieces/3010-shrub.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3011 | [3011-pool-bank.png](../assets/maps/town/pieces/3011-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3012 | [3012-pool-bank.png](../assets/maps/town/pieces/3012-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3013 | [3013-pool-bank.png](../assets/maps/town/pieces/3013-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3014 | [3014-pedestal-blue.png](../assets/maps/town/pieces/3014-pedestal-blue.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3015 | [3015-pedestal-jade.png](../assets/maps/town/pieces/3015-pedestal-jade.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3017 | [3017-target-pedestal.png](../assets/maps/town/pieces/3017-target-pedestal.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3018 | [3018-bamboo-pedestal.png](../assets/maps/town/pieces/3018-bamboo-pedestal.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3019 | [3019-courtyard-shop.png](../assets/maps/town/pieces/3019-courtyard-shop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3020 | [3020-lantern-column.png](../assets/maps/town/pieces/3020-lantern-column.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3022 | [3022-pool-bank.png](../assets/maps/town/pieces/3022-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3023 | [3023-pool-bank.png](../assets/maps/town/pieces/3023-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3024 | [3024-pool-bank.png](../assets/maps/town/pieces/3024-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3025 | [3025-pool-bank.png](../assets/maps/town/pieces/3025-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3026 | [3026-pool-bank.png](../assets/maps/town/pieces/3026-pool-bank.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3050 | [3050-dragon-lantern.png](../assets/maps/town/pieces/3050-dragon-lantern.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3051 | [3051-stone-lamp.png](../assets/maps/town/pieces/3051-stone-lamp.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3053 | [3053-stone-floor.png](../assets/maps/town/pieces/3053-stone-floor.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3054 | [3054-sun-pedestal-copper.png](../assets/maps/town/pieces/3054-sun-pedestal-copper.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3055 | [3055-sun-pedestal-red.png](../assets/maps/town/pieces/3055-sun-pedestal-red.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3056 | [3056-gold-pavilion.png](../assets/maps/town/pieces/3056-gold-pavilion.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3057 | [3057-cypress.png](../assets/maps/town/pieces/3057-cypress.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3058 | [3058-palace-wall-strip.png](../assets/maps/town/pieces/3058-palace-wall-strip.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3059 | [3059-palace-courtyard-floor.png](../assets/maps/town/pieces/3059-palace-courtyard-floor.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3060 | [3060-daoist-boy-guardian-statue.png](../assets/maps/town/pieces/3060-daoist-boy-guardian-statue.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3061 | [3061-moon-girl-guardian-statue.png](../assets/maps/town/pieces/3061-moon-girl-guardian-statue.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3120 | [3120-rock-wall-left.png](../assets/maps/town/pieces/3120-rock-wall-left.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3121 | [3121-rock-wall-right.png](../assets/maps/town/pieces/3121-rock-wall-right.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 3122 | [3122-rock-wall-center.png](../assets/maps/town/pieces/3122-rock-wall-center.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4001 | [4001-mine-v1.png](../assets/maps/mine/pieces/4001-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4002 | [4002-mine-v1.png](../assets/maps/mine/pieces/4002-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4003 | [4003-mine-v1.png](../assets/maps/mine/pieces/4003-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4004 | [4004-mine-v1.png](../assets/maps/mine/pieces/4004-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4005 | [4005-mine-v1.png](../assets/maps/mine/pieces/4005-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4006 | [4006-mine-v1.png](../assets/maps/mine/pieces/4006-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4007 | [4007-mine-v1.png](../assets/maps/mine/pieces/4007-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4008 | [4008-mine-v1.png](../assets/maps/mine/pieces/4008-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4009 | [4009-mine-v1.png](../assets/maps/mine/pieces/4009-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4010 | [4010-mine-v1.png](../assets/maps/mine/pieces/4010-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4011 | [4011-mine-v1.png](../assets/maps/mine/pieces/4011-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4012 | [4012-mine-v1.png](../assets/maps/mine/pieces/4012-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4013 | [4013-mine-v1.png](../assets/maps/mine/pieces/4013-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4014 | [4014-mine-v1.png](../assets/maps/mine/pieces/4014-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4015 | [4015-mine-v1.png](../assets/maps/mine/pieces/4015-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4016 | [4016-mine-v1.png](../assets/maps/mine/pieces/4016-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4017 | [4017-mine-source-alias-v1.png](../assets/maps/mine/pieces/4017-mine-source-alias-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4018 | [4018-mine-v1.png](../assets/maps/mine/pieces/4018-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4019 | [4019-mine-v1.png](../assets/maps/mine/pieces/4019-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4020 | [4020-mine-v1.png](../assets/maps/mine/pieces/4020-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4021 | [4021-mine-v1.png](../assets/maps/mine/pieces/4021-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4022 | [4022-mine-v1.png](../assets/maps/mine/pieces/4022-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4023 | [4023-mine-source-alias-v1.png](../assets/maps/mine/pieces/4023-mine-source-alias-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4024 | [4024-mine-v1.png](../assets/maps/mine/pieces/4024-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4025 | [4025-mine-v1.png](../assets/maps/mine/pieces/4025-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4026 | [4026-mine-v1.png](../assets/maps/mine/pieces/4026-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4027 | [4027-mine-v1.png](../assets/maps/mine/pieces/4027-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4028 | [4028-mine-v1.png](../assets/maps/mine/pieces/4028-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4029 | [4029-mine-v2-crop.png](../assets/maps/mine/pieces/4029-mine-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4030 | [4030-mine-v1.png](../assets/maps/mine/pieces/4030-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4031 | [4031-mine-v1.png](../assets/maps/mine/pieces/4031-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4032 | [4032-mine-v1.png](../assets/maps/mine/pieces/4032-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4033 | [4033-mine-v1.png](../assets/maps/mine/pieces/4033-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4034 | [4034-mine-v1.png](../assets/maps/mine/pieces/4034-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4035 | [4035-mine-v1.png](../assets/maps/mine/pieces/4035-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4036 | [4036-mine-v1.png](../assets/maps/mine/pieces/4036-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4037 | [4037-mine-v1.png](../assets/maps/mine/pieces/4037-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4038 | [4038-mine-v1.png](../assets/maps/mine/pieces/4038-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4039 | [4039-mine-v1.png](../assets/maps/mine/pieces/4039-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4040 | [4040-mine-v1.png](../assets/maps/mine/pieces/4040-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4041 | [4041-mine-v1.png](../assets/maps/mine/pieces/4041-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4042 | [4042-mine-v1.png](../assets/maps/mine/pieces/4042-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4043 | [4043-mine-v1.png](../assets/maps/mine/pieces/4043-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4044 | [4044-mine-v1.png](../assets/maps/mine/pieces/4044-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4045 | [4045-mine-v1.png](../assets/maps/mine/pieces/4045-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4046 | [4046-mine-v1.png](../assets/maps/mine/pieces/4046-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4047 | [4047-mine-v1.png](../assets/maps/mine/pieces/4047-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4048 | [4048-mine-v1.png](../assets/maps/mine/pieces/4048-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4049 | [4049-mine-v1.png](../assets/maps/mine/pieces/4049-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4050 | [4050-mine-v1.png](../assets/maps/mine/pieces/4050-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4051 | [4051-mine-v1.png](../assets/maps/mine/pieces/4051-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4052 | [4052-mine-v1.png](../assets/maps/mine/pieces/4052-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4053 | [4053-mine-v2-crop.png](../assets/maps/mine/pieces/4053-mine-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4054 | [4054-mine-v1.png](../assets/maps/mine/pieces/4054-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4055 | [4055-mine-v1.png](../assets/maps/mine/pieces/4055-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4056 | [4056-mine-v1.png](../assets/maps/mine/pieces/4056-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4057 | [4057-mine-v1.png](../assets/maps/mine/pieces/4057-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4058 | [4058-mine-v1.png](../assets/maps/mine/pieces/4058-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4059 | [4059-mine-v1.png](../assets/maps/mine/pieces/4059-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4060 | [4060-mine-v1.png](../assets/maps/mine/pieces/4060-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4070 | [4070-mine-v2-crop.png](../assets/maps/mine/pieces/4070-mine-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4071 | [4071-mine-v2-crop.png](../assets/maps/mine/pieces/4071-mine-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4072 | [4072-mine-v1.png](../assets/maps/mine/pieces/4072-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4078 | [4078-mine-v1.png](../assets/maps/mine/pieces/4078-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4079 | [4079-mine-v1.png](../assets/maps/mine/pieces/4079-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4080 | [4080-mine-v1.png](../assets/maps/mine/pieces/4080-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4081 | [4081-mine-v1.png](../assets/maps/mine/pieces/4081-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4082 | [4082-mine-v1.png](../assets/maps/mine/pieces/4082-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4083 | [4083-mine-v1.png](../assets/maps/mine/pieces/4083-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 4084 | [4084-mine-v1.png](../assets/maps/mine/pieces/4084-mine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5001 | [5001-water-v1.png](../assets/maps/water/pieces/5001-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5002 | [5002-water-v2-crop.png](../assets/maps/water/pieces/5002-water-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5003 | [5003-water-v1.png](../assets/maps/water/pieces/5003-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5004 | [5004-water-v1.png](../assets/maps/water/pieces/5004-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5005 | [5005-water-v2-crop.png](../assets/maps/water/pieces/5005-water-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5006 | [5006-water-v1.png](../assets/maps/water/pieces/5006-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5007 | [5007-water-v1.png](../assets/maps/water/pieces/5007-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5008 | [5008-water-v1.png](../assets/maps/water/pieces/5008-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5009 | [5009-water-v1.png](../assets/maps/water/pieces/5009-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5010 | [5010-water-v1.png](../assets/maps/water/pieces/5010-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5011 | [5011-water-v1.png](../assets/maps/water/pieces/5011-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5012 | [5012-water-v1.png](../assets/maps/water/pieces/5012-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5013 | [5013-water-v1.png](../assets/maps/water/pieces/5013-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5014 | [5014-water-v1.png](../assets/maps/water/pieces/5014-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5015 | [5015-water-v1.png](../assets/maps/water/pieces/5015-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5016 | [5016-water-v1.png](../assets/maps/water/pieces/5016-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5017 | [5017-water-v1.png](../assets/maps/water/pieces/5017-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5018 | [5018-water-v1.png](../assets/maps/water/pieces/5018-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5019 | [5019-water-v1.png](../assets/maps/water/pieces/5019-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5020 | [5020-water-v1.png](../assets/maps/water/pieces/5020-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5021 | [5021-water-v1.png](../assets/maps/water/pieces/5021-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5023 | [5023-water-v1.png](../assets/maps/water/pieces/5023-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5024 | [5024-water-v2-crop.png](../assets/maps/water/pieces/5024-water-v2-crop.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5025 | [5025-water-v1.png](../assets/maps/water/pieces/5025-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5026 | [5026-water-v1.png](../assets/maps/water/pieces/5026-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5028 | [5028-water-v1.png](../assets/maps/water/pieces/5028-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5029 | [5029-water-v1.png](../assets/maps/water/pieces/5029-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5030 | [5030-water-v1.png](../assets/maps/water/pieces/5030-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5034 | [5034-water-v1.png](../assets/maps/water/pieces/5034-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5035 | [5035-water-v1.png](../assets/maps/water/pieces/5035-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5036 | [5036-water-v1.png](../assets/maps/water/pieces/5036-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 5037 | [5037-water-v1.png](../assets/maps/water/pieces/5037-water-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 6001 | [6001-field-v1.png](../assets/maps/field/pieces/6001-field-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 6002 | [6002-field-v1.png](../assets/maps/field/pieces/6002-field-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 6003 | [6003-field-v1.png](../assets/maps/field/pieces/6003-field-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 6004 | [6004-field-v1.png](../assets/maps/field/pieces/6004-field-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 6006 | [6006-field-v1.png](../assets/maps/field/pieces/6006-field-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 6008 | [6008-field-v1.png](../assets/maps/field/pieces/6008-field-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7001 | [7001-turf-light.png](../assets/maps/bomb/pieces/7001-turf-light.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7002 | [7002-turf-dark.png](../assets/maps/bomb/pieces/7002-turf-dark.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7003 | [7003-spectators-own-01.png](../assets/maps/bomb/pieces/7003-spectators-own-01.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7004 | [7004-spectators-own-02.png](../assets/maps/bomb/pieces/7004-spectators-own-02.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7005 | [7005-cone-red.png](../assets/maps/bomb/pieces/7005-cone-red.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7006 | [7006-cone-blue.png](../assets/maps/bomb/pieces/7006-cone-blue.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7007 | [7007-goal-left.png](../assets/maps/bomb/pieces/7007-goal-left.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7008 | [7008-goal-right.png](../assets/maps/bomb/pieces/7008-goal-right.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7010 | [7010-corner-flag-red.png](../assets/maps/bomb/pieces/7010-corner-flag-red.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7011 | [7011-blank-scoreboard.png](../assets/maps/bomb/pieces/7011-blank-scoreboard.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7012 | [7012-football-field.png](../assets/maps/bomb/pieces/7012-football-field.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7013 | [7013-football-field.png](../assets/maps/bomb/pieces/7013-football-field.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 7014 | [7014-football-field.png](../assets/maps/bomb/pieces/7014-football-field.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8001 | [8001-green-block.png](../assets/maps/bun/pieces/8001-green-block.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8002 | [8002-green-block-leaf.png](../assets/maps/bun/pieces/8002-green-block-leaf.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8003 | [8003-yellow-block.png](../assets/maps/bun/pieces/8003-yellow-block.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8004 | [8004-yellow-block-peel.png](../assets/maps/bun/pieces/8004-yellow-block-peel.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8005 | [8005-bamboo-steamer.png](../assets/maps/bun/pieces/8005-bamboo-steamer.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8006 | [8006-jade-cylinder.png](../assets/maps/bun/pieces/8006-jade-cylinder.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8007 | [8007-blue-cloud-stone.png](../assets/maps/bun/pieces/8007-blue-cloud-stone.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8008 | [8008-three-jade-hills.png](../assets/maps/bun/pieces/8008-three-jade-hills.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8009 | [8009-bun-shop-red.png](../assets/maps/bun/pieces/8009-bun-shop-red.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8010 | [8010-bun-shop-jade.png](../assets/maps/bun/pieces/8010-bun-shop-jade.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8012 | [8012-round-tree.png](../assets/maps/bun/pieces/8012-round-tree.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8014 | [8014-bun-shop-red-state.png](../assets/maps/bun/pieces/8014-bun-shop-red-state.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8015 | [8015-gate-down.png](../assets/maps/bun/pieces/8015-gate-down.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8018 | [8018-blue-crystal.png](../assets/maps/bun/pieces/8018-blue-crystal.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8019 | [8019-restriction-block.png](../assets/maps/bun/pieces/8019-restriction-block.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8021 | [8021-stone-stack-three.png](../assets/maps/bun/pieces/8021-stone-stack-three.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8022 | [8022-stone-stack-two.png](../assets/maps/bun/pieces/8022-stone-stack-two.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 8023 | [8023-stone-stack-one.png](../assets/maps/bun/pieces/8023-stone-stack-one.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9001 | [9001-cobble-light.png](../assets/maps/pig/pieces/9001-cobble-light.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9002 | [9002-cobble-warm.png](../assets/maps/pig/pieces/9002-cobble-warm.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9003 | [9003-market-sign-left.png](../assets/maps/pig/pieces/9003-market-sign-left.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9004 | [9004-market-guildhouse.png](../assets/maps/pig/pieces/9004-market-guildhouse.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9005 | [9005-market-inn.png](../assets/maps/pig/pieces/9005-market-inn.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9006 | [9006-produce-stall.png](../assets/maps/pig/pieces/9006-produce-stall.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9007 | [9007-pig-pen-left-v2.png](../assets/maps/pig/pieces/9007-pig-pen-left-v2.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9008 | [9008-pig-pen-right-v2.png](../assets/maps/pig/pieces/9008-pig-pen-right-v2.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9009 | [9009-stone-well-v2.png](../assets/maps/pig/pieces/9009-stone-well-v2.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9010 | [9010-jade-barrel.png](../assets/maps/pig/pieces/9010-jade-barrel.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9011 | [9011-rice-block-v2.png](../assets/maps/pig/pieces/9011-rice-block-v2.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9012 | [9012-wooden-crate-v2.png](../assets/maps/pig/pieces/9012-wooden-crate-v2.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9013 | [9013-narrow-kiosk-v2.png](../assets/maps/pig/pieces/9013-narrow-kiosk-v2.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 9014 | [9014-market-sign-right.png](../assets/maps/pig/pieces/9014-market-sign-right.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11001 | [11001-martial-floor.png](../assets/maps/match/pieces/11001-martial-floor.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11002 | [11002-martial-stone-sand.png](../assets/maps/match/pieces/11002-martial-stone-sand.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11003 | [11003-martial-stone-grey.png](../assets/maps/match/pieces/11003-martial-stone-grey.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11004 | [11004-martial-gate.png](../assets/maps/match/pieces/11004-martial-gate.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11005 | [11005-hedge-left.png](../assets/maps/match/pieces/11005-hedge-left.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11006 | [11006-hedge-right.png](../assets/maps/match/pieces/11006-hedge-right.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11007 | [11007-hedge-top.png](../assets/maps/match/pieces/11007-hedge-top.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11008 | [11008-cloud-drum.png](../assets/maps/match/pieces/11008-cloud-drum.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 11009 | [11009-jade-lock-chest.png](../assets/maps/match/pieces/11009-jade-lock-chest.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12001 | [12001-painted-grass.png](../assets/maps/sculpture/pieces/12001-painted-grass.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12002 | [12002-blue-stone.png](../assets/maps/sculpture/pieces/12002-blue-stone.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12003 | [12003-green-stone.png](../assets/maps/sculpture/pieces/12003-green-stone.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12004 | [12004-grey-idol.png](../assets/maps/sculpture/pieces/12004-grey-idol.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12005 | [12005-painted-grass.png](../assets/maps/sculpture/pieces/12005-painted-grass.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12006 | [12006-pressure-square.png](../assets/maps/sculpture/pieces/12006-pressure-square.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12007 | [12007-pressure-triangle.png](../assets/maps/sculpture/pieces/12007-pressure-triangle.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12008 | [12008-red-totem.png](../assets/maps/sculpture/pieces/12008-red-totem.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12009 | [12009-green-totem.png](../assets/maps/sculpture/pieces/12009-green-totem.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12010 | [12010-palm-planter.png](../assets/maps/sculpture/pieces/12010-palm-planter.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12011 | [12011-gold-kiosk.png](../assets/maps/sculpture/pieces/12011-gold-kiosk.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12012 | [12012-ivory-kiosk.png](../assets/maps/sculpture/pieces/12012-ivory-kiosk.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12020 | [12020-green-block-left.png](../assets/maps/sculpture/pieces/12020-green-block-left.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12021 | [12021-green-block-right.png](../assets/maps/sculpture/pieces/12021-green-block-right.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 12022 | [12022-painted-grass.png](../assets/maps/sculpture/pieces/12022-painted-grass.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13001 | [13001-machine-v1.png](../assets/maps/machine/pieces/13001-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13002 | [13002-machine-v1.png](../assets/maps/machine/pieces/13002-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13003 | [13003-machine-v1.png](../assets/maps/machine/pieces/13003-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13004 | [13004-machine-v1.png](../assets/maps/machine/pieces/13004-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13005 | [13005-machine-v1.png](../assets/maps/machine/pieces/13005-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13006 | [13006-machine-v1.png](../assets/maps/machine/pieces/13006-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13007 | [13007-machine-v1.png](../assets/maps/machine/pieces/13007-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13008 | [13008-machine-v1.png](../assets/maps/machine/pieces/13008-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13009 | [13009-machine-v1.png](../assets/maps/machine/pieces/13009-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13010 | [13010-machine-v1.png](../assets/maps/machine/pieces/13010-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13011 | [13011-machine-v1.png](../assets/maps/machine/pieces/13011-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13012 | [13012-machine-v1.png](../assets/maps/machine/pieces/13012-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13013 | [13013-machine-v1.png](../assets/maps/machine/pieces/13013-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13014 | [13014-machine-v1.png](../assets/maps/machine/pieces/13014-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13015 | [13015-machine-v1.png](../assets/maps/machine/pieces/13015-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13016 | [13016-machine-v1.png](../assets/maps/machine/pieces/13016-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13017 | [13017-machine-v1.png](../assets/maps/machine/pieces/13017-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13024 | [13024-machine-v1.png](../assets/maps/machine/pieces/13024-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13034 | [13034-machine-v1.png](../assets/maps/machine/pieces/13034-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13035 | [13035-machine-v1.png](../assets/maps/machine/pieces/13035-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13036 | [13036-machine-v1.png](../assets/maps/machine/pieces/13036-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13037 | [13037-machine-v1.png](../assets/maps/machine/pieces/13037-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13038 | [13038-machine-v1.png](../assets/maps/machine/pieces/13038-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13039 | [13039-machine-v1.png](../assets/maps/machine/pieces/13039-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13040 | [13040-machine-v1.png](../assets/maps/machine/pieces/13040-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13042 | [13042-machine-v1.png](../assets/maps/machine/pieces/13042-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13043 | [13043-machine-v1.png](../assets/maps/machine/pieces/13043-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13044 | [13044-machine-v1.png](../assets/maps/machine/pieces/13044-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13045 | [13045-machine-v1.png](../assets/maps/machine/pieces/13045-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13046 | [13046-machine-v1.png](../assets/maps/machine/pieces/13046-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13047 | [13047-machine-v1.png](../assets/maps/machine/pieces/13047-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13048 | [13048-machine-v1.png](../assets/maps/machine/pieces/13048-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |
| 13056 | [13056-machine-v1.png](../assets/maps/machine/pieces/13056-machine-v1.png) | 已画候选，几何/锚点/游戏验收未通过 |

已画之外全部维持pending。水岸合成稿分别记录新AI纹理与原图区域mask来源，不重复计为模型新生图；其接缝与视觉锚点仍未通过。不能以已计划、已提交提示词或源参考解码替代完成回执。后续重跑此脚本按现存art.json与哈希刷新，不自动认定通过。

## 来源、候选映射与去重

- 社区发行ZIP：[https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip](https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip)，SHA256 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`；腾讯原始版本身份未核实。
- 只静态读取object.idx/pkg，并使用本项目独立的`inspect-reference-dimg.py`解包/解码；输入字节数、哈希均与社区release-manifest核对。没有执行被检查的Python、客户端或其他二进制。
- ID千位组与包内family/elem编号采用全后缀匹配及377张地图的family共现核对，但尚无客户端ID查找表证明，全部标candidate。主题中文仅为生产分类描述。
- 对全DIMG做SHA256去重，再对可见RGBA画面做去重；透明像素RGB与透明留边不制造新画面。每个ID仍保留自身frame尺寸、offset、size与GridAttr；画面别名不代表几何可互换。
- 原生PNG保存某一代表的完整首个非空帧，不裁切、不缩放。每family最多24个不同画面做联系表；联系表可能缩小，仅供检查，实际缩放记录逐项列出。未选代表仍可从完整索引定位原生帧。

## 缺口与验收门槛

- 另有 **27** 个正元素ID出现在地图中但不属于这721条定义；在JSON的unknownSourceElementIds列其地图，保持缺失，不猜资源。
- 包内tank目录尚无本批721定义对应组，未盲目导出其图片；不能把它漏记成制作完成。
- 首帧不覆盖行走/触发/死亡/破坏动画，完整状态制作仍待单独合同。
- 每条正式原创资源必须保留实际生成来源记录，核对候选IDlookup、原生frame尺寸/偏移、建筑占地/通路/遮挡与像素锚点，并完成游戏内等比例截图验收后才能从候选升为accepted。

## 重建

使用带Pillow的本机Python执行：

```text
python -B scripts/build-map-art-inventory.py
```

脚本只更新本任务库存/参考输出与生产索引，不修改地图数据、运行贴图、UI或Git。
