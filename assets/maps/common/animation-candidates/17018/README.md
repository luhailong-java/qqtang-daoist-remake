# 17018 完整源资源相同的候选复用

《灵葫大作战》生产候选。实际重新读取本目标package条目并只zlib解包/metadata_only校验，完整原DIMG SHA `ba1daa7fb39aad0b61f733bd4a123ca3eea5ee1f549d6ead2466e14b31061509` 与8018实证一致，逐帧index、尺寸、frameOffset和encoded payload SHA也逐项核对。无本目标新增RGBA解码/生图/裁切/缩放，新增生图0，直接引用8018已有own PNG；不把跨定义相同字节说成帧内别名。

本目标自己的definition见definition-evidence.json；footprint、GridAttr、lifeTime、canMove均取自身。源frameOffset与本目标mapElemOffset `[0, 15]` 分开保留，未复制8018的地图偏移、未推组合原点或时序。所有原始来源/模型历史保持不变。

sequence.json保留本目标4个帧位索引与1倍/4倍PNG绑定，reusedFromCandidateElement=8018，PNG像素完全不改；复用图的比例、轮廓、局部亮点等既有待修全部继承。accepted/geometry/stateCorrespondence/runtime均false，目标运行和放置未验。未改任何main art/global/index/runtime/src/Git，未本地测试或浏览器。
