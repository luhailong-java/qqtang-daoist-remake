# 用户提供客户端的原生 UI 资源绑定

用户本次验收目标是从提供的 QQTang-Local 目录启动原客户端，进入道家 Q 版的全部界面。本轮对固定来源包进行了静态 UI 清查，取得了原生路径、画幅、逐帧偏移和页面模块的字面绑定。现有 PNG、CSS 及浏览器页面需要先转换、安装到这些原生路径，才有原客户端显示的依据。资源来源和完整清单见 [QQ堂参照源](QQTANG_REFERENCE_SOURCE.md)及[原生 UI 库存](../references/qqtang-ui-data/native-ui-inventory.json)。

固定 ZIP 的 288,298,460 字节及 SHA-256 已重新核对。解压后的 object.pkg、object.idx 也与 ZIP 同名成员逐字节核对。13 个 PYC 文件由项目已有的有界常量树解析器作为数据读取，保留 3,213 个代码作用域中的路径出现位置和 1,608 条路径记录；其中包含同一字面量的常量出现和直接 STORE_NAME 赋值两种记录。没有执行这些 PYC、原 EXE 或 DLL。

| 来源范围 | 源路径数 | 可核对的结构 |
|---|---:|---|
| object.pkg 内 object/ui | 772 | 771 份 DIMG、1 份 TGA |
| 松散 object/ui | 2 | 登录 logo DIMG、fight.gsa 光标资源 |
| 松散 ui | 14 | 13 份 DIMG、1 份 TGA |
| 松散 res/uiRes | 3,435 | 3,420 份 DIMG、2 份 GIF、13 份 PYC |
| 全部独立原生路径 | 4,223 | 4,209 份图像、13 份脚本、1 份 GSA |

图像共声明 5,398 个帧位置，包含 4,205 份 DIMG 的 5,394 个位置。4,203 份 DIMG 的声明结构、边界和 EOF 核查通过；cladorn568.img 和 eye80.img 各有未解释的 65537 版本尾随数据，记录了声明帧及尾随长度、哈希。此批采用元数据读取，未解码全部像素，全部图像状态／透明包络仍需逐项检查。guideBar/btn_check.img 虽有 img 后缀，实际是 10×8 RGBA TGA，转换器需按真实格式分支处理。

Client.exe 中找到 res/uiRes/uiMain.pyc 字符串，文件偏移为 3,767,928，data\\object.pkg 字符串偏移为 3,769,780。uiMain 的 UI 作用域常量中有 uiLogo、uiLogin、uiSelSect、uiSelRoom、uiRoom、uiShop、uiWeb、uiGame 八个页面模块路径。Client.exe 另外有 33 处 UI 路径字符串，32 个能精确命中本清单；原生对局侧栏也有编译进 EXE 的资源路径。字符串位置均已记录，静态字符串本身未确认运行分支和加载优先级。

| 页面／控件 | 字面绑定 | 原声明尺寸与帧 |
|---|---|---|
| 启动画面 | uiLogo → object/ui/bg/bg_logo.img | 800×600，1 帧 |
| 登录底图 | uiLogin → ui/selSect/bg_login.img | 800×600，1 帧 |
| 登录框 | uiLogin → object/ui/login/dlg_login.img | 346×429，1 帧，实际 346×428，偏移 (0,1) |
| 登录 logo | uiLogin → object/ui/login/img_logo.img | 201×175，1 帧，实际 196×172，偏移 (5,3) |
| 登录按钮 | uiLogin → object/ui/login/btn_login.img | 82×33，3 帧，各帧偏移不同 |
| 登录退出 | uiLogin → object/ui/login/btn_quit.img | 44×32，3 帧，各帧偏移不同 |
| 选区／频道 | uiSelSect → object/ui/bg/bg_selSect.img | 800×600，1 帧 |
| 大厅／选房 | uiSelRoom → object/ui/bg/bg_selRoom.img | 800×600，1 帧 |
| 房间 | uiRoom → object/ui/bg/bg_room.img | 800×600，1 帧 |
| 商城 | uiShop → object/ui/bg/bg_shop.img | 800×600，1 帧 |
| 对局侧栏 | Client.exe 字符串 → object/ui/bg/bg_game.img | 200×600，1 帧 |
| 通用叉号 | uiLogin 等六模块 → object/ui/common/btn_cross.img | 22×22，4 帧 |
| 通用取消 | uiLogin 等五模块 → object/ui/common/btn_cancel.img | 44×32，4 帧，各帧偏移不同 |

PYC 中 481 个原生 UI 路径有精确字面引用，另有 42 种动态模板。例如 res/uires/icon/%s/%s%d.img 依运行数据选择类别和资源号。3,742 个清单路径没有精确字面引用，其中包括经模板读取的物品图标；不能据此删除或跳过。9 个带目录的字面路径在包及松散目录中未命中，另有 6 个不完整路径片段。缺失表与每个控件所属模块、作用域、属性名、字节位置及可直接识别的 rect 均保留在机器清单，运行分支和动态拼接还需验证。

772 份包内 UI 主要分布在 room 133、shop 132、guideBar 75、level 72、kinTotem 49、marriage 45、selRoom 33、common 28、game 25 等 23 个子组。清单提供资源分母；全部界面验收还包括登录、选区、大厅、房间、商城、对局和其余弹窗的普通、指向、按下、禁用及交互状态，具体状态含义要从原控件行为核对。

最小原生替换增量可从登录链执行。把原创底图、logo、登录框、登录按钮和通用关闭／取消等图片转换成同名原生资源，保留声明画幅、原帧顺序、逐帧尺寸与偏移。松散资源按原路径安装；包内资源可在 object.pkg 末尾增加新的独立 zlib 流并更新对应 object.idx 条目的偏移和长度，保持其他条目原值。随后从提供目录启动原客户端，逐项观察正常／指向／按下等状态。原生格式转换、包内安装、启动后实际显示与全 UI 覆盖分别记录，源库存本身没有签署替换验收。

审计也只读比较了用户提供目录中的全部 3,451 份松散 UI、两个 object 数据包文件和 Client.exe，共 3,454 个静态文件。捕获时 3,450 个与固定包一致，登录 logo、登录底图、object.pkg、object.idx 四个已存在字节变化。差异路径和实际哈希保存在机器清单的 providedDirectoryStaticComparison，与固定源基线分开记录。本轮仅写项目内的库存和本说明，未改动用户目录，未读取账号、存档、日志、服务或网络配置。
