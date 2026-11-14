# 对局边框、动态遮罩和录像控件

固定 QQTang-Local 源包共提取 24 个尚未覆盖的 game 图像路径、41 个原图像位置。此批先绘制 23 件、40 个位置，原生解码图和声明几何均保留在 [源合同](manifest.json)；玩家列表底板已经在 core 批次覆盖。 [原按钮及全部状态](source-controls.png) · [原底板](source-surfaces.png)

三个大按钮沿用“取消保存、保存录像、查看背包”的意义及原 `[0,0,2,2,3,3,1,1]` 映射。录像暂停资源的原图形是方块，本批仍用方块，不擅自改成双竖线；继续播放复用自有播放图标。倍速采用 2×、4×。录像四个小按钮的源图各只有三个位置，而静态 framescheme 引用了位置 3；这一源数据矛盾保留，未补造第四帧，实际运行行为待验。

自有绘制复用玉纹金边按钮、纸绢窗框、单选圆框和播放图标。`DYMASK` 对应的物品遮罩、环形冷却遮罩，以及生命条、玩家底罩、进度条，全部保留源 Alpha 逐像素形状，仅使用自有纹理或新配色替换 RGB。三种玩家生命条保留绿、蓝、红区分。主清单将这些源 Alpha 明确列为结构输入，未将其列为自有画稿。九件遮罩在最终原生编码后 Alpha 与源图逐像素一致，另有回归检查；这仍不等于原客户端运行验收。

`dlg_statusBar.img` 底板中的三种固定道具图标尚未转换。源图看似针、红色药瓶和带翼鞋，但局部常量只有三个数量位置，具体原生道具绑定尚未完整证明，当前保留缺口，不用猜测的图形代换。其余原生 UI 也继续制作。

绘制器见 [native-ui-game-controls-art.py](../../../scripts/native-ui-game-controls-art.py)，输出统一由主构建导出到 login-v1。 [安装进度](../../../docs/NATIVE_CLIENT_UI_DELIVERY_20261113.md)

```powershell
python -B assets/native-client-ui/game-controls-reference/decode-references.py
python -B scripts/build-native-login-art.py --check
python -B tests/native-ui-format.test.py
```
