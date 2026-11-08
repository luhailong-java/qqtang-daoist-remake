# 新社交与制作图标的小尺寸检查

2026-10-28。只读取6个当前256px导出图标：friends、add-friend、remove-friend、private-chat、forge、compose。`scripts/preview-selected-ui-icons.py`每次限制1–6个显式ID，逐张预乘透明等比缩至24/32/48px，在暖米白和深青背景按真实像素显示；不运行浏览器、不做全库解码或页面验收。

诊断图`qa/ui-selected-social-crafting-actual-sizes.png`已实际查看。32/48px下双人好友、单人加号、单人减号、信笺、砧台、丹炉轮廓可分。24px的加减标记较小，不能依赖其独立表达添加/删除；正式控件保留中文，涉及加减的图标建议至少32px。明暗底未见实体色块背景或被截断轮廓。

这6项仅通过本次静态辨识检查；不据此接受其全部状态、按钮点击区、灰态、焦点、对比度或实际页面布局。其余10图标及20头像的小尺寸检查仍待补齐，所有最终accepted与browserVerified保持false。派生图与源SHA在PNG旁provenance，不记为新生图。
