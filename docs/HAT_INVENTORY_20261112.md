# cap 冠帽库存制作

本批补充源目录 `cap` 的独立库存候选。该类别有 447 个源 ID，与 `thadorn` 35 件世界头饰及 `eye` 72 件趣味装饰分开。当前七组共有 42 个 ID 的库存候选，其余 405 个尚无本类候选；accepted 和 runtime 均为 0。本记录不构成全类或整款游戏完成声明。

## 云游帽组

原创名依次为绒云暖帽、青岚行旅帽、云羽礼冠、竹纹云笠、桃枝玉环、灵蜂双触帽。源 itemId 与 resourceId 分别保留，不按 itemId 猜资源文件。六件均从 catalog 的 `installed_files` 明确库存图路径读取：cap1／3／4／5／7／8.img。

固定 ZIP 为社区修改后留存样本 `QQTang-Local-v1.3.4.zip`，SHA256 为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`。只用本项目 DIMG 读取器静态读取所选成员，没有运行客户端程序；目标腾讯原始身份和历史版本仍未确认。逐图成员 SHA、原帧、偏移、解码像素及库存 PNG 的证据均位于本批 `references/` 与 `source-contract.json`。源图只作结构参考，不作运行素材。

实际查看六源图板和邮件／组队两张主风格图后，通过宿主内置 `image_gen` 生成一张 1536×1024 RGBA 母图。当前配置目标为 2.6／high，工具没有提供模型／质量选择器或返回身份，实际值均为 null。原始提交参数和提示词从 `functions.store` 直接按 UTF-8 留存并保存哈希，未用 `read_text`／换行归一化重建。此次调用一次返回，没有重试；母图旁的 `.generation.json` 保留实际证据。

羽冠左羽略越名义 x1024 分格线，实际透明分界在 x996，已按该透明间隔分离，保全两个帽子的轮廓；不是拉伸或程序补画。每件使用原生母图切口、预乘 alpha 等比缩小至 256 RGBA、可见边距至少 16px；隐藏 RGB 背景没有被压进不透明底。256 双底与 32／48／64 诊断板均已实际查看，未因此标视觉 PASS。

文件入口：

- [本批清单](../assets/items/hats/cloud-roaming-a/art.json)
- [源与导出技术检查](../assets/items/hats/cloud-roaming-a/technical-qa.json)
- [256 实际尺寸双底](../assets/items/hats/cloud-roaming-a/contact-native-256.png)
- [32／48／64 双底诊断](../assets/items/hats/cloud-roaming-a/contact-mobile-32-48-64.png)
- [本类机器交接](HAT_INVENTORY_20261112.json)

六件均为未接入的静态库存候选，accepted／visualAccepted／runtimeAdopted 均为 false。实际穿戴、头部挂点、四方向、全部动作与原时序尚无完整交付，不能用六张图代替这些项。画风及手游可读性待用户手动审核；没有使用 GUI／CUA，没有操作 Git。

## 晨游礼帽组

第二组 37／38／40／41／43／46 分别新画桃锦绢冠、青羽朝冠、朱风云带冠、晴翎晨冠、绛罗云檐帽、绛玉云冕。已实际查看本组六个明确库存图：原 item40 的红色尖簇轮廓改为独立的朱红绢羽帽物件，不绘制穿戴人物或人物头发；其余保留绢褶、双羽、翼檐、丝带或珠冠等类别结构，采用同一套原创云纹金玉细节。

本组另一次内置生图返回 1536×1024 RGBA，实际 model／quality 仍为 null，没有重试。名义 512 分格边界 alpha 最大 2，六件按完整透明间隔裁出，256 画布和至少 16px 留白检查通过；双底与小尺寸板均实际查看，但视觉接受与穿戴仍待用户审核。

- [本组清单及逐件来源](../assets/items/hats/morning-courtesy-b/art.json)
- [技术检查](../assets/items/hats/morning-courtesy-b/technical-qa.json)
- [256 实际尺寸双底](../assets/items/hats/morning-courtesy-b/contact-native-256.png)
- [32／48／64 双底诊断](../assets/items/hats/morning-courtesy-b/contact-mobile-32-48-64.png)

## 灵兽趣帽组

第三组为 51／58／116／191／253／283：桃云章鱼帽、月绒兔帽、金翎雏冠、霜耳灵狼帽、赤鳞蜥盔、绯云猫耳圈。原 253 库存图包含穿戴头像和蓝色 UI 框，283 也有 UI 框；生成只参考帽体与耳圈结构，新图没有这些人物或 UI，穿戴开口保持透明。

首张 v1 真实 RGBA 的空白分格仍有 alpha10–12 色雾，严格 alpha8 裁切闸门失败，未导出候选。随后实际附入 v1，用内置图像编辑请求清除背景／内部孔洞，返回 v2；新分格最大 alpha0／1，才进行切片。v1 作为 v2 的实际编辑父图保留，两个实际提示词、参数和输出分别留证。不能把编辑请求中的“形状保持”当作实际像素完全相同或自动视觉通过。

选用 v2 导出六张 256 RGBA，检查边距至少 16px，源 SHA／透明／双底小尺寸板已经核对；八触手的可视计数、材质细节和实际穿戴仍由用户审核。三组总计四次内置调用（含本次编辑），只计 18 个候选，不将失败母图或编辑重算为物品。

- [本组清单及来源](../assets/items/hats/spirit-creatures-c/art.json)
- [技术检查](../assets/items/hats/spirit-creatures-c/technical-qa.json)
- [256 实际尺寸双底](../assets/items/hats/spirit-creatures-c/contact-native-256.png)
- [32／48／64 双底诊断](../assets/items/hats/spirit-creatures-c/contact-mobile-32-48-64.png)

## 碗面趣帽组

第四组 155／156／157／158／159／160 仍属于 cap 冠帽，不是 food 消耗品类别。新画海苔云面帽、金玉火腿面帽、玉鲤鲜汤帽、酱香绢面帽、椒香担担面帽、青荷蛙盏帽，分别以海苔、粉白圆片、蓝灰鱼形饰、豆酱宽面、双蛋红碗和玉蛙摆件区分；未新增消耗品作用或其他玩法。

母图一次返回 1536×1024 RGBA，分格最大 alpha1，六件已等比导出 256 RGBA 并查看实际双底与 32／48／64 诊断。材质、食材细节、穿戴是否合适仍待用户审核。当前共五次内置调用，四张选用母图和一个失败后用于编辑的父图，不重复计物品。

- [本组清单](../assets/items/hats/noodle-festival-d/art.json)
- [技术检查](../assets/items/hats/noodle-festival-d/technical-qa.json)
- [256 实际尺寸双底](../assets/items/hats/noodle-festival-d/contact-native-256.png)
- [32／48／64 双底诊断](../assets/items/hats/noodle-festival-d/contact-mobile-32-48-64.png)

## 四组独立复核

[24 件显式批次复核](../assets/items/hats/cloud-roaming-a/verified-four-batches.json)重新读取固定 SHA ZIP 中这 24 个已明确库存成员，核对 catalog 的 category／itemId／resourceId／installed_files、成员 SHA、编码帧 SHA、原 RGBA 解码像素、源 PNG SHA；没有只凭新图文件名认领来源。另对 24 个 256 输出逐像素重放裁切／预乘 alpha 等比缩放／放置，结果完全一致，逐件透明边距满足 16px；五份含编辑父图的生成记录、原参数及提示词字节哈希一致，errors 为空。该检查仅覆盖这 24 件，没有宣称全 447 候选齐备或视觉通过。

## 礼仪探行冠盔组

第五组 83／161／180／193／238／250 新画绛云礼冠、祈安符帽、青墨书冠、玄铁云盔、玉穹探行盔、紫岚云锥帽。保留圆礼冠、垂纸帽、方学帽、铁盔、开口探行盔与弯尖宽檐帽的类别结构；原 161 字符和 238 数字均换为自有非文字云纹，盔内没有人物。

v1 空白分格 alpha10–34，未导出；内置编辑 v2 清理后分格最大 alpha1，才采用。两次实际提交及父图均有记录。六件实际 256 双底与 32／48／64 板已查看，仍是未接受的库存候选。本组收齐时五组共七次内置调用，含 C／E 两次编辑。

- [本组清单](../assets/items/hats/ceremony-journey-e/art.json)
- [仅本组 6 件独立复核](../assets/items/hats/ceremony-journey-e/verified-batch.json)
- [256 实际尺寸双底](../assets/items/hats/ceremony-journey-e/contact-native-256.png)
- [32／48／64 双底诊断](../assets/items/hats/ceremony-journey-e/contact-mobile-32-48-64.png)

第五组新增的来源／重放／透明检查单独执行；前 24 件输入未变，继续引用原固定通过记录，不重复扫描历史图片。两份技术回执合计只覆盖上述 30 个 ID，不替代用户人审。

## 海风节庆帽组

第六组 285／319／404／451／454／1086 新画竹编海风笠、赤帆云帽、绒雪节庆帽、绛潮水手巾、墨羽航海冠、金潮潜行盔。源 319 与 454 都名为海盗帽，但原资源号分别 76／87，新图是不同的红革双角帽和黑羽航海帽，不能合并一个物品。四张源库存的蓝框、454 穿戴头像与 319 原骷髅标记均未画入新物件。

母图一次返回 1536×1024 RGBA，分格最大 alpha2，潜行盔开口中心 alpha0。256 双底与 32／48／64 板已实际查看；独立本组 6 件的原源成员解码、SHA 与输出像素重放通过，errors 为空。六组计八次内置调用，仍只计 36 个候选 ID。

- [本组清单](../assets/items/hats/seaside-festival-f/art.json)
- [仅本组 6 件独立复核](../assets/items/hats/seaside-festival-f/verified-batch.json)
- [256 实际尺寸双底](../assets/items/hats/seaside-festival-f/contact-native-256.png)
- [32／48／64 双底诊断](../assets/items/hats/seaside-festival-f/contact-mobile-32-48-64.png)

## 云游奇帽组

第七组新增 45、84、137、240、280、281 六件库存图。采用实际生成的 V2 母图，V1 提交记录保留。输出为 256×256 RGBA，开口透明，外边留白至少 16 像素。七组合计 42 个源 ID，帽类库存还有 405 个未制作，佩戴与相位待补。 [本组双底预览](../assets/items/hats/cloud-masquerade-g/contact-native-256.png) · [小尺寸预览](../assets/items/hats/cloud-masquerade-g/contact-mobile-32-48-64.png)
