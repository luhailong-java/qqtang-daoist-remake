# 沙漠族原创图元候选

2026-10-26：43条元素已建立原创绘制候选，来自41幅不同源画面；7张内置image_gen母图，2条源画面别名复用，正式几何/锚点/游戏验收通过0条。

母图实际原生尺寸：A/B/E/G为1536×1024，C/D/F为1254×1254。所有切片按各原始frame画布的4倍输出，过程只有裁切、等比适配和透明画布放置；不是声称模型原生4倍细节。

输入实际附上image邮件/组队主图及每批结构联系表；每张母图的.generation.json保存配置快照、实际提交、引用SHA256、时间与工具来源，实际型号/质量未披露为null。

## 索引

- art.json：与town兼容的逐件清单和裁切坐标。
- props-[a-g]-v1.png.generation.json：7张母图的独立生成记录。
- pieces/*.png.provenance.json：43条派生、源frame/size/GridAttr/offset与未通过点。
- qa.json：完整未通过阈值/数值/文件。
- references/：结构参考联系表，只参考形状，不作为原创图元。

## 已知未通过项

| ID | 可见宽高比偏差 | 门槛 | 文件 |
|---|---:|---:|---|
| 1004 | 0.173 | 0.100 | [1004-cloud-stone-block.png](pieces/1004-cloud-stone-block.png) |
| 1005 | 0.234 | 0.100 | [1005-gold-fruit-planter.png](pieces/1005-gold-fruit-planter.png) |
| 1008 | 0.117 | 0.100 | [1008-desert-v1.png](pieces/1008-desert-v1.png) |
| 1009 | 0.361 | 0.100 | [1009-desert-v1.png](pieces/1009-desert-v1.png) |
| 1010 | 0.118 | 0.100 | [1010-desert-v1.png](pieces/1010-desert-v1.png) |
| 1114 | 0.160 | 0.100 | [1114-desert-v1.png](pieces/1114-desert-v1.png) |
| 1115 | 0.106 | 0.100 | [1115-desert-v1.png](pieces/1115-desert-v1.png) |
| 1119 | 0.135 | 0.100 | [1119-desert-v1.png](pieces/1119-desert-v1.png) |
| 1123 | 0.205 | 0.100 | [1123-desert-v1.png](pieces/1123-desert-v1.png) |
| 1127 | 0.178 | 0.100 | [1127-desert-v1.png](pieces/1127-desert-v1.png) |
| 1132 | 0.178 | 0.100 | [1132-desert-source-alias-v1.png](pieces/1132-desert-source-alias-v1.png) |
| 1135 | 0.323 | 0.100 | [1135-desert-v1.png](pieces/1135-desert-v1.png) |
| 1137 | 0.114 | 0.100 | [1137-desert-v1.png](pieces/1137-desert-v1.png) |
| 1141 | 0.244 | 0.100 | [1141-desert-v1.png](pieces/1141-desert-v1.png) |
| 1143 | 0.261 | 0.100 | [1143-desert-v1.png](pieces/1143-desert-v1.png) |

比例阈值只是自动提示，数值未超阈值也不代表源内部分界、入口、占地与画面已经验收。所有地形边仍需同坐标区域与重复接缝检查；没有改变原地图几何来掩盖绘图差异。1001/1113/1142地面重复接缝尚未通过。

1012复用1001，1132复用1127；1132保留独立原offset[0,-1]，尚未证明渲染锚点。

没有在本批运行游戏内截图验收，当前浏览器入口不可用。未修改town、全局生产统计或Git。
