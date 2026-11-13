# 童趣背包库存候选

题名主题规则：源目录category=npack且name字面包含“背包”的全部6项：1169/1329/1330/1331/1553/3027。它不是同一发行套装，也不包含所有包袋类物品。最终选择见 `art.json` 和 `selected-index.json`；历史母图/未选出图不能直接glob成当前素材。

只补库存：256 RGBA与64/96实际移动端变体。世界只保留每件源位置0静态参考及24位置的原始metadata，没有生成任何世界候选，不能说全相位/时序/挂点完成。

源输入在 `references/{ID}/`：完整原库存PNG、原始frame/rawOffset、精确ZIP member/IMG/像素/PNG SHA、物理包络reference裁口、world静态图及合同。前五件源UI是不透明蓝框，源native alpha并非物理物件alpha；3027带非物理落地阴影。物理边界的实测整数裁口有明确notNativeAlphaBBox标志，不伪装成源原生透明包络；新图用AI直接去UI，不用源像素作运行时。

`mothers/*.generation.json` 与 `submissions/*.json` 保留实际内置调用原字符串（CRLF不归一）、原始prompt文件bytes SHA、refs顺序/角色/SHA、hostSource/返回字段、实际原生extent与PNG SHA。工具未暴露实际模型/quality，actual始终null；项目2.6sunburst/high仅为目标。编辑裁格 `.source.json` 绑定前母图和generation SHA。

每母图按实际extent/安全裁口导出，alpha≥16物理包络相对源物理物件偏差≤10%，并复测256/64/96三个实际导出。只crop+等比premultiplied-alpha LANCZOS；不代码绘图、拉伸、镜像。原源画幅/rawOffset记录不变，归一图是库存UI表示，不是世界挂点注册。

查看：`previews/inventory-six-{light,dark}.png`、`mobile-six-{light,dark}.png`（实际64/96像素）及`source-vs-candidate-{light,dark}.png`。这些都是已存在图像的拼版，无新增绘制物件。浅深底也不等于用户已批准。

只读完整性检查：

```powershell
python -B assets/items/back-adornments/travel-backpacks/audit_inventory.py
```

期望6项、18张256/64/96 PNG、worldCandidatePositions=0、errors=[]、exit0。完整JSON输出可重定向本族validation目录；无时间戳，冻结后相同输入会得到相同审计bytes。

按当前选择重放导出（不生新图）：

```powershell
$backpackIndex = Get-Content -Raw assets/items/back-adornments/travel-backpacks/selected-index.json | ConvertFrom-Json
foreach ($backpackTakeName in $backpackIndex.replaySelectedSpecVersions) {
    python -B assets/items/back-adornments/travel-backpacks/export_inventory.py $backpackTakeName
}
python -B assets/items/back-adornments/travel-backpacks/make_previews.py
python -B assets/items/back-adornments/travel-backpacks/audit_inventory.py
```

源恢复必须显式限6个已知ID：

```powershell
python -B assets/items/back-adornments/travel-backpacks/prepare_sources.py --kind inventory --ids 1169 1329 1330 1331 1553 3027
python -B assets/items/back-adornments/travel-backpacks/prepare_sources.py --kind world-static --ids 1169 1329 1330 1331 1553 3027
```

全部新候选visualAccepted/geometryAccepted/accepted/runtimeAdopted/completeAnimationAccepted=false，userReviewStatus=pending；directionSemantic/frameDuration/loop/nativeAttachment未知均null。禁GUI/CUA/sky/替代GUI，视觉与实速由用户审核。不修改冻结honor-capes、full清单、其他agent文件或Git。
