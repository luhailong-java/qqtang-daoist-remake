# 47件松散原生控件候选

本批严格覆盖全量census中 storage=loose、路径以 `res/uiRes/` 开头、排除 `icon/` 和 `face/faces/`、format=QQF/DIMG的 **47个控件资源**。原容器共 **132个声明位置，131个非空位置及1个结构空位**。范围包括表情菜单控件5件、提示泡3件、gameChat8件、数字、房间/录制/网络与沙漏等控件；不包含168个表情实体、GIF/广告资源或库存icon，不能据此宣称所有松散UI或整款美术完成。

绘制器为 `scripts/native-ui-loose-controls-art.py`，沿用现有自有深玉、米金纹理和播放图标，kind统一为 `loosecontrols-`。`manifest.json` 保存固定源档案、逐资源原生容器元数据与源帧；`candidate-manifest.json` 保存47个原生patch、131个非空解码PNG、逐帧Alpha政策、来源/字体哈希和离线诊断图。原声明画布、实际裁片尺寸、偏移、像素模式、帧顺序、头部及全部非像素字节保持源值。

Alpha分为 **31个结构平面精确保留源值** 与 **100个装饰/字形平面在各自完整原帧ROI内重绘**。后者移除旧数字字体、图标和装饰轮廓，不将原字形Alpha冒充功能遮罩。逐帧记录原/新Alpha哈希、差异包络、数量和重绘理由；重绘结果偶然与源Alpha同值不改变其政策分类，因此不能将整批标成 `allSourceAlphaUnchanged=true`。所有新像素仍受原像素平面范围约束，不修改原生布局、回调或数据。

唯一空位是 `selRoom/mapFilter/mapfilter_selected_dashl.img` 的index1，原宽高0、pixelMode0，原样保留，不补造占位像素。`gameChat/duihuakuang.img` 的raw0/1/2是 **top/body/tail三个拼接裁片**，不是普通/悬停/按下按钮态。其他多帧控件分别依据实际源图处理，不套统一下标意义。

四件 `number` 资源与房间人数图的全部原始字形已单独确认：

| 资源 | 保留的原始索引/特殊符号 |
|---|---|
| number/fenye.img | f0斜杠 `/` |
| number/itemNum.img | f0–9数字0–9 |
| number/num.img | f0–9数字0–9，f10冒号 `:` |
| number/youxibi_shuzi.img | f0–9数字0–9；f10底边水平线7×1、偏移(1,12)；f11小数点2×2、偏移(2,10) |
| selRoom/room/num_player.img | f0–9数字0–9，f10斜杠 `/` |

细窄“1”和冒号采用独立原生小框的自有码笔绘制，避免大字号缩放后缺笔或空白。`youxibi_shuzi` 的7×1底线不能画成中置减号，2×2点也不扩展到别的位置。itemNum与num_player的控件基类明确为 `TPicLabel + Static`；观察到的索引字形与未执行的引擎字符选择约定分别记录。

[静态证据](dynamic-layout-evidence.json) 完整惰性解析13个顶层UI PYC、3,213个代码scope，保留162个相关scope和全部34个uiTemplate scope。**22件有精确PYC路径，另25件没有精确路径证明**；正/反斜杠与大小写规范化后，没有发现 `number/num.img` 等本批相对前缀路径命中，不能凭同名文件猜加载根。

7件有整原始DIMG字节相同的packed副本：loose chatpopo2/3与 `object/ui/game` 对应文件，及5件loose netspeed与 `object/ui/selSect` 对应文件。这个SHA等价只证明内容可以对照，**不是loader alias证明**，每个松散目的路径仍独立导出。尤其 `NotifyAddHint` 的实际模板是 `object/ui/game/chatpopo%d.img`，不能直接当作loose三个提示泡的活动绑定。

动态文字按实际字色留底：`uiGame.chat.edit` 的(12,4,244,12)区域明确蓝色(51,113,149,255)，采用浅纸底；`hint.words` 的(55,20,180,140)同色，同样使用浅底。不能套用此前房间聊天白字的深底规则。TLabel/TEdit默认黑、TEditID/TEditPassword明确白色与各控件覆盖分别保留；未声明的TButton/TEXTLIST字色继续unknown，不烘焙另一套文字遮盖运行时内容。

宝石两资源的14/15个原始位置用自有差异光泽分别绘制，保留全部位置与原裁片；原时序、状态含义和循环仍未证明。录制图标、网络/服务器标志与salou的路径、精确或未知用途分别在合同中记录，不从沙漏图形推断倒计时长，也不把录制文件名当作实际用户文件读取。

制作阶段已静态查看源与候选各6页，诊断图仅合成实际解码像素于浅/深底，不是原客户端截图或用户审核。复现及只读验证顺序为：

```powershell
python -B assets/native-client-ui/loose-controls-reference/capture-source.py --check
python -B assets/native-client-ui/loose-controls-reference/export-loose-controls.py --check
python -B assets/native-client-ui/loose-controls-reference/verify-loose-controls.py --check
```

检查应覆盖47路径、132声明位/131非空、1空位、31结构Alpha、100整帧装饰重绘、原生编码/解码回放、全部非像素字节、窄字形及来源哈希。本批未修改主构建器、bundle、实际客户端或Git，没有执行原程序或GUI。`sourceTimingVerified`、`nativeRuntimeVerified`、`visualAccepted`、`installedToClient` 与 `allLooseUiOrRuntimeTextComplete` 均为false；活动加载、动态字宽、原时长和用户最终画面仍待验证。
