# 全物品候选缺口基线（2026-11-12）

基线HEAD `1accecfc9dc0764f1a938764084817ba330c6f90`。逐个读取全部items/**/art.json并校验候选PNG实际存在及SHA；2945个源ID中476个已有至少一种表示，2469个没有候选。库存/长短名片/world表示不重复增加源ID，battlefield按sceneId单列不混入2945。候选存在不等于全动作/穿戴/运行完成。

| 源类别 | 源ID | 至少一种候选 | 无候选 |
|---|---:|---:|---:|
| bg | 395 | 0 | 395 |
| bomb | 295 | 0 | 295 |
| cap | 447 | 0 | 447 |
| card | 20 | 20 | 0 |
| cladorn | 365 | 0 | 365 |
| ear | 62 | 62 | 0 |
| enter | 71 | 0 | 71 |
| eye | 72 | 72 | 0 |
| food | 10 | 10 | 0 |
| footprint | 74 | 74 | 0 |
| forge | 7 | 7 | 0 |
| fpack | 146 | 0 | 146 |
| frame | 160 | 0 | 160 |
| huanying | 103 | 0 | 103 |
| item | 32 | 32 | 0 |
| kubi | 2 | 2 | 0 |
| mouth | 145 | 0 | 145 |
| namecard | 145 | 0 | 145 |
| namecardbound | 5 | 5 | 0 |
| npack | 197 | 0 | 197 |
| petcard | 48 | 48 | 0 |
| platform | 29 | 29 | 0 |
| skill | 80 | 80 | 0 |
| thadorn | 35 | 35 | 0 |

完整source/img→project候选映射、逐清单SHA和每ID路径见相邻JSON。新作选择npack中148/149/150/151/152五阶赛事披风：每件stand/walk字节相同，12独立相位+1库存图。计划完成全部60世界raster及5库存图；此五件是目录描述明确的一组，不把它们当整个197件背饰。

唯一新增物品目录assets/items/back-adornments/honor-capes/，不改head-adornments/full world-art或其他窗口文件。不使用GUI/CUA/外部API，新候选全部pending；native cardinal/时序/挂点未知仍null。后续交付另记实际增量，不改写本基线476。
