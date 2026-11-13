# 五阶披风候选交付（2026-11-12）

已完成源 `npack` 五阶赛事披风完整小族148–152的内置 AI 候选：60/60 独立世界位置、5/5 归一库存图，另5张原库存画幅 density4 变体，共70张当前选用 PNG。全部待用户审核，未接运行。不把候选完成冒称全游戏完成。

| 源ID | 源名 | 本项目身份 | 世界位置 |
|---|---|---|---:|
|148|羽林披风|青岚羽林披|12/12|
|149|骁骑披风|紫雾骁风披|12/12|
|150|冥袭披风|玄霜夜行披|12/12|
|151|影羽披风|金霞影羽披|12/12|
|152|太御披风|朱金太御披|12/12|

资产唯一新增目录 `assets/items/back-adornments/honor-capes/`，独立 `art.json` 与 `world-art.json`。本轮没有改头饰全族采用清单、其他物品、运行接线或 Git。精确源身份/源 IMG/PNG 链与未知语义见 `docs/HONOR_CAPES_SOURCE_CONTRACT_20261112.md`。

最终选用索引 `assets/items/back-adornments/honor-capes/selected-index.json` SHA256 `0a2bc2a7d77c66e4085a992f879d95abcb7769d1e249c45241689bf7a8322188`。其中逐项列出70张 PNG、源合同、逻辑画幅与 rawOffset、实际母图/extent、切口、generation/实际 submission SHA、12张浅深底预览，以及精确重放规格顺序。

独立库存清单 SHA256 `0944fca4acc5877a5360710367f2685c5e7de33d2fed99da99de33ac15d3e437`；世界清单 SHA256 `4e4f5bb3c2b4f9fcf498f6a1daa6c7b72dc14076c21a853518b7e15f749ae263`。17次真实 builtin 生成/重试均保留，当前采用其中14张母图；3张未被选作最终 raster 的母图仍作为历史证据，不删除也不混入当前清单。

源每件 stand/walk 字节相同，各12个独立 raster，合计60，未按两个状态重复计120。源 declared directions=4，但 cardinal/帧时长/循环/原生挂点未证仍 null。世界导出保留源 local logical canvas×4、原 rawOffset，仅作等比 premultiplied-alpha LANCZOS 派生，不程序绘制、拉伸或镜像充相位。

真实 alpha≥16 包络比例偏差：世界0.046875%–9.940992%，库存物理披风0.196921%–5.082903%。17份母图的 PNG/原生尺寸、exact prompt与实际CRLF提交 SHA、原始prompt文件 bytes SHA、refs/SHA、actualnull、编辑裁格来源链全部核对；源 PNG、70个导出、预览输入和12个预览文件一起共235个文件SHA核对，errors=[]。`python assets/items/back-adornments/honor-capes/audit_family.py` 默认只读，exit0；不会重写已冻结审计文件使索引 SHA 失联。

静态对照预览在 `previews/`，实际查看了全部5件×12相位与库存浅深底文件。对照图只显示 native cropped raster，不推断穿戴位置；150源位置3的不明白色边绘保留在reference，自己的披风不靠新增散点凑包络。低alpha边缘与跨相位外观仍须用户视觉判断。

新候选所有 `visualAccepted`、`geometryAccepted`、`accepted`、`runtimeAdopted`、`completeAnimationAccepted` 为false，userReviewStatus=pending。没有本批用户视觉批准，时序/挂点/实机/完整游戏均未宣称通过。禁止GUI/CUA/sky/替代GUI。

全2945源ID缺口基线另见 `docs/ITEM_GAP_AUDIT_20261112.{json,md}`：476 ID有至少一种候选、2469无候选。本小族净增加5个源ID，因此只叠加本批是481/2945，npack仍有192个源ID没有本族候选；并行其他族的增量另算，不能把本批70张PNG当成70个新增源ID，也不改写基线476。
