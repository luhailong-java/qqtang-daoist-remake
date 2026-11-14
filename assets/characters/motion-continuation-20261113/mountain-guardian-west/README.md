# 山岳西向步行六相位

2026-11-13（America/New_York）。固定 QQTang-Local 社区样本的角色 1 对应山岳，脸层探针确认组 2 朝屏左。其步行资源声明 100×100 画布，西向源位置为 f12–f17。逐帧解码 body1、foot1、leg10101、cloth10101、face10101、hair10101、npack10101，共 42 个层位置，另记录 head1 元数据。八个声明层的编码及几何逐对核对，15 对均有差异。该叠放用于静态诊断。 [QQ堂参照源](../../../../docs/QQTANG_REFERENCE_SOURCE.md) · [朝向探针](source-face-groups.png) · [逐相位来源](source-west-evidence.json)

使用山岳西向待机作身份参照，保留棕发绿绦、近手玉盾及远手金环杖。首轮 A 图 f13 的前鞋整只抬高，第二版保留较低的前脚跟。两张选用母图均为 2172×724 RGBA，旁附实际提示词、引用摘要和工具回执。实际模型与质量未披露。六张 256×256 RGBA 诊断帧以 0.3184 等比导出，Alpha≥8 像素未触及裁格或输出边。原时长、循环和角色锚点待核验，候选尚未接入运行。 [相位清单](manifest.json) · [浅深底 112／64／48／32 像素预览](review-light-dark.png)

f15 保留眨眼，f16 前鞋抬起，f17 后跟抬起。两张母图中杖杆下段被衣袍遮挡的程度不同，盾缘与垂穗形态略有差异，待人工核对步态和道具连贯性。

道童的 `player9.ini` 声明 `[trigger] cloth=10902`。固定 ZIP 名称和 `object.idx` 路径未检出 10902，对应放泡动作仍缺映射证据。此次补的是可按源位核对的山岳步行，既有运行跑步资源另行记录。 [既有动作接入](../../../../docs/CHARACTER_MOTION_ADOPTION.md)

在仓库根目录复核。

```powershell
python -B assets/characters/motion-continuation-20261113/mountain-guardian-west/inspect-role1-west.py
python -B assets/characters/motion-continuation-20261113/mountain-guardian-west/export-diagnostics.py
```
