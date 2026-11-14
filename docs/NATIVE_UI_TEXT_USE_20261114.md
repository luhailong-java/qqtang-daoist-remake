# 九处主题文案的静态使用点

只读解析固定源的代码对象与指令，不执行原客户端。九个目标分别只有一处 `LOAD_CONST` 使用点，确认用于展示值、消息、标题或价格单位，未把逻辑键或协议值改成新名称。变量命名空间、字库、宽度和实际运行仍待人工验收。

| 目标 | 数量 | 静态使用证据 |
|---|---:|---|
| levelCFG 的三个等级称号 | 3 | `LevelCfg` 相对字节 645 构建 30 项列表，648 存入 `titles`；`Level.getInfo` 读取名称，与数值等级分开返回 |
| uiMain 的婚姻提示 | 1 | `PlayerWord.const[12]` 写入 `priestwords`，uiRoom 的 `tempTimer.OnTimer` 经 `Win_SetText` 更新 `UI.room.priestword.words` |
| uiMain 的出价不足提示 | 1 | `NegotiateBtn.OnClick.const[5]` 用作 `Win_ShowMsgBox` 正文 |
| uiRoom 的地图提示标题 | 1 | `selMapDlg.children.sel.OnClick.const[6]` 用作消息框标题 |
| uiSelSect 的公告占位文字 | 1 | `billboard.const[13]` 拼接进 `caption` |
| uiShop 的币种页签 | 1 | `functionTab.OnClick.const[8]` 经 `Win_SetText` 写到 `UI.shop.subTab4` |
| uiShop 的价格单位 | 1 | `ware1.buyA.OnClick.const[23]` 参与 `makeStr`，结果经 `Win_SetText` 写到 `price2` |

[数据计划](../assets/native-client-ui/brand-text-v1/manifest.json) 以模块、完整作用域、常量索引、前后字符串和源代码段 SHA 固定这九个位置。独立按字段范围降序重放、逆补均得到精确原字节；还原九个目标后，完整惰性树与前像相等，2,257 个 `co_code`、全部网址和目标外序列化字节保持。

uiMain 的前像必须是已着色 `54b1bc…`，文案叠加后的实际版本为 `132ffe…`。恢复文字保留颜色；完整恢复先文字后颜色。 [实际回读](native-ui-brand-installation-20261114.json) · [工具与恢复](../assets/native-client-ui/brand-text-v1/README.md)
