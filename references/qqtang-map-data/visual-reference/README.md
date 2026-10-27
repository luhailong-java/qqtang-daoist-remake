# 中国城01结构取证图

这些 PNG 是社区修改后客户端中现存像素的只读解码与检查拼版，只用于核对建筑外形和地图结构。它们不是新生图、高清重绘、道家 Q 版成品，也没有接入游戏运行资源。来源仍为社区 v1.3.4，腾讯原始文件身份尚未认证。

- `town01_4-thumbnail-frame.png`：目录 ID 201 明确关联 `town01_4.map` 与 `town01_4.img`。从该 `.img` 解码得到原帧 **150×125**，没有缩放。DIMG 声明画布字段是 `0xCCCCCCCC`，不能把它当尺寸；本次只读取有效、有界的 frame。
- `town01_4-thumbnail-4x-inspection.png`：上述原帧按最近邻放大 4 倍的检查图，**600×500 是检查图尺寸，不是原地图像素宽高**。
- `town01-building-candidates-contact-sheet.png`：中国城01三层使用的 17 个正元素 ID 对应的文件名候选，原 frame 以 1:1 像素拼版，另加中性底色和数据标签。候选关系 `3000+N → object/mapElem/town/elemN_stand.img` 来自目录与编号的推断，尚未取得客户端 imageID 查找表证明；不得把候选关系写成已经确认的原版映射。
- `town-candidate-*-frame.png`：逐候选资源的首个可见原帧解码，保留透明度，不缩放、不裁切、不应用地图锚点。
- `manifest.json`：记录 ZIP 来源和 SHA-256、object.idx/pkg 哈希、路径与压缩流偏移、压缩与解压哈希、DIMG 原始 canvas/frame/offset/模式、mapElem 原始占地与 offset、输出 PNG 哈希以及未确认项。

`object.idx` 本地记录为 16 字节头、3,482 个变长路径记录，各条含包偏移和压缩/解压长度；所有条目恰好读到索引结尾。所用流按索引边界解压，检查 zlib EOF、无多余流和解压长度，再核验 DIMG 签名与全帧边界。没有运行社区解析器代码或客户端。

mapElem offset 和 DIMG frame offset 是两组独立原值。例如大建筑候选 3019 的逻辑占地为 **4×2 格**，首帧 **161×110**、DIMG frame offset **[0,17]**，mapElem offset **[0,30]**。未核实客户端的正负方向、原点与组合规则，因此没有用猜测锚点重拼整屏。地图缩略参考直接来自目录明确指向的文件。

解码工具为本项目从零实现的 `scripts/inspect-reference-dimg.py`。Pillow 只负责编码 PNG 与检查拼版。RGB565 与独立 0..32 alpha 平面、BGRA、BGR 等解码规则依据社区格式研究并以人工已知像素测试；现存参考图已实际查看。对应验证命令为 `python -B tests/dimg-reference.test.py`（使用含 Pillow 的工作区依赖 Python）。
