# 原生启动器与美术资源持久性

固定 QQTang-Local 构建的普通「启动一个客户端」路径中，未找到恢复 object.pkg、object.idx、登录底图或 logo 的操作。对本轮已安装美术的静态判断是这些文件会继续被原客户端读取。本轮依据真实启动器二进制的调用和写入目标作判断，启动后的实际保留情况待用户运行核验。

QQTang-Launcher.exe 使用 runtime/bin/qqt-launcher-core.exe；GUI 中的客户端操作对应 start-client。核心管理器的 StartClient 位于 VA 0x1403b8ce0。LLVM 对固定包内核心程序的静态反汇编确认了以下自动写入，均以传入的客户端目录为根。

| 普通启动中的调用 | 明确目标和条件 | 本轮代码证据 |
|---|---|---|
| ensureClientAliases | 读取 config/combineforge.ini；config/combineforge.xml 不存在或 SHA-256 不同时，从 ini 复制到临时文件，再替换 xml 并复核哈希；相同则直接返回 | StartClient 的 0x1403b91ce 调用 0x1403bd480；两次 filepath.join 使用 config、combineforge.ini、combineforge.xml 三个实际字符串 |
| restoreClientDownloadScript | config/DLScript.xml 已等于内嵌内容则返回；缺失或不同且当前客户端计数为 0 时原子写入；计数非 0 时返回错误 | StartClient 的 0x1403b9d8e 调用 0x1403bde20；计数检查位于 0x1403bdfaa–0x1403bdfb5；原子写入调用位于 0x1403be076 |
| 帧率与连接设置 | 调用原有连接配置、帧率和客户端兼容性检查，以及状态、日志操作 | StartClient 可见 ApplyClientTarget、CheckStaticShopServer、CheckStaticMultiClient、CheckStaticFrameRate、applyClientFrameSettings 等调用 |

DLScript 的内嵌基线是 35 字节的 `<?xml version="1.0"?>\r\n<Command/>\r\n`。指针／长度／容量位于 VA 0x1408255c0，内容位于 VA 0x1407cb880。已有其他客户端且下载队列变化时，程序返回“客户端下载队列在另一个客户端运行期间发生变化；请先停止全部客户端再启动新实例”。这里的恢复目标是下载队列文件。

核心命令帮助列出 status、start-server、stop-server、start-client、stop-clients、save-gm 六个动作。当前发行包的 scripts 目录为空，也未携带启动器 Go／C# 源文件。根 start-server-windows.cmd 只校验服务程序和配置存在、创建运行目录并调用服务器，没有复制 UI 或重新解压资源的命令。管理器 New 仅做根路径和必需路径检查；StartServer 的已检查调用没有 UI 包恢复。被普通启动调用的两个辅助程序也未包含 object.pkg、object.idx 或 release-manifest.json 路径字符串。

release-manifest.json 有 9,637 条原发行文件记录，其中包含原 object.pkg、object.idx、登录底图和 logo 的大小及哈希。启动核心中未出现 release-manifest.json 字符串，普通 StartClient 调用中也未找到读取该清单并恢复美术的分支。重新解压原发行 ZIP 到同一目录会覆盖同名文件；这一行为和外部修复工具属于另一个入口，当前 GUI／核心动作清单中没有整包修复命令。

用户目录中的启动器、核心、两个辅助程序、README、release-manifest 和 Windows 服务脚本共七个静态文件，均与固定 ZIP 逐字节相同。审计输入的关键 SHA-256 如下。

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| QQTang-Launcher.exe | 271,360 | c649a065f1c6180672f3c497e5cf4cd3114e9d4e9f121f2eb1bd32b1f4deb0a3 |
| runtime/bin/qqt-launcher-core.exe | 13,073,920 | 568bf7560150a243122095a965888727e7841f7c79e0b577ed669d9d17b4380e |
| runtime/bin/qqt-launch-local.exe | 5,024,768 | b1d85433bc4fe9e16c49bc88367467243f4d5f6a98c13a837a1fec69a8a9da2b |
| runtime/bin/qqt-login-immediate.exe | 4,988,416 | 16d872b672db2153652c4ab199fc5a6dada7b37f4fc4b6db0a9f7b4858bc6541 |
| release-manifest.json | 1,850,860 | bccfa25e8799f2cc0f0e9b31806a288b4400b71534b5330d32153b61718e6b32 |

Go build info 标注核心为 qqtang/cmd/qqt-launcher-ctl、Go 1.26.7、提交 77178ada0f9db05baf14d5b0554e33889c1cc580，并标注修改过工作树。审计直接使用发行二进制，未把其他源码版本当作这份构建的证明。临时静态反汇编留在项目忽略目录 .artifacts/native-ui-audit-20261113/。全程没有启动原程序或辅助程序，未读用户账号、存档、日志、网络配置，未修改提供目录。
