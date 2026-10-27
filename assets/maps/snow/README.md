# snow 地图美术候选交付

2026-10-26：现有源定义 47 项，本目录已有 47 项候选、46 张不同画面、8 张内置生成母图。生成入口失败 0 次。**accepted／geometryAccepted／seamlessVerified／inGameAccepted 全为 false。**

[源图／自有候选并排概览](comparison-overview.png) · [逐件清单](art.json) · [本族核验](validation.json)

原始 frame 尺寸乘四作为导出画布，footprintCells、gridAttr、mapElemOffsetRaw、selectedFrameOffsetRaw 原样保留。裁切与统一缩放是派生处理，不是模型原生细节或几何验收；没有修改任何地图文件、全局生产索引或客户端代码。当前底图边缘有透明留白，部分可见外形比例与源不同，需后续返修／拼接核验，不能投入最终地图验收。

每次生图前实际重读 image 的 AGENTS、统一配置及执行策略，实际附上邮件主参考、组队主参考和该批结构 contact。配置快照目标 gpt-image-2.5-sunburst／max；工具没有 model／quality 参数，返回未披露这两个字段，所有实际提交／返回型号和质量仍为 null。官方核对依据：[模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)、[图像参数](https://developers.openai.com/api/reference/resources/images/methods/generate)。本任务未用 API／CLI 生图。

## 母图与记录

| 批次 | 元素 ID | 原生母图 | 记录与裁切 |
|---|---|---|---|
| batch-01 | 2001, 2002, 2003, 2004, 2006, 2007 | [batch-01/sheet-v1.png](batch-01/sheet-v1.png) | [generation](batch-01/sheet-v1.png.generation.json) · [crops](batch-01/crops.json) · [qa](batch-01/qa.json) |
| batch-02 | 2008, 2014, 2019, 2040, 2041, 2020 | [batch-02/sheet-v1.png](batch-02/sheet-v1.png) | [generation](batch-02/sheet-v1.png.generation.json) · [crops](batch-02/crops.json) · [qa](batch-02/qa.json) |
| batch-03 | 2005, 2011, 2013, 2015, 2016, 2017 | [batch-03/sheet-v1.png](batch-03/sheet-v1.png) | [generation](batch-03/sheet-v1.png.generation.json) · [crops](batch-03/crops.json) · [qa](batch-03/qa.json) |
| batch-04 | 2018, 2021, 2022, 2023, 2024, 2025 | [batch-04/sheet-v1.png](batch-04/sheet-v1.png) | [generation](batch-04/sheet-v1.png.generation.json) · [crops](batch-04/crops.json) · [qa](batch-04/qa.json) |
| batch-05 | 2026, 2027, 2028, 2029, 2030, 2031 | [batch-05/sheet-v1.png](batch-05/sheet-v1.png) | [generation](batch-05/sheet-v1.png.generation.json) · [crops](batch-05/crops.json) · [qa](batch-05/qa.json) |
| batch-06 | 2032, 2033, 2034, 2035, 2036, 2037 | [batch-06/sheet-v1.png](batch-06/sheet-v1.png) | [generation](batch-06/sheet-v1.png.generation.json) · [crops](batch-06/crops.json) · [qa](batch-06/qa.json) |
| batch-07 | 2038, 2039, 2042, 2043, 2044, 2045 | [batch-07/sheet-v1.png](batch-07/sheet-v1.png) | [generation](batch-07/sheet-v1.png.generation.json) · [crops](batch-07/crops.json) · [qa](batch-07/qa.json) |
| batch-08 | 2046, 2047, 2048, 2049 | [batch-08/sheet-v1.png](batch-08/sheet-v1.png) | [generation](batch-08/sheet-v1.png.generation.json) · [crops](batch-08/crops.json) · [qa](batch-08/qa.json) |

Snow 的 2012 与 2003 是源 visibleContentSHA／frame 尺寸已核对的同图别名，复用已新画的 2003 PNG，2012 自身规则字段单独保留；没有额外模型生成。

## 未通过的检查，逐条记录

以下 WARN 不是通过记录。alpha-positive 裁切告警统计的是所有 alpha>0 像素；每批 qa 另外记录 alpha>=8 实物像素丢失数。极低 alpha 的外光晕没有静默改成“无损”。可见比例与地面边缘诊断详见 validation.json。

| id | 元素 | value | threshold | 文件 |
|---|---:|---:|---:|---|
| crop.dropped_alpha_positive_fraction | 2001 | 0.03658606562080402 | 0.01 | `assets/maps/snow/pieces/2001-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2002 | 0.026665945478147986 | 0.01 | `assets/maps/snow/pieces/2002-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2003 | 0.017684692571890363 | 0.01 | `assets/maps/snow/pieces/2003-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2004 | 0.0181562893386269 | 0.01 | `assets/maps/snow/pieces/2004-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2006 | 0.024895245121685915 | 0.01 | `assets/maps/snow/pieces/2006-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2008 | 0.017134195253149624 | 0.01 | `assets/maps/snow/pieces/2008-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2014 | 0.02858869272803699 | 0.01 | `assets/maps/snow/pieces/2014-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2019 | 0.013435021970806607 | 0.01 | `assets/maps/snow/pieces/2019-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2040 | 0.01809802787469448 | 0.01 | `assets/maps/snow/pieces/2040-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2041 | 0.01087278837600079 | 0.01 | `assets/maps/snow/pieces/2041-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2020 | 0.02618095616752811 | 0.01 | `assets/maps/snow/pieces/2020-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2013 | 0.011168220727606237 | 0.01 | `assets/maps/snow/pieces/2013-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2015 | 0.015454106417431323 | 0.01 | `assets/maps/snow/pieces/2015-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2017 | 0.017413285887927846 | 0.01 | `assets/maps/snow/pieces/2017-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2018 | 0.0813176414926962 | 0.01 | `assets/maps/snow/pieces/2018-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2021 | 0.0201915622095627 | 0.01 | `assets/maps/snow/pieces/2021-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2022 | 0.01601125509935838 | 0.01 | `assets/maps/snow/pieces/2022-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2024 | 0.024090406374953917 | 0.01 | `assets/maps/snow/pieces/2024-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2025 | 0.032328539452344894 | 0.01 | `assets/maps/snow/pieces/2025-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2026 | 0.09009807814701387 | 0.01 | `assets/maps/snow/pieces/2026-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2027 | 0.016289056715533837 | 0.01 | `assets/maps/snow/pieces/2027-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2028 | 0.14886460722154773 | 0.01 | `assets/maps/snow/pieces/2028-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2029 | 0.032099137623267514 | 0.01 | `assets/maps/snow/pieces/2029-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2030 | 0.04435788897651736 | 0.01 | `assets/maps/snow/pieces/2030-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2031 | 0.03031705623698218 | 0.01 | `assets/maps/snow/pieces/2031-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2038 | 0.022531689018559835 | 0.01 | `assets/maps/snow/pieces/2038-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2039 | 0.02540202806514391 | 0.01 | `assets/maps/snow/pieces/2039-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2042 | 0.021956058490704682 | 0.01 | `assets/maps/snow/pieces/2042-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2043 | 0.013175811171463797 | 0.01 | `assets/maps/snow/pieces/2043-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2044 | 0.013888061627653027 | 0.01 | `assets/maps/snow/pieces/2044-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2046 | 0.052585206831231 | 0.01 | `assets/maps/snow/pieces/2046-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2047 | 0.035172259221311473 | 0.01 | `assets/maps/snow/pieces/2047-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2048 | 0.017722163474718992 | 0.01 | `assets/maps/snow/pieces/2048-snow-v1.png` |
| crop.dropped_alpha_positive_fraction | 2049 | 0.034586492015196056 | 0.01 | `assets/maps/snow/pieces/2049-snow-v1.png` |
| visible.aspect_relative_difference | 2001 | 0.06849315068493156 | 0.05 | `assets/maps/snow/pieces/2001-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2001 | 640 | 0 | `assets/maps/snow/pieces/2001-snow-v1.png` |
| visible.aspect_relative_difference | 2002 | 0.09335867620751337 | 0.05 | `assets/maps/snow/pieces/2002-snow-v1.png` |
| visible.aspect_relative_difference | 2004 | 0.09521943573667713 | 0.05 | `assets/maps/snow/pieces/2004-snow-v1.png` |
| visible.aspect_relative_difference | 2005 | 0.18181818181818188 | 0.05 | `assets/maps/snow/pieces/2005-snow-v1.png` |
| visible.aspect_relative_difference | 2006 | 0.05591291439881252 | 0.05 | `assets/maps/snow/pieces/2006-snow-v1.png` |
| visible.aspect_relative_difference | 2007 | 0.05882352941176494 | 0.05 | `assets/maps/snow/pieces/2007-snow-v1.png` |
| visible.aspect_relative_difference | 2008 | 0.08608321377331418 | 0.05 | `assets/maps/snow/pieces/2008-snow-v1.png` |
| visible.aspect_relative_difference | 2011 | 0.1549586776859504 | 0.05 | `assets/maps/snow/pieces/2011-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2013 | 640 | 0 | `assets/maps/snow/pieces/2013-snow-v1.png` |
| visible.aspect_relative_difference | 2015 | 0.08897876643073821 | 0.05 | `assets/maps/snow/pieces/2015-snow-v1.png` |
| visible.aspect_relative_difference | 2016 | 0.1470588235294117 | 0.05 | `assets/maps/snow/pieces/2016-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2017 | 640 | 0 | `assets/maps/snow/pieces/2017-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2018 | 640 | 0 | `assets/maps/snow/pieces/2018-snow-v1.png` |
| visible.aspect_relative_difference | 2019 | 0.1394557823129252 | 0.05 | `assets/maps/snow/pieces/2019-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2020 | 1280 | 0 | `assets/maps/snow/pieces/2020-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2021 | 1280 | 0 | `assets/maps/snow/pieces/2021-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2022 | 1280 | 0 | `assets/maps/snow/pieces/2022-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2023 | 1280 | 0 | `assets/maps/snow/pieces/2023-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2024 | 640 | 0 | `assets/maps/snow/pieces/2024-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2025 | 640 | 0 | `assets/maps/snow/pieces/2025-snow-v1.png` |
| visible.aspect_relative_difference | 2026 | 0.10489510489510478 | 0.05 | `assets/maps/snow/pieces/2026-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2026 | 960 | 0 | `assets/maps/snow/pieces/2026-snow-v1.png` |
| visible.aspect_relative_difference | 2027 | 0.060317460317460325 | 0.05 | `assets/maps/snow/pieces/2027-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2027 | 960 | 0 | `assets/maps/snow/pieces/2027-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2028 | 638 | 0 | `assets/maps/snow/pieces/2028-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2029 | 640 | 0 | `assets/maps/snow/pieces/2029-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2030 | 640 | 0 | `assets/maps/snow/pieces/2030-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2031 | 640 | 0 | `assets/maps/snow/pieces/2031-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2032 | 640 | 0 | `assets/maps/snow/pieces/2032-snow-v1.png` |
| visible.aspect_relative_difference | 2033 | 0.069620253164557 | 0.05 | `assets/maps/snow/pieces/2033-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2033 | 640 | 0 | `assets/maps/snow/pieces/2033-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2034 | 640 | 0 | `assets/maps/snow/pieces/2034-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2035 | 640 | 0 | `assets/maps/snow/pieces/2035-snow-v1.png` |
| visible.aspect_relative_difference | 2036 | 0.07006369426751591 | 0.05 | `assets/maps/snow/pieces/2036-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2036 | 640 | 0 | `assets/maps/snow/pieces/2036-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2037 | 640 | 0 | `assets/maps/snow/pieces/2037-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2038 | 1280 | 0 | `assets/maps/snow/pieces/2038-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2039 | 640 | 0 | `assets/maps/snow/pieces/2039-snow-v1.png` |
| visible.aspect_relative_difference | 2040 | 0.09855334538878835 | 0.05 | `assets/maps/snow/pieces/2040-snow-v1.png` |
| visible.aspect_relative_difference | 2041 | 0.22799295774647899 | 0.05 | `assets/maps/snow/pieces/2041-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2042 | 1280 | 0 | `assets/maps/snow/pieces/2042-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2043 | 1280 | 0 | `assets/maps/snow/pieces/2043-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2044 | 1280 | 0 | `assets/maps/snow/pieces/2044-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2045 | 1280 | 0 | `assets/maps/snow/pieces/2045-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2046 | 640 | 0 | `assets/maps/snow/pieces/2046-snow-v1.png` |
| visible.aspect_relative_difference | 2047 | 0.08441558441558439 | 0.05 | `assets/maps/snow/pieces/2047-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2047 | 640 | 0 | `assets/maps/snow/pieces/2047-snow-v1.png` |
| visible.aspect_relative_difference | 2048 | 0.2661290322580645 | 0.05 | `assets/maps/snow/pieces/2048-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2048 | 960 | 0 | `assets/maps/snow/pieces/2048-snow-v1.png` |
| terrain.transparent_outer_edge_pixels | 2049 | 960 | 0 | `assets/maps/snow/pieces/2049-snow-v1.png` |

当前技术核验只证明文件可读、SHA 正确、画布及规则元数据保留。原版文件身份、ID 查找、细分轮廓、建筑入口、纹理遮挡、无缝、碰撞与实机视觉仍未通过。角色与其他地图族不在本目录的修改范围。

## 诊断与边界

doctor.json 保留本任务依赖诊断，host_image 可用。Bundled Python 的 path／scipy／stdout／files 项为 WARN，resvg、FFmpeg、API keys 和 Grok 为 MISSING；本任务仅作 PNG 素材与内置生成，不安装这些无关依赖、不验证收费路线。没有运行视频或 SVG 生图。
