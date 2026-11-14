# 原生 UI 接入及接续画稿

2026-11-13 开始，接续至 2026-11-14。用户的交付入口已明确为下载目录中的 QQTang-Local 原生客户端。首批已安装 25 个原生 UI 资源、51 个状态位置，包含登录、选区、大厅、房间、商城、设置和对局侧栏的底板及部分控件。安装后重新读取松散文件并解出包内资源，逐字节核对通过。全部界面与整款美术继续待完成。 [原生 UI 交付与恢复](NATIVE_CLIENT_UI_DELIVERY_20261113.md)

| 接续画稿 | 当前实物 | 审核入口 |
| --- | --- | --- |
| 月影步行 | 北、西、南三个方向，共 18 个源位置、17 张独立透明图，结合已有东向形成四向候选 | [北向](../assets/characters/motion-continuation-20261113/moon-shadow-north/review-light-dark.png) · [西向](../assets/characters/motion-continuation-20261113/moon-shadow-west/review-light-dark.png) · [南向](../assets/characters/motion-continuation-20261113/moon-shadow-south/review-light-dark.png) |
| 山岳步行 | 西、北各六个源位置，共 11 张独立透明图 | [西向](../assets/characters/motion-continuation-20261113/mountain-guardian-west/review-light-dark.png) · [北向](../assets/characters/motion-continuation-20261113/mountain-guardian-north/review-light-dark.png) |
| 丹羽凤翼 | 九张独立原创图覆盖 stand／walk 各 16 个源位置，保留双翼中空与底部相接 | [浅底对照](../assets/items/wing-adornments/world-147/contact-light.png) · [深底对照](../assets/items/wing-adornments/world-147/contact-jade.png) |
| 玉龙迎云 | 六张入场图逐一对应源位置，另有一张库存图 | [源图及小屏对照](../assets/items/entry-effects/world-1658/contact-source-candidate-mobile.png) |
| 衣饰库存 | 六款法袍、武衣及甲胄，对应 1194／1195／1196／1197／1453／1460 | [32／48／64 像素预览](../assets/items/clothing-adornments/dragon-guard-a/contact-mobile-32-48-64.png) |
| 地图动态 | 四组直轨铁网、三组灯火以及三组法器，共补 68 个源位置 | [铁网](MAP_STRAIGHT_GRATE_ANIMATION_REVIEW_20261113.md) · [灯火](MAP_RITUAL_LIGHTS_ANIMATION_REVIEW_20261113.md) · [法器](MAP_ACTIVE_PROPS_ANIMATION_REVIEW_20261113.md) |
| 探险试稿怪物 | 初芽团精与灵芝盘翁各六个原创姿态，提供待机、两种踏步、蓄势、挥杖和受击画稿 | [初芽团精](../assets/maps/exploration/creatures/draft-motion-20261113/sprout-contact.png) · [灵芝盘翁](../assets/maps/exploration/creatures/draft-motion-20261113/lingzhi-contact.png) |

这些接续 PNG 已加入项目 HTTP 美术检查页，原生格式安装仍需按各自实际引用继续推进。人物衣摆、抬脚、持刃及盾杖衔接，凤翼挂点和遮挡，入场触发，地图动态时序和整图拼接均待核验。六款衣饰在小尺寸下的区分和深玉底对比也待人工确认。山岳南向返回了两张带白底的母图，未导出合格透明帧，状态保留为失败。 [山岳南向记录](../assets/characters/motion-continuation-20261113/mountain-guardian-south/README.md)

探险姿态延续两种自有静态身份。初芽团精首稿挥杖换错手，单独修正后采用同手挥杖。六姿态目前用于审图。项目 HTTP 对局的营救事件另接上下云弧，采用本地选定的 320 毫秒提示时长，原版时长待证。该事件表现需在人工对局中继续核对。

物品候选覆盖 584／2,945 个源 ID，仍有 2,361 个缺图。地图多帧候选覆盖 38／45 个定义、202 个源位置，尚缺 16005 和 17024–17029 七组。角色、装扮及地图画稿的生产数量与原生安装范围分别记在清单中，完整游戏继续待完成。 [本轮机器清单](ART_PROGRESS_20261113B.json)
