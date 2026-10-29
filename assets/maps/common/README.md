# 公共场景原创美术候选

2026-10-28：88/88 源元素定义已各有真实 PNG 候选，仍全部 accepted:false。A–Q 共17张内置生成母图，首轮覆盖78件独立新绘，其余为明确返修；4件以原参考PNG SHA256和原帧尺寸完全相同为条件跨族复用；6件为本族同源图片别名复用。没有把复制、裁切和放大计作新生图。

本项目业务/尺寸合同见 README.md、docs/UI_SPEC.md、docs/USER_REQUIREMENTS_LOCK_20261026.md。每次生成前实际重读 image/AGENTS.md、config/image-generation.json 和 docs/IMAGE_MODEL_POLICY.md；实际附本族源结构图、邮件/组队两张主风格，必要时附已画本族母图，保持道家Q版高清手绘。源解码图只参考结构，不作为运行美术。

逐图实际型号和质量宿主未披露，记录为 null；配置目标与实际提交字段分开。源占地、GridAttr、MapElemOffset、FrameOffset 全部逐件保留。导出为原帧×4、等比缩放；不把它称为原生4倍细节。

## 记录

- art.json、pieces/*.provenance.json：当前路径、哈希、源属性、生成母图、alpha、裁边与等比加工/显式复用。
- props-*.png.generation.json、batch-*.prompt.txt：逐图生成来源、实际参考哈希、时间和未确认字段。
- references/structure-*.png.source.json：原帧等比放大的结构板，非运行素材。
- QA_NOTES.md：已修复的串格裁边、真实alpha核对与具体未通过项。
- generation-attempts.json：失败调用；失败不计入成图数。
- production_tools.py、refresh_aliases.py：逐批记录、明确同源别名更新；全族audit尚未执行。

K–M 的17件方形地面分别核实原alpha(255,255)，从AI实心区域内接方形裁切，保持输出全幅alpha255。M图行界线偏移，实际裁区如实记录，部分边饰和重复接缝待修。M额外试画的17112实心转角不接入，原透明轮廓是正确属性，不进行强制实心化。

## 尚未通过

比例、内部结构、轮廓、图案/柱数、透明网孔、接缝、原客户端ID/锚点与实际运行尺度均未全验。O/P返修后书桌7.5%、树桩5.7%、栏门5.9%、横桥5.1%、灯6.7%已改善；石凳仍11.4%、细杆12.8%、头盆约13%、围栏约12.7%未过粗比例门槛。P的石凳、细杆、头盆、围栏较原最佳差而未采用；Q地面虽比M行界线略好仍不是等行，内接方形裁切与边框/接缝保持未过。不能据88项覆盖宣称公共族完成验收。全族解码/接触图/测试按当前本机重型作业时段暂缓，只继续当前1–6件必要落盘。

## 项目关联

项目QQ堂道家Q版重制，GitHub https://github.com/luhailong-java/qqtang-daoist-remake 。本族实际素材位置 assets/maps/common/，由主协调者维护运行接入。image 相对参考路径 designs/mail-ui-v1/01-mail-event.png、designs/team-ui-v2/team-ui-v2.png，关联类型为风格参考；PNG为新画或明确同源画作复用。核实日期2026-10-28。image自身远端与新项目地址分别见主关联记录，不据目录名猜测。
