# 房间、商店、对局与设置的原生参照

本目录保存六件 QQTang-Local 源资源的逐帧解码结果。原始 SHA-256、包索引条目、帧结构、五份 UI 模块的静态字面量及原坐标见 [manifest.json](manifest.json)。

| 原生路径 | 声明画布 | 实际帧 | 原始偏移 | 图上固定文字和布局 |
| --- | --- | --- | --- | --- |
| `object/ui/bg/bg_room.img` | 800×600 | 800×600 | `[0,0]` | 左侧人员区与聊天区，右侧模式、地图、队色与七格装备栏；装备道具栏、A–H、1–7 |
| `object/ui/bg/bg_shop.img` | 800×600 | 800×600 | `[0,0]` | 左侧商品区，右侧预览、名片和三行五列物品格；酷比宝石、QQ糖币、我的名片、我的道具箱 |
| `object/ui/bg/bg_game.img` | 200×600 | 200×600 | `[0,0]` | 时间栏、八条玩家信息槽、底部提示框；时间、TIMER |
| `object/ui/bg/bg_logo.img` | 800×600 | 800×600 | `[0,0]` | 原 Jade Studio 标志与版权文字 |
| `object/ui/common/dlg_setup.img` | 423×497 | 423×497 | `[0,0]` | 键盘设置、游戏设置，各按键用途与鼠标说明 |
| `object/ui/game/dlg_playerList.img` | 191×600 | 184×600 | `[7,0]` | 时间栏、八条玩家信息槽、底部提示框；时间、TIMER |

`bg_game.img` 在已解析 `uiGame` 的静态字面量中未找到直接绑定。`UI_children_game.children.playerListDlg` 明确使用 `dlg_playerList.img`，控件坐标 `[609,0,1,1]`。因此两个侧栏分别制作；运行中是否还使用前者待确认。

`UI.children.setupDlg` 的 `bkimagepos` 为 `[-8,-6]`。源图上的字段和提示保持原位置，控件坐标另存。设置框中原固定说明为角色选择、队伍选择、玩家资料、系统设置，七个使用道具和七个商店按键，以及音效、背景音乐、特效、全屏、软件渲染和硬件渲染。

自有替换绘制器在 [native-ui-core-art.py](../../../scripts/native-ui-core-art.py)，调用现有道家 Q 版画板和界面边框。商城输出把两项货币显示名改为“灵玉”和“灵币”，设置输出采用“放置灵葫”。本目录保留原始参照像素及其原始文字。实际安装及待验范围见 [原生 UI 交付](../../../docs/NATIVE_CLIENT_UI_DELIVERY_20261113.md)。 [QQ 堂来源](../../../docs/QQTANG_REFERENCE_SOURCE.md)
