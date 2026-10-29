# 9008全帧位原创候选

2026-10-28。实际核图4个源帧位，生成4个不同可见内容的自有候选，保留4个原始帧索引/offset记录。主art/index/runtime未改；本文件不是正式验收。

当前母图`sequence-v1.png`真实原生2079×756，记录在同名`.generation.json`；内置目标Sunburst/max，实际型号/质量未披露为null。源结构板、当前own master及image两主风格均实际附图；修图另附前一母图。

源原生小帧与逐帧解码/可见像素归组证据见`source-context.json`。相同可见像素仅复用PNG，每帧index与DIMG frameOffset仍独立；mapElemOffset另存，组合渲染原点为null，未推两者相加。

导出`frames-logical-x1/`对应每个源帧自身宽高，`frames-compatible-x4/`为各自4倍兼容画布。全部派生于当前母图；整帧裁切、统一等比PMA缩放、整帧底部居中注册，没有非均匀拉伸、程序移部件或把静态变换声称新画。原生母图与派生尺寸分别记录。

当前尺寸/独立帧/alpha边界结果见`sequence.json`；预览`frame-preview.png`为浅深底诊断合成，不是游戏截图。四周无触边不等于源轮廓或状态对应通过；模型重画的小幅细节变化、源亮斑/形状对应、真实时序/循环/方向和组合渲染原点仍待核实。

本件为《灵葫大作战》右槽双猪围栏，实际参考9008自身四源与右槽own master重新生成，未程序翻转9007。当前母图真实原生2079×756；可见比例误差5.58%、5.58%、5.79%、5.58%，四源帧各80×64、frameOffset[0,0]，mapElemOffset独立[0,22]、footprint[2,1]、GridAttr[0,0]保留。双尺寸80×64/320×256各四种自有RGBA，4倍alpha>8边缘触边0。

源细微猪耳/身体/饲料状态的精确对应、木纹/花朵/小金边跨帧稳定尚未接受，局部轮廓偏差继续pending。当前全帧位候选不等于原时序或运行已验。

仅此资源必要小批源像素与当前图导出，未全45解码/QA，未本地测试、浏览器或Git。全部accepted/geometry/stateCorrespondence/runtime仍false，冻结的三个源码文件未动。
