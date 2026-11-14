# 共享弹窗文字底色依据

`SysMsgbox.children.textlabel` 使用非字面量 `drawcolor=zoneChooseColor`。`TLabel` 模板虽然默认黑字，局部 `literalAssignments` 没有 drawcolor 不能据此推断未覆盖。uiMain 根作用域的 `zoneChooseColor=[255,250,236,255]` 为浅米白。 [uiMain 常量](../references/qqtang-ui-data/constants/uiMain.json) · [全局值](../assets/native-client-ui/core-reference/manifest.json) · [字节级复核](NATIVE_UI_TEXT_CONTRAST_AUDIT_20261114.md)

正文采用深玉底以适配该浅色字。回归测试从原全局声明读取颜色，检查最终原生解码像素，而不按默认黑字假定。顶部压在玉梁上的烘焙标题已移除，共享消息含义继续由运行时数据决定。 [解码候选](../assets/native-client-ui/login-v1/decoded/object__ui__common__dlg_msgBox-00.png)

`hyPerLink1` 原为蓝色，现通过单独的数据补丁改为 `[200,200,255,255]` 浅蓝紫，共享描边同步改为 `[255,200,200,200]`。仅改变一个共享整数的数据负载，全部代码段、网址、文案、矩形和回调不变；两项颜色的联动明确记录。正文和新的链接颜色均在最终原生背景采样点达到选定对比阈值，实际字库描边和运行显示仍待人工核验。 [样式数据](../assets/native-client-ui/text-color-v1/README.md)
