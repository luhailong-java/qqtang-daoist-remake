# 新增五位自有静态身份候选

2026-10-28。本目录只补固定社区配置20个具体候选逻辑槽位中、现存15个自有master之外的5个原创身份。项目：[qqtang-daoist-remake](https://github.com/luhailong-java/qqtang-daoist-remake)。这是本项目外观分配，不是腾讯旧角色身份恢复。随机ID23不新画人物，历史9条缺失图不恢复。

|当前社区候选roleID|自有展示名/目录|静态设计特征|原生尺寸|
|---|---|---|---|
|11|玄龟 / cloud-tortoise-warden|宽方圆暖棕脸、小杏眼、短黑低髻、敦实玉绿短袍；右竹拍左龟纹牌|1254×1254|
|13|松翁 / pine-cloud-elder|白眉长白须、慈祥老者窄脸、低白髻松簪；右竹杖左拂尘|1254×1254|
|14|玉匠 / jade-craft-artisan|黑齐刘海bob/短侧辫、雀斑方圆脸、工坊围裙；右玉锤左云纹玉料|1254×1254|
|15|纸鸢 / paper-kite-wanderer|宽竹笠、低双辫、青米短装；右线拐左折纸鸢，脸仍偏幼圆待阵容对照|1254×1254|
|16|赤砂 / cinnabar-seal-keeper|赤褐短卷、细长铜眼/雀斑、成年感和赤砂围腰；右方印左云印样纸|1254×1254|

每位正式候选源图为目录内`master.png`，实际提示词为`master.prompt.txt`，逐图记录`master.png.generation.json`，调用输入说明`master.register.json`。五张都由内置image_gen新生成，请求1536方图、实际均返回1254方图，保存原字节，没有放大成4096，没有切片、去边或AI后修。配置目标来自image统一设置；工具未开放model/quality参数、返回也未披露可核实值，因此实际型号/质量均为null。官方目标核对见项目docs/IMAGE_CONFIG_VERIFICATION_20261028.md。

每次生成前重读image的AGENTS.md、config/image-generation.json和docs/IMAGE_MODEL_POLICY.md；实际附上本项目保存的两主风格原图：`references/image/01-mail-event.png`、`references/image/team-ui-v2.png`。玄龟/松翁另附`assets/characters/runtime/mountain-guardian.png`，其余三位附`assets/characters/runtime/lotus-healer.png`，仅承接自有Q版比例/手绘完成度，不复制身份。逐图记录保存参考哈希及输入角色。

本批实际看过内置返回画面，五位身份/发型/法器剪影有区分；仍为`source_pending_alpha_anchor_and_runtime_review`。黑底预览可见彩色边缘，不能据隐藏RGB猜其实际不透明程度；等重型时段明确交还后检查alpha、米白/暗底、外轮廓余量（尤其赤砂顶发）、人物比例与实际场景。静态master不表示方向/连续动画、装扮挂点、客户端、房间/战斗尺度验收已经通过。

完整独立映射及来源六数值在父目录`roster-skin-mapping-20261028.json`；静态取证说明`ROSTER_STATIC_EVIDENCE_20261028.md`。六属性来自固定社区Go表，并与固定ZIP Client.exe数据20/20逐值匹配，保持来源语义边界。道具、年龄、脸型不新增技能、改速度、容量、威力、碰撞或地图尺度。没有改src、全局资源manifest或Git。

## 本轮新增四正向待机基础

根随后转交五位各一张2×2方向基础。当前8个原生结果/5当前最佳候选与实际格序见`idle-directions-candidates-20261028.manifest.json`，具体视觉/alpha/余量/缺方向说明见`IDLE_DIRECTIONS_REVIEW_20261028.md`。四位可见N/E/S/W，玉匠两次仍N/W/S/W、E缺失，未以重复W或镜像充数。全部根点/尺度合同/运行未通过；未切片/接入。每张仍有独立generation记录，实际model/quality为null。

本次对刚生成单张按根允许作必要alpha/米白查看；这不表示原master五张或历史动作全量QA已恢复。本机重型时段仍未交还。新增四向是静态方向基础候选，不是完整移动动画或五人全动作完成。
