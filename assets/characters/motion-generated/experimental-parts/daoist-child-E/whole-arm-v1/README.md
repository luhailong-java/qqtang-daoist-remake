# 《灵葫大作战》道童E：两条连续整臂实验

2026-10-28 America/New_York（UTC记录已跨29日）。仅一次内置image_gen，新画`whole-arm-v1.png`实际原生1536×1024。不是旧碎片拼臂、移手、镜像或完整人物/动画帧。未切片、绑定、追加返修或修改运行资源。

本批逐一实看现有torso和旧近远upper/forearm、空拳、持葫芦手7张自有裁片。`own-material-reference-board.png`把它们按原生1:1像素放到米白板上，仅取衣料与手/葫芦材质；来源、位置、哈希和旧生成记录均在其`.source.json`。不是新生图，不把旧分段接口当新构造。torso肩孔已有的玉绿金边归躯干所有。

`synthetic-structural-guide.png`是明确标注的项目人工骨点结构意图（Pillow线稿），不是游戏美术、QQ源姿态或恢复的精确解剖。近RIGHT空拳/远LEFT持葫芦两条臂采用相同223.22/163.48示例上/前臂长度，记录v3手工肩孔参考与未来比例意图，但新图实际pivot、共同bind scale仍null。来源点/脚本及非模型声明在其`.source.json`。调用实际附该guide、材质板和两张已确认主风格。

## 实看结果

实际看了母图与原生米白合成`whole-arm-v1-ivory.png`。可见2个主要完整部件：近右白袖到空拳一体；远左白袖到握持金色太极葫芦的手一体，葫芦顶、珠链、红穗均在同件。素白封闭圆肩cap、连续肘袖已经画出，没有肩部金色成品杯口或肘中间金圈；各腕保留一个自然金云袖边。衣料、肤色及太极葫芦大体承接现有自有身份，葫芦新增少量金云纹。

持物手按源与任务固定为LEFT/far；可见握指链与自有旧手接近，但拇指大部遮住，孤立部件还不能独立证明解剖左右手。未借此改身份或玩法。

当张alpha0–254，alpha≥8为319473像素，bbox[65,238,1526,816)，四外边0，中心x767/768均0。米白合成未见实体棕光晕，原查看器的背景彩色是alpha0隐藏RGB，未据此报坏。**右流苏只留10px透明边，未达到请求60px，但当前末梢未触边或可见截断。** 不能声称留边合同通过，亦未擅自补画或扩画。

当前`continuous_two_arm_candidates_clearance_and_bind_pending`。共同像素比例/肩cap真实埋入量、左右手与近远遮挡、完整人形静态均未绑定批准；全身动态、96px及运行未验收。中心空也不构成切片授权。本批到此停止，由协调者决定下一步。

## 来源与记录

- 模型原画：`whole-arm-v1.png` → `whole-arm-v1.png.generation.json`，实际提示词`whole-arm-v1.prompt.txt`及`whole-arm-v1.tool-result.json`。
- 实看/规格：`whole-arm-v1.review.json`、`whole-arm-v1.alpha-review.json`；米白派生图旁`.source.json`。
- `actualModel` / `actualQuality`未披露，均null。配置目标快照与项目官方批次核对分开保留，不将目标当实际锁定API参数。
- 仅必要当张alpha与米白派生，没有测试/构建/浏览器、全库解码、正式rig.json、src或Git操作。
