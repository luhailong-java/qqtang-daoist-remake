# 1246 三叶清风世界表示

源item1246/thadorn/迷你电扇，真正world为参考ZIP中`QQTang-Local/runtime/client-patched/object/thadorn/thadorn43_stand.img`和`thadorn43_walk.img`，各49960bytes、SHA256 `69899c76fe11c204b0d1e914f164a5b3308e471436f41f50e465a4e40d679fed`。metadata_only禁用RGBA守卫先解析24帧头/EOF；4声明方向、65536、头canvas100×100、未知24/28均0。结构通过并非完整像素/运行通过，strictCompleteContainerAccepted=false/runtimeUsable=false保留。

6 encoded raster/6含offset组：`[0,3] [1,4] [2,5] [6,9,12,15,18,21] [7,10,13,16,19,22] [8,11,14,17,20,23]`，仅解0/1/2/6/7/8六代表。全24位置各自原frame记录和sourcePhaseIndex，不抹掉别名位置；cardinal/方向分块/时长/loop未知。全帧36×19、rawOffset[32,18]，导出144×76；算术包络[32,18,68,37]，声明100×100不替代真实单帧尺寸。

真实源是横向旋转三叶扇，没有台扇支柱。源轻青椭圆是实际半透明旋转盘：frame0外角(0,0)alpha0，盘上(18,1)/(1,9)/(18,18)alpha80，hub alpha255，非不透明灰色地板。采用原有同item三片暖金云纹叶、玉接头、象牙白低椭圆hub身份；A/B/C每次实际附真实相位、两主风格和自有高分辨裁图，B/C还实际附A作编辑目标并留editOf。

A母图1536×1024；B实际1881×836、C实际1874×839，未把提示1536×1024当实际返回，也未改母图比例。三母图及generation.json均在world/，配置目标Sunburst/max，实际型号质量未知null。导出只等比裁切缩放，非新模型生成。

初A的0/1/8包络偏高14.50%/15.02%/12.23%；B0/1改善2.58%/0.61%，B8仍11.24%。A6/7跨512切到邻图盘沿，实际窄带alpha证据523—540为安全间隙，改530只重裁，白色邻条消失；干净A7真实比例差11.97%才被揭示，不能保留被污染时较好数字。C实际编辑A7/8后改善7.28%/7.50%。当前0/1选B，2/6选A，7/8选C，六份PNG按实际144×76灰底复核，bbox都不碰裁边。

当前比例仍约0.61%—7.50%，源80alpha盘的完整转译/全边缘透明/相位连续性、native头挂点原点/符号、时序和实机尚待，未放宽通过。全部geometryAccepted/visualAccepted/accepted/runtimeAdopted=false。详见world-art.json、exports/1246-a-cut-band-observations.json和1246-a-export-observations.json。
