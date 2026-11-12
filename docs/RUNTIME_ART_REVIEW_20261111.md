# 2026-11-11 当前美术接入复验

本轮检查基线为 `8cdabaf36056c8d49ee73f24c6b38be0cfd31d5d`，项目路径 `E:\work\qqtang-daoist-remake`。日期采用 America/New_York。以下仅确认实际检查过的范围，完整游戏全部美术仍未完成。

用户在本轮后续明确要求不使用 computer use，交由用户审核。收到约束时本子任务已停止 CUA；此后不再使用 CUA、sky 或其他 GUI 自动化，也不以其他工具绕过。后续只做文件、数据、HTTP 与构建检查。下述约束前的实际观察保留其历史范围；主观画风、动作实速、界面和游戏效果均保持待用户审核，不据此标最终 PASS。

2026-11-12 的 408 新候选另有 [独立技术复验记录](RUNTIME_ART_REVIEW_20261112.md)。本文及其回执保持 2026-11-11 固定范围，文中 408 当时仅有参考输入的说明不覆盖后续新制作。

## 已采用范围与技术检查

- `src/character-motion.js` 从 `assets/characters/idle/v1/manifest.json` 懒载入四名首发角色各 N/E/S/W 四张静态图，共 16 张。脚底锚点均为 `[128,232]`，256×256 RGBA；对局待机及匹配跑步帧尚未解码时使用对应方向。没有把静态图计为连续动画，未作镜像替代。
- `src/trapped-art.js` 从 `assets/characters/trapped/v2/manifest.json` 载入四张人物与泡壳合成静态图。对局以 76×76 显示于现有困泡中心；未解码时保留原回退。清单 `clientApproved:false` 保持。
- 39 珍藏篮在 `art.html?kind=headWorld39` 的专用清单中为 24 源位置、20 个独立 PNG。方向语义、原版时长、循环与头挂点仍未知，状态仍为 `world-frame-candidate-not-runtime-approved`，没有实机佩戴入口。
- `node --test tests/*.test.mjs`：64/64 通过。包括本轮待机/困泡资源、源地图严格解析、联网状态、检查页覆盖与结算等断言；不证明原版版本身份、全部规则或美术终验。
- 六组 Python 检查：DIMG reference 7、metadata-only 7、旧 UI 常量 5、库存参考边界 7、世界导出闸门 4、水面地砖 1，合计 31/31 通过。
- `node scripts/build.mjs`：基线构建通过；可信参考按固定 SHA 恢复、第一审核批 8 张新 PNG 全部落盘后，最终完整构建也通过，输出为忽略目录 `dist/`。逐字节复核包内 8 张新 PNG 与 2 份变更清单，SHA256 均与源文件一致；回执见 [final-build.json](runtime-evidence-20261111/final-build.json)。
- 仅在本项目启动本地服务 `http://127.0.0.1:4387`；health 返回 `ok:true`、`authoritative:true`。对三个清单及其 40 个不同 PNG 做真实 HTTP GET，返回字节 SHA256 与本机、清单均一致。具体逐文件回执为 [assets-http.json](runtime-evidence-20261111/assets-http.json)。这是服务字节一致性，不能代替可见效果验收。

39 新修复帧落盘后，另读取更新后的清单与 12/15/19/20 四位置对应的三张新 PNG，全部 HTTP 200、`image/png` 且与本机和新清单 SHA256 一致；12/15 仍共享同一个真实文件。此增量回执为 [world-39-http.json](runtime-evidence-20261111/world-39-http.json)。前述 40 PNG 回执保留为修复前基线，不混称其校验了新字节；新增几何与静态视觉证据另由对应制作记录说明。

第一审核批最终落盘后，再对最终 `world-39-art.json`、`world-art.json` 及本次 39 的 12/13/14/15/19/20、138 的 2/13、1539 的 10 共 9 个源位置进行真实 HTTP GET。别名去重后恰为 8 个新 PNG；均返回 200、`image/png`，哈希与最终清单和本机文件一致。两个清单的最终 SHA 与逐文件回执见 [final-new-assets-http.json](runtime-evidence-20261111/final-new-assets-http.json)。旧的 39 四位置回执仅属中间检查点，以最终回执确认当前引用。408 只有参考输入准备，没有候选图，未纳入新增美术数量。

## 实际视觉观察

本轮以 CUA 原生 Chrome 在 1920×1080 窗口实际查看当前登录页：背景、字标、四位角色缩略图、昵称框与进入按钮均显示。点选月影后可见其独立高亮，进入后实际看到“本地服务已连接”的频道页、人物头像及玉绿/象牙/暖金皮肤。可见中文没有观察到截断；仅此窗口和这两页，不覆盖全部视口与长名状态。浏览器自身扩展横幅覆盖了部分顶部区域，未把它记成项目内控件。

另实际查看现有 `assets/characters/idle/v1/contact.png` 与 `assets/characters/trapped/v2/contact.png`：深浅底下四人身份、四个实际朝向和完整泡壳可辨，未见整块不透明底或画布边缘切断主体。此处为静态检查板观察，非对局脚底、叠层或动作时序通过。

## 浏览器与播放限制

当前 CUA 浏览器库存没有 DOM 浏览器，创建 iab 返回 `Browser is not available: iab`。原生 Chrome 可用，故历史“所有浏览器被 Work 设置禁用”不适用于本次登录/频道观察。

导航到本项目美术页后，原生窗口出现另一项目新开的标签页，且工具曾返回 `Computer Use helper already has an active request`。为避免共享 UI 竞争，按主任务指示停止进一步 Chrome 操作，未改设置、未关闭或操作另一项目页面。已发送 CUA completion summary。停止前创建的独立空白窗口未继续导航。

39 检查页标签标题曾载入，未取得其帧画面的实际观察或循环播放验收。人工检查页提供的 80/120/180ms 只是诊断节奏，不能被记为原版实速。当前 39 的方向、原时序、头挂点与跨帧连续性继续 pending。

## Git 与交付边界

本项目公开远端为 `luhailong-java/qqtang-daoist-remake`，正常提交与 push 已获用户授权。仅纳入本项目已核实的自有资产、来源、验收与文档；研究 ZIP/pkg、`.artifacts/`、`dist/`、凭据和缓存不上传。不 force、不 reset/clean、不改历史，提交前核对差异与目标远端，push 后确认 SHA。当前报告由子任务提供，未执行 Git 提交。
