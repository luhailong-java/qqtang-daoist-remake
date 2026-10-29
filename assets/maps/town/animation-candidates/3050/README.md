# 3050四帧原创灯饰候选

2026-10-28。已实际查看四张源小帧及当前自有master，生成并导出**四个原始帧位0–3的原创候选**；没有覆盖town当前38件主清单，也没有接入运行或宣称完整动画验收。四帧均有尺寸/内容，非全透明未知标记；实际为同一灯饰构造的RGB/局部alpha差异。帧语义、播放时长和循环仍未证明。

源精确候选路径为`object\mapElem\town\elem50_stand.img`，原始DIMG SHA256 `b82ee0728bb2ec7d15f601b490a55989699aaa2427615d4c01e1e4822f14909a`。四帧各43×101，DIMG frameOffset均[0,0]，mapElemOffset独立为[1,60]，占地1×1、GridAttr[0]保留；**没有将两种偏移相加，组合渲染原点为null**。源查名仍为社区数据候选，腾讯原件身份未确认。

仅本资源四个源帧被解码，逐帧原始payload/解码RGBA/PNG哈希及alpha见`source-frame-provenance.json`。参考板`four-source-structure.png`是四帧最近邻4倍放大，不是新模型生成，也不是游戏美术。

每次生图/AI修图均重读image根规则、统一配置与执行策略，实际附上自有master、四源帧结构板和邮件/组队两主风格。目标Sunburst/max；内置入口实际型号/质量未披露，记录为null。三张母图记录如下：

| 原图 | 实际原生尺寸 | 操作/采用情况 | 逐图记录 |
|---|---|---|---|
| sequence-v1.png |1536×1024|首次四帧生成；偏窄/排间留白不足|sequence-v1.png.generation.json|
| sequence-v2.png |1536×1024|AI比例修正，约3.3–4.3%；行边界靠近，未选作导出|sequence-v2.png.generation.json|
| sequence-v3.png |2172×724|AI改为单行四列，选作完整独立切片候选；约7.6–8.3%比例差异仍未过|sequence-v3.png.generation.json|

当前导出为`frames-logical-x1/frame-000.png`至`003.png`（43×101）和`frames-compatible-x4/`同四帧（172×404）。这些尺寸是**派生兼容画布**，不是43×101或172×404原生生图。整幅灯饰裁切后置于统一311×665制作画布，整帧底部居中注册；所有四帧使用同一等比缩放，先RGBa预乘alpha、LANCZOS再转RGBA。没有非均匀拉伸、从旧AI图搬移部件或补造动作。

全套当前候选与逐帧操作记录见`sequence.json`和每PNG旁`.source.json`。每套四帧RGBA哈希各不相同；4倍导出均未发现alpha>8像素触边。该结果只证明本批尺寸、独立帧文件和粗切片边界，不等于源状态对应/动画美术通过。

预览`four-frame-preview.png`为浅/深中性底诊断合成，不是游戏截图，未添加臆定播放时序。正式未通过项：可见比例仍约7.6–8.3%、四幅AI重画存在小幅装饰/形状变化、源局部alpha与亮斑的对应仍需细看、原生时序/循环/渲染原点未知。`accepted`、`geometryAccepted`、`visualStateCorrespondenceAccepted`、`runtimeIntegrated`均false。

仅当前四帧的必要制作/导出检查已执行，没有全45像素扫描、测试、浏览器或Git操作。冻结的读取器/CLI/测试源码没有继续修改。
