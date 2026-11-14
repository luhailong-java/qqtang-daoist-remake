# 原生商城操作控件

2026-11-14（America/New_York）。本批为 11 个操作按钮、6 个商城分类页签和 3 个背包页签，共 20 个原生资源、62 个状态位置。逐帧查看固定 QQTang-Local 包的解码图，沿用原字“购买、默认、收藏、赠送、锻造合成、收藏柜、修复、索要、恢复、装备、背包”及各页签标签。紫钻分类的两帧底板原本无字，继续保留空白。 [原状态对照](source-contact.png) · [原图尺寸、偏移和绑定](manifest.json)

11 个按钮均有 uiShop 中的精确路径赋值与原 framescheme `[0,0,2,2,3,3,1,1]`。9 个页签保留两个原状态位置。默认、灰态、高亮与按下的外观按原图各自位置制作，运行时状态意义及切换仍需人工观察。源码仅作为有界常量树读取，实际控件运行分支待验。

新画面复用现有原创玉绿暖金按钮及纸绢窗框，用 Microsoft YaHei 在原控件画幅内排字。画面在原生 RGB565／Alpha32 像素模式下编码再解码，原声明画布、全部帧数、原帧顺序、逐帧尺寸、偏移及结构字段通过核对。每张输出保留字体和现有画稿来源，当前为现有画稿派生。 [新状态对照](candidate/contact-native-2x.png) · [候选资源与来源](candidate-manifest.json) · [标准渲染接口](../../../scripts/native-ui-shop-controls-art.py)

此批已由主构建器重导出，并安装到用户提供目录。人工视觉与交互验收仍待定。当前文件已由主构建器注册 `PATHS` 及 `render(kind, label, index, size, paints, font_path, nine_slice, scaled)`，原生路径无须更名。

```powershell
python -B assets/native-client-ui/shop-controls-reference/decode-references.py
python -B assets/native-client-ui/shop-controls-reference/verify-renderer.py --check
```
