# 大厅按钮、频道页签和小弹窗

本批二十件原生资源包含四十二个非空帧位。每件的原始画布、帧尺寸、偏移、包索引、源 PNG 与 SHA-256，及 `uiSelSect`、`uiSelRoom` 的字面量绑定，均见 [manifest.json](manifest.json)。 [源控件全部帧位](source-controls.png)

| 路径，位于 `object/ui/` | 源图文案 | 帧位 |
| --- | --- | --- |
| `selSect/btn_practice.img` | 新手练习 | 3 |
| `selSect/btn_sysSetup.img` | 系统设置 | 3 |
| `selSect/tab_practice.img` | 练习频道 | 2 |
| `selSect/tab_greenhand.img` | 新手频道 | 2 |
| `selSect/tab_match.img` | 比赛频道 | 2 |
| `selSect/tab_party.img` | 活动频道 | 2 |
| `selSect/btn_choose.img` | 区域列表底条，动态文字 | 1 |
| `selRoom/tab_chat.img` | 聊天房间 | 2 |
| `selRoom/tab_explore.img` | 探险模式 | 2 |
| `selRoom/tab_honor.img` | 抢宝场 | 2 |
| `selRoom/tab_item.img` | 道具场 | 2 |
| `selRoom/tab_noItem.img` | 无道具场 | 2 |
| `selRoom/tab_player.img` | 玩家 | 2 |
| `selRoom/tab_friend.img` | 好友 | 2 |
| `selRoom/tab_allKinMember.img` | 全家福 | 2 |
| `selRoom/btn_shop.img` | 道具商城 | 3 |
| `selRoom/btn_match.img` | 家族联赛 | 3 |
| `selRoom/dlg_pwRoom.img` | 请输入密码！ | 1 |
| `selRoom/map/dlg_mapFilter.img` | 地图分类列表底板，动态文字 | 1 |
| `selRoom/btn_mapFilter.img` | 向下与向左箭头 | 3 |

所有二十件均有精确路径字面量或属性绑定。频道与多数大厅页签使用 `hotcover`/`hotrect`，第一频道的分组映射为 `[[0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1]]`。三个大按钮帧依次呈实色、亮色、描边文字。地图筛选按钮帧 0 朝下，帧 1 和 2 朝左，绘制器分别保留。

密码框输入 `pwRoom.children.pw` 通过相邻 `LOAD_NAME TEditPassword`、`BUILD_CLASS`、`STORE_NAME pw` 字节码结构确认继承 `TEditPassword`。该模板显式设置白字，因此使用深色输入底。普通 `TEdit`、`TLabel` 的模板默认黑字另行记录。地图筛选的 `mapMode0.children.name` 和 `mapFilterBtn.children.text` 均显式设置白字，也使用深色底。上述来源、字节偏移和属性证据保存在 `contrastEvidence`，未执行源字节码。

自有绘制器 [native-ui-lobby-controls-art.py](../../../scripts/native-ui-lobby-controls-art.py) 复用现有道家 Q 版画板和字体。`verify-renderer.py` 在项目忽略目录生成原生编码后的预览，并检查全部帧尺寸、偏移和非像素 DIMG 字节。完整帧位已通过编码检查，实际触发状态与界面布局仍待运行核验。 [QQ 堂来源](../../../docs/QQTANG_REFERENCE_SOURCE.md)
