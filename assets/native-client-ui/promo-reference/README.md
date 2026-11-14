# 原生推广图与资料默认角色候选

本组替换 15 个 loose 图像路径 / 15 个原图位置：顶层 `ui` 剩余 13 张推广图（12 DIMG + 1 TGA）和 `res/uiRes/avt_boy.gif`、`avt_girl.gif` 两张资料默认全身角色图。全部使用仓库现有原创品牌、世界、道童、莲灯及本轮原创道侣庭院母图组合。没有新增模型调用，没有沿用原活动字、原人像、品牌像素或其 Alpha 轮廓，也没有改原客户端代码。

`manifest.json` 记录固定 QQTang-Local v1.3.4 ZIP、原 loose member 路径、原文件 SHA、几何、格式、帧与静态源绑定；`frames/`、`source-contact.png` 是原图静态取证。固定 ZIP 的 SHA-256 为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。

`patch/` 为 15 个原格式候选，`decoded/` 为统一 codec 回读 PNG，`candidate-contact.png` 可进行人工视觉审核。模块 `scripts/native-ui-promo-art.py` 提供 `promo-` 前缀的 15 个 PATHS、`REFERENCE_MANIFEST`、`REFERENCE_INPUTS` 与六项 `PAINT_INPUTS`。`format-contract.json` 为主构建可引用的逐件语义合同。

- 12 DIMG 的画布、单帧、宽高、偏移、模式和全部非像素字节保持不变。
- TGA 为 330×165、24-bit BGR、未压缩、bottom-left、descriptor=0，原 18 字节头与标准 26 字节尾逐字节保留，只替换 `[18,163368)` 像素。原长 163394 字节不变，方向经回读确认。
- 两 GIF 保持真实 GIF89a、P 模式、140×226 全画布、单帧、不透明，原 duration=500ms、loop=0、disposal=1、background 索引 0、interlace=false 均保持。原透明索引和 comment 均不存在，候选也不添加。新调色板、LZW 编码及文件字节长度允许变化，不能声称 GIF 的非像素字节逐字节不变。
- 两 GIF 在源 `uiMain.UI.children.playerInfoDlg.children.avt` 与 `uiSelRoom.ui_getPlayerDetail` 中有完整路径字面量；13 张推广图在原清单的 13 个惰性 PYC 中没有完整路径字面量。路径计算、实际加载、点击目的地、角色换装叠加与活动运行均待验。

推广图使用新岁、桃源、青木、云海、星阵、莲灯等常驻主题文案，没有保留旧日期、奖券、商业合作人像或虚构新增活动功能。原文件名作为兼容路径保留；其旧活动名称不表示仍采用旧活动画面。两 GIF 使用完整道童/莲灯原创画稿，原生画布保留，原程序的资料逻辑未改。

在仓库根目录重放：

```powershell
python -B -X utf8 assets/native-client-ui/promo-reference/export-promo.py
python -B -X utf8 assets/native-client-ui/promo-reference/export-promo.py --check
```

`--check` 只读，验证源归档哈希、15 个来源哈希、回读尺寸/模式、13 个容器的全部非像素字节、两 GIF 的格式/计时/loop/处置/画布与输出确定性。静态检查通过不等于原生运行或用户视觉通过；完整 UI、整款游戏美术和手游适配仍未宣称完成。未执行原程序、PYC 或 GUI，未写用户客户端或 Git。

根代理补充共享格式回归，16→17 项后又加入真实源兼容与安装篡改检查，最终 **19 项通过**。最终 codec `44c2643eb25b28daaaa4c0f914072bf249b8bf22c4161a5ee4e4c1d46d138508` 拒绝非零 GIF 像素宽高比、comment、plain-text、未知应用扩展、user-input、透明和未知 reserved 组合；GCE 和固定结构 NETSCAPE2.0 各只允许一个。

两张真实源 GIF 的 GCE flags 为 `0xc4`：可见语义仍是 disposal=1、无透明、无 user-input，但原文件置有非标准的高保留位 `0xc0`。最终版明确保留这组已知源位，不将其归一化成 `0x04`；源 manifest 的 `gifControlReservedBits` 与实际解析到的 `gifControlFlagsOffset` 提供证据，安装器也检查保留位一致。相对初版候选，这两 GIF 的 GCE 控制字节补回 `0xc4`，原生文件 SHA 随之更新；全部 15 件的解码像素不变。
