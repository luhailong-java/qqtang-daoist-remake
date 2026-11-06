# 箱庭地图原创美术候选

2026-10-28：66/66 源元素定义已有真实 PNG 候选，仍全部 accepted:false。37 件根据源参考 PNG 的 SHA256 与原帧尺寸完全一致，显式复用其他地图族已画的同源图片；29 件为本族新画，A–G 共7张内置生成母图含3件返修。未把复制或缩放算作新生图。

先读本项目 README、docs/UI_SPEC.md、docs/USER_REQUIREMENTS_LOCK_20261026.md；源结构与属性来自 assets/maps/production-index.json。每次调用前实际重读 image/AGENTS.md、统一配置和执行策略，实际附源结构图、邮件／组队两张主风格，必要时附自身前批母图。14107 的五个乘客采用自身四名原创角色与新原创老道长。

原图模型/质量为宿主管理且未披露，逐图 actualModel/actualQuality 为 null。原帧尺寸 ×4 是裁切等比导出，不是原生 4 倍模型细节。源占地、GridAttr、MapElemOffset 和 FrameOffset 逐件保留；不因新画轮廓改变地图尺寸。

## 记录与入口

- art.json：当前全部候选与各自源属性、裁切和处理记录。
- props-*.png.generation.json、batch-*.prompt.txt：7 张逐图配置目标、实际参数、时间、引用哈希与未确认字段。
- pieces/*.provenance.json：生成源、透明处理、裁切、等比缩放或明确复用记录。
- reuse_existing.py：仅对源 SHA256 和原帧尺寸完全一致的跨族同图显式复用。
- production_tools.py：单批来源补充及待恢复的全族审查工具。

## 已发现与尚未通过

14121 与 14124 首次名义网格裁切发现串入邻格星顶，已用批次 D 原母图重新裁切，当前引用 v2；旧切片保留至主协调者核实无引用后清理。地面 14001、14101、14102、14127 使用实心方形纹理模式，记录原 alpha=255 后保持全幅，不把建筑/岸线套用该处理。

G批已修14106房屋、14123鹿头、14125雪人，可见粗比例偏差分别降至1.3%、2.8%、6.4%；实际对象越过名义行界线，按y0–700完整隔离裁区导出，没有切去物件下半部。源内部结构、轮廓、五舱位置、纹样数量、地面重复接缝与运行尺度均未验收。源 ID 查找和原客户端锚点尚无认证证据。全族解码/接触表与全量 QA 遵照当前本机重型作业时段安排暂缓，不能据数量覆盖宣称整族通过。

## 项目关联

项目：QQ堂道家 Q 版重制。项目 GitHub：https://github.com/luhailong-java/qqtang-daoist-remake 。本族实际使用位置：assets/maps/box/，运行接入由主协调者维护。风格参考为 image 仓库 designs/mail-ui-v1/01-mail-event.png、designs/team-ui-v2/team-ui-v2.png；本族 PNG 为新画或明确同源画作复用，原游戏解码图仅作为结构参考。核实日期：2026-10-28。image 仓库自身远端与本项目 GitHub 分别由主关联记录标明，不推测二者为同一仓库。
