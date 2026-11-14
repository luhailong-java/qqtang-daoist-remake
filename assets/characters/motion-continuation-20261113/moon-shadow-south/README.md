# 月影南向步行六相位

2026-11-13（America/New_York）。固定 QQTang-Local 社区样本的 player22.ini 对应月影。四方向脸层探针显示组 3 为南向，源位置 f18–23，声明画布为 100×100。每个位置解码 body1、foot2、leg12201、cloth12201、face12201、hair12201，另读 head1 元数据。六个原位置的七层编码及几何未发现完全相同的两帧，各用一张导出。 层叠只用于静态相位诊断。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [朝向探针](../../motion-continuation-20261112/moon-shadow-east/source-face-groups.png) · [逐相位来源](source-south-evidence.json)

原创重绘承接自有待机的银发、深蓝围巾、金边衣袍及双月刃。两张母图的原生尺寸为 2188×719 和 2170×725。保留实际提示词、参考图摘要和工具回执。内置工具未披露实际模型和质量。导出统一采用 256×256 RGBA 和 0.3184 等比缩放，裁格及导出边缘通过 Alpha≥8 检查。髋部坐标与底线仅用于诊断排版。 [相位清单](manifest.json) · [浅深底 112／64／48／32 像素预览](review-light-dark.png)

f19/f20 屏右鞋在下，f22/f23 屏左鞋在下，f21 保留眨眼。f20、f23 分别抬起对侧月刃。两母图的头顶高度和衣摆轮廓略有差异，仍需人工核对循环衔接。原播放时长、循环、角色锚点仍待证，候选尚未接入运行。

在仓库根目录执行以下命令重建来源证据和导出。

```powershell
python -B assets/characters/motion-continuation-20261113/moon-shadow-north/inspect-role22-walk.py south
python -B assets/characters/motion-continuation-20261113/moon-shadow-north/export-role22-walk.py south
```
