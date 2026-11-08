# 44 鸟巢帽世界表示合同

源类别thadorn、item44、显示名竹云雏巢。原名称/描述保存在catalog与world-art，不改原功能属性。真正world源为已固定参考ZIP内`QQTang-Local/runtime/client-patched/object/thadorn/thadorn16_stand.img`及`thadorn16_walk.img`，两者151018bytes、SHA256均`f4ee733ecf9762836b5138bae4c77fabe61814a1aa023e483286739a1b62ff9c`，不借inventory图标尺寸代替。

先通过metadata_only+禁用RGBA守卫读取完整24帧头，4声明方向，版本65536，canvas59×60，unknownHeader24/28为21/7。保留metadata-only字段strictDeclaredStructureAccepted=true、strictCompleteContainerAccepted=false、pixel/alpha未知、runtimeUsable=false；EOF结构证据不等于全像素验收。

编码raster去重后18组：`[0,2,4] [1] [3] [5] [6] [7] [8] [9] [10] [11] [12,14,16] [13] [15] [17] [18,20,22] [19] [21] [23]`。含rawOffset则24组。实际像素分3批，每批6个代表：A=0/1/3/5/6/7，B=8/9/10/11/12/13，C=15/17/18/19/21/23。没有全24像素解码。别名只依据encoded SHA+尺寸+pixelMode相同，每个原位置保留自己的rawOffset/sourcePhaseIndex。

实际观察源有三只不同颜色雏鸟、左右侧视、背视和正视，并有黄/青/橙轮流跃起。新外观承接已有本项目同item44原画裁图：青绿叶羽、金黄雏鸟、橙羽雏鸟、暖色藤枝巢、少量玉叶与金玉连接。每次实际附源相位板、邮件/组队两主风格及自己的同身份图；B/C另附前批世界图保持一致，均是新相位生成，没有冒记AI编辑。world/world-44-{a,b,c}-v1.png及其generation.json记录每张母图；目标配置Sunburst/max，实际型号/质量未知null。

18份当前PNG分别按源52/53宽和35—45高的各自native canvas×4导出，宽208/212、高140—180；不非等比压缩。24线性位置、18PNG、24源raster+offset分开统计。world-art与各position-NNN.alias.json保存完整源头/原偏移，directionIndex/cardinal、方向分块语义、每帧时长、loop都null。

A初裁第二分隔1034处误入下一帧左侧细枝。实际单母图窄带alpha检查找到第二间隙1016—1030，改为1024，第一间隙516—527仍选524，仅重新裁切导出、没有AI重画。修后18相位包络比例差约0.42%—6.73%，所有当前母图内容bbox均未碰所选单元边；仍不是几何通过。记录见exports/44-a-cut-band-observations.json及44-{a,b,c}-export-observations.json。

三批各6份当前PNG均按实际×4尺寸在灰底合成查看，三鸟数、前后朝向与跃起对象可区分。alpha各有0—255极值，但未全面检查边缘/相位连续性，不宣称全像素验收。最大比例残差为phase10约6.73%，phase7约5.31%；原始native挂点原点/符号、当前角色头节点、时序与实机未知。rawOffset+size算术包络[23,-11,83,49]、60×60，与源声明59×60各自保留，不据此推断坐标符号。全部accepted/geometryAccepted/visualAccepted/runtimeAdopted=false，完整动画未验收。
