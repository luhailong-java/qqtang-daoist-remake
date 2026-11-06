# 13020 满幅矩形水渠六帧候选

《灵葫大作战》生产候选。源六帧各120×520，footprint3×13、frameOffset[0,0]、mapElemOffset[0,0]及39个GridAttr0分别保留。真实原生母图1476×1066、六完整列各246×1066，原生比严格等于120:520，等比密度2.05；不是原生480×2080。原生RGB→RGBA的alpha天然255，无alpha规范化、透明fit、内接矩形搜索、岸线裁边或非均匀拉伸。

导出120×520与480×2080均为完整原生列裁取后严格等比PMA派生，4倍表示输出密度，不冒称模型原生细节。逐图generation.json实际submitted transparent_background=false，目标Sunburst/max，工具未披露实际型号/质量为null；实际附own master、源满幅六列结构及两主风格。

六个源可见像素各不同，六个own候选各不同。内渠/岸线/跨条板固定形状与源的对应、水光相位、边界拼缝和模型细节跨帧稳定未验收；外矩形比例与全不透明通过记录不代表内部几何或状态通过。accepted/geometry/stateCorrespondence/seamless/runtime仍false，时序/loop/组合原点null。

未改主art/index/runtime/src/Git或冻结三源码；只当前六源必要核图/当张切片，无本地测试/浏览器/全族QA。
