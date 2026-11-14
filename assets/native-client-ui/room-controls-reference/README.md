# 原生房间控件参照与道家 Q 版绘制器

本批解码十八件房间资源，共四十四个非空帧位。原生画布、逐帧尺寸、偏移、像素模式、包索引、原图 SHA-256 和源码作用域保存在 [manifest.json](manifest.json)。源图与源码来自固定 QQTang-Local 资源包；参照提取未改动用户输入，随后此批已由主构建器重导出并安装到用户目录。

| 原生路径末段，均位于 `object/ui/room/` | 帧位 | 源图文字或用途 |
| --- | --- | --- |
| `btn_selMode.img` | 4 | 选择模式 |
| `btn_roomProp.img` | 4 | 房间属性 |
| `btn_selMap.img` | 4 | 选择地图 |
| `btn_ready.img` | 4 | 准备、ready |
| `btn_start.img` | 4 | 开始、start |
| `btn_unready.img` | 4 | 取消准备、cancel |
| `btn_storage.img` | 4 | 我的背包 |
| `dlg_selMode.img` | 1 | 选择游戏模式；模式、竞技、探险；房间、无道具、道具 |
| `dlg_roomProp.img` | 1 | 修改房间属性；模式、自由、标准、名称、保密、是、密码 |
| `dlg_selMap.img` | 1 | 左侧地图条目区、右上预览框，其余右侧透明 |
| `btn_equipItem.img` | 1 | 装备格底图 |
| `btn_map.img` | 1 | 地图名称高亮条 |
| `scl_block.img` | 3 | 聊天滚动条滑块 |
| `dlg_chatPanelSmall.img`、`dlg_chatPanelBig.img` | 各 1 | 深色聊天底板 |
| `tab_integration.img`、`tab_kin.img`、`tab_whisper.img` | 各 2 | 综合、家族、私聊 |

工具栏的前三件源图为蓝色普通、较亮、压下和灰色四帧；准备、开始、取消准备、背包资源的灰色帧位为 1，较亮和压下帧位为 2、3。根据原图外观与局部 `framescheme` 分别重绘两组帧位，避免将相同下标直接解释为相同交互状态。 [原工具栏全部帧位](source-buttons.png)

`selModeBtn`、`roomModifyBtn` 有 `[[0,0,1,1,2,2,3,3],[0,0,1,1,0,0,3,3]]` 局部映射。`startBtn` 和 `storageBtn` 有 `[[0,0,2,2,3,3,1,1]]`。`btn_start.img` 与 `btn_unready.img` 出现在房间席位或准备状态通知函数的路径字面量中。`selMapBtn` 的局部作用域没有显式映射字面量。运行中的状态触发顺序仍需核验。

聊天页签使用 `hotcover` 与 `hotrect`，两张聊天底板暂未找到完整路径字面量绑定，其实际使用状态待确认。地图选择框保留右下透明区域，装备格、地图高亮条与聊天底板为动态图标或文字留出底色。 [小控件与页签原图](source-small-controls.png)

自有绘制器为 [native-ui-room-controls-art.py](../../../scripts/native-ui-room-controls-art.py)。它复用现有道家 Q 版画板和字体，保留上述原文字义与独立尺寸。运行 `verify-renderer.py` 可在项目忽略目录导出全部原生像素模式预览，检查四十四个帧位和 DIMG 非像素字节；不安装到客户端。 [QQ 堂来源](../../../docs/QQTANG_REFERENCE_SOURCE.md)
