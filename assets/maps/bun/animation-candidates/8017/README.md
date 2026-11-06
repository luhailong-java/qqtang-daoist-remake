# 8017 十一帧位原创候选

源0–10共11帧已分6+5两个必要小批实际核图，canonical visible RGBA十一种各不相同，无可复用源像素。每源帧40×40、frameOffset[0,0]，mapElemOffset[0,0]和GridAttr3855原样独立保留，组合原点/时序/loop/帧状态语义均null。

首批整套选batch-01/sequence-v3.png，后批选batch-02/sequence-v1.png；均真实原生1536×1024、每格512²。后批第六格是无source index的灰色排版占位，明确未导出。全部40²和160²是原生完整方格等比PMA派生，alpha255，无alpha规范化或透明立物fit；每张及模型/时间/来源记录在各批。目标Sunburst/max，实际型号/质量null。

11/11仅指不同源帧位均有自有绘制候选，所有accepted/geometry/stateCorrespondence/seamless/runtime仍false。源0的首段格栅仍偏低，部分侧轨接缝和条带坐标偏差、跨帧纹理稳定及邻接拼缝待修。首批v1/v2重复了相近边轨接缝，v3重画改善部分侧轨差异，但没有宣称全部准确；未程序移条带或拼坏帧。

入口sequence.json含所有逐帧索引和双密度路径，source-aggregate.json为只聚合JSON的源像素去重证据。主bun/art.json、全局index/runtime、冻结三源码及Git均未改，未本地测试/浏览器或全族扫描。
