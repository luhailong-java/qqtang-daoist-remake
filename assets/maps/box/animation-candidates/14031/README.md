# 14031 五帧像素相同、坐标独立的候选复用

《灵葫大作战》生产候选。本目标实际逐帧核图后，0–4与10006的尺寸、encoded payload SHA、decoded RGBA SHA、canonical visible RGBA及原帧PNG SHA全部一致。两个完整DIMG SHA不同，不能称完整资源字节别名。证据见pixel-equivalence-evidence.json。

目标frameOffset为[0,19]/[0,20]/[0,19]/[0,17]/[0,20]，10006为[0,2]/[0,3]/[0,2]/[0,0]/[0,3]；自己的mapElemOffset[0,20]和definition/footprint/Grid/lifeTime/canMove保留。不按+17差值推客户端组合原点，也不把两类offset相加。

5个源帧位复用10006已有own候选PNG，像素不改，新增生图0、不裁切/不缩放。每帧独立index、源尺寸和offset都在sequence.json，双尺寸160×236/232/236/244/232与对应x1保留。原母图真实原生1983×793，历史模型/质量/来源不改写。借用预览仍标10006来源，不冒充本目标运行截图。

火焰/火星高差、局部状态和雕云/石块跨帧细节等10006原待修全部继承，accepted/geometry/stateCorrespondence/runtime均false，时序/loop/组合原点null。未改main art/index/runtime/src/Git或冻结三源码，未本地测试/浏览器/全族扫描。
