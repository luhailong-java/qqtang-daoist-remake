# 丹羽凤翼世界装扮帧候选

物品 147 对应社区客户端档案的 `object/fpack/fpack18_stand.img` 和 `object/fpack/fpack18_walk.img`。两份成员逐字节一致，各有 16 个非空原位置，头部声明为四个方向、96×65 画布。原位置中有 9 份独立 RGBA 图；两份成员各自的 16 个位置与每位置原偏移均登记在[世界清单](world-art.json)。原档案 SHA、成员 SHA、声明画布和逐位置数据见[源记录](source-contract.json)。

九张原创帧延续[丹羽凤翼库存图](../spirit-wings-a/147-ember-phoenix-wings.png)的丹金羽片和金色如意卷。两组六个单翼姿态保留外扫方向以及收拢、平扫、抬羽三种形态；三张双翼姿态保留上部中空和底部相接。第二次内置编辑重画了 04、05、06 的金卷接合。两次实际母图分别为 1254×1254 和 2172×724，工具没有披露实际模型和质量。见[首张母图记录](phoenix-v1.png.generation.json)、[返修母图记录](phoenix-v2.png.generation.json)和[选用裁口](selection.json)。

导出为原逻辑尺寸的 4 倍 RGBA。仅按 alpha 包络裁切、预乘 alpha 等比缩放，并沿源图包络横向居中、下缘对齐。最大裁口边缘 alpha 为 2，九张图相对源图轮廓宽高比最大偏差 6.39%。04、05、06 中缝中央测点 alpha 均为 0，底部中线峰值分别为 253、255、252。重复位置只按源尺寸与解码 RGBA 像素相同复用，仍保留逐位置原偏移。见[检查记录](verification.json)。

[浅底逐位置对照](contact-light.png)和[深玉底逐位置对照](contact-jade.png)以 2 倍逻辑大小显示源图和原创帧。画面待用户审核。实际方向含义、帧时长、人物遮挡层与佩戴挂点仍待实机证据，未接入运行。

```powershell
python -B assets/items/wing-adornments/world-147/world.py
```
