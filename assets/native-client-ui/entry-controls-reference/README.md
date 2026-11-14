# 登录附属窗口、网络状态与录像文件图标

2026-11-14。16 件资源、25 个原位置：登录目录剩余八件、选区状态六件、录像文件图标两件。登录页主图和字标沿用既有自有素材，此处补验证码、VNET、等待窗口、连接条及旧 `img_lago` 路径的自有字标。`img_lago` 未命中当前脚本的精确静态绑定，保留为同名原路径候选，不能据此断言实际显示。

以固定原包、索引及有界 DIMG 解码建立 [源合同](manifest.json)。uiLogin、uiSelSect、uiMain、uiTemplate 只读常量树，未执行脚本。原画布、偏移、模式、帧数、空位和所有非像素字节保留。 [原生再解码候选](candidate-all-states.png) · [导出清单](candidate-manifest.json)

按钮按各自原帧位绘制：换图按钮四态、动画和 VNET 三态；连接条保留两相位，不自定运行时长。状态条仅沿用原 Alpha 的分段轮廓，全部 RGB 已替换为米金至玉绿。五种网速仍有独立原路径及文字。录像文件／目录使用本项目原创图标，不复用原图像素。

验证码输入框保留 `(50,120,100,24)` 和原题图显示区。[静态颜色证据](input-color-evidence.json) 记录源 `verifyEdit` 在相邻指令中将 `LOAD_NAME darkColor` 赋给 `drawcolor`，所以留浅米色输入底。当前 uiMain 的 `darkColor` 是 `(102,51,0,255)`，运行命名空间的实际传递仍待确认。VNET 的动态内容保持空白可绘制区。其加载分支、实际文本、原时序及所有新视觉继续待人工验收。

素材是既有原创 UI 画稿的切片、排版和原生编码，没有新模型生图。导出重放：

```powershell
python -B assets/native-client-ui/entry-controls-reference/decode-references.py
python -B assets/native-client-ui/entry-controls-reference/export-entry.py --check
```

此目录为独立候选；实际安装范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和安装回读为准。全部 UI、整款美术和运行验收均未完成。

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前安装与恢复范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收状态继续待完成。
