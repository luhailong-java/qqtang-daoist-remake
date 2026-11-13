# 2026-11-12 对局美术实际替换

工作基线 `1accecf`。本次只改表现层：在 `src/app.js` 的既有绘制位置接入 `src/render-battle-art.js`，不修改 `game.js`、服务端、网络、移动、坐标、碰撞、掉落、伤害或计时。以下“显示候选”表示代码实际会画出对应 PNG，不代表用户视觉审核通过或整款美术完成。

## 已实际接入

| 对局表现 | 新候选与来源入口 | 采用边界 |
|---|---|---|
| 容量／威力／速度拾取物 | `assets/items/battlefield/art.json` 的 scene 1／2／3 三张不同 PNG | 按现有 `capacity`／`range`／`speed` 语义绑定。保持场景工厂 ID 与账号库存 itemId 分开；有明确 sceneId 时精确查表，冲突不猜 |
| 当前技术探险普通怪物 | `assets/maps/exploration/creatures/30000-master-v1.png`，初芽团精 | 仅用于 `draft-map`／`adventure` 中没有原生实体 ID 的 synthetic 怪物，属于原创临时外观；`sourceEntityId:null` |
| 当前技术探险 Boss | `assets/maps/exploration/creatures/boss-extension/30006-master-v1.png`，灵芝盘翁 | 同上，按现有 boss 布尔选择另一原创临时外观，不声称这一波原版 Boss 就是实体 30006 |
| 已有明确 entityId 的怪物 | `assets/maps/exploration/creatures/art.json` 精确实体 ID 索引 | 不把未知实体 ID 回退成上述临时皮肤；源图缺 ID 时不猜。没有批量预解码全部怪物 |
| 糖泡 | `assets/effects/bubbles/manifest.json` 中 bomb1 的第 0 帧 | 静态新画糖泡取代旧 atlas；现有倒计时、放置、滚动和爆开规则照旧 |
| 每个实际爆散危险格 | `assets/effects/flames/manifest.json` 中 flame10 的第 0 帧 | 透明云火作为该格静态原创表现，取代程序渐变。只遍历现有 `g.blasts`，不另算射线、不新增格子或伤害 |
| 针／护盾／包子 | `assets/runtime/battle-props-20261112/manifest.json` 的 needle／shield／bun 三张 256 RGBA | 明确登记的当前技术对局原创外观，原生 `sceneId`／`sourceEntityId` 保持 null。替换线条针、共用图标与旧包子 atlas；不是取得了原版对局原件映射 |

三个拾取物仍使用旧 54×54 显示框；糖泡仍为旧 74×74 框；怪物仍为旧 84×84 框；危险格仍为旧 84×84 框。位置与地图统一缩放由原调用者提供。两张临时怪物按登记的 alpha8 主体包围框等比裁显，不修改原 PNG；其他有明确实体 ID 的 master 保留其完整画布。相对尺度、脚底、遮挡与游戏画面都仍需用户审核。

新增针／护盾沿用当前拾取类别的 54×54 容器作为候选对齐，针的原生单图几何仍未知。包子保持 64×64 拾取、80×80 基地和 35×35 携带三种旧显示框；数量文字与携包规则没有变化。针旧线条实际所占范围不被冒称为已核原生针尺寸。

## 默认资源和读取失败路径

`src/battle-art-fallback-data.js` 是默认自有资源表，`assets/art.json` 为严格镜像，由测试逐项核对。`src/art.js` 在 JSON 缺失、读取失败或返回不匹配的过期表时仍只采用该自有表；即使慢载或失败，也不会重新请求 `qqtang-characters-v2.png`／`game-atlas.png`。旧原图和历史证据保留，没有删除。

- 四个主角的文件路径、1024 画布和原裁显 rect 全部保持不动。characters 槽 4 为自有临时普通怪物、5 为新包子，另有自有临时 Boss 槽 6。
- tiles 槽 0／1／2 显式为 null。3／4／5／6／7 分别为新画糖泡、云石方块、木箱、浅石铺地及通用增益兼容外观；未知槽返回空或 false，不借槽 0 或地面。
- 当前 draft stone／box／floor 使用 `assets/maps/desert/pieces/1004-cloud-stone-block.png`、`assets/maps/pig/pieces/9012-wooden-crate-v3.png`、`assets/maps/town/pieces/3002-pavement-light.png`。这些编号只登记原画 catalog 出处，`sourceElementMapping:null`；没有拿三个通用皮肤覆盖 source-map 的精确图元映射。显示位置和现有 70／72 像素框照旧。
- 独立 pickups 默认表按 capacity／range／speed／needle／shield／bun 分别预载对应自有图，不再用同一图冒充全部类型。明确 sceneId 冲突或未知 ID 时不借临时皮肤。effects 默认表另预载同一静态透明云火，使专用特效清单读取失败时仍可画自有候选。
- 有明确原生实体 ID 的怪物即使缺图也不会借 synthetic 普通／Boss 默认皮肤。无对应图时保留 HP／标签等状态信息，等待正确图或缺口修复。

## 来源、加载与回退

资源模块读取现有各专用清单，保留文件 SHA256、母图生成记录／派生来源和源帧元数据。既有记录中未披露的历史模型／质量不由本次配置回填。只允许项目 `assets/` 下的 PNG；解码后的尺寸必须与其清单一致。专用模块启动预解码当前三种增益、三个新道具、糖泡和云火；其他怪物按实际需要懒解码并缓存。默认表另外预载当前角色及技术稿的明确自有回退。

缺清单、未知 ID、缺图、解码失败或尺寸不符时，专用绘制函数返回 `false`，调用点仅按上述明确规则尝试已预载的自有默认图；未知槽和身份冲突保持缺失。失败图不会每帧反复发起解码。若连默认云火文件也不可解码，原渐变仍作为故障时危险格反馈保留；它不是正式特效。原资产清单中的 accepted／visualAccepted 等值没有由本次代码修改。

所有新接入均为静态候选。源播放时长仍是未知，代码不设 80／120／180ms 等原版帧速、不循环首帧、不用程序缩放形变充作动作。现有游戏状态负责出现、消失和糖泡倒计时；现技术稿的 700／850ms 危险生命周期也没有被改成所谓原版参数。

## 尚未接入或缺少证据

- 针、护盾、包子已使用新自有静态外观；三件的原版单图尺寸、真实 scene/entity ID、方向／动作和挂点仍未确认，不能把当前技术稿的显示框改记为原生几何证据。
- flame1–9 的原生方向／端点关联没有验证，不能仅靠编号推断。当前通用云火格没有被记成原版十字段或端点还原。
- 困泡沿用此前四位自有静态泡壳合成图；角色完整动作、怪物完整动作、营救／复活／护罩等效应及全原版版本映射没有由这批静态接入完成。
- 全主题地图、完整 UI／社交／商城、其余物品／装扮／声音仍按整款清单推进，本次没有缩小完整游戏合同。

## 本次验证范围

`tests/battle-art-runtime.test.mjs` 已通过 11 项针对性检查：命名空间与明确 ID、synthetic 临时外观的身份边界、10 张本批采用图的真实 SHA／RGBA 规格／来源链、静态绘制与等比框、游戏状态不变、缺图及错尺寸回退、只解码选中怪物、三新道具与包子多显示框、默认表同步／四主角不变／无 legacy 路径／全部默认 PNG 哈希规格，以及 JSON 离线或过期时仍预载自有图、未知槽不借图。

独立临时端口的项目 HTTP 服务实际返回新模块和 10 张本批 PNG 原字节。`src/app.js`、`src/art.js`、`src/render-battle-art.js`、`src/battle-art-fallback-data.js` 的 Node 语法检查通过。本子任务没有重复全套规则测试或为纯文档再构建，最终整合构建与全套复验由主任务在音频／地图等并行改动收齐后执行。

未使用 GUI、CUA 或浏览器自动化；画风、实速、脚底、图层及游戏效果全部待用户手动审核。技术检查不构成视觉 PASS。提交与 push 由主任务最终办理。
