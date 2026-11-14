# 47件松散原生控件静态证据

[dynamic-layout-evidence.json](dynamic-layout-evidence.json) 严格选择全量census里 storage=loose、路径以 `res/uiRes/` 开头、排除 `icon/` 和 `face/faces/`、format=QQF/DIMG的47资源。共132个声明位置，其中131非空。这里只读取固定ZIP和项目的惰性解析器，没有运行/导入原客户端或构造CodeType，没有GUI、实际用户目录、Git或新美术写入。

13个顶层UI PYC完整解析共3,213个代码scope，保留162个相关scope，包括全部34个uiTemplate scope、相关布局/字色、父BUILD_CLASS窗口与整数构造证据。22件资源有精确PYC路径。正/反斜杠及大小写均已规范化检索，没有发现本批相对前缀路径命中；尤其没有 `number/num.img`、`number/fenye.img`、`number/youxibi_shuzi.img` 的相对或完整字面路径。这个结论仅限这13个PYC，不能冒充原生加载器已证。

不能混淆命名空间：`uiGame.NotifyAddHint` 明确选择 `object/ui/game/chatpopo%d.img`，不是 `res/uiRes/game/chatpopo*.img`；`object/ui/selRoom/num.img` 也不是 `res/uiRes/number/num.img` 的别名。例外的内容等价有直接SHA证据：loose chatpopo2/3与对应packed object/ui版本原始DIMG整字节一致，loose五件netspeed图也分别与packed object/ui/selSect同名图整字节一致。可据此复用自有绘制内容的依据，但每个原生路径仍独立，不能将内容等同当作运行路径绑定证明。

数字的全部源位置已在内存中解码，实际看过最近邻放大的深底诊断图，未由本审计写PNG。逐帧原尺寸、偏移和encoded-pixel SHA在JSON中：

| 资源 | 实际观察到的原始索引 |
|---|---|
| number/fenye.img | f0为斜杠 `/` |
| number/itemNum.img | f0–9为数字0–9 |
| number/num.img | f0–9为数字0–9，f10为冒号 `:` |
| number/youxibi_shuzi.img | f0–9为细线数字0–9；f10是底边水平线，实际7×1、偏移(1,12)；f11是2×2小数点、偏移(2,10) |
| selRoom/room/num_player.img | f0–9为数字0–9，f10为斜杠 `/` |

`youxibi_shuzi` f10不能改画成中置减号。观察到的字形与引擎实际字符索引约定分开，未执行的用途仍unknown。itemNum和num_player均直接继承 `TPicLabel + Static`，不是猜测NUM_LABEL类型；前者rect=(48,42,12,12)、初始caption="0"；后者rect由(60,70,15*4,19)构成，即(60,70,60,19)，textsize=10。数字自身的Alpha是字体画稿，不自动当作功能遮罩。

唯一empty位置是 `selRoom/mapFilter/mapfilter_selected_dashl.img` 的index1：宽高0、pixelMode0。必须保留空位，不生成占位像素或套两态按钮逻辑填满。

字色关键点：`uiGame.chat.children.edit` 明确为(51,113,149,255)，rect由(12,4,278-12-22,12)构成，即(12,4,244,12)；输入框这一区应为浅纸底。`uiGame.hint.children.words` 同色，rect=(55,20,180,140)，hint父rect334×165，提示正文也宜浅底。不能将此前房间聊天白字深底规则套在这里。chatList的TEXTLIST未声明字色，保持unknown。其他区域按JSON的直接RGBA、命名加载或有BUILD_CLASS证据的继承处理；TLabel/TEdit默认黑色与TEditID/TEditPassword明确白色分别保留，TButton未声明的引擎字色不猜测。

录制文件/文件夹/磁盘图标、网络图标、表情菜单、salou等的精确或未知引用逐件保留。`salou`在商品、交易、典当和宠物更新中有明确路径引用，但未凭文件名推断倒计时时长或账号/支付含义。原始Alpha是否夹带旧文字须由源图逐帧检查；旧字形不得直接当作功能孔洞保留。

本审计不安装资源，不证明原生交互、状态时长、相对加载根、运行分支、动态字宽或用户视觉通过。
