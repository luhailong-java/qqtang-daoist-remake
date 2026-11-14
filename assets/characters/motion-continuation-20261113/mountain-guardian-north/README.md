# 山岳北向步行六相位

2026-11-13（America/New_York）。角色 1 对应山岳，固定社区参照包的四方向脸探针显示组 1 为背向，源位置 f6–f11。原声明画布为 100×100。每个位置解出 body1、foot1、leg10101、cloth10101、face10101、hair10101、npack10101，另读 head1 元数据。f6 与 f9 的八个声明层在编码、尺寸、偏移、模式及空标记上相同，六原位置采用五张各异诊断图。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [朝向探针](../mountain-guardian-west/source-face-groups.png) · [逐相位来源](source-north-evidence.json)

本批已发出的两次内置生图均返回 2172×724 RGBA 母图，实际模型和质量未披露。用自有山岳北向待机及两张道家 Q 版风格图作参照，保留屏左玉盾与屏右金环杖。五张 256×256 RGBA 导出使用 0.3184 等比缩放、量取的诊断髋部及基线。母图和导出中的 Alpha≥8 像素均未触及裁边。 [相位清单](manifest.json) · [112／64／48／32 像素浅深底预览](review-light-dark.png)

f7/f8 屏右鞋在下，f10/f11 屏左鞋在下，f8 稍抬盾臂，f11 稍抬杖臂。跨母图的衣摆纹样与脚掌露出略有差异，整组步态连贯和小屏辨识待人工审核。原播放时长、循环及角色锚点仍待证，候选尚未接入运行。

在仓库根目录复核。

```powershell
python -B assets/characters/motion-continuation-20261113/mountain-guardian-north/inspect-role1-walk.py north
python -B assets/characters/motion-continuation-20261113/mountain-guardian-north/export-role1-walk.py north
```
