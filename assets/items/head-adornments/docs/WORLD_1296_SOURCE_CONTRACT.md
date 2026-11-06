# 1296 彩虹相随世界表示

源item1296/thadorn/彩虹相随，真正world为固定参考ZIP中`QQTang-Local/runtime/client-patched/object/thadorn/thadorn51_stand.img`和`thadorn51_walk.img`，各114976bytes、SHA256 `a7afd84e1c3418dd0ffe0d5b15bbdf8daa438c53df65f8b582075febd28d6f88`。metadata_only禁RGBA守卫读取24帧头/EOF，4声明方向、65536、声明canvas100×100、未知24/28为0/0；结构通过不替代像素或运行通过，strictCompleteContainerAccepted=false/runtimeUsable=false保留。

12 encoded raster/12含offset组：0/1/2/3/4/5各独立，`[6,12,18] [7,13,19] [8,14,20] [9,15,21] [10,16,22] [11,17,23]`。实际源像素仅0—5、6—11两批各6。真实结构始终三朵云：前组大云左/小云右/中央小云，后组大云右/小云左/中央小云；虹桥与三云相位位移细小但编码不同，不能拿一张背包图替代24位置。

自有原画为head-adornments-c-v1.png的[0,0,540,512]原比例裁图，承接绢光彩虹、暖金细边、米白云卷与少量玉饰。A新绘0—5；B实际编辑A为6—11相反云大小关系，留editOf A。每次实际附真实相位板、两主风格与自有图。B6/8包络偏高16.01%/15.32%，C实际编辑B但左小云被放大、层级变弱，未选/未导出。D再次明确编辑B、只附实际源两相位及两主风格，恢复小左/大右，改善6/8至0.97%/3.94%。C、D均分别editOf B，不伪写D编辑C。A/B实际1536×1024，C/D实际1774×887；每母图有generation.json、配置目标Sunburst/max而实际型号质量null。提示尺寸不冒当实际返回，未改母图比例。

当前选A0—5，B7/9/10/11，D6/8，共12不同PNG与24原位置。源宽56—58、高27—29，各自×4输出224—232宽/108—116高；每sourcePhaseIndex、原rawOffset和源frame头独立保留，别名只共享图片。算术包络[20,2,80,31]为60×29，头声明100×100另存，不用来扩单帧。方向cardinal/分块语义、时长、loop和native挂点原点/符号未知。

12当前PNG按6+6实际×4尺寸灰底查看，均有三云、大小云左右角色正确，内容bbox都不碰所选裁边；每位置原offset一致。比例约0.97%—9.52%，7/10仍9.52%/9.10%，三云内部相对尺度/位置连续性、完整alpha边缘与虹桥中空、头挂点/时序/实机都待完整验收。geometryAccepted/visualAccepted/accepted/runtimeAdopted均false，完整动画未通过。索引world-art.json；当前选择exports/1296-selection.json；两批检查1296-a-export-observations.json、1296-b-export-observations.json。
