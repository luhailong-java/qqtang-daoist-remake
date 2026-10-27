# 原创人物现存动作接入记录

核实日期：2026-10-26。制作范围为现存动作核验、确定性导出和独立浏览器绘制模块；未新生图、未AI修图、未生成新姿势，未改地图、玩法、角色数值、服务器或主客户端。没有恢复已缺失文件。

## 实际来源与身份

图像来源为 `image/qdao_original_roster_v14_hd/action-remake-20261001/characters/`。对照已接入的 `assets/characters/` 四张透明原图，实际查看山岳四向跑动联系图及E/W受击帧、莲花四向跑动联系图及受击关键帧，确认发型、服装、器物和身份对应。两张首要UI参考已实际查看：`image/designs/mail-ui-v1/01-mail-event.png`、`image/designs/team-ui-v2/team-ui-v2.png`。

已读本项目最新要求锁定 `USER_REQUIREMENTS_LOCK_20261026.md`，image根规则及原人物来源记录、03的 `manifest.json` / `MERGE_HANDOFF.md`、04的 `manifest.delivery.json` / `runtime_timing.json` / `IDENTITY_NOTES.md`、00和07的实际manifest。采用 `generate2dsprite` 的现存帧来源、统一画布/根点和逐帧核验规范；`art_source=existing`，没有调用生成路线。项目根 `AGENTS.md` 和 image的 `qdao_ui_redesign_v5/UI_SPEC.md` 当前不存在，不据旧文档恢复。

| 当前身份 | 源ID | 实际现存文件 | 本项目导出 | 当前判断 |
| --- | --- | --- | --- | --- |
| 道童 | `00_reference_topright_boy` | 当前动作目录仅manifest，无PNG/alphaWebM | 0帧，静态原图回退 | 历史清单不能证明动作文件已取得；缺四向站立/跑动、受击、困泡、离场 |
| 月影 | `07_moon_shadow_assassin_girl` | 当前动作目录仅manifest，无PNG/alphaWebM | 0帧，静态原图回退 | manifest虽写过接受，当前真实文件缺失；缺项同上 |
| 山岳 | `04_mountain_guardian_boy` | `frames/`196张RGBA PNG；无WebM | 四向run各16 + E/W hit各6，共76帧 | 历史离线完成，客户端根点未标定；本次均为客户端候选，W跑动13帧触边未通过 |
| 莲花 | `03_lotus_healer_girl` | `candidate/`144张PNG；无WebM | 四向run各16 + E/W hit各6，共76帧 | 源记录本来就是未接受候选；不改记为正式接受 |

同身份在当前v14其他目录中未找到00/07动作实图。`character_move_8dir`、`qdao_original_roster_v14`、`qdao_character_diversity_v9` 当前缺失；`qdao_chibi_roster_v12`现存八人是灯穗小使等其他身份，未替用。本次不以其他人物、镜像或CSS晃动补齐动作。

03当前144张由八向run128、hit12和cast/W末4帧组成，不能沿用历史“196已导出”的字样断言当前完整。04现存attack/cast与非四向run未复制：当前玩法没有对应施法动作契约，不能为了装饰任意挂接伤害/技能。两人的独立方向站立、困泡专用动作、离场专用动作没有现存可核实序列。受击只提供E/W，不把它宣称为四向受击或困泡动画。

## 导出合同与结果

- 输出：`assets/characters/motion/{mountain-guardian,lotus-healer}/{run,hit}/{方向}/01.png` 等。
- 152张源帧均真实1024×1024 RGBA，alpha范围0–255；对应原生成记录中的图片SHA256全部吻合，04另与delivery记录及其记录SHA核对。
- 本次输出256×256 RGBA，先转预乘alpha `RGBa`，整幅LANCZOS等比缩小0.25，再转RGBA。完整画布，无裁切、无平移、无镜像、无逐帧包围盒适配、无补姿势或插值。不是256原生生成，也不是新增原生4K。
- 原1024文件仍在image源处，本项目没有复制1024图像副本。152张运行图共约12.59 MiB，全部解码约38 MiB；模块默认最多保留48张已解码帧，约12 MiB像素数据，仅延迟读取当前角色/动作/方向。
- 每张派生PNG旁的 `.source.json` 记录源/目标SHA、源生成记录哈希、确定性变换、锚点和风险；`.generation.json` 为现存源记录原样字节复制，不回写历史型号。配置目标与实际返回分开，源记录未披露的实际型号/质量仍为未确认。
- 汇总清单：`assets/characters/motion/manifest.json`；逐帧数值核验：`verification.json`；关键源manifest/计时/身份文本的原样副本及哈希：`provenance/index.json`。

## 锚点、时序与未通过项

run为16帧×60ms=960ms循环；hit为6帧×40ms=240ms单次。时序承接源离线/试用值，未声称已获得本客户端验收。hit播放后可持最后一帧，但调用方应根据真实事件结束回到站立，不能把hit无限循环当困泡。

山岳所有动作的源布局锚点为(512,928)，导出为(128,232)。源文本明确它是历史布局目标，**不是已测脚底根点，客户端标定未完成**。

莲花采用源清单固定的方向根点，乘0.25：N(128,237.6267942584)、E(163.3173843700,237.6267942584)、S(128,240.0765550239)、W(124.5295055821,240.6889952153)。受击E/W同对应run根点；源记录均为待客户端批准的候选，不能强行将每帧脚底吸到同一线。

明确未通过：`mountain-guardian/run/W/13.png` 的1024源帧右边有25个alpha>8像素接触画布边界，实际查看为法杖/流苏贴边，有裁边风险。本次原样缩小保留风险，`verification.json` 中为 `not_passed`；未补画、扩边或将缩小后的边界数值当修复。

数值核验还确认每条采用序列源图与派生图均无精确重复，PNG可解码、透明存在、尺寸统一、逐帧文件齐全。数值不等于动态美术批准；两套动作仍需在真实显示尺寸下检查循环接缝、道具手持一致性、地面滑动、跨方向尺度和受击恢复。没有宣称四人完整动作已完成。

## 提供给主客户端的接口

`src/character-motion.js` 不导入或修改引擎。旧角色ID只作兼容映射：`wukong → mountain-guardian`、`titan → lotus-healer`、`maomao → daoist-child`、`asha → moon-shadow`。

```js
import { loadCharacterMotion, drawCharacterMotion } from './character-motion.js';
await loadCharacterMotion(); // 只取JSON，不预解码全部帧

// x/y为世界根点，size为完整方形画布的显示边长。
const drawn = drawCharacterMotion(ctx, player.character, rootX, rootY, 96, {
  action: 'run', direction: player.facing, elapsedMs: visualElapsed,
  allowCandidate: true, // 当前两套都必须明确启用候选
});
if (!drawn) drawOriginalStill();
```

`direction`支持N/E/S/W、up/right/down/left或引擎`{dx,dy}`；不替换斜向，不镜像。`getCharacterMotionFrame`返回帧/锚点/风险与加载状态，缺项返回null；`preloadCharacterMotion`只加载指定clip；`characterMotionStatus`可取缺项与候选状态。解码期间绘制函数返回false，调用方保留静态原图。模块不从本地时钟推进对局、不改服务器移动，不以静态图CSS摆动伪装真实动作。

本子任务没有改 `app.js` / `art.js`。主窗口负责接入真实移动/受击事件、显示时钟、动态验收和服务器重启。
