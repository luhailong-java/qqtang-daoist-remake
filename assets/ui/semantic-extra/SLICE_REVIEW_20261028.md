# 新语义图标16片：单母图派生候选

2026-10-28。独立`manifest.json`与每张PNG旁`.provenance.json`保存源、nativeROI/所有权、SHA、统一比例/placement和检查记录。**只有一张既有内置生成母图，派生16片，切片阶段没有模型调用。** 不把裁切/缩放称为16次生成或原生256画稿。

## 实际读到的合同与源

实际读取本项目`docs/UI_SPEC.md`、`docs/UI_READABILITY_20261028.md`、母图generation记录及其真实提示词路径`docs/ui-semantic-extra-v1.prompt.txt`，查看1254方原图。源`assets/ui/qdao-ui-semantic-extra-v1.png`，SHA `994aaa7ff7442cd0950183e48aac1620a27ed1688a8854cdaa2822539e04a986`，alpha0–255、alpha≥8原四边均0。源记录的实际型号/质量未披露为null，配置目标保留原源记录，不回填其他图版本。

image指定的`qdao_ui_redesign_v5/UI_SPEC.md`当前实际路径未找到；没有从Git恢复。两主风格已实际查看，源生成记录也实际附了这两张主参考，本次只按既有母图画法、当前新项目UI合同和根给的语义顺序切片。

## 非等格所有权与闸门

不能按1254/4等格切。`source-measurement.json`测得全宽空行分别325..336、636..653；第三/第四行没有贯穿整宽空行，必须分列确定。实际第一排结束331、第二排结束645；第三排forge/compose/save-replay/cancel-replay结束940/950/930/940。各行列边界也不同，完整人工选择见`ownership.json`。

forge长锤柄/红穗越过名义x313。forge/compose共有边界沿真实空隙从(325,645)到(325,825)，再折向(350,845)下至950；forge自身到940结束。它们以两个必要多边形分配，未把越线长穗裁掉或分给合成炉。

新建专用`export-semantic-extra.py`，只处理这一明确源，不修改root的`export-painted-cutout-parts.py`。先为全部16片检查每个alpha≥8源像素唯一归属，再用3×3内缩边界检查所有切口有无实体像素；随后准备全部16张输出并检查透明外边，全部通过后才写任何候选PNG。

- 源alpha≥8可见像素：744,976。
- 未归属：0；重复归属：0；16项切边上的可见像素：全部0。
- 16项输出边界／非空检查在第一次写PNG前全部通过。
- `ownership-gate.json`保留原值；没有静默裁主体、删小组件或丢弃“碎片”来凑通过。

原图中fullscreen四角等本来不连通的部件全部保留。源阈值以下的RGB不当作实色污染；所有权之外的其他图标alpha设0，当前图标内的源alpha原样保留。

## 导出与实际查看

每项源可见轮廓外保留8个native像素作nativeROI，整块ROI在预乘alpha空间以单一精确等比仿射BICUBIC缩放；alpha≥8轮廓fit224，置于256透明画布。没有分别拉伸x/y、重画/镜像或重新排列组件。实际16张alpha≥8四边全0，可见余量至少16px；nativeROI、sourceVisibleBounds、uniformScale与浮点placement逐项记录。

已实际查看`contact-ivory.png`的4×4原256每格拼图（无格内缩放），16种语义和完整轮廓均保持；另单独实际看256的forge和compose，锤穗完整、炉腿完整，彼此没有混入邻图零件。米白预览未见明显实色彩晕；不因原透明黑底显示的隐藏彩RGB就误报坏图。

按行语义：friends/add-friend/remove-friend/private-chat；guild/task/backpack/warehouse；forge/compose/save-replay/cancel-replay；pet-card/fullscreen/mute/reconnect。逐项观察在provenance及manifest内。源图人物是无五官的通用道家小人符号，不以此替代任何自有人物身份头像。

本批只通过当前切片/局部视觉闸门，runtimeAdopted/clientApproved仍false。实际UI24–48px的语义可读性、背景对比、交互状态、CSS接入和客户端验证由根后续处理；不能用256预览替代小尺寸验收。未运行客户端、浏览器、测试、构建或全族QA；未改root的src/art/UI README/Git，机器重型时段仍未交还。
