# 97实体动作与方向资源合同

2026-10-28。97个源实体均有独立原创静态首稿；**原生模型映射、动作映射、方向顺序和播放时序均未确认，动作帧0，完整实体美术未完成**。本合同为完整缺项清单，不把未知值补成通用四向六帧。

源ID来自`npc_drop_groups.boss_id`，不同于道具`item_id`、玩家`player`和角色`avatar`。现有完整战斗组只提供count/health/damage/defense/speed/is_boss及掉落池，没有图像或动作字段。30087保留逐地图混合分类。

仅读取两份小INI和六个明确选定DIMG的40字节头，使用缓存object.idx的固定包偏移有界解压；没有解码像素、遍历帧体、验证整个DIMG容器或重哈希大ZIP/包。每资源记录原始与压缩数据SHA、头SHA、路径、偏移、声明帧数/方向数。来源是社区修订客户端，腾讯原始官方真实性仍未确认。

| 未绑定样本 | 头声明总帧 | 头声明方向 | 每方向声明帧 |
|---|---:|---:|---:|
| `object\cloth\cloth16701_stand.img` | 6 | 1 | 6 |
| `object\cloth\cloth16701_walk.img` | 24 | 4 | 6 |
| `object\cloth\cloth16701_die.img` | 9 | 1 | 9 |
| `object\cloth\cloth17301_stand.img` | 6 | 1 | 6 |
| `object\cloth\cloth17301_walk.img` | 24 | 4 | 6 |
| `object\cloth\cloth17301_die.img` | 8 | 1 | 8 |

这些样本由player67/73的cloth层关联选出，**未绑定任何97实体**。player73的cry原值173701按原文保留，没有纠正为17301。INI列出的trigger/win/cry/lose/wait不能仅凭同一cloth编号认定对应动作文件存在，更不能作为NPC动作合同。DIMG头没有原生每帧时长，GM示例100ms也不作为客户端时序。方向索引的东南西北顺序、镜像策略和根点不猜。

每个实体的JSON条目分别保留地图、分类、静态当前路径和动作缺项。交付目标命名模板为`motion/<ID>/<已证实动作>/<已证实方向>/NN.png`，目前未创建假帧。需先取得ID→模型/图层、模型→动作文件、状态→播放调用及原生方向/时序/偏移证据，再确定逐ID帧预算和制作。

动作候选类别为站立/移动、已证实战斗前摇/反应、已证实离场，以及有实际规则依据的Boss特殊状态；它们是待确认交付项，不是新玩法或已验证源动作名。不得以静态图平移/旋转、无关玩家动作或自定三波怪代替全集。

固定来源与哈希见`six-header-evidence.json`及六份`.header.json`；完整97行见`entity-motion-contract.json`。本轮未构建、未运行客户端、未做全族图像QA，重型作业暂停仍有效。
