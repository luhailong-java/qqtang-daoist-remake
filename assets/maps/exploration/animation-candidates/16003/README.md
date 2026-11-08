# 16003全帧位原创候选

2026-10-29（UTC记录日）。实际核图4个源帧位，生成3个不同可见内容的自有候选，保留4个原始帧索引/offset记录。主art/index/runtime未改；本文件不是正式验收。

当前母图`sequence-v3.png`真实原生1254×1254，记录在同名`.generation.json`；内置目标Sunburst/max，实际型号/质量未披露为null。源结构板、当前own master及image两主风格均实际附图；修图另附前一母图。

源原生小帧与逐帧解码/可见像素归组证据见`source-context.json`。相同可见像素仅复用PNG，每帧index与DIMG frameOffset仍独立；mapElemOffset另存，组合渲染原点为null，未推两者相加。

导出`frames-logical-x1/`对应每个源帧自身宽高，`frames-compatible-x4/`为各自4倍兼容画布。全部派生于当前母图；整帧裁切、统一等比PMA缩放、整帧底部居中注册，没有非均匀拉伸、程序移部件或把静态变换声称新画。原生母图与派生尺寸分别记录。

当前尺寸/独立帧/alpha边界结果见`sequence.json`；预览`frame-preview.png`为浅深底诊断合成，不是游戏截图。四周无触边不等于源轮廓或状态对应通过；模型重画的小幅细节变化、源亮斑/形状对应、真实时序/循环/方向和组合渲染原点仍待核实。

《灵葫大作战》123×43横向长条熔岩地面。四源1=3实际RGBA相同；新增0/1/2三档亮度，3.binding复用1PNG且独立索引。源各frameOffset[1,1]，mapElemOffset独立[2,3]、footprint[3,1]保持。x1各123×43、x4各492×172，3种ownRGBA，未把方块非等比拉成长条。

整套选v3，母图真实原生1254×1254、三行完整长条。v1过扁且跨名义行边，v2比例仍约21%偏差，均未导出；v3重新以实际源结构作为第一图、own master第二图加两主风格从新生成，比例误差已到1.50%、0.90%、0.59%。v3不是程序拉伸或裁掉侧面修正，也不拼旧坏帧。各稿真实入口、参数、时间和引用分别保留，目标Sunburst/max，实际型号/质量null。

显式地面guard0、无alpha规范化/内接方形搜索/非等比或程序移动裂纹。源x1 alpha8BBox[0,0,123,43]、edge116；当前[1,0,122,43]，edge104/103/104。仍有左右各约1像素透明留边、轮廓和固定裂纹跨帧差异、亮度对应待验，见floor-boundary-evidence.json。不能据接近比例或双尺寸落盘宣称状态/几何通过；accepted/stateCorrespondence/runtime仍false。

仅此资源必要小批源像素与当前图导出，未全45解码/QA，未本地测试、浏览器或Git。全部accepted/geometry/stateCorrespondence/runtime仍false，冻结的三个源码文件未动。
