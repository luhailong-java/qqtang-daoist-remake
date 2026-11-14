# 共享弹窗文字底色依据

uiTemplate 的 `?.TLabel` 声明默认 `drawcolor=(0,0,0,255)`。uiMain 的 `SysMsgbox.children.textlabel` 未覆盖此颜色，矩形 `[40,82,280,130]`；`SysMsgbox.children.hyPerLink1` 明确使用 `(0,0,255,255)`。 [模板常量](../references/qqtang-ui-data/constants/uiTemplate.json) · [uiMain 常量](../references/qqtang-ui-data/constants/uiMain.json)

common-message 因此采用浅纸正文区，移除压在玉梁上的烘焙标题，保留运行时消息含义。最终原生解码图正文采样点与黑字、蓝字对比均达到 4.5:1；回归测试从上述常量读取文字颜色后计算对比，而不固定某个新底色。控件继承和实际运行显示尚需人工核验，当前证据只支持静态字面量与候选底色的关系。 [解码候选](../assets/native-client-ui/login-v1/decoded/object__ui__common__dlg_msgBox-00.png) · [回归检查](../tests/native-ui-format.test.py)
