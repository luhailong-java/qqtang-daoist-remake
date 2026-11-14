# 原生头饰世界帧安装计划

2026-11-14（America/New_York）。只读核对固定 QQTang-Local ZIP、用户提供目录及现有自有世界帧。39、114、407、2000 和 408 的 stand／walk 共十个路径均为松散文件，固定 ZIP 和用户当前 object.idx 均无这些路径的包内条目。用户目录的十个 IMG 全部与固定源逐字节一致，可组织为独立的十文件松散资源安装批。 [逐资源哈希、尺寸与编码试验](native-head-world-install-plan-20261114.json)

| 物品 | 原生路径的文件名，目录均为 object/thadorn | 每状态原位置 | 独立自有 PNG |
| --- | --- | ---: | ---: |
| 39 云玩珍藏篮 | thadorn11_stand.img / thadorn11_walk.img | 24 | 20 |
| 114 绯霞纱花环 | thadorn34_stand.img / thadorn34_walk.img | 24 | 20 |
| 407 霞角鹿灵 | thadorn41_stand.img / thadorn41_walk.img | 24 | 18 |
| 2000 五心祈愿 | thadorn65_stand.img / thadorn65_walk.img | 24 | 24 |
| 408 绯耳灵伴 | thadorn40_stand.img / thadorn40_walk.img | 24 | 12 |

五件的源 stand／walk 各自字节相同，现有 94 张独立自有 PNG 通过原位置别名覆盖十个资源的 240 个位置。每个源位置的 density4 PNG 宽高恰为原帧四倍，logicalFrameSize 与原帧宽高吻合，frameOffsetRaw 逐项吻合。源 IMG 及现有画稿合同的 SHA-256 均相同。

规划检查在内存中进行预乘 Alpha 的 0.25 等比 LANCZOS 降采样，并用现有原生编码器替换像素平面。十个资源的完整原帧集合均能编码为 RGB565／Alpha32。编码后，版本、声明画布、方向数、未知头字段、帧数、原顺序、宽高、偏移、模式和字节长度均保持。计划 JSON 保存每个内存输出的摘要。随后已完成独立的原生候选导出，详见[世界头饰导出批](../assets/native-client-heads/world-v1/README.md)。

后续转换器可按现有安装器的 loose-only 清单约定输出这十个文件，并保留逐帧自有 PNG、别名和原图来源。主窗口完成临时目录的安装、重复执行和恢复核验后，统一处理用户目录安装。原时长、角色头挂点、图层遮挡和小尺寸视觉继续待人工确认，当前仍为候选。

输入画稿清单如下。

- [39](../assets/items/head-adornments/world-39-art.json)
- [114](../assets/items/head-adornments/world-114-art.json)
- [407](../assets/items/head-adornments/world-407-art.json)
- [2000](../assets/items/head-adornments/world-2000-art.json)
- [408](../assets/items/head-adornments/world-408-art.json)
