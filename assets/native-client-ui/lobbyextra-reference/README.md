# 大厅聊天、房间数字与指引候选

2026-11-14。补齐本轮清单中 `object/ui/selRoom` 尚未转换的十七件资源，共四十一个源位置。使用现有自有深玉／米金画板、原创冠饰与新字体栅格；没有保留原 RGB 或原数字字形。 [源图全部位置](source-all-states.png) · [候选全部位置](candidate-all-states.png) · [来源合同](manifest.json) · [候选清单](candidate-manifest.json)

| 类别 | 资源 | 源位置 |
| --- | --- | --- |
| 大厅按钮与通知 | 命令下拉、聊天展开／收起、左右翻页、信封消息，共六件 | 21 |
| 聊天面板 | 最大、最小、普通三个尺寸 | 3 |
| 房间与广播标记 | VIP、popo 底条、speaker 遮罩 | 3 |
| 房间号 | `num.img`，十个独立数字位置 | 10 |
| 指引气泡 | 三个空白指向气泡、进入商城提示 | 4 |

全部源位置的原始尺寸、偏移、模式、空位、帧顺序和非像素字节保留。三十一份非数字帧只沿用原 Alpha 作为结构遮罩，全部颜色来自自有画板与新绘制；源 RGB 不参与合成。聊天面板保留顶边轮廓和滚动沟槽，动态聊天文本不烘焙到图片。信封三位置保留 `(0,5)`、`(0,3)`、`(0,4)` 原偏移，通知时长仍待证。

数字资源有十个独立帧，原声明画布为 `11×14`，各帧使用不同裁片和偏移。[字格合同](glyph-layout.json) 保留源 0–9 顺序，并记录新字形在原裁片及声明画布中的可见范围。新字形统一使用 Microsoft YaHei 13px 与一像素描边，完整墨迹居中放入原裁片，没有逐字拉伸。六像素宽的“1”完整保留新字形；原生运行字距另待验。静态指令确认 `room1.no` 的两个基类为 `TPicLabel`、`Static`；模板 `TPicLabel.type` 为 `PICLABEL`，该子控件明确设置 `textsize=10`。 [原生声明证据](ui-evidence.json)

`uiSelRoom` 的聊天列表明确设置默认颜色 `(199,242,252,255)`，字体边缘类型为 `-1`；本批聊天底板使用深玉色。[最终原生像素样点](chat-contrast.json) 按原 Alpha 与最浅底层合成，核对这一默认青字的对比度。逐条消息颜色、链接更新、广播遮罩混合和实际交互继续待运行检查，样点不代表所有动态文本通过。

命令下拉和三个空白指引气泡，在检查的 `uiMain`、`uiTemplate`、`uiSelRoom`、`uiRoom` 中未命中精确路径绑定；四件仍是同名源路径候选。空白气泡保持浅色底及原指向轮廓，没有猜测动态文案。其余十三件有十九处静态路径绑定；源流程未执行。进入商城文字、VIP 标记和通知信封分别用新字体、项目原创冠饰和新图形绘制。

本批独立候选尚未负责安装客户端。画风、运行时序、遮罩实际作用和全部交互均未验收，也不构成整款美术完成。主构建器接入键为 `lobbyextra`，模块为 `native-ui-lobbyextra-art.py`，所有绘制种类均采用 `lobbyextra-` 前缀。

```powershell
python -B assets/native-client-ui/lobbyextra-reference/decode-references.py
python -B assets/native-client-ui/lobbyextra-reference/read-ui-evidence.py
python -B assets/native-client-ui/lobbyextra-reference/export-lobbyextra.py
python -B assets/native-client-ui/lobbyextra-reference/export-lobbyextra.py --check
```

[QQ 堂参照来源](../../../docs/QQTANG_REFERENCE_SOURCE.md) · [自有绘制器](../../../scripts/native-ui-lobbyextra-art.py)

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收继续待完成。
