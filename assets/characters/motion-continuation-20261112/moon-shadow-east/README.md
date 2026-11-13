# 月影东向步行六相位

2026-11-12。月影沿用银灰短发、深蓝围巾、月形腰扣与双弯刃。本项目映射对应 sourceRole22。固定社区参照包的 SHA-256 与项目记录一致。角色 ini 指定的 body1、foot2 和 leg/cloth/face/hair12201 walk 容器都声明 100×100 画布及 4×6 帧。脸部首相位显示组 0 朝屏右。本批从该组解出六相位，每相位六个图层，保留各层编码摘要、解码摘要、尺寸与偏移。原图仅用于动作证据。 [朝向探针](source-face-groups.png) · [相位证据](source-east-evidence.json) · [源下身对比](source-east-lower-body.png)

两次内置 image_gen 返回 2172×724 RGBA 母图。实际提示词、五张参考图、母图哈希及工具返回记录随图保存。工具没有披露实际模型或质量。六个 724×724 母图单元的 Alpha≥8 像素均未触及裁边。共用一次 0.3184 等比缩放与地面基准，按手工估计的髋部位置排版到 256×256 画布。六个导出样本彼此不同，边缘无 Alpha≥8 像素。 [导出清单](manifest.json) · [浅深底 112/64 像素预览](review-light-dark.png)

f0 与 f3 保留通过姿势，f3 闭眼以体现源脸层差异。f1 和 f2 可沿前景裤腿金边看到该脚在屏右，f4 和 f5 则转到屏左，右手持刃也从后摆转到前摆。f4 后脚着地、前脚抬起，f5 后脚抬跟、前脚落地。f4/f5 的前景裤腿比前半周期更长，衣摆和腿形连续性及整组步态仍需人工检查。 [下身放大对比](lower-body-diagnostic.png)

原始播放时长、循环和原生角色锚点留空。当前导出供静态诊断，人工审核待定，运行入口未接这组样本。

源板复核运行 `python -B assets/characters/motion-continuation-20261112/moon-shadow-east/inspect-role22-east.py`，确认组 0 后加 `--east-group 0`。候选裁格与来源复核运行 `python -B assets/characters/motion-continuation-20261112/moon-shadow-east/export-diagnostics.py`。
