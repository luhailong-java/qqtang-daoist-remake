# 中国城与通用地图候选的原生转换计划

本轮逐文件核对中国城 38 件与通用场景 88 件，共 126 个定义。120 件候选通过完整原生格式预检，包含 98 件单帧图和 22 件齐全序列，覆盖 224 个源帧位。中国城 38 件全数通过，通用场景 82 件通过。另 6 件仍缺完整序列。其余 647 个定义本轮未逐件审核。

预检在内存中完成了 PNG 等比降采样、源像素模式编码、DIMG 重解码，以及全部非像素字节保持检查。各位置按原生帧尺寸和原始 frameOffset 写入，地图定义的 mapElemOffset、占地与 GridAttr 单独保留。120 件均可进入统一原生候选导出批次。正式登记通过的 geometryAccepted 与 accepted 目前均为 0 件，原始播放时序、循环、组合挂点与实机效果继续待核。

逐帧 PNG 路径、实际密度、源像素模式、Alpha 数值、原始偏移、包索引和内存编码哈希见 [逐文件 JSON](native-map-conversion-plan-20261114.json)。accepted 与 geometryAccepted 的待验标记单独保留，技术预检按实际像素、帧位和编码约束判定。

## 技术可转清单

下表每行代表一个完整源文件。单帧行列出实际 PNG，序列行列出记录全部帧 PNG 的 manifest。所有候选实际导出密度均为 4，原生编码会从对应四倍帧画幅等比降采样。

| 元素 | 族 | 原生路径 | 源帧位 | 原生帧尺寸 | mapElemOffset | 候选 |
| --- | --- | --- | ---: | --- | --- | --- |
| 3001 | town | `object/mapElem/town/elem1_stand.img` | 1 | 40×40 | `[0,0]` | [3001-wood-floor.png](../assets/maps/town/pieces/3001-wood-floor.png) |
| 3002 | town | `object/mapElem/town/elem2_stand.img` | 1 | 40×40 | `[0,0]` | [3002-pavement-light.png](../assets/maps/town/pieces/3002-pavement-light.png) |
| 3003 | town | `object/mapElem/town/elem3_stand.img` | 1 | 40×40 | `[0,0]` | [3003-pavement-dark.png](../assets/maps/town/pieces/3003-pavement-dark.png) |
| 3004 | town | `object/mapElem/town/elem4_stand.img` | 1 | 42×54 | `[2,13]` | [3004-drum.png](../assets/maps/town/pieces/3004-drum.png) |
| 3005 | town | `object/mapElem/town/elem5_stand.img` | 1 | 44×78 | `[2,34]` | [3005-red-shrine.png](../assets/maps/town/pieces/3005-red-shrine.png) |
| 3006 | town | `object/mapElem/town/elem6_stand.img` | 1 | 120×80 | `[0,0]` | [3006-taiji-courtyard-slab.png](../assets/maps/town/pieces/3006-taiji-courtyard-slab.png) |
| 3007 | town | `object/mapElem/town/elem7_stand.img` | 1 | 43×58 | `[3,17]` | [3007-house-gold.png](../assets/maps/town/pieces/3007-house-gold.png) |
| 3008 | town | `object/mapElem/town/elem8_stand.img` | 1 | 43×58 | `[3,17]` | [3008-house-grey.png](../assets/maps/town/pieces/3008-house-grey.png) |
| 3009 | town | `object/mapElem/town/elem9_stand.img` | 1 | 43×58 | `[3,18]` | [3009-house-jade.png](../assets/maps/town/pieces/3009-house-jade.png) |
| 3010 | town | `object/mapElem/town/elem10_stand.img` | 1 | 43×53 | `[2,13]` | [3010-shrub.png](../assets/maps/town/pieces/3010-shrub.png) |
| 3011 | town | `object/mapElem/town/elem11_stand.img` | 1 | 40×40 | `[0,0]` | [3011-pool-bank.png](../assets/maps/town/pieces/3011-pool-bank.png) |
| 3012 | town | `object/mapElem/town/elem12_stand.img` | 1 | 40×40 | `[0,0]` | [3012-pool-bank.png](../assets/maps/town/pieces/3012-pool-bank.png) |
| 3013 | town | `object/mapElem/town/elem13_stand.img` | 1 | 40×40 | `[0,0]` | [3013-pool-bank.png](../assets/maps/town/pieces/3013-pool-bank.png) |
| 3014 | town | `object/mapElem/town/elem14_stand.img` | 1 | 43×53 | `[3,10]` | [3014-pedestal-blue.png](../assets/maps/town/pieces/3014-pedestal-blue.png) |
| 3015 | town | `object/mapElem/town/elem15_stand.img` | 1 | 43×53 | `[2,10]` | [3015-pedestal-jade.png](../assets/maps/town/pieces/3015-pedestal-jade.png) |
| 3017 | town | `object/mapElem/town/elem17_stand.img` | 1 | 43×53 | `[2,10]` | [3017-target-pedestal.png](../assets/maps/town/pieces/3017-target-pedestal.png) |
| 3018 | town | `object/mapElem/town/elem18_stand.img` | 1 | 43×53 | `[2,10]` | [3018-bamboo-pedestal.png](../assets/maps/town/pieces/3018-bamboo-pedestal.png) |
| 3019 | town | `object/mapElem/town/elem19_stand.img` | 1 | 161×110 | `[0,30]` | [3019-courtyard-shop.png](../assets/maps/town/pieces/3019-courtyard-shop.png) |
| 3020 | town | `object/mapElem/town/elem20_stand.img` | 1 | 40×54 | `[0,14]` | [3020-lantern-column.png](../assets/maps/town/pieces/3020-lantern-column.png) |
| 3022 | town | `object/mapElem/town/elem22_stand.img` | 1 | 40×40 | `[0,0]` | [3022-pool-bank.png](../assets/maps/town/pieces/3022-pool-bank.png) |
| 3023 | town | `object/mapElem/town/elem23_stand.img` | 1 | 40×40 | `[0,0]` | [3023-pool-bank.png](../assets/maps/town/pieces/3023-pool-bank.png) |
| 3024 | town | `object/mapElem/town/elem24_stand.img` | 1 | 40×40 | `[0,0]` | [3024-pool-bank.png](../assets/maps/town/pieces/3024-pool-bank.png) |
| 3025 | town | `object/mapElem/town/elem25_stand.img` | 1 | 40×40 | `[0,0]` | [3025-pool-bank.png](../assets/maps/town/pieces/3025-pool-bank.png) |
| 3026 | town | `object/mapElem/town/elem26_stand.img` | 1 | 40×40 | `[0,0]` | [3026-pool-bank.png](../assets/maps/town/pieces/3026-pool-bank.png) |
| 3050 | town | `object/mapElem/town/elem50_stand.img` | 4 | 43×101 | `[1,60]` | [sequence.json](../assets/maps/town/animation-candidates/3050/sequence.json) |
| 3051 | town | `object/mapElem/town/elem51_stand.img` | 3 | 39×70 | `[-1,30]` | [sequence.json](../assets/maps/town/animation-candidates/3051/sequence.json) |
| 3053 | town | `object/mapElem/town/elem53_stand.img` | 1 | 40×40 | `[0,0]` | [3053-stone-floor.png](../assets/maps/town/pieces/3053-stone-floor.png) |
| 3054 | town | `object/mapElem/town/elem54_stand.img` | 1 | 43×53 | `[2,12]` | [3054-sun-pedestal-copper.png](../assets/maps/town/pieces/3054-sun-pedestal-copper.png) |
| 3055 | town | `object/mapElem/town/elem55_stand.img` | 1 | 43×53 | `[3,12]` | [3055-sun-pedestal-red.png](../assets/maps/town/pieces/3055-sun-pedestal-red.png) |
| 3056 | town | `object/mapElem/town/elem56_stand.img` | 1 | 45×62 | `[3,21]` | [3056-gold-pavilion.png](../assets/maps/town/pieces/3056-gold-pavilion.png) |
| 3057 | town | `object/mapElem/town/elem57_stand.img` | 1 | 37×69 | `[-2,29]` | [3057-cypress.png](../assets/maps/town/pieces/3057-cypress.png) |
| 3058 | town | `object/mapElem/town/elem58_stand.img` | 1 | 600×142 | `[0,22]` | [3058-palace-wall-strip.png](../assets/maps/town/pieces/3058-palace-wall-strip.png) |
| 3059 | town | `object/mapElem/town/elem59_stand.img` | 1 | 600×400 | `[0,0]` | [3059-palace-courtyard-floor.png](../assets/maps/town/pieces/3059-palace-courtyard-floor.png) |
| 3060 | town | `object/mapElem/town/elem60_stand.img` | 1 | 63×92 | `[21,51]` | [3060-daoist-boy-guardian-statue.png](../assets/maps/town/pieces/3060-daoist-boy-guardian-statue.png) |
| 3061 | town | `object/mapElem/town/elem61_stand.img` | 1 | 63×92 | `[2,51]` | [3061-moon-girl-guardian-statue.png](../assets/maps/town/pieces/3061-moon-girl-guardian-statue.png) |
| 3120 | town | `object/mapElem/town/elem120_stand.img` | 1 | 40×80 | `[0,0]` | [3120-rock-wall-left.png](../assets/maps/town/pieces/3120-rock-wall-left.png) |
| 3121 | town | `object/mapElem/town/elem121_stand.img` | 1 | 40×80 | `[0,0]` | [3121-rock-wall-right.png](../assets/maps/town/pieces/3121-rock-wall-right.png) |
| 3122 | town | `object/mapElem/town/elem122_stand.img` | 1 | 40×80 | `[0,0]` | [3122-rock-wall-center.png](../assets/maps/town/pieces/3122-rock-wall-center.png) |
| 17001 | common | `object/mapElem/common/elem1_stand.img` | 1 | 40×40 | `[0,0]` | [17001-shared-painted-candidate.png](../assets/maps/common/pieces/17001-shared-painted-candidate.png) |
| 17018 | common | `object/mapElem/common/elem18_stand.img` | 4 | 40×56 / 40×58 | `[0,15]` | [sequence.json](../assets/maps/common/animation-candidates/17018/sequence.json) |
| 17019 | common | `object/mapElem/common/elem19_stand.img` | 3 | 39×59 | `[-1,15]` | [sequence.json](../assets/maps/common/animation-candidates/17019/sequence.json) |
| 17021 | common | `object/mapElem/common/elem21_stand.img` | 1 | 40×57 | `[0,16]` | [17021-intact-marker-v2.png](../assets/maps/common/pieces/17021-intact-marker-v2.png) |
| 17022 | common | `object/mapElem/common/elem22_stand.img` | 1 | 40×55 | `[0,15]` | [17022-cracked-marker-v2.png](../assets/maps/common/pieces/17022-cracked-marker-v2.png) |
| 17023 | common | `object/mapElem/common/elem23_stand.img` | 1 | 40×52 | `[0,12]` | [17023-shattered-marker-v2.png](../assets/maps/common/pieces/17023-shattered-marker-v2.png) |
| 17030 | common | `object/mapElem/common/elem30_stand.img` | 6 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17030/sequence.json) |
| 17033 | common | `object/mapElem/common/elem33_stand.img` | 6 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17033/sequence.json) |
| 17037 | common | `object/mapElem/common/elem37_stand.img` | 6 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17037/sequence.json) |
| 17038 | common | `object/mapElem/common/elem38_stand.img` | 6 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17038/sequence.json) |
| 17039 | common | `object/mapElem/common/elem39_stand.img` | 6 | 114×96 / 114×94 / 114×86 / 114×91 | `[-3,16]` | [sequence.json](../assets/maps/animation-continuation-20261112/17039/sequence.json) |
| 17040 | common | `object/mapElem/common/elem40_stand.img` | 1 | 40×40 | `[0,0]` | [17040-jade-flame-seal-floor.png](../assets/maps/common/pieces/17040-jade-flame-seal-floor.png) |
| 17045 | common | `object/mapElem/common/elem45_stand.img` | 1 | 40×40 | `[0,0]` | [17045-jade-star-seal-floor.png](../assets/maps/common/pieces/17045-jade-star-seal-floor.png) |
| 17046 | common | `object/mapElem/common/elem46_stand.img` | 5 | 40×50 / 40×49 / 40×51 / 40×55 | `[0,10]` | [sequence.json](../assets/maps/animation-continuation-20261112/17046/sequence.json) |
| 17047 | common | `object/mapElem/common/elem47_stand.img` | 1 | 40×57 | `[0,17]` | [17047-violet-vase-leaves.png](../assets/maps/common/pieces/17047-violet-vase-leaves.png) |
| 17048 | common | `object/mapElem/common/elem48_stand.img` | 4 | 40×57 | `[0,17]` | [sequence.json](../assets/maps/animation-continuation-20261112/17048/sequence.json) |
| 17050 | common | `object/mapElem/common/elem50_stand.img` | 1 | 78×99 | `[-2,58]` | [17050-horn-skull-altar-small-v2.png](../assets/maps/common/pieces/17050-horn-skull-altar-small-v2.png) |
| 17051 | common | `object/mapElem/common/elem51_stand.img` | 1 | 43×47 | `[2,5]` | [17051-jade-berry-shrub.png](../assets/maps/common/pieces/17051-jade-berry-shrub.png) |
| 17052 | common | `object/mapElem/common/elem52_stand.img` | 4 | 36×59 | `[2,28]` | [sequence.json](../assets/maps/animation-continuation-20261112/17052/sequence.json) |
| 17053 | common | `object/mapElem/common/elem53_stand.img` | 1 | 40×56 | `[0,16]` | [17053-jade-monitor-terminal.png](../assets/maps/common/pieces/17053-jade-monitor-terminal.png) |
| 17054 | common | `object/mapElem/common/elem54_stand.img` | 5 | 48×72 / 48×73 / 48×74 | `[4,31]` | [sequence.json](../assets/maps/animation-continuation-20261112/17054/sequence.json) |
| 17055 | common | `object/mapElem/common/elem55_stand.img` | 1 | 51×52 | `[5,10]` | [17055-dark-sprout-cluster.png](../assets/maps/common/pieces/17055-dark-sprout-cluster.png) |
| 17056 | common | `object/mapElem/common/elem56_stand.img` | 1 | 29×34 | `[-5,0]` | [17056-dark-sprout-small.png](../assets/maps/common/pieces/17056-dark-sprout-small.png) |
| 17057 | common | `object/mapElem/common/elem57_stand.img` | 1 | 40×55 | `[0,15]` | [17057-bear-marker.png](../assets/maps/common/pieces/17057-bear-marker.png) |
| 17058 | common | `object/mapElem/common/elem58_stand.img` | 1 | 120×105 | `[0,25]` | [17058-blue-mushroom-house-v2.png](../assets/maps/common/pieces/17058-blue-mushroom-house-v2.png) |
| 17059 | common | `object/mapElem/common/elem59_stand.img` | 1 | 120×164 | `[1,84]` | [17059-horn-skull-shrine-v2.png](../assets/maps/common/pieces/17059-horn-skull-shrine-v2.png) |
| 17060 | common | `object/mapElem/common/elem60_stand.img` | 1 | 43×51 | `[2,11]` | [17060-turquoise-fire-chest.png](../assets/maps/common/pieces/17060-turquoise-fire-chest.png) |
| 17061 | common | `object/mapElem/common/elem61_stand.img` | 1 | 78×109 | `[-1,69]` | [17061-ribbed-horn-skull-altar.png](../assets/maps/common/pieces/17061-ribbed-horn-skull-altar.png) |
| 17062 | common | `object/mapElem/common/elem62_stand.img` | 1 | 41×75 | `[2,34]` | [17062-tilted-book-lectern.png](../assets/maps/common/pieces/17062-tilted-book-lectern.png) |
| 17063 | common | `object/mapElem/common/elem63_stand.img` | 1 | 131×135 | `[2,15]` | [17063-sealed-book-platform.png](../assets/maps/common/pieces/17063-sealed-book-platform.png) |
| 17064 | common | `object/mapElem/common/elem64_stand.img` | 1 | 40×60 | `[0,20]` | [17064-tall-violet-vase.png](../assets/maps/common/pieces/17064-tall-violet-vase.png) |
| 17065 | common | `object/mapElem/common/elem65_stand.img` | 1 | 86×83 | `[4,39]` | [17065-book-candle-desk-v2.png](../assets/maps/common/pieces/17065-book-candle-desk-v2.png) |
| 17066 | common | `object/mapElem/common/elem66_stand.img` | 1 | 72×77 | `[-4,-2]` | [17066-flower-vine-stump-v2.png](../assets/maps/common/pieces/17066-flower-vine-stump-v2.png) |
| 17067 | common | `object/mapElem/common/elem67_stand.img` | 1 | 10×64 | `[-16,0]` | [17067-thin-bamboo-post-v2.png](../assets/maps/common/pieces/17067-thin-bamboo-post-v2.png) |
| 17068 | common | `object/mapElem/common/elem68_stand.img` | 1 | 65×53 | `[12,-4]` | [17068-barred-gate-v2.png](../assets/maps/common/pieces/17068-barred-gate-v2.png) |
| 17069 | common | `object/mapElem/common/elem69_stand.img` | 1 | 51×79 | `[1,36]` | [17069-olive-thorn-coil.png](../assets/maps/common/pieces/17069-olive-thorn-coil.png) |
| 17070 | common | `object/mapElem/common/elem70_stand.img` | 1 | 51×79 | `[6,36]` | [17070-green-thorn-coil.png](../assets/maps/common/pieces/17070-green-thorn-coil.png) |
| 17071 | common | `object/mapElem/common/elem71_stand.img` | 1 | 120×52 | `[0,6]` | [17071-horizontal-stone-bridge-v2.png](../assets/maps/common/pieces/17071-horizontal-stone-bridge-v2.png) |
| 17072 | common | `object/mapElem/common/elem72_stand.img` | 1 | 52×120 | `[6,0]` | [17072-vertical-stone-bridge-v2.png](../assets/maps/common/pieces/17072-vertical-stone-bridge-v2.png) |
| 17073 | common | `object/mapElem/common/elem73_stand.img` | 1 | 40×60 | `[0,20]` | [17073-red-eye-skull-planter.png](../assets/maps/common/pieces/17073-red-eye-skull-planter.png) |
| 17074 | common | `object/mapElem/common/elem74_stand.img` | 1 | 54×32 | `[0,-6]` | [17074-short-wood-fence.png](../assets/maps/common/pieces/17074-short-wood-fence.png) |
| 17075 | common | `object/mapElem/common/elem75_stand.img` | 1 | 41×40 | `[0,0]` | [17075-olive-face-relief.png](../assets/maps/common/pieces/17075-olive-face-relief.png) |
| 17076 | common | `object/mapElem/common/elem76_stand.img` | 1 | 84×56 | `[1,14]` | [17076-slate-cloud-bench-v2.png](../assets/maps/common/pieces/17076-slate-cloud-bench-v2.png) |
| 17077 | common | `object/mapElem/common/elem77_stand.img` | 4 | 36×59 | `[-2,19]` | [sequence.json](../assets/maps/animation-continuation-20261112/17077/sequence.json) |
| 17078 | common | `object/mapElem/common/elem78_stand.img` | 1 | 10×64 | `[0,1]` | [17078-common-source-alias-v1.png](../assets/maps/common/pieces/17078-common-source-alias-v1.png) |
| 17079 | common | `object/mapElem/common/elem79_stand.img` | 1 | 10×64 | `[-31,0]` | [17079-common-source-alias-v1.png](../assets/maps/common/pieces/17079-common-source-alias-v1.png) |
| 17080 | common | `object/mapElem/common/elem80_stand.img` | 1 | 54×32 | `[14,-8]` | [17080-common-source-alias-v1.png](../assets/maps/common/pieces/17080-common-source-alias-v1.png) |
| 17081 | common | `object/mapElem/common/elem81_stand.img` | 1 | 54×32 | `[0,0]` | [17081-common-source-alias-v1.png](../assets/maps/common/pieces/17081-common-source-alias-v1.png) |
| 17082 | common | `object/mapElem/common/elem82_stand.img` | 1 | 120×52 | `[0,6]` | [17082-common-source-alias-v1.png](../assets/maps/common/pieces/17082-common-source-alias-v1.png) |
| 17083 | common | `object/mapElem/common/elem83_stand.img` | 1 | 52×120 | `[7,0]` | [17083-common-source-alias-v1.png](../assets/maps/common/pieces/17083-common-source-alias-v1.png) |
| 17100 | common | `object/mapElem/common/elem100_stand.img` | 1 | 40×54 | `[0,13]` | [17100-beige-square-relief-block.png](../assets/maps/common/pieces/17100-beige-square-relief-block.png) |
| 17101 | common | `object/mapElem/common/elem101_stand.img` | 1 | 40×54 | `[0,13]` | [17101-blue-star-relief-block.png](../assets/maps/common/pieces/17101-blue-star-relief-block.png) |
| 17102 | common | `object/mapElem/common/elem102_stand.img` | 1 | 40×54 | `[0,13]` | [17102-winged-seal-block.png](../assets/maps/common/pieces/17102-winged-seal-block.png) |
| 17103 | common | `object/mapElem/common/elem103_stand.img` | 1 | 42×53 | `[1,12]` | [17103-ice-thorn-slab.png](../assets/maps/common/pieces/17103-ice-thorn-slab.png) |
| 17104 | common | `object/mapElem/common/elem104_stand.img` | 1 | 41×57 | `[0,17]` | [17104-spiked-cyan-pool.png](../assets/maps/common/pieces/17104-spiked-cyan-pool.png) |
| 17105 | common | `object/mapElem/common/elem105_stand.img` | 1 | 42×40 | `[0,0]` | [17105-rust-square-grate.png](../assets/maps/common/pieces/17105-rust-square-grate.png) |
| 17106 | common | `object/mapElem/common/elem106_stand.img` | 1 | 40×43 | `[0,0]` | [17106-rust-grate-cross-a.png](../assets/maps/common/pieces/17106-rust-grate-cross-a.png) |
| 17107 | common | `object/mapElem/common/elem107_stand.img` | 1 | 42×43 | `[0,1]` | [17107-rust-grate-cross-b.png](../assets/maps/common/pieces/17107-rust-grate-cross-b.png) |
| 17108 | common | `object/mapElem/common/elem108_stand.img` | 1 | 42×43 | `[0,0]` | [17108-rust-grate-cross-c.png](../assets/maps/common/pieces/17108-rust-grate-cross-c.png) |
| 17109 | common | `object/mapElem/common/elem109_stand.img` | 1 | 42×40 | `[0,0]` | [17109-rust-grate-vertical.png](../assets/maps/common/pieces/17109-rust-grate-vertical.png) |
| 17110 | common | `object/mapElem/common/elem110_stand.img` | 1 | 40×43 | `[-2,0]` | [17110-rust-grate-horizontal.png](../assets/maps/common/pieces/17110-rust-grate-horizontal.png) |
| 17111 | common | `object/mapElem/common/elem111_stand.img` | 1 | 42×40 | `[0,0]` | [17111-rust-grate-rounded-corner.png](../assets/maps/common/pieces/17111-rust-grate-rounded-corner.png) |
| 17112 | common | `object/mapElem/common/elem112_stand.img` | 1 | 40×40 | `[0,0]` | [17112-grate-quarter-bottom-left.png](../assets/maps/common/pieces/17112-grate-quarter-bottom-left.png) |
| 17113 | common | `object/mapElem/common/elem113_stand.img` | 1 | 40×43 | `[0,0]` | [17113-grate-quarter-top-left.png](../assets/maps/common/pieces/17113-grate-quarter-top-left.png) |
| 17114 | common | `object/mapElem/common/elem114_stand.img` | 1 | 42×43 | `[0,0]` | [17114-grate-quarter-top-right.png](../assets/maps/common/pieces/17114-grate-quarter-top-right.png) |
| 17115 | common | `object/mapElem/common/elem115_stand.img` | 1 | 42×43 | `[0,0]` | [17115-steel-square-hatch.png](../assets/maps/common/pieces/17115-steel-square-hatch.png) |
| 17121 | common | `object/mapElem/common/elem121_stand.img` | 1 | 40×40 | `[0,0]` | [17121-upper-arrow-lower-panel.png](../assets/maps/common/pieces/17121-upper-arrow-lower-panel.png) |
| 17122 | common | `object/mapElem/common/elem122_stand.img` | 1 | 40×40 | `[0,0]` | [17122-upper-arrow-upper-panel.png](../assets/maps/common/pieces/17122-upper-arrow-upper-panel.png) |
| 17123 | common | `object/mapElem/common/elem123_stand.img` | 1 | 40×40 | `[0,0]` | [17123-lower-arrow-upper-panel.png](../assets/maps/common/pieces/17123-lower-arrow-upper-panel.png) |
| 17124 | common | `object/mapElem/common/elem124_stand.img` | 1 | 40×40 | `[0,0]` | [17124-lower-arrow-lower-panel.png](../assets/maps/common/pieces/17124-lower-arrow-lower-panel.png) |
| 17125 | common | `object/mapElem/common/elem125_stand.img` | 1 | 40×40 | `[0,0]` | [17125-right-arrow-left-panel.png](../assets/maps/common/pieces/17125-right-arrow-left-panel.png) |
| 17126 | common | `object/mapElem/common/elem126_stand.img` | 1 | 40×40 | `[0,0]` | [17126-right-arrow-right-panel.png](../assets/maps/common/pieces/17126-right-arrow-right-panel.png) |
| 17127 | common | `object/mapElem/common/elem127_stand.img` | 1 | 40×40 | `[0,0]` | [17127-left-arrow-right-panel-v2.png](../assets/maps/common/pieces/17127-left-arrow-right-panel-v2.png) |
| 17128 | common | `object/mapElem/common/elem128_stand.img` | 1 | 40×40 | `[0,0]` | [17128-left-arrow-left-panel-v2.png](../assets/maps/common/pieces/17128-left-arrow-left-panel-v2.png) |
| 17130 | common | `object/mapElem/common/elem130_stand.img` | 10 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17130/sequence.json) |
| 17131 | common | `object/mapElem/common/elem131_stand.img` | 10 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17131/sequence.json) |
| 17132 | common | `object/mapElem/common/elem132_stand.img` | 10 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17132/sequence.json) |
| 17133 | common | `object/mapElem/common/elem133_stand.img` | 10 | 40×40 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17133/sequence.json) |
| 17134 | common | `object/mapElem/common/elem134_stand.img` | 5 | 41×43 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17134/sequence.json) |
| 17135 | common | `object/mapElem/common/elem135_stand.img` | 5 | 41×43 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17135/sequence.json) |
| 17136 | common | `object/mapElem/common/elem136_stand.img` | 5 | 41×43 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17136/sequence.json) |
| 17137 | common | `object/mapElem/common/elem137_stand.img` | 5 | 41×43 | `[0,0]` | [sequence.json](../assets/maps/animation-continuation-20261112/17137/sequence.json) |

## 待补全的六件

| 元素 | 源文件 | 声明帧位 | 当前候选状态 |
| --- | --- | ---: | --- |
| 17024 | `object/mapElem/common/elem24_stand.img` | 3 | 已有首帧，完整序列尚缺 |
| 17025 | `object/mapElem/common/elem25_stand.img` | 3 | 已有首帧，完整序列尚缺 |
| 17026 | `object/mapElem/common/elem26_stand.img` | 4 | 已有首帧，完整序列尚缺 |
| 17027 | `object/mapElem/common/elem27_stand.img` | 3 | 已有首帧，完整序列尚缺 |
| 17028 | `object/mapElem/common/elem28_stand.img` | 3 | 已有首帧，完整序列尚缺 |
| 17029 | `object/mapElem/common/elem29_stand.img` | 4 | 已有首帧，完整序列尚缺 |

## Alpha 与画面复核

13 件的源图完全不透明，而候选在原生降采样后包含透明或半透明像素，元素为 3001、3002、3003、3006、3053、3120、3121、3122、17001、17071、17072、17082、17083。原像素模式能够编码这些 Alpha，格式预检通过。地面是否出现缝隙、轮廓是否符合目标场景，需要先查看实际新画。另有 59 件的可见 Alpha 包络发生变化，逐帧包络和像素计数已记录在 JSON 中。通过预检的候选中，52 件的 Alpha 透明类别和可见包络同时与源图相符，这仍需结合新画本身审核。

核查范围内的每个源帧位都保留独立对应关系。原生声明、空帧结构和原始偏移随源字节保留。候选的画风、动态连续性、占地视觉、遮挡和完整地图拼接仍待实机与人工复核。

## 原生包合并安排

本轮 126 个源文件均在 object.pkg 中，固定 ZIP 未发现同路径 loose IMG。后续批次应将清单中的完整资源合入当前 UI 与头饰替换批次，并在目标客户端的当前包上追加压缩段、逐条更新索引。每个未列入地图批次的已安装 UI、头饰和其他资源须逐字节保留，写入前后核对资源哈希和索引条目。

当前客户端已有自有 UI 与头饰，固定社区包在本计划中承担参照和源结构核验。安装流程需要统一合并所有已授权原生路径，保存完整包与索引备份，并验证回滚。直接把固定源 object.pkg/object.idx 覆盖到客户端会丢失现有美术修改。

本计划产物为本 MD 与 JSON。检查期间读取固定源包、索引及项目候选，原生候选编码仅保存在内存中。 [QQ 堂来源与身份边界](QQTANG_REFERENCE_SOURCE.md)
