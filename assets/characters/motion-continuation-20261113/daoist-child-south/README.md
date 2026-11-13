# 道童南向步行六相位

2026-11-13（America/New_York）。道童对应固定 QQTang-Local 社区样本中的角色 9。四组首相位的脸部诊断显示组 3 为正面。原资源声明 100×100 画布和 4×6 个位置，南向为 f18–f23。六个位置共解出 body1、foot1、leg10901、cloth10901、face10901、hair10901 的 36 个图层，并记录 head1 的编码元数据。七层逐对核对，15 对均有编码或几何差异。图层叠放为静态诊断顺序，原时序、循环及锚点仍待证。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [组 3 朝向探针](../../motion-continuation-20261112/daoist-child-north/source-face-groups.png) · [逐相位来源](source-south-evidence.json)

原创重绘沿用道童南向待机的金发带、玉绿袍与葫芦。首轮 A 图将 f19/f20 的支撑脚画反，首轮 B 图将 f22/f23 的鞋抬成前踢。两轮定向重绘的实际提示词和工具回执随目录保存。用于导出的 A/B 第二版母图均为 2172×724 真透明 RGBA，实际模型与质量未披露。按原生透明单元裁格，各母图依鞋底量取排版基线，各格依腰带估计水平位置。共享 0.3184 等比缩放及输出底线。六张 256×256 RGBA 诊断图均保留 Alpha 0–255，Alpha≥8 像素未触及格边或导出边。 [相位清单](manifest.json) · [浅深底 112／64／48／32 像素预览](review-light-dark.png)

f19/f20 的屏右鞋在下，f22/f23 的屏左鞋在下。f21 眨眼，f20 空手前摆，f23 持葫芦手略抬。f20 的前后脚差距比 f23 更明显，两张母图的头顶高度及衣摆形态略有差异，待人工核对整组动作连贯与小屏辨识。候选尚未接入运行。

在仓库根目录执行下列命令可复现诊断证据和导出。

```powershell
python -B assets/characters/motion-continuation-20261113/daoist-child-south/inspect-role9-south.py
python -B assets/characters/motion-continuation-20261113/daoist-child-south/export-diagnostics.py
```
