# 20个社区逻辑槽位与自有外观的独立分配

2026-10-28。这里只写本项目外观分配候选，不改src、全局manifest、Git或玩法参数。20是固定社区v1.3.4配置的具体范围，不是腾讯全部历史角色总数。

证据：固定ZIP见references/qqtang-map-data/README.md；本轮不在重型资源冻结时重算288MB包。role-rules.json为401字节、SHA256 `8f9c6e0f005b96791b3f3eef463ffac4da959248f2020dda31f0488565331963`。normal共14个ID，竞技随机额外2个，紫钻4个；随机23不计独立人物。该配置是社区规则，尚未证明每个受限ID均在同一UI直接可选。

player.py经有界AST只读赋值解析：25个playerCfg ID；109份编号INI共23179字节（含3614字节player.py）只有动作/分层资源引用。动作枚举1stand、2trigger、3sit、4walk、5ride、6die、7freeze、8cry、9jump、10win；playerCfg的300保留为未解释原字段，不当速度/帧率。INI另有lose/wait，不按相似名字擅自合并。

小配置、GameCFG、avatarforge、propdescrip、DealProp2、itemCFG/commodityCFG未给出完整ID→旧名/基础表；旧名仍null。根另取得固定commit的combat.go，本工通过GitHub连接器实际读取，并对固定ZIP Client.exe静态读PE头16KB和数据576字节，20/20行XOR0x1234后与六值表逐值一致。数据SHA256 `e509c932687b37dad63b6e3cc3926a3e267617215a75a54bb151c9815106eda9`；VA0x7f2680、RVA0x3f2680、文件offset4138624。见native-role-table-static-evidence.json。未执行/提取/编译/反编译客户端；六字段语义来自固定Go声明，未独立验证FUN使用/真实速度换算/官方原始身份。

adventure-rules中的speed是怪物条目线索，不能挪作人物属性。player_z.cfg含NUL为二进制，不解析其值。原始数据行12/17/23即使存在数字，也不能据此越过role-rules变成可玩角色。

object/body/dir.txt实际列20个.img文件名（默认body1/2及51001等stand/walk，另自列dir.txt一行）；这与根此前object.idx的body类目22条不是同一统计。109个INI、25个playerCfg和body资源文件都是不同类目，不能任一个当可选角色分母。动作资源链本轮证据止于INI引用的类别/ID；未解码pkg，不宣称图像、方向、帧数和实际选择已验收。

现存15个master均已实际查看；11候选通过单图查看原4096 PNG、显示1600预览，主4位之前已查看运行身份图。未批量做新像素QA/拼接。4096是历史兼容导出画布，非已确认原生4K；源记录缺口保留。既有9条历史缺失路径没有恢复。

下表数字→自有形象是本项目新分配，不代表识别出了腾讯旧名。主4位原string别名(maomao/asha/wukong/titan)只记录现有兼容入口；本轮没有静态证据把这些字符串与数字ID绑定，不迁移其旧试稿属性。根后续负责运行兼容。

|源ID/当前社区组|自有展示名/身份|现存master或新设计|实看/设计差异|
|---|---|---|---|
|9 / normal|道童 / daoist-child|assets/characters/daoist-child.png|金发带侧结、棕色刺发、杏眼、玉绿短袍；左葫芦右空手，短裤圆靴|
|22 / normal|月影 / moon-shadow|assets/characters/moon-shadow.png|银灰短bob/呆毛、紫眼、左月花饰、深蓝围巾、双弯刃，开放C形月扣|
|1 / normal|山岳 / mountain-guardian|assets/characters/mountain-guardian.png|棕小髻、浅玉带、木珠、金玉短甲；右环杖左圆盾，体态较敦实|
|2 / normal|莲花 / lotus-healer|assets/characters/lotus-healer.png|棕髻长发、左莲饰/额链、粉白长袖；右莲灯左药瓶，圆润幼脸|
|3 / normal|冰剑 / 01_ice_sword_girl|assets/characters/roster-candidates/01_ice_sword_girl/master.png|深棕高髻长发、蓝灰圆眼、蓝白裙；右冰剑左蓝符，长裙扇形轮廓|
|4 / normal|火符 / 02_fire_talisman_boy|assets/characters/roster-candidates/02_fire_talisman_boy/master.png|棕马尾、粗眉杏眼、红金黑袍；右扇形火符左铜铃，笑脸近雷法/炼丹|
|5 / normal|天音 / 05_celestial_musician_girl|assets/characters/roster-candidates/05_celestial_musician_girl/master.png|紫高髻长发/紫眼/莲冠；双手斜抱长琴，紫白袍和长飘带，脸型近冰剑|
|6 / normal|雷法 / 06_thunder_caster_boy|assets/characters/roster-candidates/06_thunder_caster_boy/master.png|棕短髻、太极额饰、金黄白深蓝袍；右金法器左黄符，眼眉近火符|
|7 / normal|炼丹 / 08_alchemy_prodigy_boy|assets/characters/roster-candidates/08_alchemy_prodigy_boy/master.png|棕短髻杏眼、橙金玉绿袍；右小炉左瓶、背药卷篓，幼脸近火符/雷法|
|8 / normal|竹弓 / 09_bamboo_archer_girl|assets/characters/roster-candidates/09_bamboo_archer_girl/master.png|深棕高马尾/绿眼/叶饰，绿白短装；右持竹弓左拉箭，背筒，宽弓剪影|
|18 / normal|赤枪 / 10_crimson_spear_girl|assets/characters/roster-candidates/10_crimson_spear_girl/master.png|棕双髻长双尾、琥珀眼、红金白裙甲；双手斜长枪和红绸，抬腿仅静画姿|
|19 / normal|唤雪 / 14_short_hair_snow_summoner_girl|assets/characters/roster-candidates/14_short_hair_snow_summoner_girl/master.png|银白短发狐耳紫眼、雪花左饰、白紫毛领；右雪晶左抱白狐，区别月影|
|20 / normal|水龙 / 15_water_dragon_scholar_boy|assets/characters/roster-candidates/15_water_dragon_scholar_boy/master.png|深蓝短髻蓝眼、蓝白长袍/玉佩；右水龙折扇左空掌，纵长袍轮廓|
|21 / normal|灵篆 / 17_ghost_script_calligrapher_boy|assets/characters/roster-candidates/17_ghost_script_calligrapher_boy/master.png|棕髻杏眼青额印、黑金青绿袍；右大笔左空卷、两青灵，闭口笑|
|10 / competitive_random_extra|星阵 / 20_star_formation_master_girl|assets/characters/roster-candidates/20_star_formation_master_girl/master.png|棕高髻/琥珀眼/红星冠，黑金红袍；右星盘左三星牌，牌盘外扩|
|11 / competitive_random_extra|玄龟 / cloud-tortoise-warden|assets/characters/motion-generated/roster-expansion/cloud-tortoise-warden/master.png|新作实看：宽方圆脸/小杏眼/暖棕肤、短黑低髻、敦实玉绿短袍，右竹节拍板左龟纹牌；不沿用旧缺失玉拳身份|
|13 / purple_diamond|松翁 / pine-cloud-elder|assets/characters/motion-generated/roster-expansion/pine-cloud-elder/master.png|新作实看：白眉白须、窄长慈祥老者脸、低白髻/松簪，米白玉绿道袍，右竹杖左拂尘，Q版短身|
|14 / purple_diamond|玉匠 / jade-craft-artisan|assets/characters/motion-generated/roster-expansion/jade-craft-artisan/master.png|新作实看：黑齐刘海bob/两侧小辫、雀斑方圆脸/橄榄杏眼，玉绿米白工坊围裙，右小玉锤左云纹玉料，无技能含义|
|15 / purple_diamond|纸鸢 / paper-kite-wanderer|assets/characters/motion-generated/roster-expansion/paper-kite-wanderer/master.png|新作实看：青黑低双辫、暖榛眼、宽圆竹笠、青米短袍，右线拐左折纸鸢；脸形仍偏幼圆，宽帽剪影明显，无飞行技能|
|16 / purple_diamond|赤砂 / cinnabar-seal-keeper|assets/characters/motion-generated/roster-expansion/cinnabar-seal-keeper/master.png|新作实看：成年感细长铜眼/雀斑、赤褐短卷发/玉发带、赤砂围腰/米白玉绿衣，右方印左云印样纸；顶发余量待alpha核验|

独立完整数据：roster-skin-mapping-20261028.json。原始文本解析证据：roster-player-static-evidence.json，读取器roster-static-evidence.py仅zipfile/configparser/有界AST字面量，未import/exec/eval包内代码，未下载代码或运行客户端。

五位新作原生均1254×1254、使用内置image_gen且实际model/quality未披露为null；没有放大成4096或替旧缺失图恢复。它们强调脸型/年龄/发型/器物/体态差异，但透明彩边、边界余量、全阵容对照和运行验收仍pending。器物只定义外观，不生成新技能或修改来源六属性。当前20是静态身份候选齐备，不是20人全动作/运行验收通过。

## 已核实的来源六数值

字段顺序：容量/容量上限/威力/威力上限/速度档/速度档上限。保持原值，不当作像素/秒。

|源ID|六数值|独立PE比较|
|---|---|---|
|9|2 / 6 / 3 / 7 / 5 / 8|matched|
|22|2 / 6 / 3 / 7 / 5 / 8|matched|
|1|2 / 6 / 2 / 8 / 4 / 7|matched|
|2|2 / 6 / 3 / 9 / 4 / 6|matched|
|3|1 / 5 / 2 / 9 / 5 / 7|matched|
|4|1 / 7 / 3 / 9 / 4 / 7|matched|
|5|2 / 7 / 3 / 8 / 3 / 7|matched|
|6|1 / 6 / 2 / 7 / 5 / 8|matched|
|7|1 / 8 / 3 / 9 / 3 / 8|matched|
|8|1 / 7 / 2 / 6 / 5 / 8|matched|
|18|1 / 6 / 1 / 6 / 5 / 8|matched|
|19|2 / 8 / 1 / 6 / 4 / 7|matched|
|20|2 / 6 / 1 / 5 / 4 / 6|matched|
|21|2 / 8 / 1 / 5 / 3 / 6|matched|
|10|3 / 8 / 4 / 9 / 5 / 8|matched|
|11|3 / 8 / 4 / 9 / 5 / 8|matched|
|13|2 / 8 / 3 / 7 / 4 / 6|matched|
|14|1 / 7 / 2 / 6 / 5 / 8|matched|
|15|2 / 7 / 3 / 9 / 4 / 8|matched|
|16|1 / 8 / 3 / 9 / 4 / 8|matched|

## 另列额外完整模型（用途未核实）

固定known.go把24–36标为full-model entity identities；本工实际读取固定commit，另与对应player24..36.ini的cloth引用一致性比对。详见additional-full-models-static-evidence.json。这13个仅确认额外完整模型、生产用途未核实；此前称变身候选是分类错误，已纠正。它们不是20常规/受限候选槽位，不能据其有完整模型就当作临时变身。真正scene→avatar变身映射见transformations/source-scene-catalog-evidence.json与独立manifest。
