# 珍藏篮39轮廓修复前核查

2026-11-11。针对当前独立清单 `assets/items/head-adornments/world-39-art.json`，实际解码源图、母图与导出PNG；已查看B/C源相位板、B/C母图及其灰底导出检查板。此记录是本轮修复前基线，不代替后续修复验收。

## 实际缺陷与修复输入

24源位置由20份不同PNG表示；15是12的精确源raster别名。其他精确别名为3→0、9→6、11→8。必须保留每个位置独立rawOffset记录，不能用去重减少位置数。

| 源位置 | 源逻辑尺寸 | rawOffset | 当前母图切口LTRB | 当前可见宽高比偏差 |
|---|---|---|---|---:|
| 12、15 | 37×31 | [31,0] | `world-39-b-v1.png` [0,512,512,1024] | 11.7320% |
| 19 | 46×34 | [25,-7] | `world-39-c-v1.png` [0,512,512,1024] | 13.7326% |
| 20 | 37×28 | [32,7] | `world-39-c-v1.png` [512,512,1024,1024] | 17.3005% |

母图均位于 `assets/items/head-adornments/world/`。源实际参考为 `assets/items/head-adornments/references/world/39/source-phases-b.png`（12在下排左）、`source-phases-c.png`（19在下排左、20在下排中）；单独源小图为同目录 `frame-012.png`、`frame-019.png`、`frame-020.png`。源像素只作姿态、构图和轮廓参考，不作为导出成品像素。

12的自有玩偶应在画面左侧，侧身/脸转向左；卷轴在前右，扇与葫芦在后右。完整可见轮廓目标比值37/31≈1.19355。现稿整体偏高。

19应为正面中心玩偶；卷轴向画面左侧大幅斜伸，篮身宽浅，葫芦在左后、扇在右后。完整可见轮廓目标46/34≈1.35294。当前卷轴过于直立、物件轮廓偏高。

20同为正面中心玩偶，玩偶低坐，卷轴在左方较竖直、扇在右后。完整可见轮廓目标37/28≈1.32143。应通过重新绘制更浅篮身及压低内容物实现，不能非等比拉伸现图。

三种姿态均保留本项目金发带原创道童玩偶、赤红卷轴、金葫芦、浅玉折扇、金色编竹篮及前面玉云饰牌。主风格图为 `references/image/01-mail-event.png` 与 `references/image/team-ui-v2.png`，真实生成时应实际附图；禁止保留源QQ企鹅的黑白身体、红围巾和喙。

## 新的独立核查工具

`python scripts/audit-head-world-geometry.py --item 39` 独立解码实际像素，核对源/目标尺寸与SHA、alpha空白、源别名、母图切口、alpha≥16包围框、记录QA数值、等比scale和X居中/Y底对齐注册。它不依赖清单里存好的偏差作为计算输入，能发现修改PNG后保留旧QA记录的情况。工具仅输出JSON，不写素材与清单。

修复前实际结果：技术errors为空，按实际像素重测的超10%位置恰为12、15、19、20；返回码2表示仍有轮廓门槛未通过。同工具复查114花环，24位置/20PNG，errors及轮廓超限位置均为空，返回码0。脚本语法检查通过。此处只确认工具实测及有限几何门槛，不是花环或篮子完整动画PASS。

原工具仍可复用：`python scripts/verify-head-world-114.py --item 39 --expected-count 24 --expected-unique 20`。

导出器 `assets/items/head-adornments/export_world_batch.py` 每批允许1至6帧，执行alpha边界闸门，然后按源alpha包络等比缩放、X居中/Y底对齐，保留原逻辑尺寸×4及rawOffset。本轮新增可选spec字段 `manifestPath`，按项目相对路径选择独立清单；省略时仍写原全族`world-art.json`。更新代表帧时，只沿已有明确 `rasterAliasOfSourceFrameIndex` 及源合同匹配关系刷新别名图像链，保留别名自己的rawOffset、sourceReference、sourceNativeFrameRecord和包络位置。不能因独立清单已修复而声称全族旧选择同步完成。

`tests/world-export-manifest.test.py` 的两项隔离测试已通过：独立清单导出不修改全族文件，代表12及别名15的新file/SHA/派生链同步，并保留特意设为不同值的15原偏移和源记录；省略`manifestPath`时仍写全族且不改独立清单。测试只在本仓库`.artifacts`临时目录运行，不改生产素材。原alpha边界闸门四项测试也通过。审计工具缺位及负index拒绝已分别实际验证；默认完整覆盖，确需局部审计时必须显式传 `--allow-partial`。

`complete_raster_aliases.py 39` 仍写全族清单，新独立导出无需再运行它。`register_world_batch.py` 仍含旧机node绝对路径，注册前须核实实际运行环境；历史配置里的目标型号不能当成本轮实际返回型号。

源头未知字段、方向分块/cardinal、帧时长/loop、原生head层原点和符号仍无可靠客户端运行证据。修正比例之后也不能推定已知原生时序或实机佩戴通过；`accepted`、`runtimeAdopted`和`completeAnimationAccepted`保持false，待完成对应验收。
