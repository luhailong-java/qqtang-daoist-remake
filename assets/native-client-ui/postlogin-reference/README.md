# 选区与房间列表原生资源参照

从固定 QQTang-Local v1.3.4 资源包解码十件界面资源、二十个帧位，并对 `uiSelSect.pyc`、`uiSelRoom.pyc` 做静态字面量读取。完整源路径、源码作用域、坐标、原始帧偏移、像素模式、源字节与 PNG 的 SHA-256 见 [manifest.json](manifest.json)。

| 原生资源路径 | 声明画布 | 各帧尺寸及原始偏移 | 图上文字 |
| --- | --- | --- | --- |
| `object/ui/bg/bg_selSect.img` | 800×600 | 800×600 `[0,0]` | 公告栏、小区选择，英文 Announcement、RegionSelection |
| `object/ui/bg/bg_selRoom.img` | 800×600 | 800×600 `[0,0]` | 底图无独立中文标题 |
| `object/ui/selSect/dlg_selServer.img` | 229×331 | 229×331 `[0,0]` | 区域选择 |
| `object/ui/selSect/img_sect.img` | 187×26 | 187×26 `[0,0]` | 空条目背景 |
| `object/ui/selRoom/dlg_room.img` | 181×111 | 178×107 `[1,4]`；181×110 `[0,1]`；178×107 `[1,4]` | 房间信息槽，无固有文字 |
| `object/ui/selSect/btn_selZone.img` | 51×57 | 51×55 `[0,2]`；51×57 `[0,0]`；51×57 `[0,0]` | 区域选择 |
| `object/ui/selSect/btn_quickJoin.img` | 51×57 | 51×55 `[0,2]`；51×57 `[0,0]`；51×57 `[0,0]` | 快速加入 |
| `object/ui/selRoom/btn_createRoom.img` | 51×57 | 51×55 `[0,2]`；51×57 `[0,0]`；51×57 `[0,0]` | 创建房间 |
| `object/ui/selRoom/tab_compete.img` | 98×30 | 两帧均 98×25 `[0,5]` | 竞技模式 |
| `object/ui/selSect/tab_freedom.img` | 72×37 | 67×33 `[2,3]`；70×36 `[1,1]` | 自由频道 |

声明画布和实际每帧尺寸分别保留。原生按钮文字有深浅、实心和描边变化。房间卡的三个帧位有不同边框与填色。状态语义需要继续结合控件框架和运行结果核对。

选区底图左侧为公告和活动留白，右侧有两列区域列表底槽。房间列表底图左侧有两列、四行灰色房间占位，右侧为玩家与聊天面板。 [原尺寸双底图](backgrounds-native.png)

`tab_compete.img` 的源码作用域为 `UI_children_selRoom.children.modeCompete`，绑定属性为 `hotcover`，`hotrect` 为 `[20,39,98,30]`，`rect` 为 `[0,0,1,1]`。`dlg_room.img` 在 `room1` 的 `framescheme` 为 `[[1,1,1,1,2,2,0,0]]`。`img_sect.img` 在 `sect1` 的 `framescheme` 为 `[[-1,-1,0,0,-1,-1,-1,-1]]`。三件大按钮的当前作用域无显式 `framescheme` 字面量。 [框体与全部状态](panels-and-states.png)

这些 PNG 保存原始参照像素，供制作自有界面时核对布局和状态。未改动用户客户端。来源版本与认证边界见 [QQ 堂参照记录](../../../docs/QQTANG_REFERENCE_SOURCE.md)。
