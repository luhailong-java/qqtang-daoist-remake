# 月影北向步行六相位

2026-11-13（America/New_York）。固定 QQTang-Local 社区样本的 player22.ini 对应月影。四方向脸层探针显示组 1 为北向，源位置 f6–11，声明画布为 100×100。每个位置解码 body1、foot2、leg12201、cloth12201、face12201、hair12201，另读 head1 元数据。已声明的七层中，f6 与 f9 的编码内容、尺寸、偏移、像素模式及空标记相同，故两原位置共用一张导出，保留五张各异候选图。 层叠只用于静态相位诊断。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [朝向探针](../../motion-continuation-20261112/moon-shadow-east/source-face-groups.png) · [逐相位来源](source-north-evidence.json)

原创重绘承接自有待机的银发、深蓝围巾、金边衣袍及双月刃。母图原生尺寸分别为 1942×809、2100×749，保留实际提示词、参考图摘要和工具回执。内置工具未披露实际模型和质量。导出为 256×256 RGBA，按母图使用 0.3184 与 0.3459 等比缩放以接近同一角色高度，裁格及导出边缘通过 Alpha≥8 检查。髋部坐标与底线仅用于诊断排版。 [相位清单](manifest.json) · [浅深底 112／64／48／32 像素预览](review-light-dark.png)

f7/f8 屏右鞋低，f10/f11 屏左鞋低，f8 和 f11 对侧袖与月刃抬起。两张母图的金边纹样与衣摆曲线有差异，抬脚的足底露出程度和动作衔接待人工审核。原播放时长、循环、角色锚点仍待证，候选尚未接入运行。

在仓库根目录执行以下命令重建来源证据和导出。

```powershell
python -B assets/characters/motion-continuation-20261113/moon-shadow-north/inspect-role22-walk.py north
python -B assets/characters/motion-continuation-20261113/moon-shadow-north/export-role22-walk.py north
```
