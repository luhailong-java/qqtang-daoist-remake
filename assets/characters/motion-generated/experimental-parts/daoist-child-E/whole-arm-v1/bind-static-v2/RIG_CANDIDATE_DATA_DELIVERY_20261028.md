# 静态A/B候选数据交付：《灵葫大作战》道童E

本批只读`src/cutout-rig.js`真实schema/矩阵代码，依据已实看v2 proposal导出两个数据文件：`rig-contact-A.candidate.json`、`rig-contact-B.candidate.json`。没有默认`rig.json`，不改src/Git，不调用模型、渲染、测试或浏览器，不解码PNG。

## schema可表达当前静态结果

当前schema要求`schemaVersion=1`和`animationSource="procedural_skeletal_animation"`。此值在候选中**仅是renderer分类标签**；真实内容另标`contentMotionKind="static_painted_parts_assembly"`，`renderedMotion=false`。只有`static` action，`loop=false, tracks={}`，没有walk、idle抖动、时长或动画轨道。源码中空tracks合法；本批未执行validate/sample/draw或import模块来作测试。

原生已裁PNG肩圈可以作为普通第7个前景节点，layer80，当前模块不需要新增运行时mask能力。两个候选各为7节点：far整臂5、far腿10、near腿20、头35、torso40、near整臂70、原torso肩圈80。源路径均以`assets/`开头，存在性与编码文件SHA记录在`rig-candidates.delivery.json`；未解析PNG头或解压图像。

## 精确保留已渲染矩阵

torso为顶层，bindPosition直接保留[313.5,401]；其余主体节点parent为torso，局部bindPosition=原设计平面绝对位置−torso位置，角度均0。源码不把父节点`imageScale`传给child bind translation，所以**不再乘除torso0.48**。平移代数：`T(torso)*T(child−torso)=T(child)`；各图仍用原pivot、imageScale和layer。

肩圈parent为torso、bindPosition[0,0]；ring pivot=torso pivot[184,188]−源ROI起点[22,35]=[162,153]，scale0.48。因此裁片图矩阵等于原torso矩阵按ROI偏移，仍为[0.48,0,0,0.48,235.74,327.56]。pivot位于该108×139裁片之外是同源裁片锚点换算，schema只要求有限数对；不是新测解剖肩点。原ROI、outer减inner多边形、源torso与裁片SHA保留在ring节点，未重切/重画。

每个节点的`expectedStaticImageMatrix`**原样复制**对应已渲染proposal矩阵，供恢复后独立比较；`expectedStaticBoneMatrix`和手工源点也保留。数据转换仅做平移/比例代数，双精度舍入量单独记录，不把该算式称renderer实测通过。

## 手工参考根与验收边界

实际schema必须有有限`referenceRoot`。本批原样引用既存`experimental-parts/daoist-child-E/bind-static-v1.proposal.json`的[313.5,528.8719512195123]兼容美术锚点，来源文件与SHA附在候选中。该旧记录已明确它不是测得脚底、原客户端锚点或批准物理地面；**没有从art-ground528.5猜造一个新世界根**。`worldRoot=null`，`nativeTiming=null`，`sourceNativeTimingMs=null`。

未来若只比较设计平面矩阵，可用候选`referenceRoot`本身作caller root、size627，抵消drawCutoutRig外层平移/缩放；此仅写成未来比较说明，当前未调用、未改caller/game root。真正游戏位置如何接入仍待协调者验收。

所有候选`runtimeEnabled=false`、`runtimeAdopted=false`、`staticAccepted=false`、`fullAnimationAccepted=false`。v2是当前最佳静态候选而非已动人物；左右手解剖、手脚交换、连续动画及客户端显示仍未因此得到批准。
