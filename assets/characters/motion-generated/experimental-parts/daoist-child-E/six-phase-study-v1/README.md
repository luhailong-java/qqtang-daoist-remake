# 《灵葫大作战》道童E：六位置组合检查研究

2026-10-29。仅用于检查自有绘画的组合变化，**不是匹配native6帧、6次模型原画、完整walk或已通过loop**。新imagegen0；4个既有627RGBA和对应4个96PNG按编码原字节复用，SHA相同；只实际渲染2个新组合。未改src/正式rig/游戏，未用浏览器、测试或构建。

## 自有槽位与原来源

| 自有检查槽 | 近RIGHT | 远LEFT | 处理 |
|---|---|---|---|
| 0 | ContactA forward | ContactA backward | 原ContactA字节复用 |
| 1 | P1 planted | P1 raised | 原P1字节复用 |
| 2 | ContactB backward | P1 raised | 仅新组合，继承两原矩阵 |
| 3 | ContactB backward | ContactB forward | 原ContactB字节复用 |
| 4 | P2 raised | P2 planted | 原P2字节复用 |
| 5 | P2 raised | ContactA backward | 仅新组合，继承两原矩阵 |

这是协调者提议的自有检查顺序，槽0–5**不等于原QQ源索引0–5**。源1/2/4/5身份和第4位置接触解释仍待确认。没有通过换近远标签、镜像或每帧fit来制造交换。

头/torso/双臂和同源肩圈全固定为whole-arm-v1/bind-static-v2；新2/5仍按far臂5、far腿10、near腿20、头35、torso40、near臂70、肩圈80。oldContactB原2.4px注册、passing共同−12.84family偏移、源pivots/有效矩阵均原样保留，未另调脚根或上身。完整节点/来源proposal SHA/图SHA逐槽在`manifest.json`和每PNG旁`.source.json`。

## 产物

- `frames627/`：6个627方透明静态PNG。0/1/3/4是原字节复用，2/5是这次唯一两张确定性组合。
- `frames96/`：四个既有96字节复用；仅新2/5整627画布PMA LANCZOS等比缩96，没有按角色bbox放大。
- `six-poses-627-contact.png`：3×2原627格、每格上方32px标签，总1881×1318，已实际查看。
- `six-poses-96-contact.png`：3×2原96格、每格下方20px标签，总288×232，已实际查看。
- `six-poses-inspection-120ms.gif`：96方米白底、共享256色调色板，每格120ms；无循环扩展、单遍播放。只供检查硬切节奏，nativeTiming仍null，不据此批准loop。

所有联系表/GIF都有来源JSON，没把合成/缩放/编码说成新模型生成。GIF已导出，但本机hold未解除，没有在浏览器或客户端动态播放验收；不声称已完整看过其动画运动。

## 静态实看结论

627联系表中新2/5可读为后支撑+抬腿组合，未见新增裤腿断裂或源边截断。2有近RIGHT向后支撑和远LEFT前弯抬足；5为近RIGHT抬足、远LEFT向后支撑。5的近靴仍遮住部分远下腿/靴区域，小图踝部较挤，保留问题。

**过渡风险仍明确：** 1→2的farRaised是同一部件同一矩阵，只有near从髋下支撑切换为后伸；4→5则nearRaised保持，只有far换为后伸。头、躯干和臂全程固定，没有自然摆臂、重心或发带运动。硬切120ms可能产生停顿/跳变，这是从静态联系表和部件保持关系作出的推断，非动态实测通过。没有为此重做、补AI或多渲染。

96画布中人物实际约68px高，身份、葫芦与抬脚区别可认，但不足以认证遮挡/左右手或连续运动。固定源/共同尺度和art offsets不是原native世界根；worldRoot/nativeTiming均null。

当前`inspection_only_six_assembled_slots_not_native_six_frames`；`loop=false`、`sourceCorrespondence=false`、`runtimeAccepted=false`、`completeWalk=false`。脚本发现已有manifest或新2帧会拒绝重构；本批到检查研究停止。
