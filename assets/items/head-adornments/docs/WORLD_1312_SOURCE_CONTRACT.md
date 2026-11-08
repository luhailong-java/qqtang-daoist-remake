# 1312 明月当空照世界表示

源item1312/thadorn，真正world是固定参考ZIP的`QQTang-Local/runtime/client-patched/object/thadorn/thadorn47_stand.img`及同目录walk.img；两者167608bytes、SHA256 `a1e9f105924427f1648702882239c6d2901060827bd40ed5f2ff2f8ff985ee61`相同。来源为未验证官方真实性的社区客户端。metadata_only禁RGBA守卫确认24帧头/EOF、版本65536、4声明方向、声明100×100、未知头24/28为0/0。strictDeclaredStructureAccepted不替代像素/运行通过；strictCompleteContainerAccepted=false保留。

12 encoded raster/12含offset组：0—5各独立；[6,12,18]、[7,13,19]、[8,14,20]、[9,15,21]、[10,16,22]、[11,17,23]。仅0—5与6—11两批各6实际解码/查看，不解全24像素。真实为月牙、三朵遮挡云及细小星点/光晕：0—5开口右、大前云左；6—11开口左、大前云右。不能把背包两云的数量当world事实，亦不由像素镜向猜cardinal。

自有appearance来自head-adornments-c-v1.png的[1024,0,1536,510]原比例裁片，只承接象牙雕金月牙、玉青云纹材质。A画正向，B实际编辑A画反向；二者月体/光晕偏高。C实际编辑A修正0—5为0.17%—2.97%包络比例残差；D实际编辑B并附C作几何参考，6—11仅改善至14.45%—15.31%。E再实际编辑D、继续附C参考，以浅云横向展开和宽浅光晕改至2.10%—4.08%。C只为D/E支持参考，不伪记为其编辑目标。五母图均实际1536×1024，各自prompt/generation.json、editOf和源参考链保留，配置目标Sunburst/max而实际型号质量null。

当前选C0—5、E6—11，共12不同PNG；24源位置各自保留phaseIndex、native61×38和rawOffset：0—5[19,0]，其余[20,0]。PNG244×152仅为4倍像素密度。算术offset+size包络[19,0,81,38]为62×38，声明100×100另存。每个别名有独立position-NNN.alias.json，不继承代表坐标。native原点/符号、角色head节点、方向分块/cardinal、时长和loop未知。

当前12图按6+6必要小批灰底实看，均三云、月牙开口正确，内容bbox不碰选定裁边，整体残差0.17%—4.08%。星点明暗跨帧节奏、内部几何连续性、全alpha边缘、挂点/播放及实机仍未通过；geometryAccepted/visualAccepted/accepted/runtimeAdopted=false。不是完整动画验收。选择见exports/1312-selection.json，检查见1312-c-export-observations.json和1312-e-export-observations.json。
