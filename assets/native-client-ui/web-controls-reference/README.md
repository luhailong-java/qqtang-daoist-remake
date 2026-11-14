# 原生网页外框控件候选

2026-11-14。固定 `object/ui/web` 的十件资源、24 个原生位置已用本项目玉面、金边与纸绢窗框重绘，包含上下条、后退／前进／返回游戏／关闭按钮和嵌入面板。所有原 Alpha、尺寸、原始偏移、帧数、像素模式与非像素字节均保留。 [源图与静态合同](manifest.json) · [原生再解码候选](candidate-all-states.png) · [导出记录](candidate-manifest.json)

四份惰性解析的 uiMain／uiTemplate／uiFunc／uiShop 未命中这十条完整路径。原生包中这些资源确实存在，但实际加载及三帧引擎状态的语义仍待验证。按钮文字与箭头根据源图含义重新排版，英文候选采用同义中文；没有修改地址、网络连接或导航回调。

本批只处理外框。嵌入网页的远端 HTML、品牌、用户内容和运行时显示不由边框图控制，不能记作已换为自有界面。现有旧站点入口与原生动态文案仍在 [品牌文字差额](../../../docs/NATIVE_UI_BRAND_TEXT_20261114.md) 中待处理。

```powershell
python -B assets/native-client-ui/web-controls-reference/decode-references.py
python -B assets/native-client-ui/web-controls-reference/export-web.py --check
```

未运行原客户端、脚本或 GUI。自有纹理排版不增加生图；本目录独立导出器不负责安装，实际范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和回读为准。画面、运行及完整 UI 仍待验收。

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收继续待完成。
