# 《灵葫大作战》道童E：一次passing P1/P2静态注册

2026-10-29。只对当前passing母图作4条真实native裁切，并复用whole-arm-v1/bind-static-v2固定头、torso、双臂和肩圈，唯一一次两姿装配。P1=nearRIGHT planted+farLEFT raised；P2=nearRIGHT raised+farLEFT planted。0AI图、无完整动作/正式rig，也没有第二次试装。

## 原生裁区与手工来源点

4裁区分别为near planted[355,14,617,498]、near raised[952,19,1234,436]、far planted[350,512,568,991]、far raised[1002,518,1284,929]。各保留整条裤腿/帽/靴，无尺寸变换；源alpha≥8共237849像素完整归属一次，漏0/重0，安全边界全过后才写裁片。`native-crops.json`及每裁片`.source.json`保留母图/生成链和当前SHA。

实际逐一看4张原生裁片后，手工源坐标如下（数值为视觉候选，不是解剖/原客户端骨点）：

| 部件 | 帽内cap | heel | toe | sole |
|---|---|---|---|---|
| nearR planted | (416,60) | (417,471) | (605,468) | (530,488) |
| nearR raised | (1006,66) | (966,363) | (1134,408) | (1085,421) |
| farL planted | (476,551) | (367,964) | (555,961) | (468,980) |
| farL raised | (1058,561) | (1022,846) | (1184,904) | (1140,913) |

源cap均采样为实体象牙白，alpha252–253；其他选点也在当前可见像素上。far planted sole在抗锯齿边缘alpha8，手工点不因此拥有精确地面含义。完整cap/knee/ankle/heel/toe/sole与RGBA样本、crop局部点均在`manual-landmarks.proposal.json`和本批`proposal.json`。

## 共同0.24与明确的family摆放偏移

全部新腿scale0.24。骨接口保持near[307,439]、far[319,438]。真实帽内点原样绑定时，人工支撑sole会落在541.72/540.96，较既有art-ground528.5低，说明不能偷偷把pivot移到帽外后声称准确帽内hip。

根明确授权另加**四腿同一**family art imageOffset。一次计算采用528.5−两支撑sole平均541.34=**−12.84设计px**，近远和P1/P2均相同，来源是已选手工sole，不是每姿bbox fit。上身/臂/肩圈位置与像素完全不动。

实际source cap仍是上表真实帽内点，bone bind仍为固定hip；画稿cap在偏移后落near[307,426.16]、far[319,425.16]。`effectiveImagePivotForEquivalentMatrix`只是为了等价表达摆放的`capLocal−imageOffset/0.24`，**不是帽内解剖hip或native根**。原cap/骨接口/共同偏移/最终矩阵分别保留，不能混写。未扭曲、镜像、改源alpha或分别缩放。

## 本次真实结果

实际看`two-passing-627-ivory.png`和`two-passing-96-ivory.png`。抬腿膝弯/足离地可见，帽大体埋入原衣摆。P2近抬靴遮住far支撑踝部较多，far下方靴仍可见；保留为后续运动可读性问题，不再移动解决。

| 姿态 | 手工支撑soleY/残差 | 抬足最低可见像素行 | 到art-ground的像素中心/底边间隙 | 两足最低底边相差 |
|---|---|---|---|---|
| P1 | 528.88 / +0.38 | 510 | 18.5 / **17.5**设计px | 18设计px |
| P2 | 528.12 / −0.38 | 512 | 16.5 / **15.5**设计px | 16设计px |

支撑腿的最低可见行均528、像素底边529，诊断art-ground528.5居中，栅格残差±0.5；表中实体点和像素边界分开，未伪造统一抬高。沿原一次固定比例56.25/444换算，抬足底边间隙约P1 **2.2171逻辑px**、P2 **1.9637逻辑px**，只是数学建议，未接游戏。不能说两条都满足75源像素或70–80范围目标。

两整人alpha≥8 bbox均[111,88,449,529)，高度441；原跨姿参考444及统一绘制比例保持，不按新bbox重撑到56.25高。96图为整个627画布等比缩96，人物约68px高，不是96高人物；小图足踝层次较挤，不据此批准身份/运动。

## 边界与文件

`proposal.json`保存全部源SHA/ROI/手工点、每腿矩阵及残余测量；各RGBA和96文件旁有完整`.source.json`，米白联系表也可追溯。`visual-review.json`保存实际看图与具体问题。脚本有已存在passing结果即拒绝再次渲染的闸门；只执行一次。裁片导出也拒绝自动重复。

源1/2/4/5解剖身份与相位对应仍候选，worldRoot/nativeTiming仍null，sixPhaseComplete/runtimeEnabled/fullAnimationAccepted均false。无v2修改、源alpha修改、src/Git、测试/构建/浏览器或主游戏接入。当前停在两张静态候选，保持整游戏交付要求。
