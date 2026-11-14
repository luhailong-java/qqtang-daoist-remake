# 原生聊天控件候选

本批完整覆盖固定源 `object/ui/chat` 的15件与 `object/ui/chatRoom` 的12件，共27个资源、65个原始帧位。只写独立候选，没有接入主构建器、修改bundle、安装客户端、运行原程序、操作GUI或Git。`visualAccepted`、`nativeRuntimeVerified` 仍为 false。

绘制器为 `scripts/native-ui-chat-controls-art.py`，与现有模块保持相同 `render(kind,label,index,size,paints,font_path,nine_slice,scaled)` API。`PATHS` 的 kind 统一使用 `chat-` 前缀。`PAINT_INPUTS` 引用现成自有私聊与商城图标；按钮/面板引用既有自有深玉、米金纹理和窗框。小尺寸按钮仅取玉面纹理与金边，避免大卷云边挤压符号、文字；箭头、笑脸、喇叭与网格为本模块原创代码绘制。没有新增生图，也没有复用原图颜色或文字像素。

`STRUCTURAL_ALPHA_INPUTS` 提供65个源PNG路径。它们只贡献原始Alpha平面，每个候选在原生编码后均再次验证Alpha逐字节相同。聊天区中心128透明度、命令菜单中心179透明度、地图筛选遮罩全不透明，以及按钮外缘都保留。原容器版本、全部非像素字节、声明画布、实际帧尺寸、偏移、像素模式、帧顺序不变。

静态查看了三张源全状态图及最终三张候选全状态图，未作为用户视觉验收。依据实际源帧区分状态：发送/表情/命令下拉为0常态、1灰禁用、2高亮、3按压；喇叭为0常态、1高亮、2按压、3灰禁用。会员/普通和伸缩各三帧，频道页签分别保留浅底深字与深底浅字。这里的顺序来自源图观察，原引擎framescheme执行仍待验。

`text-color-source-evidence.json` 保存完整惰性PYC解析得到的字色、相邻符号赋值与父节点类构造指令窗口。没有执行、导入下载的脚本或构造CodeType。`contrast-contract.json` 保留具体解释：

- 密码与房间/大厅表情页码明确为白字，候选保留深玉底；密码值与页码由运行时绘制，不烘焙。
- 聊天编辑框明确 `LOAD_NAME lightColor`，`uiMain` 顶层同名常量为白色；模块共享全局的运行解析仍未实测。
- 大厅聊天列表明确为(199,242,252,255)，房间列表颜色未显式声明，逐消息颜色仍为运行数据，不能宣称全部消息对比度已验。
- 命令菜单 `profileView` 直接继承 `TButton`，其余项继承该类；该模板只声明BUTTON类型，没有字色。保留源暗底极性，未编造TLabel继承或白字证明。其高亮条还用于明确白字的地图筛选名称。默认引擎菜单字色与真实半透明叠底的可读性仍待运行确认。
- `img_chatMenu` 没有精确静态路径绑定，仅作为该源资源路径的候选导出；共享表情面板还用于家族图腾，相关运行效果待验。已有表情图片、头像和所有聊天页并未由此宣称完成。

候选清单 `candidate-manifest.json` 包含27个原生patch、65个解码PNG、Alpha证据、字色合同、源与自有素材哈希。三张 `candidate-all-states-*.png` 是浅/深底离线诊断图，不是原客户端截图。

从仓库根目录只读重放：

```powershell
python -B assets/native-client-ui/chat-controls-reference/capture-source.py --check
python -B assets/native-client-ui/chat-controls-reference/export-chat-controls.py --check
```

导出器验证原包哈希、所有原始状态、原生编码后解码、再次编码的像素平面、源Alpha逐字节一致及所有非像素字节不变。正式接入与客户端回读由统一主构建器/安装器另行处理。

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前安装与恢复范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收状态继续待完成。
