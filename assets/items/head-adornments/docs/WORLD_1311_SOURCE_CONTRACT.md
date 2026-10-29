# 1311 神奇的树世界表示

源item1311/thadorn/神奇的树，真正world为固定参考ZIP中`QQTang-Local/runtime/client-patched/object/thadorn/thadorn46_stand.img`和`thadorn46_walk.img`。两者77140bytes、SHA256 `1aa53c1dc42d1d0b838c198bfd00b576158f08f869a346f4fe3b05fb9f8b1bcd`。metadata_only禁RGBA守卫读取24帧结构，4声明方向、65536、头canvas100×100、未知24/28为0/0；源strictCompleteContainerAccepted=false、runtimeUsable=false仍保留，EOF结构不是完整像素验收。

10 encoded raster/10含offset组：`[0,5] [1] [2] [3] [4] [6,11,12,17,18,23] [7,13,19] [8,14,20] [9,15,21] [10,16,22]`。只按6+4两批实际解0/1/2/3/4/6与7/8/9/10。源真实变化为圆树冠轻微相位、左右镜向的叶序、稀少/较多叶光出现与消退。没有用静态图标冒充24动作，也没有全24像素解码。

每原位置保留sourcePhaseIndex、native尺寸、rawOffset和源头。33×32/33×33→132×128/132×132，原offset[33或34,1或2]不重心化；算术包络[33,1,67,34]、34×33，与头声明100×100分别保留。cardinal/方向分块/帧率/loop未知，不猜顺序语义。头挂点原点符号与当前角色head节点沿HEAD_ATTACHMENT_CONTRACT待证。

自有高分辨身份裁图来自head-adornments-c-v1.png，[545,0,1020,512]475×512，仅裁切。玉绿云叶、暖金细边、象牙幼叶、短暖木干、小中央玉饰承接同item原画。A绘六相位、B绘后四相位；每次实际附源相位板、两主风格和自有参考。B没有遵守镜向叶序，且7/8偏宽15.53%/11.86%，不能当通过。C实际编辑B，额外实际附A中正确镜向phase6原比例单项裁图；纠正上/左右金卷叶朝向并保留8左侧/9两侧叶光、绿玉短端，7/8比例改善0.91%/6.33%，9/10约3.69%。

当前选A的0/1/2/3/4/6及C的7/8/9/10，共10新PNG、24源位置。A/B/C均实际1536×1024，各有generation.json；C有editOf B，裁图也有来源链。配置目标Sunburst/max、实际型号质量null。导出仅裁切等比缩放，没有程序画树/非等比挤压。当前10PNG按6+4灰底实际尺寸查看，内容bbox均不碰所选裁边，源offset逐位置一致。

比例约0.91%—6.33%、叶光数量/节奏、全alpha/相位连续性和真实挂点/时序/实机仍待完整验收。geometryAccepted/visualAccepted/accepted/runtimeAdopted全部false，完整动画未验收。当前索引world-art.json；小批记录exports/1311-a-export-observations.json与1311-c-export-observations.json。
