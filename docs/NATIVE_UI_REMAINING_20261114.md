# 原生 UI 剩余覆盖

本次显式读取 3 份转换清单和 1 份静态安装回执。源目录共 4223 个路径，其中 4209 份图像。当前有 740 个同名原生资源导出，安装回执覆盖 740 个路径，其中 740 个与当前导出 SHA 一致。

| 来源组 | 源图像路径 | 已转换 | 回执已装 | 图像仍待转换 |
|---|---:|---:|---:|---:|
| object/ui | 773 | 156 | 156 | 617 |
| ui | 14 | 1 | 1 | 13 |
| res/uiRes/icon | 3205 | 583 | 583 | 2622 |
| res/uiRes other | 217 | 0 | 0 | 217 |

图标行统计物品库存、角色头像等图像路径；其余三行统计界面图像。文件路径覆盖与整页、所有控件状态、动态文字和实际交互分别验收。静态安装回执也保留运行与用户画面审核的待验状态。

| 原生子组 | 源图像 | 已转换 | 回执已装 | 待转换 |
|---|---:|---:|---:|---:|
| loose/object/ui/login | 1 | 1 | 1 | 0 |
| loose/res/uiRes | 2 | 0 | 0 | 2 |
| loose/res/uiRes/face | 5 | 0 | 0 | 5 |
| loose/res/uiRes/face/faces | 144 | 0 | 0 | 144 |
| loose/res/uiRes/face/faces/member | 24 | 0 | 0 | 24 |
| loose/res/uiRes/game | 3 | 0 | 0 | 3 |
| loose/res/uiRes/gameChat | 8 | 0 | 0 | 8 |
| loose/res/uiRes/icon/bg | 395 | 6 | 6 | 389 |
| loose/res/uiRes/icon/bomb | 295 | 24 | 24 | 271 |
| loose/res/uiRes/icon/cap | 447 | 42 | 42 | 405 |
| loose/res/uiRes/icon/card | 20 | 20 | 20 | 0 |
| loose/res/uiRes/icon/chatBg | 10 | 0 | 0 | 10 |
| loose/res/uiRes/icon/cladorn | 365 | 6 | 6 | 359 |
| loose/res/uiRes/icon/ear | 62 | 62 | 62 | 0 |
| loose/res/uiRes/icon/enter | 71 | 1 | 1 | 70 |
| loose/res/uiRes/icon/eye | 71 | 71 | 71 | 0 |
| loose/res/uiRes/icon/food | 10 | 10 | 10 | 0 |
| loose/res/uiRes/icon/footprint | 74 | 74 | 74 | 0 |
| loose/res/uiRes/icon/forge | 7 | 7 | 7 | 0 |
| loose/res/uiRes/icon/fpack | 146 | 6 | 6 | 140 |
| loose/res/uiRes/icon/frame | 160 | 6 | 6 | 154 |
| loose/res/uiRes/icon/huanying | 103 | 0 | 0 | 103 |
| loose/res/uiRes/icon/item | 226 | 32 | 32 | 194 |
| loose/res/uiRes/icon/kubi | 2 | 2 | 2 | 0 |
| loose/res/uiRes/icon/light | 3 | 0 | 0 | 3 |
| loose/res/uiRes/icon/mouth | 145 | 6 | 6 | 139 |
| loose/res/uiRes/icon/namecard | 147 | 2 | 2 | 145 |
| loose/res/uiRes/icon/namecardbound | 3 | 3 | 3 | 0 |
| loose/res/uiRes/icon/npack | 197 | 11 | 11 | 186 |
| loose/res/uiRes/icon/npcIcon | 7 | 0 | 0 | 7 |
| loose/res/uiRes/icon/pet | 18 | 0 | 0 | 18 |
| loose/res/uiRes/icon/petItem | 21 | 0 | 0 | 21 |
| loose/res/uiRes/icon/petcard | 48 | 48 | 48 | 0 |
| loose/res/uiRes/icon/platform | 37 | 29 | 29 | 8 |
| loose/res/uiRes/icon/skill | 80 | 80 | 80 | 0 |
| loose/res/uiRes/icon/thadorn | 35 | 35 | 35 | 0 |
| loose/res/uiRes/number | 4 | 0 | 0 | 4 |
| loose/res/uiRes/selRoom | 2 | 0 | 0 | 2 |
| loose/res/uiRes/selRoom/icon | 6 | 0 | 0 | 6 |
| loose/res/uiRes/selRoom/mapFilter | 1 | 0 | 0 | 1 |
| loose/res/uiRes/selRoom/recorder | 9 | 0 | 0 | 9 |
| loose/res/uiRes/selRoom/room | 1 | 0 | 0 | 1 |
| loose/res/uiRes/selSect | 7 | 0 | 0 | 7 |
| loose/res/uiRes/shop | 1 | 0 | 0 | 1 |
| loose/ui/pawnshop | 1 | 0 | 0 | 1 |
| loose/ui/selSect | 13 | 1 | 1 | 12 |
| packed/object/ui/bg | 6 | 6 | 6 | 0 |
| packed/object/ui/chat | 15 | 0 | 0 | 15 |
| packed/object/ui/chatRoom | 12 | 0 | 0 | 12 |
| packed/object/ui/common | 28 | 28 | 28 | 0 |
| packed/object/ui/cursor | 2 | 0 | 0 | 2 |
| packed/object/ui/deal | 20 | 0 | 0 | 20 |
| packed/object/ui/forge | 21 | 0 | 0 | 21 |
| packed/object/ui/game | 25 | 25 | 25 | 0 |
| packed/object/ui/guideBar | 75 | 26 | 26 | 49 |
| packed/object/ui/kinTotem | 49 | 0 | 0 | 49 |
| packed/object/ui/level | 72 | 0 | 0 | 72 |
| packed/object/ui/login | 12 | 4 | 4 | 8 |
| packed/object/ui/map | 17 | 0 | 0 | 17 |
| packed/object/ui/marriage | 45 | 0 | 0 | 45 |
| packed/object/ui/pet | 23 | 0 | 0 | 23 |
| packed/object/ui/record | 2 | 0 | 0 | 2 |
| packed/object/ui/room | 133 | 18 | 18 | 115 |
| packed/object/ui/selRoom | 33 | 16 | 16 | 17 |
| packed/object/ui/selSect | 18 | 12 | 12 | 6 |
| packed/object/ui/shop | 132 | 20 | 20 | 112 |
| packed/object/ui/storage | 9 | 0 | 0 | 9 |
| packed/object/ui/task | 13 | 0 | 0 | 13 |
| packed/object/ui/web | 10 | 0 | 0 | 10 |

现有绘制资源中，0 个原生路径已有独立 renderer 定义、尚未出现在本次转换清单里；1 件库存候选仍在转换器的 pendingItems 中。对应精确路径、源尺寸和原因见机器清单。数值会随新增模块和转换清单变化，脚本接受多个 --manifest 与 --installation 参数后重算。

启动器标题／品牌、原生系统窗口标题、PYC 文案、运行时动态文字和 GBK12.bmp 字库均需单独核对。它们的替换状态保持 unknown 或 pending，本路径统计没有证明这些内容已换完。角色佩戴、地图、怪物、特效与音频属于整款游戏的另一个制作分母。

[完整机器清单](native-ui-remaining-20261114.json)保留输入哈希、逐路径差额、待转候选和审核边界。

```powershell
python -B scripts/audit-native-ui-remaining.py `
  --manifest assets/native-client-ui/login-v1/manifest.json `
  --manifest assets/native-client-ui/inventory-v1/manifest.json `
  --manifest assets/native-client-ui/inventory-phases-v1/manifest.json `
  --installation docs/native-client-installation-20261114.json
```
