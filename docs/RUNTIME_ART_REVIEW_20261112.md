# 2026-11-12 408 世界候选技术复验

408 本批 24 个源位置对应 12 张新 PNG，HTTP 与构建字节检查通过；画风、动作实速、界面和游戏效果保持待用户手动审核。没有使用 CUA、sky、浏览器自动化或其他 GUI 工具，没有将技术检查记为美术接受或运行采用。

基线提交为 `8cdabaf36056c8d49ee73f24c6b38be0cfd31d5d`，检查对象是其工作树内本批新文件；日期采用 America/New_York。清单和每个 PNG 的固定 SHA256 见下述机器回执，不把基线提交误称为已经包含这些增量。

## 本次固定范围

- 独立清单 `assets/items/head-adornments/world-408-art.json` 和全族清单 `assets/items/head-adornments/world-art.json` 中的 408 条目逐字段一致。
- 源顺序为 0–23，共 24 个位置，去重后恰为 12 个 PNG；重复位置仍共享原映射的文件，没有用重复帧虚报新画数量。
- 所有 408 帧的 `geometryAccepted`、`visualAccepted`、`runtimeAdopted`、`accepted` 均保持 `false`。源方向语义、原版时长和挂点没有被本次技术检查确认。
- 当前全族清单计数为 18 项、390 个已有候选的源位置、201 个不同候选 PNG。这只是清单计数，不是整款游戏的完成率，也不代表这 18 项已经通过用户审核。

## HTTP、检查页数据与构建

复用 `http://127.0.0.1:4387` 服务端点。两个变更清单及本批全部 12 个新 PNG 均真实 GET 返回 200；PNG 的 Content-Type 为 `image/png`，返回字节的 SHA256 与本机和清单完全一致。逐文件记录见 [world-408-http.json](runtime-evidence-20261112/world-408-http.json)。

`node --test tests/art-review-coverage.test.mjs` 的现有 4 项检查通过。其断言范围是检查页数据转换及既有 39/114 覆盖和名称边界，不是 408 的浏览器、动画或主观视觉验收。本次没有重跑此前已通过的 Node 全套 64 项。

新增资产落盘后重新运行一次 `node scripts/build.mjs`，exit code 为 0。随后对 `dist/` 内 12 张新 PNG 和 2 份变更清单共 14 个文件逐字节复核，哈希均与 HTTP 检查时固定的源快照一致。回执为 [world-408-build.json](runtime-evidence-20261112/world-408-build.json)。`dist/` 仍是忽略的构建目录，本次没有执行 Git 提交或 push。

构建完成后才写入本报告与新回执；没有为这些纯文档新增再次构建。

## 与前批回执的关系

[2026-11-11 复验记录](RUNTIME_ART_REVIEW_20261111.md)及其回执保留原来固定范围：首发待机/困泡、39/138/1539 的 8 张修复 PNG，以及当时的清单快照。该记录中“408 只有参考输入”的说明属于前批检查点，不能套用到本批新候选；本批也没有重新认证前批的所有资产。

408 的新增候选和技术通过均不改变完整游戏全部美术尚未完成的结论。用户手审通过前，不将本批改记为 accepted 或 runtime adopted。
