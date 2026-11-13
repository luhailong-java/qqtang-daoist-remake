# 773定义 / 377场景地图美术覆盖接入

2026-11-12。本批基线为 `1accecfc9dc0764f1a938764084817ba330c6f90`。完成的是现存原创候选的来源核对、运行索引补齐、明确二进制定义合并与缓存元数据纠正；没有生成或修改PNG，没有宣布整图、完整动画或整款美术通过。

| 核对项 | 本批之前 | 当前 |
|---|---:|---:|
| 生产索引定义 | 721 | 773（721原导出+52明确二进制行） |
| 生产索引已登记首帧候选 | 338 | 773 |
| 运行索引实际候选ID | 398 / 12族 | 773 / 19族 |
| 377源场景中的未定义正ID | 27个，影响22目录条目 | 0 |
| 374可解析目录条目缺少首帧候选 | 部分 | 0 |
| 旧352条运行几何改变 | — | 0 |
| 源缓存字段差异 | 29处 | 已修正29处，剩0 |
| 地图美术正式accepted | 0 | 0 |

## 实际接入

`assets/maps/production-index.json`现在逐条记录773定义、19族现有原创PNG、真实SHA、原生逻辑帧、生成/派生来源及每件来源记录。旧721参考总账和原参考PNG保持原字节，作为`legacyReferenceInventory`明确引用。附加52的原始参考来自已有`binary-supplement/art-reference-index.json`；没有按物品编号猜图，也没有新增空地/普通箱替代。

`assets/maps/runtime-manifests.json`补入此前遗漏的box、common、exploration、practice、pve、tank、treasure七族。773个不同elementId均有现存RGBA PNG，PNG SHA、实际画布、原帧×导出密度、每件来源ID/SHA、原画来源文件SHA已核对。运行显示依然取源sceneObject的offset和完整占地，未改`src/map-art.js`或`src/original-maps.js`的40逻辑格距、坐标、图层排序或碰撞算法。

`assets/maps/source-elements-supplement.json`只保存52条明确附加记录。新增纯数据合并器`src/source-map-elements.js`由`server/map-catalog.mjs`调用：核对721基线SHA、源计数、重复/冲突ID、每行原始二进制几何/属性和显式ID集合。`canDoSpecial`与`canHide`未序列化，逐行保持null，拒绝把它们写为false；没有据此开启未证特殊机制。

全部377源JSON的SHA与旧地图索引一致。`assets/maps/scene-art-coverage.json`逐文件列出实际引用ID、目录关联和缺图列表；377张的缺定义/缺首帧图列表均为空。这覆盖包括10张尚无可靠目录ID的文件，不能把文件覆盖当作它们已获得玩法身份。

## 已纠正的29处缓存字段

box20件、common7件、practice2件的候选来源字段继承了同图复用donor的GridAttr或offset。29处字段分别为22个offset字段、7个GridAttr字段，字段语义明确，目标元素自己的Python与二进制值完全一致。

已实际修正三族art.json和各自的来源JSON（29件、32个metadata文件），逐件保存old→new、权威文件SHA及修正原因；仍保留donor的绘画来源。没有修改来源地图、实际碰撞值或PNG字节。完整回执：[source-metadata-corrections.json](map-art-evidence-20261112/source-metadata-corrections.json)。

## 可解析与可开局仍分开

381目录条目不变。52定义使22条此前因UNKNOWN_ELEMENT拒绝的目录项恢复源数据投影，但它们仍属于未支持规则，不自动开局。当前190条支持规则候选、184条规则未支持、5条出生数量不足、1条出生点被阻挡、1条缺rand.map；这些限制没有被放开。新旧均可解析的352条运行数据，在三层、场景实例、占地、偏移、GridAttr/碰撞、出生、目标与逻辑尺寸上逐项哈希完全相同。

[运行/几何对照回执](map-art-evidence-20261112/runtime-coverage-and-geometry.json)保留精确结果。源身份仍是用户提供目录与固定社区v1.3.4一致的数据；不是腾讯未修改原件认证。50张目录/文件头尺寸差异、未知原生挂点和历史目标版本边界继续保留。

## 后续维护与验证

```powershell
python -B scripts/refresh-map-art-coverage.py
python -B scripts/refresh-map-art-coverage.py --check
node --test tests/map-art-inventory.test.mjs tests/map-art-rendering.test.mjs tests/map-art-complete-coverage.test.mjs tests/source-maps.test.mjs
```

刷新器以固定721参考+52补充+当前19族art为输入，保留773定义；原图输入SHA不变时复用已有核验，不反复重建参考或改PNG。发生新候选/来源metadata更新时重新登记当前来源。旧`build-map-art-inventory.py`已安全转发此刷新器，不会再覆写回721。轻量`snapshot-art-production.py`改用历史721参考作基线，再加52，不会把新773当原Python分母；轻量快照仍不是视觉/运行终验。

定向回归验证：773精确ID覆盖、全部377源文件哈希、完整source->candidate关系、重复/冲突与unknown-null拒绝、352旧投影保持、22条只恢复数据不启用未知规则、重复运行新旧维护入口不退回721。未使用GUI/CUA；画风、接缝、相位、实速与手游显示效果均待用户审核。

## 实际剩余

773只是首帧映射。45个定义声明多帧资源，目前20项有序列候选、25项仍没有；原时长/loop/组合原点未确认。全图接缝、动态物件、遮挡和原版运行比较仍pending。全游戏逐类实量见[当前缺口JSON](FULL_GAME_ART_GAPS_20261112.json)：2945源物品中476个ID有至少一种候选，2469个ID尚无候选；人物、怪物、变身完整动作、其他world装扮、UI全状态与音频仍未完成。不能把本批索引齐全改记整款完成。
