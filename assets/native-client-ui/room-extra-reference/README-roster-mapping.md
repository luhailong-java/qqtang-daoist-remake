# 房间与商城角色图的确证配对

[roster-mapping-audit.json](roster-mapping-audit.json) 是两组共同使用的20个项目身份合同；其中 `entries` 的18条供房间选择页及商城使用，`pveAdditionalEntries` 的2条只补充有证据的PVE头像别名。所有 `uiShortName` 直接沿用现有头像清单的2字项目名，没有猜腾讯旧名或重分配角色。

`uiRoom` 根代码在字节161–230构造 `RoleNameList`，230–299构造平行 `RoleIDList`，以 `STORE_GLOBAL` 保存。此前只识别 `STORE_NAME` 的文字识别器会遗漏这两表。按组和位置配对可得到18个具体角色以及随机23；随机只是占位，不是第21个自有角色。`ui_UpdateRole` 及角色提示回调按同一索引格式化图标、名字和插画路径。

`uiShop.charIconList` 具有22项、包含空位，`getCharIconName` 使用源角色索引减1取得文件别名。18个非空别名的索引与房间两张平行表所得角色ID完全相等。

`uiGame.g_RoleNameList` 是带空首项的23元组，字节174–249构造。`ui_InitPVEPlayer` 按 `m_nRoleID` 直接索引，证实 `cbz=10→星阵` 和 `xz=11→玄龟`；这两项复用既有独立项目形象。另一个原列表成员 `12=ls` 不在当前20具体角色分配，也没有本批路径，不据此新增人物。

| 源ID | 原生别名 | 项目UI名 |
|---:|---|---|
| 1 | xwk | 山岳 |
| 2 | tt | 莲花 |
| 3 | xq | 冰剑 |
| 4 | cl | 火符 |
| 5 | bbl | 天音 |
| 6 | hy | 雷法 |
| 7 | mly | 炼丹 |
| 8 | hwz | 竹弓 |
| 9 | boy | 道童 |
| 10 | cbz | 星阵 |
| 11 | xz | 玄龟 |
| 13 | kl | 松翁 |
| 14 | nz | 玉匠 |
| 15 | wll | 纸鸢 |
| 16 | yy | 赤砂 |
| 18 | yd | 赤枪 |
| 19 | ld | 唤雪 |
| 20 | ge | 水龙 |
| 21 | tb | 灵篆 |
| 22 | girl | 月影 |

数字头像的命名空间另列：[extra-icon-source-semantics.json](extra-icon-source-semantics.json)。`ui_InitPVEBoss` 使用 `bossInfo.m_iImageID` 格式化 `icon_%d.img`，未证明它等于角色ID、NPC ID或玩家INI编号。因此没有凭 `icon_117` 文件名或骷髅占位同图，把117认作玩家117或与78合并；17条未定画像路径各有独立原创UI母图。8个已有变身master的avatar41/42/43/44/45/46/54/55也没有硬套到这些画像槽。

这里只确证原生路径/索引与本项目已有外观分配的衔接。原时序、世界动作、挂点、统计单位、可选限制以及原程序运行仍待验，不是腾讯历史角色身份识别或整套动作完成证明。
