# 原生锻造控件候选

本批覆盖固定源 `object/ui/forge` 全21件、52个原始帧位。绘制器为 `scripts/native-ui-forge-controls-art.py`，使用现有自有深玉/米金UI、锻造砧与合成图标，没有新增收费生图。所有kind均为 `forge-`；`render(kind,label,index,size,paints,font_path,nine_slice,scaled)` API与已有模块相同。未修改主构建器、bundle、实际客户端或Git，未运行原程序或GUI。

`manifest.json` 保存每件原生资源的完整源元数据、每帧PNG、原包/索引哈希和精确PYC路径绑定。源全状态图三张及两张完整427×587面板已静态查看；最终候选全状态图和完整面板也已静态查看，仍不代表用户画面验收。

状态按真实源图分别记录：锻造、还原、拆分、确认、开始按钮与滚动箭头具有常态/灰禁用/高亮/按压四个原位置；`btn_item` 是130×17渐变帧与124×17、偏移(3,0)的平涂帧；`btn_type` 只有一帧。合成/锻造页签原帧高度22/24，四类部位页签19/29，按浅短/深高两位置保留，未将这些页签位置臆断为禁用/高亮。原framescheme执行和运行仍待验。

`text-color-source-evidence.json` 使用独立惰性PYC解析保存字色、符号赋值与父类构造指令窗口，没有import/exec原客户端或构造CodeType。`constantArithmeticRectStores` 只读取相邻整数字面量、加减乘和tuple/list构造作为数据，不处理变量、调用、分支或原代码执行。15个物品控件的位置及62×62输入、100×100输出、三个操作按钮位置可由此复算；原背景槽与所有实际控件坐标分别保留。

`contrast-contract.json` 记录这些布局和字色依据：

- 合成的 `curItemName`、`curItemInfo` 直接继承默认黑色TLabel，其(270,67,120,12)/(270,87,120,60)区域用浅纸底。
- `meterialInfo0` 明确白字，1/2通过父节点BUILD_CLASS继承它；材料面板局部x80文字区域保持深玉底，空槽不烘焙材料或假库存。
- 动态 `forgeText` 保留(10,10,180,28)和棕色(135,113,87,255)，内腔用浅米白底，不烘焙价格、动作或确认文案。
- 合成历史 `composeInfo` 使用 `zoneChooseColor`，uiMain明确定义为(255,250,236,255)，使用深底；锻造历史的逐消息颜色、TButton的引擎默认字色仍未知。
- `btn_type`、`btn_item` 和上下箭头还被典当界面复用，使用场景与对比度仍待原生运行确认。`btn_startForge`、`dlg_forgeMask` 没有精确静态UI路径绑定，仅导出源路径候选，不冒充用途或时序已证。

Alpha有一项明确例外。原 `dlg_forgeconfirm` 的内腔Alpha本身含旧示例确认文字、按钮矩形和关闭块，深底合成可见；直接复制会将旧字形带入自有图。[源深底诊断](source-confirm-dark-diagnostic.png) 与 [原Alpha](source-confirm-alpha-diagnostic.png) 保留证据。只将ROI **[6,5,221,107)** 内部Alpha统一为255，实际变更15,282个像素，差异包络恰为该ROI。ROI外圆角轮廓、尾角和所有Alpha逐字节保持源值；原帧尺寸、偏移、模式、容器头和全部非像素字节不变。其余 **51帧** 全Alpha逐字节保持源值，包括 `dlg_forgeMask` 的15个透明槽孔及分隔区。清单明确 `allSourceAlphaPlanesExactlyPreserved=false`，并逐帧给出差异范围、数量和原因；模块 `ALPHA_NORMALIZATIONS`/`VISUAL_MAPPING_ASSUMPTIONS` 同步记录，不能标为全部Alpha不变。

`candidate-manifest.json` 包含21个patch、52个原生解码PNG和三张浅/深底全状态诊断图；它们不是客户端截图。`visualAccepted`、`nativeRuntimeVerified`、`allForgeUiComplete` 为false，动态文本宽度、运行分支和最终画面仍待验证。

从仓库根目录只读重放：

```powershell
python -B assets/native-client-ui/forge-controls-reference/capture-source.py --check
python -B assets/native-client-ui/forge-controls-reference/export-forge-controls.py --check
```

检查包含源哈希、完整原始帧位、原生编码/解码/重编码、51帧全Alpha及确认框ROI外Alpha、元数据和全部非像素字节一致。正式接入/安装由主构建器和事务安装器另行完成。

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收继续待完成。
