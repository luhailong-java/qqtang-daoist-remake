# 1248 乌云世界表示

源item1248/thadorn/乌云，真正world为固定参考ZIP中`QQTang-Local/runtime/client-patched/object/thadorn/thadorn45_stand.img`和`thadorn45_walk.img`，各157312bytes、SHA256 `bf1164cdfb75ff13e08a3c7ab7fdf0e110c2ff59821647957031fd33dc336e8b`。metadata_only禁RGBA守卫读取24帧结构，4声明方向、65536、声明100×100、未知24/28为0/0。strictDeclaredStructureAccepted与strictCompleteContainerAccepted=false/runtimeUsable=false分开，结构记录不当全像素通过。

12 encoded raster/12含offset组：0/1/2/3/4/5独立，`[6,12,18] [7,13,19] [8,14,20] [9,15,21] [10,16,22] [11,17,23]`。源0—5与6—11分两批各6实际解码。真实云卷左右镜向；0/6小电光、1/7分离小电光碎片、2/3/4和8/9/10无闪电、5/11较大下方闪电，明暗随相位变化，没有雨滴。源云体中心样本alpha255保留，不凭浅色推断全局淡出。采样见references/world/1248/source-a-bounded-alpha-samples.json。

自有原画参考为head-adornments-b-v1.png的[1024,530,1536,1024]裁图，只承接炭灰青灰云块、细暖金云卷与手绘质感；背包大闪电不能套全部world状态。A新绘0—5，B实际编辑A画相反云卷6—11，右尾/左大云块、左右电光位置随真实源改变；B有editOf A。每次实际附真实源相位板、两主风格、自有图；A/B均实际1536×1024，各有generation.json。配置目标Sunburst/max，实际型号质量null未披露。

每原位置自己的sourcePhaseIndex、native尺寸与rawOffset完整保留。帧宽55或57、高35—46→导出220或228宽、140—184高。算术rawOffset+size包络[20,2,80,48]、60×46，声明100×100另存，不用来扩每帧。cardinal/方向分块语义/帧时长/loop、native挂点原点符号和当前角色头节点未知。别名只共享PNG，不共享坐标或伪造时序。

12份PNG按6+6灰底实际×4尺寸查看，左右云尾、无电/小电/大电分别可见。B下排前两图分隔530，避免右卷尾跨名义512。所有当前内容bbox未碰所选单元边，导出尺寸和每位置offset吻合。比例约0.33%—9.06%，最高phase10约9.06%、phase9约8.83%、phase4约8.00%；这些残差和全alpha/相位连续性、挂点时序实机仍待验，不放宽通过。全部geometryAccepted/visualAccepted/accepted/runtimeAdopted=false，完整动画未验收。索引world-art.json，检查exports/1248-a-export-observations.json、1248-b-export-observations.json。
