# 八个真实来源映射的原创临时形态静态候选

2026-10-28。独立于常规20个逻辑人物，亦独立于24–36那13个用途未核实的额外完整模型。该13项已改名additional-full-models-static-evidence.json；不能因存在完整模型就叫临时变身。

实际读取固定commit的internal/clientdata/sceneelement/catalog.go，Git blob SHA `83ef5a6fc73dfd51aa4d881b10c9a32eb4bb6db5`，链接：https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/clientdata/sceneelement/catalog.go。返回文本与来源字段见source-scene-catalog-evidence.json。8/8 scene→avatar赋值已与独立清单逐项匹配；函数语义/回调实际行为仍仅社区声明，本批没有独立核验客户端函数或运行。

## 原始映射、参数与自有身份

DurationMS原声明30000，默认CanCollectItems=true；未赋值字段保持Go零值0/false，不能把0自行解释为真实零速度/容量或猜fallback。下列别名仅来自社区注释，不作为本项目展示名。avatar43原名/物种未知，保持null，不凭目录猜。

|scene→avatar|社区注释别名|自有展示名|区别于默认的来源赋值|静态源|
|---|---|---|---|---|
|104→41|duck|青羽云鸭|TraverseStaticTerrain=true；CanCollectItems=false；RecoverOnlyOnOpenCell=true|assets/characters/motion-generated/transformations/avatar-41-qingyu-cloud-duck/master.png|
|110→42|demon|墨角灵狸|SpeedRate=8；BombCapacity=8；ReverseDirection=true|assets/characters/motion-generated/transformations/avatar-42-ink-horn-fox/master.png|
|101→43|未知/null|如意芝灵|无额外赋值|assets/characters/motion-generated/transformations/avatar-43-ruyi-lingzhi-spirit/master.png|
|109→44|panda|玉掌竹熊|CanKickBomb=true；CanPushBreakable=true|assets/characters/motion-generated/transformations/avatar-44-jade-palm-bamboo-bear/master.png|
|107→45|fast ghost|轻云灯灵|SpeedRate=8|assets/characters/motion-generated/transformations/avatar-45-cloud-lantern-spirit/master.png|
|108→46|candy king|金葫胖仙|BombCapacity=8|assets/characters/motion-generated/transformations/avatar-46-golden-gourd-sage/master.png|
|114→54|crab|碧甲灵蟹|HorizontalSpeedRate=5；VerticalSpeedRate=2|assets/characters/motion-generated/transformations/avatar-54-jade-shell-crab/master.png|
|115→55|axe gang|青岩钺童|GrantedActionID=46；GrantedActionCount=9|assets/characters/motion-generated/transformations/avatar-55-jade-stone-axe-child/master.png|

## 原画、逐图记录与单件检查

8张当前候选均由内置image_gen新画，灵蟹另外做1次AI下脸修正/整幅reframe，共9个模型结果。每次生成前实际重读image/AGENTS.md、config/image-generation.json及IMAGE_MODEL_POLICY；每次实际附邮件/组队两主风格和自有道童比例参考。灵蟹AI编辑还实际附master-v1编辑目标。实际提交model/quality均null（无选择器），返回实际型号/质量未披露为null。每张旁保存prompt/register/generation记录，失败/修正版分别对应，不倒填旧图。

本批请求1536方图、原生均返回1254方图，保存原字节；没有放大为4096、切运行帧或改源像素。qa/master-ivory.jpg只是单件米白合成并整体缩到900上限的检查图，有derivedFrom记录，不是新生成原画。只检查刚生成单件，未恢复历史全量QA/批量解码/构建测试。

|avatar|原生|真实Alpha|alpha≥8外四边(左/右/上/下)|最小余量px|检查说明|
|---|---|---|---|---|---|
|41|1254×1254|0–255|0/0/0/0|66|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|42|1254×1254|0–255|0/0/0/0|27|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|43|1254×1254|0–255|0/0/0/0|78|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|44|1254×1254|0–255|0/0/0/0|46|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|45|1254×1254|0–255|0/0/0/0|49|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|46|1254×1254|0–255|0/0/0/0|53|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|54|1254×1254|0–255|0/0/0/0|72|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|
|55|1254×1254|0–255|0/0/0/0|31|实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验|

灵蟹v1下脸两棕弧像额外闭眼，未采用；master.png为AI修正版，只保留两根眼柄上的眼睛，下脸仅嘴与腮红。修正版左右余量约72/76像素，未达到提示词100像素目标，但alpha≥8不触边；是否加共享透明边/按原版尺度导出须后续合同和客户端核验，不把请求目标当成已达。墨角灵狸/青岩钺童最小余量也较紧，仍未触边。所有形态相对体积、地面根点、方向、待机/移动/受击/困泡/离场/恢复动画和状态转换都未因静态master齐备而完成。

本批不写src、不改全局资源manifest或Git，不把绘制的器物/形状变成新规则，runtimeEnabled/clientApproved/fullAnimationComplete均false。

## 方向／动作基础的后续批次

8个真实DIMG方向/动作头已核对，54实际仅单向两帧walk，其余7位为四向。当前新增方向基础、逐图检查、55斧刃窄修与54未通过的六足反相分别见`DIRECTION_ACTION_FOUNDATIONS_REVIEW_20261028.md`和独立`direction-action-foundations-20261028.manifest.json`。本README上方的8master统计仍只表示静态身份；后续28个四向位置+2个单向关键姿态不是完整连续动画或运行批准。部分图跨格、共同根和实际比例未验，未自动接入。
