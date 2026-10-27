# QQ堂地图数据参考

这是一份**社区 v1.3.4 修改后客户端的数据导出**，用于建立可追踪的几何参考。不是腾讯公开源码，不是经过腾讯签名核验的原始安装包，不是已完成的道家 Q 版地图。没有把腾讯地图贴图放入游戏运行资源，也没有执行被检查的 Python、EXE 或 DLL。

## 来源

- 发行 ZIP：<https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip>
- ZIP SHA-256：`fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`；下载后由本任务重新计算核对。
- 包内数据：`QQTang-Local/runtime/client-patched/map/*.map`、`map/mapDesc.py`、`object/mapElem/mapElem.py`。
- 格式研究基线：社区提交 `4b3a245fd985cabd4abd68ade6c282cc163d9edb`，逐项依据见 `../../docs/QQTANG_MAP_DIMENSION_EVIDENCE.md`。
- 每份 JSON 保留来源类别 `community-patched-client-data`、原始文件 SHA-256、包内路径及 `officialOriginalAuthenticity: unverified`。文件可成功解析不等于官方原始身份已确认。

## 文件与核验结果

| 文件 | 用途 |
|---|---|
| `catalog.json` | GB18030 严格解码后，使用 AST 和 `literal_eval` 静态读取的 381 条地图目录；保留原 13 字段和未确认字段。 |
| `elements.json` | UTF-8 严格解码后静态读取的 722 个类、721 条元素；只解析字面量赋值、单继承和类名字典映射，不导入或实例化被检查文件。保留 `size`、`offset`、`GridAttr`、`LifeTime` 等原值。 |
| `maps/*.json` | 377 张 `.map` 的全部三层有符号格值、墙内物品记录、隐藏物品、出生组 A/B、目标格及分段偏移。文件名对应原 `.map` 文件名。 |
| `index.json` | 每张源文件和导出 JSON 的哈希、版本、实际宽高、目录关联、缺项和差异清单。 |

377 张全部解析到文件结尾，无拒绝、无被忽略尾数据。188 张为 v3，189 张为 v4；327 张是 15×13，另外 50 张有 40×40、40×17、20×30 等实际宽高。`mapDesc.py` 对这 50 张仍声明 15×13，目录元数据不能覆盖 `.map` 文件头。

721 条元素的注册 ID、继承后 `size` 与 `GridAttr` 长度校验通过。22 张地图存在本次 `mapElem.py` 未定义的正元素 ID，在 `index.json` 和逐图 `validation.unknownPositiveElementIdsByLayer` 中保留；不能为它们猜碰撞或贴图。`rand.map` 目录占位没有文件；10 张文件未出现在目录中，未擅自补 ID。

地图 ID 1601 关联 `pve01_8.map`，实际头为 v4、40×17，MD5 `ad8c5668c199c5521616a7d2d1829ddc` 与固定社区运行时测试的预期一致。这是社区样本一致性线索，不是腾讯官方认证。

首张可定位的中国城01为 ID 201、`maps/town01_4.json`，v3、15×13；源文件 SHA-256 `10f84593742d90af379f9698d7e003111ea8c5b209f87ac27f3717afdcbec4ca`。此记录锁定当前社区样本的格值；逻辑像素格距、原客户端版本、建筑画法和最终运行碰撞仍需各自验证。

## 重新导出

先核实项目内忽略目录的 ZIP 与抽取清单。以下命令只运行本项目编写的解析器，不运行包内代码：

```powershell
python -B scripts/export-reference-map-data.py --client-root .artifacts/reference-inputs/extracted/QQTang-Local/runtime/client-patched --manifest .artifacts/reference-inputs/extracted-data-manifest.json --output references/qqtang-map-data
node scripts/export-reference-maps.mjs --client-root .artifacts/reference-inputs/extracted/QQTang-Local/runtime/client-patched --manifest .artifacts/reference-inputs/extracted-data-manifest.json --output references/qqtang-map-data
```

单图检查：`node scripts/inspect-original-map.mjs <map路径> --summary`。批量检查：`node scripts/inspect-original-map.mjs --directory <map目录> --summary`；任何文件被拒绝时批量结果保留错误且退出码为 1。

自动核验包括恶意语句拒绝、继承/字面量静态读取、导出 JSON 哈希和所有 377 图按 JSON 原值重建字节后的 SHA-256/MD5 完全一致。重建只在测试内存中进行，不制作运行贴图，不证明玩法与原版完全一致。
