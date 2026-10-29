# 236 竹风蜻蜓世界表示

源item236/thadorn/竹蜻蜓，真正world为参考ZIP中`QQTang-Local/runtime/client-patched/object/thadorn/thadorn38_stand.img`和`thadorn38_walk.img`，各174664bytes、SHA256 `aa520e671d7ff16420f2e4ef29c716f8b782a9159e556ffb755d9ad8546ffedc`。先读24帧metadata_only、禁止RGBA守卫；4声明方向、65536、头canvas100×100、未知24/28均0。EOF结构通过与完整像素通过分开，源strictCompleteContainerAccepted=false/runtimeUsable=false保留。

仅4 encoded raster/4含offset组：`[0,2,4] [1,3,5] [6,8,10,12,14,16,18,20,22] [7,9,11,13,15,17,19,21,23]`。只明确解码0/1/6/7四个代表。24个原位置仍各自sourcePhaseIndex、native尺寸、rawOffset和原frame头；未从24/4猜cardinal/方向分块语义或播放时长。源0/6宽77高32、1/7宽74高32，导出308×128/296×128，原offset不改。算术rawOffset+size包络[11,3,89,38]、78×35，不能拿声明100×100替代单帧，也不推断native坐标符号。

实际看到两片竹叶桨有宽横向和深度缩短的转向相位，弧形速度痕在不同侧。承接本项目已修掉电弧的`head-adornments-g-v1.png`玉竹金边/红白玉金底座身份。每次内置调用实际附源板、两主风格和自有图。A新生四相位；B实际编辑A的横向0/6，有editOf。A1536×1024，B实际2172×724（提示1536×1024未原样返回，未偷偷改母图尺寸）。每母图有generation.json，配置目标Sunburst/max，实际型号质量null未披露。

当前0/6选B、1/7选A。横向A比例差11.63%/15.46%，B改善4.87%/5.92%；1/7为2.98%/4.54%。四份当前PNG按实际×4尺寸灰底查看，所选单元内容bbox均不碰裁边，没有用非等比挤压。速度弧/相位连续性、全alpha边缘、头挂点原点与符号、时序和实机仍待，全部accepted/geometryAccepted/visualAccepted/runtimeAdopted=false。索引world-art.json与exports/236-a-export-observations.json。
