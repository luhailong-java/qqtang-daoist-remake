# 霞角鹿灵、五心祈愿与手游素材准备

2026-11-12。承接前两批道家Q版高清手绘风格，以用户提供的QQTang-Local静态资源核对相位结构，用本项目自有角色和玉饰身份继续绘制。参照对象与来源统一见[QQ堂参照源](QQTANG_REFERENCE_SOURCE.md)，后续手游目标已写入[需求锁定](USER_REQUIREMENTS_LOCK_20261026.md)和[手游美术方向](MOBILE_ART_DIRECTION_20261112.md)。

## 本轮画面

| 物品 | 本轮独立PNG / 原位置 | 人审板 | 手游小尺寸诊断 |
|---|---|---|---|
| 407 霞角鹿灵 | 18 / 24 | [原像素双底](art-review-20261112b/407-candidate-contact.png) | [32/48/64](art-review-20261112b/407-mobile-32-48-64.png) |
| 2000 五心祈愿 | 24 / 24 | [原像素双底](art-review-20261112b/2000-candidate-contact.png) | [32/48/64](art-review-20261112b/2000-mobile-32-48-64.png) |

407保留朝画面右、背面、朝画面左和正面四组可见视向。原创身份为可可棕斑点鹿、奶油口鼻、淡紫杏晶角和靛蓝短巾；正面包含半闭、睁眼、单眼闭与双眼闭相位。六个别名位置只复用源像素证据相同的图，各自原偏移保留。首份侧脸因轮廓偏瘦长被退稿，通过实际AI重画收短晶角、颈巾，未用拉伸修正。

2000每相位保持五颗分离粉珊瑚玉心、金云细边和中空椭圆分布，沿源相位改变位置；不增加实体环、绳或中心物。24份源图像均不同，不因肉眼近似合并。退稿和补画分别保留来源，技术不合格的相位不进入候选导出。

两张人审板在米白、深青背景按实际density4 PNG原像素展示，没有缩放或镜像。手游诊断板另按最大边32/48/64等比缩小，记录整数取整后的实际尺寸，只供小屏辨识与边缘检查；不定义最终手游格距、占地、碰撞、显示尺度或挂点。

## 文件与生成来源

完整48个源位置和42张不同导出图由[407独立清单](../assets/items/head-adornments/world-407-art.json)、[2000独立清单](../assets/items/head-adornments/world-2000-art.json)及[全族清单](../assets/items/head-adornments/world-art.json)逐位置索引。每张PNG有SHA、原生逻辑尺寸、density4尺寸、原偏移、母图和逐位置provenance。每张母图旁的`.png.generation.json`记录完整实际提示词、参考角色/哈希、实际原生尺寸、入口及退稿/编辑来源。

407提示词位于[本轮目录](art-review-20261112b/)，五次真实工具输入另存[407调用证据](art-review-20261112b/407-builtin-submissions.json)；2000逐次提示词位于[头饰提示词目录](../assets/items/head-adornments/prompts/)，十四次原调用保存在[2000调用证据](art-review-20261112b/2000-builtin-submissions.json)。实际提交文本按原字符串保留换行，与提示词文件分别记录SHA。全部使用内置image_gen。配置目标沿用当次核实设置；工具未开放model/quality选择器、结果未披露实际型号/质量，逐图实际值保留null。

源逻辑画布和rawOffset没有随美术或手游意向改变。只作alpha包络裁切、预乘alpha LANCZOS一次等比适配及居中/底部注册，不执行源客户端程序。源合同分别见[407](../assets/items/head-adornments/docs/WORLD_407_SOURCE_CONTRACT.md)、[2000](../assets/items/head-adornments/references/world/2000/source-contract.json)。

## 检查与审核范围

- 逐源位置的尺寸、顺序、偏移、源/母图/导出SHA、透明与可见像素、裁格边界、精确别名和全族/独立清单一致性检查；本批轮廓比例偏差均不超过10%。
- 技术报告：[407几何](art-review-20261112b/407-geometry-audit.json)、[2000几何](art-review-20261112b/2000-geometry-audit.json)、[本轮文件来源链](art-review-20261112b/source-chain-file-audit.json)。407另有逐像素重放与预览绑定记录，均为文件/数据检查。
- 展示覆盖与身份4项、导出清单2项、静态审核保护6项本地回归通过；两件独立规格检查、19次生成来源链与运行包构建通过。HTTP静态清单及两张代表PNG均返回200且与本地字节一致，不作为界面或游戏运行验收。
- 新候选visualAccepted、geometryAccepted、accepted、runtimeAdopted及完整动画验收均为false，时长、loop、方向语义和挂点未知；未以数值检查代替人工画面或实速审核。未使用GUI自动化。

此前第一批8张修复图仍仅保留用户明确给予的静态画面批准；本轮没有修改其像素。408批及本轮两件仍待用户审核。

整款美术尚未完成。人物连续动作、其余装扮、地图全态、怪物/特效、UI与音频继续制作，原实速与挂点仍待证据。后续手游的系统、方向、引擎和操作方案尚未指定，本轮完成的是素材增量与诊断准备。
