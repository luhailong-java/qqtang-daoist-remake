# 原生房间剩余图像候选

本组已导出锁定清单中的全部 **115件 IMG、159个原生状态位置**。包括18组角色提示半身插画/名牌、20个已确证项目角色头像、17个独立新画像、随机头像、属性单位/面板、房间控件、键盘说明、17类地图筛选及8个队色状态。未运行原客户端、未安装用户目录、未操作Git；本组画面与运行仍待验，不代表世界人物/怪物动作、时序、挂点、手游或整款美术完成。

- [全部原生状态](candidate/contact-native.png)
- [37个身份的原生头像](candidate/role-icons-native.png) · [额外画像的深玉/米白底诊断](candidate/extra-icon-edge-diagnostic.png)
- [恢复源逻辑偏移的半身插画](candidate/role-busts-native.png) · [主要面板](candidate/panels-native.png)
- [来源合同](manifest.json) · [原生候选清单](candidate-manifest.json)
- [20角色映射说明](README-roster-mapping.md) · [映射合同](roster-mapping-audit.json)
- [额外画像命名空间证据](extra-icon-source-semantics.json) · [字色核验](palette-evidence.json) · [头像注册/边缘核验](portrait-evidence.json)

源为固定 `QQTang-Local-v1.3.4.zip` 的 `object.pkg`，归档SHA为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。每个原IMG、包目录项、压缩/解压SHA、完整头、每态尺寸/模式/偏移和源UI声明均保留。`uiMain/uiRoom/uiShop/uiGame` 等常量均作为惰性数据读取，没有导入、执行原字节码或构造CodeType。

18个房间/商城别名通过原生 `RoleNameList/RoleIDList` 的平行位置和商城索引配对，另由PVE元组确证 `cbz=10`、`xz=11`，合计20个角色均使用各自现有形象。20张UI输入按已有头像清单中实际选过的头发/脸/衣领ROI，从原自有master直接预乘Alpha缩至512画布，未放大256头像冒充高清。裁框、放置、缩放、原画和已有来源记录见 [派生合同](owned-portrait-derivations.json)。这些是UI半身/肖像，不是世界动作新帧。

额外15个数字图标由 `PVEBossInfo.m_iImageID` 选取，`xxm/zjl` 未在13份UI常量树取得角色绑定。相同数字的玩家INI、旧骷髅占位像素相同以及已有变身master，均不能单独证明实体别名。故17条路径各自生成独立原创UI画像，不把同一张脸重复填满缺口；画像内部项目名用于素材管理，不声称是已恢复的原NPC名或世界模型绑定。

17张新原图均通过宿主内置 `image_gen` 实际返回，原生为 `1254×1254 RGBA`，各自原图SHA和最终原生额外头像SHA均互不相同。逐张保留完整实际提示词、两个指定风格参考的SHA、工具返回提示/实际路径、时间、原生尺寸、PNG哈希及配置快照。实际内置model/quality未披露，提交及返回值均为 `null`，不将配置目标当成已锁定型号；没有调用收费API或CLI。

| 原生后缀 | 独立项目UI画像 | 实际原图 / 逐图记录 |
|---|---|---|
| 67 | 玉墨面师 | [图](extra-icons/icon-67-master.png) · [记录](extra-icons/icon-67-master.png.generation.json) |
| 69 | 苔盏灵蛙 | [图](extra-icons/icon-69-master.png) · [记录](extra-icons/icon-69-master.png.generation.json) |
| 72 | 青崖甲卫 | [图](extra-icons/icon-72-master.png) · [记录](extra-icons/icon-72-master.png.generation.json) |
| 73 | 铜铃渡客 | [图](extra-icons/icon-73-master.png) · [记录](extra-icons/icon-73-master.png.generation.json) |
| 75 | 松潮长髯 | [图](extra-icons/icon-75-master.png) · [记录](extra-icons/icon-75-master.png.generation.json) |
| 77 | 瓷骨灯灵 | [图](extra-icons/icon-77-master.png) · [记录](extra-icons/icon-77-master.png.generation.json) |
| 78 | 朱炉卜者 | [图](extra-icons/icon-78-master.png) · [记录](extra-icons/icon-78-master.png.generation.json) |
| 79 | 赤陶面灵 | [图](extra-icons/icon-79-master.png) · [记录](extra-icons/icon-79-master.png.generation.json) |
| 81 | 雪玉鸮灵 | [图](extra-icons/icon-81-master.png) · [记录](extra-icons/icon-81-master.png.generation.json) |
| 85 | 夜云守星 | [图](extra-icons/icon-85-master.png) · [记录](extra-icons/icon-85-master.png.generation.json) |
| 117 | 月瓣小仙 | [图](extra-icons/icon-117-master.png) · [记录](extra-icons/icon-117-master.png.generation.json) |
| 118 | 古玉龟卜 | [图](extra-icons/icon-118-master.png) · [记录](extra-icons/icon-118-master.png.generation.json) |
| 119 | 霜晶角灵 | [图](extra-icons/icon-119-master.png) · [记录](extra-icons/icon-119-master.png.generation.json) |
| 124 | 丹岩小狮 | [图](extra-icons/icon-124-master.png) · [记录](extra-icons/icon-124-master.png.generation.json) |
| 125 | 桂金鹏灵 | [图](extra-icons/icon-125-master.png) · [记录](extra-icons/icon-125-master.png.generation.json) |
| xxm | 竹叶符使 | [图](extra-icons/icon-xxm-master.png) · [记录](extra-icons/icon-xxm-master.png.generation.json) |
| zjl | 朱仪仙翁 | [图](extra-icons/icon-zjl-master.png) · [记录](extra-icons/icon-zjl-master.png.generation.json) |

原生编码及透明处理：

- 每件文件只替换原像素平面，完整验证所有非像素字节和长度原样保留；原DIMG模式、帧数、空位结构、rawoffset与每态尺寸不变。115件均有 `nonPixelBytesIdentical=true` 及非像素SHA。
- 110态功能Alpha在最终原生回读后逐字节等于来源。头像卡片内部实际核实为全不透明面，保留的是外层功能轮廓；没有沿用旧人物轮廓。地图按钮文字区也实际核实为Alpha255，替换其RGB不会留下旧字形透明度。
- 其余49态为旧人物半身轮廓、旧角色名、准备/房主/页签/属性文字、装备指示及含旧人物的休息室背景；使用自己的主体、字形和面板Alpha，逐项明列 `alphaPolicy`，不把旧中文字形Alpha涂色后冒充新图。
- 原图可见框按Alpha≥8外扩1px，框外最大Alpha≤7。保持主体RGBA，预乘Alpha等比缩放。头像先在统一55逻辑画布的固定 `(4,4,51,51)` 主体区注册，再按各态原始偏移裁窗；37身份全部窗口裁损为0，不分别缩放造成抖动。
- 17个最终额外原生头像按 `A≥8、G≥150、G-R>80、G-B>80` 的饱和绿阈值计数为0，并提供实际原生卡片的深玉/米白底Alpha合成诊断；没有因PNG是RGBA就宣称边缘已视觉通过。

动态白色玩家名保留深底，并分别检查上排和下排的真实名字坐标。8个队色索引及颜色提示保留为宽左色块与顶部色带，原名字范围使用深玉底，避免黄色等亮队色压住白字。休息室3个公告字段明确为白字；广播发送者的 `broadcastColor=maskColor` 和正文的 `TRichEdit` 黑字继承均有原指令/模板证据，按原0.6背景因子核对合成。共17处最终原生文字采样达到所选4.5对比阈值，运行中的富文本附加颜色、长名和裁切仍待验。

全量复验，在仓库根目录执行：

```powershell
python -B assets/native-client-ui/room-extra-reference/prepare-owned-portraits.py --check
python -B assets/native-client-ui/room-extra-reference/verify-renderer.py
python -B assets/native-client-ui/room-extra-reference/verify-renderer.py --check
python -B assets/native-client-ui/room-extra-reference/check-portraits.py --check
```

`--core-only` 仅为制作期间的98件/142态子集选项，最终交付、统一合包必须使用全量命令。新母图请求及真实返回分见 [请求](extra-icon-generation-requests.json)、[合并工具记录](extra-icon-tool-results.json)；导入器只复制已实际返回的文件，不调用收费接口。

主接入键为 `room-extra`，模块 [native-ui-roomextra-art.py](../../../scripts/native-ui-roomextra-art.py) 声明 `RENDERER_PREFIX='roomextra-'`、`REFERENCE_MANIFEST`、`REFERENCE_INPUTS` 及17项 `ART_GENERATION_RECORDS`，避免与旧 `room-` 模块分派重叠。独立原生文件在 `candidate/patch/object/ui/room/`，须由协调者纳入同一object.pkg事务包；这里没有单独改写用户包。
