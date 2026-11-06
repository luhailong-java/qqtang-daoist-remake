# 结算三态灵葫徽章

《灵葫大作战》2026-11-02。新增胜利、平局、再接再厉三态，一张内置生成母图`result-crests-v1.png`，实际原生2032×774；提示目标1536×1024，保留真实返回尺寸，没有放大成目标尺寸。逐图记录在同名`.generation.json`，实际附邮件/组队主参考及当前UI母图，实际型号/质量未披露保持null。

按透明空隙x675/1360手工分区，切边alpha≥8像素为0；三态各派生512×512，预乘alpha等比fit448，32px留白，`manifest.json`记录SHA/裁区/比例。裁切缩放不是三次新模型生成。原生暖米白合成和144/112显示尺寸联系图已实际查看，图形完整且可区分。

`src/result-art.js`根据服务端winnerTeam及本方队伍选择唯一状态，`src/app.js`显示图与实时中文，未知结果不记录为失败。只做外观接入，不改变胜负、计时、分数、地图大小/建筑占位。`src/ui-skin.css`负责144px桌面/112px窄屏及文字对比；本机浏览器入口被Work设置禁用，全视口/八人长名/键盘返回尚未实机验收，visualAccepted仍false。

检查入口`art.html?kind=resultCrests`，派生联系图`qa/result-crests-display-contact.png`。不是腾讯原版结算资产或已完成全部UI的声明。
