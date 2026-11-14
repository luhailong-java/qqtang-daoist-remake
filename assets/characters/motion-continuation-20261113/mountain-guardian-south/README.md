# 山岳南向步行未通过透明门槛

2026-11-13（America/New_York）。角色 1 对应山岳，四方向脸探针显示组 3 朝正面，对应 f18–f23，原声明画布为 100×100。各位置共解码 42 个层像素并记录 head1 元数据。f18/f21 的八个声明层编码及几何相同。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [源六位置](source-south-evidence.json)

本批已发出的两个内置生图调用返回原生 2172×724 RGBA 母图，实际模型及质量未披露。A 图 Alpha 范围为 163–251，B 为 166–251，整幅画布都被白底覆盖。两张保留为在制母图及真实调用来源，记录为技术失败，导出帧数为零。 [失败清单](manifest.json) · [A 母图](mother-a-v1.png) · [B 母图](mother-b-v1.png)

原时长、循环和角色锚点仍待证。透明背景及导出尚待修复，候选尚未接入运行。

在仓库根目录可重建源证据并复核失败。

```powershell
python -B assets/characters/motion-continuation-20261113/mountain-guardian-north/inspect-role1-walk.py south
python -B assets/characters/motion-continuation-20261113/mountain-guardian-south/record-technical-failure.py
```
