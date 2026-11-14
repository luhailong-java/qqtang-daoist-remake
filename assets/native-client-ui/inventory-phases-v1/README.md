# 五件原生库存资源的完整状态

2026-11-14（America/New_York）。本批对应勇气多多 27061、亲密多多 27073 及铁／银／金锤 9011、9012、9013，共五份原生 IMG、24 个源位置。固定社区 ZIP 的原始 IMG、原帧像素、画布、尺寸、偏移及模式均已核对。 [原状态对照](source-all-phases.png) · [原始合同](source-contract.json)

27061 的十个位置显示等级 1–10，27073 的八个位置显示等级 3–10。已有原创书的首等级保留。其余 16 个等级分别从两张真实内置生图母图逐格裁出，阿拉伯数字与原位置一一对应。勇气母图原生为 1254×1254，亲密为 1774×887，裁边的 Alpha≥8 像素检查通过。实际提示词、四张参考图、返回路径、哈希和可得参数随图保存。实际模型与质量未披露。

三把锤子的两个源位置具有逐字节相同的 Alpha 平面，第二态所有不透明像素的 RGB 总和均不下降。原生两态呈同姿势、同轮廓的明亮材质变化。本批沿用已有原创锤图，第二态采用从源像素统计的亮度系数 1.243263、1.408993、1.326051，保留自有图形及透明通道。

24 张替换帧全部不同，按原帧的实际尺寸等比居中导出并编码到原生像素模式。原声明画布、帧数、索引顺序、尺寸、偏移和结构字段均通过核对，原始时长留空。 [原生尺寸浅深底预览](contact-native-light-dark.png) · [可供安装器读取的清单](manifest.json) · [转换器](../../../scripts/build-native-inventory-phases.py)

当前文件为待人工审核的原生候选，用户客户端安装由主窗口统一处理。等级槽位的运行选择、材质切换及小尺寸外观仍待核验。

```powershell
python -B assets/native-client-ui/inventory-phases-v1/inspect-sources.py
python -B scripts/build-native-inventory-phases.py --check
```

本批已在用户提供的原生目录安装。独立副本的安装、重复安装和恢复通过，实际写入后已逐文件回读。运行显示及人工视觉仍待验，恢复此批必须显式传 `--manifest assets/native-client-ui/inventory-phases-v1/manifest.json`。
