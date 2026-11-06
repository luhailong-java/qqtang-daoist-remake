# 《灵葫大作战》道童E两接触：一次艺术注册微调

本批是协调者明确授权的一次静态A/B调整，不是新原画、完整动画或原客户端锚点恢复。2026-10-28 America/New_York。源为`../root-contact-diagnostic/proposal.json`及其中四条原生裁腿、旧head/torso；未重裁母图，没有调用image_gen。执行代码`../make-registered-contact-v3.py`含已有PNG即拒绝再运行的防重复闸门。

只执行指定变换：A/B的head+torso一起y+3；A两腿不动，B两腿一起y+2.4。四腿共同scale0.24、原裁区、原手工hip/ankle/toe/sole点、近RIGHT/远LEFT身份与遮挡层均保留，没有逐帧alpha bbox fit、镜像、扭曲或源PNG修改。A近前远后，B近后远前；额外hem、旧分段腿和旧肩臂均未使用。caller/game root及原native frameOffset未变；所有原矩阵、局部pivots与新矩阵逐件在`proposal.json`和两张图旁`.source.json`中保留。

已实际查看`two-contacts-ivory.png`（1254×627、两个原627未缩放）及`contact-B-ivory.png`。颈部未见新增断口，连续裤腿/单一踝边的改善保持。两姿的**未批准手工soleCandidate**变换后相同：近RIGHT y528.52、远LEFT y528.48，候选art-ground528.5，±0.02；这只说明该人工注册消除了原两相2.4设计像素差，不是alpha像素接地、原生物理根或动画脚锁通过。联系图的虚线栅格化在y529，仅诊断用途，不输出成游戏素材。

B裤裆中央下摆底仍可见很短的金色尖边，约627画布x315–324/y453–460范围；未将此视觉估计当像素测量或单件所有权归因。不能批准所有髋cap金边完全被挡住，也不据此自动追加移动或返修。A未见大片成品髋口外露，两姿都未再出现旧多节膝金环。

当前状态`registered_sole_points_matched_small_crotch_gold_edge_unresolved`。保留本次唯一结果，停止微调；肩臂全缺，完整人物静态、96px显示、暗浅底动态/慢放、连续运动均未验收，没有正式rig.json或动作时长。由协调者看图后决定是否继续完整臂独立原画。
