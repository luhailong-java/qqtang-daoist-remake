# 从用户提供目录启动的原生 UI 替换

用户明确的完成目标是从下载的 QQTang-Local 目录启动客户端，登录后进入我们的整套道家 Q 版界面。登录、选区、频道、大厅、房间、商城、设置、对局、结算和其余弹窗都在交付范围内。

截至 2026-11-14，已将首批 25 个资源、51 个原状态位置安装到该目录的 `runtime/client-patched`。安装后的松散 IMG 和包内 IMG 已重新读取，与本项目导出的资源逐字节核对。 [安装复核记录](native-client-installation-20261113.json)

| 已安装范围 | 资源 |
| --- | --- |
| 登录 | 原生背景、自有字标、登录面板、登录／离开／新手帮助按钮 |
| 通用控件 | 确定、取消、叉号的四个原帧位置 |
| 选区与频道 | 整屏底图、区域弹窗、条目背景、区域选择、快速加入、自由频道页签 |
| 大厅房间列表 | 整屏底图、三态房间卡、创建房间按钮、竞技模式页签 |
| 核心底板 | 房间、商城、设置底板、启动标识、对局背景侧栏及玩家列表侧栏 |

画稿沿用项目已有的仙山庭院、字标、玉纹金边按钮及纸绢窗框。字号、文字底色和边框按原控件画幅排版，透明、颜色按原 DIMG 的 RGB565／Alpha32 或 BGRA 格式编码。原始 `framescheme`、帧数、每帧宽高和偏移保留，按钮的各个图像位置分别导出。两张列表底图是既有切片的原生布局组合，整屏交互显示还需逐页人工核对。 [原生替换清单](../assets/native-client-ui/login-v1/manifest.json) · [解码后的登录面板](../assets/native-client-ui/login-v1/decoded/dlg_login-00.png) · [选区底图](../assets/native-client-ui/login-v1/decoded/bg_selSect-00.png) · [大厅底图](../assets/native-client-ui/login-v1/decoded/bg_selRoom-00.png)

23 个包内资源以新增 zlib 流装入 `data/object.pkg`，对应更新 `data/object.idx`。原包字节作为完整前缀保留，另外 3,459 个包内条目维持原值。登录背景和字标另安装到原松散路径。原文件备份与本机回执位于项目忽略目录 `.artifacts/native-client-ui-backup/login-v1/` 的客户端专属子目录。安装器已在独立副本核对安装、重复执行、升级和恢复。

设置底板保留按键输入框和七组道具／商店按键的位置，图上提示采用“放置灵葫”。商城两项货币的显示名采用“灵玉”和“灵币”，数值仍由原客户端绘制。对局背景侧栏另有编译路径字符串，玩家列表使用 `dlg_playerList.img` 的字面绑定，两者都已生成和安装。鼠标提示、动态字体对比、侧栏透明叠放和各控件交互仍需从客户端人工核对。 [源布局与文字](../assets/native-client-ui/core-reference/README.md)

在项目根目录可重新核对当前导出。安装器根据本机回执识别当前版本，更新同批资源时先恢复已校验的原文件，再安装新版本。

```powershell
python -B scripts/build-native-login-art.py --check
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched"
```

恢复到安装前资源可执行下列命令。

```powershell
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --restore
```

全部原生 UI 仍未完成。原生包内共有 772 个 UI 图像资源，首批已安装其中 23 个。各页面的剩余按钮、图标、结算以及大量状态和弹窗继续待换。全部物品、人物及地图候选的 PNG 还要逐项按原生格式和实际引用安装。整款美术、全部界面及原客户端启动后的视觉与交互验收均保持待完成。 [原生资源绑定](NATIVE_CLIENT_UI_BINDINGS_20261113.md) · [完整源库存](../references/qqtang-ui-data/native-ui-inventory.json) · [启动器资源持久性检查](NATIVE_LAUNCHER_UI_PERSISTENCE_20261114.md)
