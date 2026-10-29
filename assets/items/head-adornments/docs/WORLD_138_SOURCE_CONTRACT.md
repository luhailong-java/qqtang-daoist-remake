# 138 天使环世界表示合同与当前选择

真正源是`object/thadorn/thadorn36_stand.img`及`thadorn36_walk.img`，来自本项目已固定参考ZIP的两个明确成员。两者87256bytes、SHA256均`14b9e22c087a32011e845b0c85c3f540566e4a1aa0f1b32ed351b6823a8d46d3`。背包`res/uiRes/icon/thadorn/thadorn36.img`不作为world几何来源。object.pkg的CLI索引不含这两个loose路径，因此调用同一解析器metadata_only API，禁用decode_frame_pixels作守卫，不猜其他路径。

`references/world/138/metadata/metadata-inspection.json`保存全部24帧头、宽高、rawOffset、pixelMode、encodedPixelSha256和EOF结构。4方向、版本65536、声明canvas52×29、unknownHeader24/28为24/9。metadata-only严格结构通过不等于完整像素通过，strictCompleteContainerAccepted仍false，pixel/alpha未知，runtimeUsable=false。仅0/1/2/6/7/8和12/13/14两批代表相位实际解码，单批最多6；其余依据同encoded SHA+宽高+模式的严格别名，没有另解RGBA。

编码raster组共9：`[0,3] [1,4] [2,5] [6,9] [7,10] [8,11] [12,15,18,21] [13,16,19,22] [14,17,20,23]`，若计rawOffset则18组。原24个线性位置各保留自己的sourcePhaseIndex、rawOffset、native尺寸和源头；不能把9份图片称为9帧原始动作。方向cardinal、方向分块语义、时长、loop与播放状态时序仍null。

自有身份参考为`icons/138-jade-gold-angel-halo.png`及`head-adornments-a-v1.png`的[1050,581,1536,900]486×319裁图，原比例裁切，不是新生成/放大或world画布。两主风格原图实际附入每次内置image_gen。world母图和独立记录为`world/world-138-a-v1.png(.generation.json)`、`world-138-b-v1.png(.generation.json)`、`world-138-c-v1.png(.generation.json)`；C是明确编辑B并保留editOf，A/B为新相位生成。配置目标Sunburst/max，实际型号质量均未披露/null。

当前选A的0/1/2/6/7/8、C的12/13、B的14。C的14新增错误大右侧星，未采用。B12/13可见包络比例偏差18.67%/18.92%，C改善到6.07%/13.63%；A2仍10.65%，其余A约4.81%—7.80%，B14为9.42%。始终等比缩放，未挤压补齐。9份PNG按各自原world尺寸×4导出：49×24→196×96、51×26→204×104、48×23→192×92。

`world-art.json`保留24位置、9份PNG、18源raster+offset组；共享图片额外位置有独立`world/138/position-NNN.alias.json`，不覆盖代表PNG的provenance。rawOffset全部保留。挂点沿HEAD_ATTACHMENT_CONTRACT.md；native原点/符号与当前角色头节点未知，不接运行。

9份当前PNG按6+3小批实际查看并按×4尺寸灰底合成检查，没有全族QA/构建/浏览器。中央alpha采样0或1，未泛称全孔0。低alpha残留、边缘闪光、相位几何一致性、挂点及实机仍待；geometryAccepted/visualAccepted/accepted/runtimeAdopted全部false，完整动画未验收。当前选择及未通过项见`exports/138-selection.json`。
