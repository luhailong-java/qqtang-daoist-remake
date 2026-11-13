# 五阶短披风候选

源 ID148–152 的完整小族：60 个世界独立 raster、5 个归一库存图、5 个原库存画幅 density4 变体。未接入运行，全部 pending。源只用于姿态/尺寸参考，不作为运行时像素。

当前选择只看 `art.json`、`world-art.json` 和 `selected-index.json`。目录保留失败母图和已被替换的历史导出，不能把所有 PNG 直接 glob 成当前素材。`selected-index.json` 给出每 PNG、母图/实际原生 extent、精确切口、源记录、generation/SHA、实际 submission/SHA 与预览的完整映射。

## 查看与验证

- `previews/inventory-five-light.png` / `inventory-five-dark.png`：5 件库存候选。
- `previews/{148..152}-source-vs-candidate-{light,dark}.png`：每件 12 位置的源/候选对照；源 nearest4，候选实际 density4，无穿戴/挂点推断。
- `validation/final-source-chain-audit.json`：冻结时的 235 个文件 SHA / 实际 prompt / refs / 源画幅与 rawOffset 核对报告，errors=[]。
- `validation/take-decisions.json`：历次比例观察；它不替代当前选用索引，也不代表用户视觉接受。

默认只读复核：

```powershell
python assets/items/back-adornments/honor-capes/audit_family.py
```

期望 exit0、5 库存、60 世界位置、errors=[]。脚本默认只输出，不覆盖冻结报告。`--write-report` 只在明确重新冻结时使用，随后必须同步 `selected-index.json` 的 audit SHA。

仅重放已选等比导出（不生新图，全部仍 pending）：

```powershell
$capeIndex = Get-Content -Raw assets/items/back-adornments/honor-capes/selected-index.json | ConvertFrom-Json
foreach ($capeTakeName in $capeIndex.replaySelectedSpecVersions) {
    python assets/items/back-adornments/honor-capes/export_take.py $capeTakeName
}
python assets/items/back-adornments/honor-capes/make_previews.py
python assets/items/back-adornments/honor-capes/audit_family.py
```

原始源输入工具仅接受这五个固定 ID，每次世界解码 1–6 个明确位置：

```powershell
python assets/items/back-adornments/honor-capes/prepare_sources.py --icons
python assets/items/back-adornments/honor-capes/prepare_sources.py --item 148 --indices 0 1 2 3 4 5
python assets/items/back-adornments/honor-capes/prepare_sources.py --item 148 --indices 6 7 8 9 10 11
```

## 导出与审核边界

世界画幅是源 nativeFrameSize×4，rawOffset 原值保留，派生像素偏移另记×4。只裁格、裁可见内容并等比 premultiplied-alpha LANCZOS 缩放到源包络；不拉伸、镜像或补绘。技术包络按 alpha≥16 测量，当前 60 相位偏差 0.046875%–9.940992%，库存物理披风偏差 0.196921%–5.082903%。

实际母图不是统一尺寸：多数1536×1024；148-1、150-3 最终单张为1254×1254；未选用的150-3-v2为1628×966。规格中的裁口按实际图像记录，不能按提示词预计尺寸裁图。

17 次真实内置调用全部保留 exact prompt、CRLF UTF-8 SHA、原始 promptFile bytes SHA、refs 顺序/角色/SHA、hostSource、返回字段、未改写母图和原生尺寸。项目目标2.6sunburst/high 只记录为目标；内置工具不暴露实际模型/quality，actual 始终 null。新增编辑参考裁格的 `.source.json` 还绑定原母图 generationRecord SHA，避免编辑链失联。

`visualAccepted/geometryAccepted/accepted/runtimeAdopted/completeAnimationAccepted` 全 false；方向 cardinal、时序、循环、原生挂点未知。源 stand/walk 字节相同不能证明共享时序。技术覆盖与比例通过不等于静态画面、动作连续性、穿戴或实机通过。GUI/CUA/sky/替代 GUI 禁用；这些视觉与实速判断保留用户审核。
