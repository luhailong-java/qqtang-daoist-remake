# 16004全帧位原创候选

2026-10-29（UTC记录日）。实际核图4个源帧位，生成3个不同可见内容的自有候选，保留4个原始帧索引/offset记录。主art/index/runtime未改；本文件不是正式验收。

当前母图`sequence-v3.png`真实原生1254×1254，记录在同名`.generation.json`；内置目标Sunburst/max，实际型号/质量未披露为null。源结构板、当前own master及image两主风格均实际附图；修图另附前一母图。

源原生小帧与逐帧解码/可见像素归组证据见`source-context.json`。相同可见像素仅复用PNG，每帧index与DIMG frameOffset仍独立；mapElemOffset另存，组合渲染原点为null，未推两者相加。

导出`frames-logical-x1/`对应每个源帧自身宽高，`frames-compatible-x4/`为各自4倍兼容画布。全部派生于当前母图；整帧裁切、统一等比PMA缩放、整帧底部居中注册，没有非均匀拉伸、程序移部件或把静态变换声称新画。原生母图与派生尺寸分别记录。

当前尺寸/独立帧/alpha边界结果见`sequence.json`；预览`frame-preview.png`为浅深底诊断合成，不是游戏截图。四周无触边不等于源轮廓或状态对应通过；模型重画的小幅细节变化、源亮斑/形状对应、真实时序/循环/方向和组合渲染原点仍待核实。

《灵葫大作战》43×123竖向熔岩地面。实际源1=3的PNG/decodedRGBA/canonical visible RGBA相同，只画0/1/2三档亮度，3.binding复用1PNG并保留独立索引。各源frameOffset[1,1]与mapElemOffset独立[2,2]、footprint[1,3]原样。x1各43×123，x4各172×492，3种ownRGBA，没有旋转其他横向资源或非等比拉伸。

整套选v3真实原生1254²。v1偏宽10.25%—11.76%、导出上留13px，v2矫正过窄13.0%—13.7%，v3改到偏窄7.11%、6.15%、6.50%而保留整套一致稿；没有混用不同比例旧帧。停止本点继续其他独立资源，此偏差仍未通过。

地面明确guard0，源x1 alpha8BBox全43×123、edge116，当前[1,0,41,123]、edge21/23/23，仍横向少约3px；4倍edge29/17/33/继承17见floor-boundary-evidence.json。无alpha规范化/蒙版强填/程序改裂纹/内接方形裁取。源轮廓、裂纹细节跨帧稳定和亮度对应继续pending，accepted/geometry/stateCorrespondence/runtime=false，时序/loop/组合原点null。

仅此资源必要小批源像素与当前图导出，未全45解码/QA，未本地测试、浏览器或Git。全部accepted/geometry/stateCorrespondence/runtime仍false，冻结的三个源码文件未动。
