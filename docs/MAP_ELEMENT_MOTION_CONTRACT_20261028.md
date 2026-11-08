# 地图全状态与动画缺项合同（2026-10-28）

773个源定义均有单PNG静态候选，完整状态/动画仍未完成。现有源JSON声明954个按定义计的帧位，其中45个定义多帧；选中参考帧均为0，非零181个帧位无当前覆盖证据。181可能包括空帧、重复帧或破坏态，不能直接算181张新画或一律循环。

完整分族统计、45个多帧定义列表及证据边界见[合同说明](../references/qqtang-map-data/motion-contract/README.md)，逐773定义见[elements.json](../references/qqtang-map-data/motion-contract/elements.json)，输入JSON快照/哈希见[summary.json](../references/qqtang-map-data/motion-contract/summary.json)。

汇总读取production-index、families索引、17个原manifest、52个补充记录、二进制属性JSON及19族art.json；另以显式1–6资源小批补取45多帧结构表，226帧无结构空标记，219个encoded raster+offset组，有7个确切重复槽。额外字节组代表174个，仍需视觉核验而非新画数量承诺。没有RGBA/alpha解码、全包重哈希、运行清单写入、构建、测试或Git操作；新增52未序列化字段保持未知。

方向名、时序、循环与帧语义未证明均留null。单PNG存在和粗比例改善均不等于全帧、地图轮廓或实机通过。后续先按选定小批补证状态表与原生调用，再确定逐ID实际制作合同。
