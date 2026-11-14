# 原生社交、家族、资料与道侣候选图

本组仅替换原生图像：`object/ui/guideBar` 剩余 49 件 / 83 个原图位置，以及 `object/ui/marriage` 45 件 / 92 个位置，共 **94 件 / 175 位**。93 件为 QQF/DIMG，`guideBar/btn_check.img` 为 32-bit 未压缩 TGA。未改原程序、回调、文字常量、账户流程或网页内容，未启动原客户端，也未安装到用户目录。

原图来自固定 QQTang-Local v1.3.4 ZIP，SHA-256 为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。`manifest.json` 记录包、索引、每件压缩/解压来源哈希、全部静态解码帧及源绑定；`source-page-1.png` 至 `source-page-4.png` 可检查原状态。只读解析 `uiMain/uiTemplate/uiSelRoom/uiRoom/uiShop/uiFunc` 的惰性字节码数据，没有执行 PYC。

## 候选与证据

- `patch/` 是自有玉金、纸绢与道家 Q 版图形的原格式候选；`decoded/` 为其 175 位回读结果。`candidate-all-states-1.png` 至 `candidate-all-states-4.png` 是静态候选预览，仍待用户视觉确认。
- 每件原画布、原帧宽高、偏移、像素模式、空位及位置顺序均保留；导出检查将全部像素区清零后比较原容器，验证非像素字节逐字节相同。按钮原有两、三、四位置均重绘，不添加时序或猜测原运行顺序。
- 仅九项空白功能面保留原结构 Alpha：好友遮罩、家族空白菜单、资料三条进度填充与两个遮罩、道侣亲密度条和值框。准确路径见 `semantic-contract.json`。原人物、场景、字形、物品轮廓与勾选符号 Alpha 均未用作蒙版。
- `btn_check.img` 保留原 18 字节头、26 字节 TGA 尾、364 字节长度、10×8 尺寸、descriptor=8 的 bottom-left 存储方向。只替换 `[18,338)` 像素区，新勾选字形经通用 codec 方向回读验证。
- `layout-evidence.json` 记录静态图像/控件关联、原坐标、原前景色、来源指令与原型继承。无法解析的显式覆盖保持未知，不借用父类颜色。16 个路径未发现完整路径字面量，计算文件名或实际加载仍待验。
- `palette-evidence.json` 对 75 个识别出的动态文字位置采样原生回读图，在黑、白底衬下测得最小对比度 4.9335，均达到本次选定的 4.5 阈值。采样不等于运行文字、所有像素或所有页面验收。
- 原资料父控件 mask 的 `(-10,-16)` 位置已换算到背景局部坐标；家族两套页签背景依原回调关联同一窗口；道侣确认两套背景依原常量关联共享确认窗口。以上为静态证据，不声称运行分支已执行。

原 `dlg_priestChat` 的半透明底对固定蓝字在黑底衬下不足所选可读阈值，故新绘不透明纸绢气泡，保留原尺寸、偏移及原文字控件坐标。`opacity-policy.json` 明列 Alpha 重建、取样与原因。这不是原 Alpha 精确保留项。原亲密值文字矩形与礼官段落矩形延伸到位图外的情况仍保留并记录，运行裁切待验。

## 原创画稿

内置 `image_gen` 实返四张原创母图：朱绢道侣庭院、月门桃园、朱袍葫芦礼官、玉衣结缘仙翁。四张原文件保持不变，供应十个原生派生资源（两背景、两缩略图、四张大小礼官图、两张确认对话插图）。其余装饰复用仓库已有原创画稿，见模块 `PAINT_INPUTS`，不是新增生成次数。

完整请求、实返路径与原图哈希分别保存在 `generation-requests.json`、`tool-results.json`、每张 `illustrations/*.generation.json`；本地说明见 `ART_GENERATION_RECORDS.md`。仅调用宿主内置生成工具，没有付费后备路线。宿主未披露实际 model/quality，相关字段明确为 null。场景使用自有构图，原生角色站位、遮挡与镜头适配仍待运行审核。

## 重放与接入

在仓库根目录用项目 Python 与 Pillow 执行：

```powershell
python -B -X utf8 assets/native-client-ui/social-marriage-reference/decode-references.py
python -B -X utf8 assets/native-client-ui/social-marriage-reference/read-layout-evidence.py
python -B -X utf8 assets/native-client-ui/social-marriage-reference/export-socialmarriage.py
python -B -X utf8 assets/native-client-ui/social-marriage-reference/export-socialmarriage.py --check
```

独立渲染器为 `scripts/native-ui-socialmarriage-art.py`；主注册键使用 `social-marriage`，`RENDERER_PREFIX='socialmarriage-'`，`REFERENCE_MANIFEST` 显式指向本目录，`REFERENCE_INPUTS` 提供语义、颜色、布局、Alpha 例外与母图 JSON 合同。所有 `kind` 均使用 `socialmarriage-` 前缀。

独立重放通过，350 个候选引用哈希复核一致；175 位中所有新烘焙文字包围盒均在位图内。**视觉确认、原时序、原生运行、完整 UI 与整款游戏美术验收仍为 false；本组不证明手游适配完成。** 原程序动态显示的旧产品文字不随位图自动改写。

根代理补充共享格式回归，16→17 项后又加入真实源兼容与安装篡改检查，最终 **19 项通过**。本组使用最终 codec `44c2643eb25b28daaaa4c0f914072bf249b8bf22c4161a5ee4e4c1d46d138508` 刷新依赖合同并独立重放。该共享修复不改变本组候选像素或原生文件。
