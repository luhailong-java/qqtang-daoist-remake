# UI源库存：目录证据，不是页面完成数

2026-10-28只读固定社区ZIP中央目录与现有物品JSON，见`resource-inventory.json`；本轮没有重复哈希整包、解码全部资源、导入PYC或运行客户端。来源版本和腾讯原版认证继续未确认。

`res/uiRes/`有3435文件：3205在icon、173在face、19在selRoom、8在gameChat、7在selSect、4在number、3在game、1在shop，其余为头像GIF和Python字节码。`ui/`的14文件实际是pawnshop广告1与selSect广告／登录底图13，**并非14份UI页面定义**。每文件尺寸、ZIP CRC、准确路径已记录；不能以3435或14作为完整自有界面的已完成数量。

物品源2945项的类别＋installed_files完整路径集合也有2945个不同组合；本轮没有发现可按完全相同路径集合合并的条目。相似名、近邻编号或同类别不是美术复用证据；若后续证明完整资源字节相同，需单独记录哈希、帧大小、偏移及状态才能建立别名。

新UI继续以本项目`docs/UI_SPEC.md`、最新需求锁定、`docs/ART_COMPLETION_CHECKLIST.md`及实际新画资源为准。全部页面与交互状态仍需浏览器验收；目录计数不会把待验状态改成通过。
