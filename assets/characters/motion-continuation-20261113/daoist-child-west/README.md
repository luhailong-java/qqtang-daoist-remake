# 道童西向步行六相位

2026-11-13（America/New_York）。道童对应社区参照样本 `player9.ini` 的角色 9。组 2 首相位的脸部、衣服和六层叠图朝屏左，原资源声明 100×100 画布和 4×6 个位置。组 2 的六个位置依次为 f12–f17。检查了各位置的 body1、foot1、leg10901、cloth10901、face10901、hair10901，另记录 head1 元数据。七个声明层的编码与几何信息逐对比较后，15 对均有差异。原层叠放次序、真实时长、循环和角色锚点仍待证。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [组 2 朝向探针](../../motion-generated/daoist-child/native-role9-evidence/group2-direction-probe-5x.png) · [逐相位来源](source-west-evidence.json)

沿用自有西向待机的金发带、葫芦与玉绿短袍，通过内置生图重绘。两张真透明母图的原生尺寸分别为 2188×718、2172×724。每张随附实际提示词、原生文件来源、输入摘要和工具可得参数，实际模型与质量未披露。每格直接裁切，用相同的 0.3184 等比缩放和排版底线导出到 256×256。六张图的 Alpha 范围均为 0–255，Alpha≥8 像素未触及各格或导出画布边界。诊断髋部位置由母图量取。 [相位清单](manifest.json) · [浅深底 112／64／48／32 像素预览](review-light-dark.png)

f12 和 f15 两脚接近，f15 保留源脸层的眨眼。f14 的后脚抬起，f16 的前脚抬起，f17 的后跟抬起。f13 两只鞋的离地高度接近，f17 前后鞋的明暗区分较弱。跨母图的衣摆形状、步态连续性及小屏辨识仍待人工审核。候选尚未接入运行。

可在仓库根目录执行下列命令重建诊断证据与导出。

```powershell
python -B assets/characters/motion-continuation-20261113/daoist-child-west/inspect-role9-west.py
python -B assets/characters/motion-continuation-20261113/daoist-child-west/export-diagnostics.py
```
