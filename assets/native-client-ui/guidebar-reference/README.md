# 导航与社交控件原生候选

本批 26 份同名原生资源覆盖 78 个源位置，沿用现有道家 Q 版窗框、按钮、人物／商城／任务／社交图标及中文字体。源位于 object.pkg 的 guideBar 组，逐帧解码图、原尺寸、偏移、像素模式及控件字面绑定见 [manifest.json](manifest.json)。

八个三态导航按钮、五个四态系统菜单按钮、六个四态社交按钮、三个双态资料页签，加上顶栏、两张菜单底板和上下文选择条，均已按原像素格式编码并重新解码。所有非像素字节与源资源一致。完整原生候选在 patch/，实际原生模式解码图在 decoded/。见[候选清单](candidate-manifest.json)和[全部状态预览](candidate-all-states.png)。

上下文菜单的 messageBtn 显式设置 drawcolor=lightColor，uiMain 的 lightColor 为白色。八个相关菜单类通过原字节码的 LOAD_NAME→BUILD_CLASS 继承该按钮样式，textEdgeType 为 -1。菜单和高亮条的文字区因此保留深玉色，仅让边缘和纹理形成高亮。通用系统菜单底板使用浅纸色，烘焙按钮使用自己的描边文字。见[字色与继承证据](contrast-evidence.json)。

当前菜单回调、动态文字和网址仍由源 PYC 控制；本批只替换图片。小尺寸人物图标及细金边还需用户看实际运行效果。已由主构建器重导出并通过统一图片包安装到用户目录。视觉和原生运行验收保持待验。

```powershell
python -B assets/native-client-ui/guidebar-reference/decode-references.py
python -B assets/native-client-ui/guidebar-reference/contrast-evidence.py
python -B assets/native-client-ui/guidebar-reference/export-guidebar.py
python -B assets/native-client-ui/guidebar-reference/export-guidebar.py --check
```
