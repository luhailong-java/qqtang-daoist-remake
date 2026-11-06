# 道童E四整腿：一次独立新部件验证

2026-10-28 America/New_York（记录UTC已跨29日）。本批仅一次内置image_gen，原生透明母图`whole-leg-v1.png`为1536×1024；没有裁切、放大、移腿、镜像、装配或动画。当前不通过隐藏髋接头/近远侧身份合同，不接入运行。

`synthetic-structural-pose-guide.png`为本项目人工骨点意图，用Pillow绘制的**synthetic structural pose guide**，仅内部结构参考，不是游戏美术、原QQ证据或恢复的精确骨骼。2×2格序为近RIGHT前伸/近RIGHT后伸/远LEFT前伸/远LEFT后伸；guide中的toe−hipX为+158/−52/+158/−52，四只鞋头朝屏右。脚尖朝右与脚位于髋前是两个不同条件。完整源点/分段长度/共享像素比例见其`.source.json`，代码见`make-structural-guide.py`。

调用实际附该guide、自有旧`../parts-master-v1.png`作衣料材质参考，以及两张已确认主风格图。没有附旧失败整人E或静态bind；旧parts内的姿态、分段成品接口和排版不作目标。实际提示词`whole-leg-v1.prompt.txt`，逐图记录`whole-leg-v1.png.generation.json`，actualModel/actualQuality未披露均null；配置目标及官方核对由本批项目记录保留，不将提示词当作锁定了API分支。

## 当张实看结论

已实看母图及原生米白合成`whole-leg-v1-ivory.png`。四条裤腿连靴为连续一体，前伸与后伸的方向差异这次可辨；右列从髋往左下延伸，靴尖在对应髋cap左侧且鞋头仍向屏右。没有膝中间金圈，各条可见一个踝金边。米白衣料、金云、玉绿靴/米白圆鞋头和金色薄底承接自有材质。

**仍未通过：** 四个髋端都画出了带金边的成品翻片/口边，不是素白、圆润且可以埋入躯干的隐藏布cap；近RIGHT/远LEFT靴的内外侧固定身份也未充分证明。前后伸符号有改善不等于整套可绑定。未分配认可的hip/ankle/toe pivots、共同绑定比例、world root或运行时长。详见`whole-leg-v1.review.json`。

仅当张必要alpha检查：alpha0–254，alpha≥8可见269858像素，bbox[289,35,1303,976)，四个外边及中心x767/768、y511/512可见像素均0。原查看器的棕亮背景为alpha0隐藏RGB；实际米白合成无该实体光晕，不据隐藏RGB报坏图。中心线空不授权切片，本批未切。

此分支到本次记录停止；没有追加生图、修口、裁坏帧或运行。当前母图是协调者审查本次实验的唯一在制稿，保留至具体决策。`inspect-one-whole-leg.py`只处理该张；`register-review.mjs`只写本目录记录，不改正式manifest、src、其他源PNG或Git。
