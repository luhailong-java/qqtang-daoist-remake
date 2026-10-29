# 《灵葫大作战》道童E：四条passing整腿原画候选

2026-10-29。完成前一轮源六位置/缺件文档后，协调者仅授权一次内置image_gen生成本母图。本批实际原生1536×1024，`passing-leg-v1.png`为4条独立新绘rig部件，不是整人动作表、旧图旋转/挤压、完整动画或已绑定资源。没有切片/绑定/追加返修/正式rig。

## 输入与艺术意图

生图前实际重读image真实AGENTS/config/IMAGE_MODEL_POLICY，并再次读[官方Sunburst页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)核对本批目标仍适用，详`MODEL_VERIFICATION_20261029.md`。内置入口没有model/quality/精确size选择器，实际型号/质量未披露为null，目标快照不能替代实际证据。未用API/video/付费路线。

实际附5张图：本批`synthetic-passing-guide.png`、自有whole-leg-v1母图作衣料/靴材质、真实E六位置板仅作功能参考、两张主风格图。道家自有裤靴身份保持，原QQ红发/面孔/衣服/黑鞋未采用。

Guide为Pillow人工骨点线稿，明确标synthetic art intent / not QQ bones / not game art。2×2顺序为nearRIGHT planted/raised、farLEFT planted/raised。planted H(330,86)→K(346,235)→A(338,395)→Toe(458,451)，soleY469；raised H(330,86)→K(435,193)→A(338,320)→Toe(458,376)，soleY394。两态示例上/下段长度基本相同，通过真正膝弯使足抬75源像素；不是把整腿转斜或压短。Guide与坐标均为美术意图，不是原native骨骼/时序或准确输出关节。

## 当前实看结果

已实际查看母图和原生米白合成`passing-leg-v1-ivory.png`。4条均连续裤腿连完整靴，素白闭合髋帽没有旧金色成品口，也没有膝中金圈；四鞋尖均向屏右。左列是较垂直的窄支撑形，右列有清楚前弯膝/回折胫和抬脚轮廓，区别真实，不是相同直腿改位置。玉绿/象牙白/金云材质承接自有来源。

**仍是未绑定候选：** 模型把各格髋帽移动到与guide不同的坐标；没有分配实际pivots或批准共同物理比例。名义格最低alpha像素差near/far均62px，仅是未对齐髋点前的可见边界proxy，不是sole实测；请求70–80px抬高未判通过。上外边最小22px，未达到提示词30px留边。近/远靴身份与源第4相位接触解释仍待独立验收，未把source→own身份/原时序当作已匹配。

## 当张必要alpha检查

实际1536×1024，alpha0–254，alpha≥8总237849像素，bbox[358,22,1276,983)，四外边及中心x767/768、y511/512均0。米白下未见实体棕光晕，原查看器背景棕色是隐藏RGB，不据alpha0颜色报坏。按名义格观察bbox仅为本张检查，不输出4张裁片、不批准等格切片或固定根。

`passing-leg-v1.alpha-review.json`保留原始数值，`passing-leg-v1.review.json`区分结构改善和未通过项。米白是原生整画布alpha合成，没有缩放、修图或新模型调用。

## 既有player9.ini文本时序

本轮仅读`native-walk-headers.json`中既存`playerIni.text`原285B取证文本和原SHA，未从ZIP重新解包/运行客户端。它只有walk/stand/trigger/die/win/cry/lose/wait下各层资源ID，没有明确time/duration/fps/delay/interval/tick字段；不能把资源编号当时间。`player9-existing-text-timing-check.json`保留读到的完整文本与来源，nativeTiming仍null。

## 文件索引与停止点

- 原画`passing-leg-v1.png` → `.png.generation.json`、实际`passing-leg-v1.prompt.txt`、tool-result。
- Guide及其`.source.json`，记录合成线稿方式、骨点/比例意图与抬脚数学；不是新正式游戏图。
- 原生米白合成及`.source.json`、alpha-review、review、官方核对和INI文本核查。

所有actualModel/actualQuality未披露均null，worldRoot/nativeTiming/localPivots/bindScale均未确认；runtimeEnabled/runtimeAdopted/fullAnimationAccepted均false。本批只有1次imagegen，0裁片/装配/动画/返修，没有测试、构建、浏览器、src/Git或主游戏接入。保留这一张候选给协调者决定下一步。
