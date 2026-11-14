# 原生背包与任务控件

2026-11-14（America/New_York）。本批为 object/ui/storage 的九个资源和 object/ui/task 的十三个资源，共 22 件、48 个原帧位置。原像素、原尺寸、偏移、帧数及 uiMain／uiShop／uiSelRoom 静态绑定保存在来源清单，源文件只作为数据读取。 [原状态预览](source-contact.png) · [原图与绑定合同](manifest.json)

控件复用项目已有玉绿金边按钮、纸绢窗框、人物头像及五种任务等级图。始页／末页／前后页、选中图、阴影、房间背包格及任务开始／完成按钮的 27 个功能性 Alpha 平面保留原值，编码后逐像素相同。背包四态采用原普通、灰态、高亮、按下位置。任务开始／完成按钮采用原普通、高亮、按下、灰态位置，任务入口则保留三个原位置。 [新状态预览](candidate/contact-native.png) · [候选 IMG 与检查记录](candidate-manifest.json)

任务详情原声明画布为 430×532，原像素帧为 369×497、偏移 (28,21)。渲染按原声明坐标安排标题、说明、完成条件和奖励区，再裁出原像素范围 (28,21,397,518)，客户端各子控件的矩形保持。选择页背景与两个练习按钮使用相同自有头像及原点击位置，固定欢迎文字承接《灵葫大作战》名称。五个任务等级按原索引使用自有暖金冠、银色冠、红冠、紫晶和花环，外观待人工确认。

taskName 原显式白字，taskIntroduction／taskNameBtn 原棕色字 (102,71,39,230)，deadline／progress 为不透明棕字，awardDes 为浅米色。对应区域分别采用深玉或浅纸底。九处最终原生解码像素的对比采样为 4.78–9.46，通过选定的 4.5 门槛。 [原字色及采样证据](palette-evidence.json)

原任务 NPC 图和奖励图使用独立 native 资源，具体显示取决于原运行数据。本批背景没有将这些动态图片固定成某个任务。部分翻页、任务等级及完成按钮未命中字面绑定，其原文件存在且几何已核对，实际加载分支继续待验。全部候选的图形、字库渲染、文字溢出和交互需人工审核。

接入使用 [storage-task renderer](../../../scripts/native-ui-storage-task-art.py) 的 PATHS 和标准 render 接口，全部 kind 以 storage- 开头，适配主构建器的 storage-task 模块键。主窗口统一构建和安装。

```powershell
python -B assets/native-client-ui/storage-task-reference/decode-references.py
python -B assets/native-client-ui/storage-task-reference/verify-renderer.py --check
```

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前安装与恢复范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收状态继续待完成。
