# 魔法王国1：四个Boss原创静态主图

2026-10-28。仅本批4个明确Boss ID，四张分别独立调用内置image_gen，实际返回均为1254×1254 RGBA、Alpha极值0—255，未裁切、未缩放。全部是静态主图候选，accepted=false、runtimeIntegrated=false，动作与Boss阶段均未制作。未写上级creatures索引、src、全局manifest或Git，等待协调者串行合并本目录小JSON。

| 源实体ID | 本项目原创外观名 | 原图关联 | 生命 | 伤害 | 防御 | 速度 | 静态主图 |
|---|---|---|---:|---:|---:|---:|---|
| 30006 | 灵芝盘翁 | 1603／pve03_8.map／魔法王国1 | 15400 | 85 | 0 | 4 | [PNG](30006-master-v1.png) |
| 30009 | 玉芽藤皇 | 1604／pve04_8.map／魔法王国1 | 8100 | 120 | 0 | 3 | [PNG](30009-master-v1.png) |
| 30012 | 玉简匣君 | 1605／pve05_8.map／魔法王国1 | 14800 | 200 | 0 | 3 | [PNG](30012-master-v1.png) |
| 30014 | 云角玉犀 | 1606／pve06_8.map／魔法王国1 | 20000 | 190 | 0 | 4 | [PNG](30014-master-v1.png) |

四者源组count=1、boss_count=1、is_boss=true、drop_pool=route-1-boss。`identity-mapping.json`保存未经修改的完整npc_drop_groups，以及配置成员的SHA256和原目录名。实体命名空间是adventure-rules中的boss_id，不能与库存item_id混用。原实体中文名、原外观与原动作索引均未确认；以上名字和外观是本项目原创映射，不声称复刻腾讯原怪长相。材质/剪影分别为宽灵芝盘、叶芽层冠、横玉简匣、独角玉犀；各自持物仅作外观识别和读招线索，不新增技能、范围、数值或阶段。

每张PNG旁有独立`.generation.json`，提示词为同ID`.prompt.txt`。记录当次配置目标Sunburst/max、实际提交的参考图/透明参数、返回尺寸、时间、哈希及宿主输出路径；入口未开放型号/质量选择器，actualModel与actualQuality均为null/未确认。官方统一核对引用项目`docs/IMAGE_CONFIG_VERIFICATION_20261028.md`，没有调用付费API/CLI或改凭据。

实际读取项目README、docs/UI_SPEC.md、docs/USER_REQUIREMENTS_LOCK_20261026.md、图像统一核对、image根AGENTS/统一配置/执行策略，以及generate2dsprite、imagegen技能；实际查看并在每次调用中附上image两张邮件/组队主风格与项目自有`assets/characters/daoist-child.png`比例参考。沿用本会话已落盘`assets/maps/field/doctor.json`的内置入口能力证据，未重新执行重型扫描。

仅读取固定社区ZIP的中央目录/小JSON，没有重新哈希288MB整包，没有运行外部客户端。来源是社区修订资料，腾讯原始官方真实性仍未确认。当前只做逐张必要落盘、尺寸/Alpha读取与目视检查；全量QA、脚底锚点、目标游戏尺度、浅深背景边缘、动作和实机效果仍待检查，未按候选数量宣称整款美术完成。部分暖色/细白轮廓边缘需要后续目标尺寸复核。

## 项目关联

- 新项目：[QQ堂道家Q版重制](https://github.com/luhailong-java/qqtang-daoist-remake)，本目录为`assets/maps/exploration/creatures/boss-extension/`；本轮文件尚未提交/上传。
- image当前本机origin：[Azure Repos image](https://luyuacpp.visualstudio.com/image/_git/image)。项目README记载历史GitHub为[luhailong-cpp/image](https://github.com/luhailong-cpp/image)，本批未在线核验其同步关系。
- image参考路径：`designs/mail-ui-v1/01-mail-event.png`、`designs/team-ui-v2/team-ui-v2.png`，类型为风格参考；自身人物比例参考是本项目已有直接复用素材，非本批新生成。核实日期2026-10-28。
