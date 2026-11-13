# 道童北向步行六相位

2026-11-12。用固定社区参照包里的 player9.ini 核对步行资源。四个方向组的脸部首帧显示组 1 为背向，对应原索引 6–11。原声明画布为 100×100。六个相位的 body1、foot1、leg10901、cloth10901、face10901、hair10901 共 36 个分层像素已解码。源证据保留分层原尺寸、偏移和编码摘要，叠放顺序仅用于静态对比。head1 只读元数据与编码摘要。 [朝向探针](source-face-groups.png) · [原始六相位证据](source-north-evidence.json)

使用内置 image_gen 生成两张 2172×724 RGBA 母图。两个半周期依次保留屏右脚较低、屏左脚较低的对应关系，f11 的右臂抬起。每格均为背向，头带结、持葫芦手及穗子在屏左。工具实际模型与质量未披露，真实提示词、引用、原生输出及哈希见母图旁记录。两张母图均按 724 像素裁格检查，Alpha≥8 像素没有触及格边。

原 f6 与 f9 的七个声明图层在尺寸、偏移、像素模式、空标记及编码摘要上相同。诊断序列保留两个原位置，并让 f9 引用同一 f6 导出图。B 母图的首格作为未采用绘稿保留。六个原位置对应五张独立 256×256 RGBA 诊断图，使用共享 0.3184 等比缩放、固定底线与手工估计髋部位置。 [相位清单](manifest.json) · [浅深底 112/64 像素预览](review-light-dark.png)

相位动作衔接、两母图衣摆变化及人工视觉审核仍待确认。原播放时长、循环与角色锚点留空，本组为诊断候选。

复核原始证据运行 `python -B assets/characters/motion-continuation-20261112/daoist-child-north/inspect-role9-north.py --north-group 1`，再运行 `python -B assets/characters/motion-continuation-20261112/daoist-child-north/export-diagnostics.py`。
