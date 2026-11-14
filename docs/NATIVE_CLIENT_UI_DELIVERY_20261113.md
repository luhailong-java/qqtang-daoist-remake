# 从用户提供目录启动的原生 UI 替换

用户明确的完成目标是从下载的 QQTang-Local 目录启动客户端，登录后进入我们的整套道家 Q 版界面。登录、选区、频道、大厅、房间、商城、设置、对局、结算和其余弹窗都在交付范围内。

截至 2026-11-14，已将 242 个 UI 资源、570 个原状态位置安装到该目录的 `runtime/client-patched`。安装后的松散 IMG 和包内 IMG 已重新读取，与本项目导出的资源逐字节核对。 [安装复核记录](native-client-installation-20261114.json)

| 已安装范围 | 资源 |
| --- | --- |
| 登录 | 原生背景、自有字标、登录面板、登录／离开／新手帮助按钮 |
| 通用控件 | common 目录 28 个资源全部转换：按钮、单选、勾选、提示、滚动条、弹窗和七种数字条；功能与运行验收待完成 |
| 选区与频道 | 整屏底图、区域弹窗、条目背景、区域选择、快速加入、自由频道页签 |
| 大厅房间列表 | 整屏底图、三态房间卡、创建房间按钮、竞技模式页签 |
| 核心底板 | 房间、商城、设置底板、启动标识、对局背景侧栏及玩家列表侧栏 |
| 房间操作 | 18 个资源、44 个原位置：模式／属性／地图面板，准备／开始／取消准备／背包、聊天页签与滑块 |
| 商城操作 | 20 个资源、62 个原位置：购买、默认、收藏、赠送、锻造合成等按钮及九种分类页签 |
| 对局及录像 | 24 个资源、41 个原位置：状态栏、保存／取消录像、背包、聊天气泡、边框、遮罩、生命条和倍速／播放／暂停 |
| 大厅与选区补充 | 20 个资源、42 个原位置：频道、房型、玩家／好友页签，新手练习、系统设置、商城、家族联赛、密码框及地图筛选 |
| 导航与社交 | 26 个资源、78 个原位置：商城、交易、任务、资料、菜单、好友、密聊、追踪、求婚及资料页签 |
| 登录／状态补充 | 16 个资源、25 个原位置：验证码、VNET、等待、第二字标路径、连接条、网络状态和录像图标 |
| 聊天 | chat 与 chatRoom 全 27 个资源、65 个原位置；原 Alpha 逐像素保留 |
| 交易与寄售 | deal 全 20 个资源、58 个原位置；动态名字、金额留深玉底 |
| 背包与任务 | storage／task 全 22 个资源、48 个原位置；原坐标、27 个功能 Alpha 及动态字色保留 |

画稿沿用项目已有的仙山庭院、字标、玉纹金边按钮及纸绢窗框。字号、文字底色和边框按原控件画幅排版，透明、颜色按原 DIMG 的 RGB565／Alpha32 或 BGRA 格式编码。原始 `framescheme`、帧数、每帧宽高和偏移保留，按钮的各个图像位置分别导出。两张列表底图是既有切片的原生布局组合，整屏交互显示还需逐页人工核对。 [原生替换清单](../assets/native-client-ui/login-v1/manifest.json) · [解码后的登录面板](../assets/native-client-ui/login-v1/decoded/object__ui__login__dlg_login-00.png) · [选区底图](../assets/native-client-ui/login-v1/decoded/object__ui__bg__bg_selSect-00.png) · [大厅底图](../assets/native-client-ui/login-v1/decoded/object__ui__bg__bg_selRoom-00.png)

240 个包内 UI 资源与 52 个地图资源统一以新增 zlib 流装入 `data/object.pkg`，对应更新 `data/object.idx`。原包字节作为完整前缀保留，另外 3,190 个包内条目维持原值。登录背景和字标另安装到原松散路径。PNG 文件名现采用完整原生路径，避免不同页面同名按钮互相覆盖。原文件备份与本机回执位于项目忽略目录 `.artifacts/native-client-ui-backup/review-v1/` 的客户端专属子目录。安装器已在独立副本核对安装、重复执行、升级和恢复。

通用箭头和勾号使用 Segoe UI Symbol 避免缺字方框，中文继续使用 Microsoft YaHei；两种字体哈希均记录。共享消息框正文实际使用全局浅米白 zoneChooseColor，已恢复深玉正文底；不把局部字面量缺失当作没有颜色覆盖。未烘焙会干扰动态含义的标题。数字条保留 15 个等距字格与原顺序，numberMoney 的冒号／斜杠顺序与其他条不同。设置底板保留按键输入框和七组道具／商店按键的位置，图上提示采用“放置灵葫”。商城两项货币的显示名采用“灵玉”和“灵币”，数值仍由原客户端绘制。对局背景侧栏另有编译路径字符串，玩家列表使用 `dlg_playerList.img` 的字面绑定，两者都已生成和安装。对局九件功能遮罩保留原 Alpha；录像声明引用不存在的第四位置这一源数据矛盾保留，未补造额外帧。鼠标提示、动态字体对比、侧栏透明叠放和各控件交互仍需从客户端人工核对。 [对局控件源证据](../assets/native-client-ui/game-controls-reference/README.md) [源布局与文字](../assets/native-client-ui/core-reference/README.md)

在项目根目录可重新核对当前导出。安装器根据本机回执识别当前版本，更新同批资源时先恢复已校验的原文件，再安装新版本。

```powershell
python -B scripts/build-native-login-art.py --check
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched"
```

当前安装器默认采用统一图片包。下列命令恢复本批全部图片，包括库存、头饰和地图；共享链接的颜色数据另用专用工具恢复。 [统一包说明](../assets/native-client-bundle/review-v1/README.md)

```powershell
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --restore
```

全部原生 UI 仍未完成。原生包内共有 772 个 UI 图像资源，已安装其中 240 个。各页面的剩余按钮、图标、结算以及大量状态和弹窗继续待换。已有 583 个自有库存图标另批转换并安装，其中五件含等级或材质多状态；其余物品、人物及地图候选仍须逐项按原生格式和实际引用安装。 [库存批次](NATIVE_CLIENT_INVENTORY_20261114.md)整款美术、全部界面及原客户端启动后的视觉与交互验收均保持待完成。 [原生资源绑定](NATIVE_CLIENT_UI_BINDINGS_20261113.md) · [完整源库存](../references/qqtang-ui-data/native-ui-inventory.json) · [启动器资源持久性检查](NATIVE_LAUNCHER_UI_PERSISTENCE_20261114.md)

原生图像的逐路径缺口见 [最新 UI 覆盖审计](NATIVE_UI_REMAINING_20261114.md)。启动器、系统窗口标题和动态文本不计入图像路径覆盖；这些状态仍需单独核对。

地区选择名称通过全局符号使用 `zoneChooseColor=[255,250,236,255]` 浅米白和 `maskColor=[51,51,51,255]` 描边，源值在 uiMain 根作用域中。不能按局部字面量缺失推断默认黑字。右侧列表底及行条采用深玉以适配该浅字，回归检查直接读取实际全局颜色。-1 行映射与实际运行对比继续保留待验。 [字色复核](NATIVE_UI_TEXT_CONTRAST_AUDIT_20261114.md)

共享消息链接已作两项联动颜色调整：前景浅蓝紫、边缘柔粉，仍保留原网址、文案和回调。程序的全部 830 个代码段保持一致，只有一个 UI 颜色整数的数据负载变化。该样式数据单独备份，不混入图片源位置计数。 [颜色回读](native-ui-color-installation-20261114.json)

新增四组共 85 件、196 个源位置，已同现有图片统一安装并回读。已知 UI 图像路径尚余 3,384 个，动态文案仍有原产品／币种称谓与网址，不能将图像转换数量等同于所有界面完成。 [品牌文字差额](NATIVE_UI_BRAND_TEXT_20261114.md)
