// Text-only evidence and independent appearance allocation; no runtime edits.
import{readFile,writeFile}from'node:fs/promises';
import path from'node:path';
const root=path.resolve(import.meta.dirname,'../../..');
const player=JSON.parse(await readFile(path.join(import.meta.dirname,'roster-player-static-evidence.json'),'utf8'));
const native=JSON.parse(await readFile(path.join(import.meta.dirname,'native-role-table-static-evidence.json'),'utf8'));
const fixed=JSON.parse(await readFile(path.join(import.meta.dirname,'rolecatalog-fixed-source-evidence.json'),'utf8'));
if(native.matchedPlayableRows!==20||native.mismatches.length)throw new Error('Native profile evidence not matched');
const selected=[
 [9,'daoist-child','道童','assets/characters/daoist-child.png','maomao','金发带侧结、棕色刺发、杏眼、玉绿短袍；左葫芦右空手，短裤圆靴'],
 [22,'moon-shadow','月影','assets/characters/moon-shadow.png','asha','银灰短bob/呆毛、紫眼、左月花饰、深蓝围巾、双弯刃，开放C形月扣'],
 [1,'mountain-guardian','山岳','assets/characters/mountain-guardian.png','wukong','棕小髻、浅玉带、木珠、金玉短甲；右环杖左圆盾，体态较敦实'],
 [2,'lotus-healer','莲花','assets/characters/lotus-healer.png','titan','棕髻长发、左莲饰/额链、粉白长袖；右莲灯左药瓶，圆润幼脸'],
 [3,'01_ice_sword_girl','冰剑','assets/characters/roster-candidates/01_ice_sword_girl/master.png',null,'深棕高髻长发、蓝灰圆眼、蓝白裙；右冰剑左蓝符，长裙扇形轮廓'],
 [4,'02_fire_talisman_boy','火符','assets/characters/roster-candidates/02_fire_talisman_boy/master.png',null,'棕马尾、粗眉杏眼、红金黑袍；右扇形火符左铜铃，笑脸近雷法/炼丹'],
 [5,'05_celestial_musician_girl','天音','assets/characters/roster-candidates/05_celestial_musician_girl/master.png',null,'紫高髻长发/紫眼/莲冠；双手斜抱长琴，紫白袍和长飘带，脸型近冰剑'],
 [6,'06_thunder_caster_boy','雷法','assets/characters/roster-candidates/06_thunder_caster_boy/master.png',null,'棕短髻、太极额饰、金黄白深蓝袍；右金法器左黄符，眼眉近火符'],
 [7,'08_alchemy_prodigy_boy','炼丹','assets/characters/roster-candidates/08_alchemy_prodigy_boy/master.png',null,'棕短髻杏眼、橙金玉绿袍；右小炉左瓶、背药卷篓，幼脸近火符/雷法'],
 [8,'09_bamboo_archer_girl','竹弓','assets/characters/roster-candidates/09_bamboo_archer_girl/master.png',null,'深棕高马尾/绿眼/叶饰，绿白短装；右持竹弓左拉箭，背筒，宽弓剪影'],
 [18,'10_crimson_spear_girl','赤枪','assets/characters/roster-candidates/10_crimson_spear_girl/master.png',null,'棕双髻长双尾、琥珀眼、红金白裙甲；双手斜长枪和红绸，抬腿仅静画姿'],
 [19,'14_short_hair_snow_summoner_girl','唤雪','assets/characters/roster-candidates/14_short_hair_snow_summoner_girl/master.png',null,'银白短发狐耳紫眼、雪花左饰、白紫毛领；右雪晶左抱白狐，区别月影'],
 [20,'15_water_dragon_scholar_boy','水龙','assets/characters/roster-candidates/15_water_dragon_scholar_boy/master.png',null,'深蓝短髻蓝眼、蓝白长袍/玉佩；右水龙折扇左空掌，纵长袍轮廓'],
 [21,'17_ghost_script_calligrapher_boy','灵篆','assets/characters/roster-candidates/17_ghost_script_calligrapher_boy/master.png',null,'棕髻杏眼青额印、黑金青绿袍；右大笔左空卷、两青灵，闭口笑'],
 [10,'20_star_formation_master_girl','星阵','assets/characters/roster-candidates/20_star_formation_master_girl/master.png',null,'棕高髻/琥珀眼/红星冠，黑金红袍；右星盘左三星牌，牌盘外扩'],
 [11,'cloud-tortoise-warden','玄龟','assets/characters/motion-generated/roster-expansion/cloud-tortoise-warden/master.png',null,'新作实看：宽方圆脸/小杏眼/暖棕肤、短黑低髻、敦实玉绿短袍，右竹节拍板左龟纹牌；不沿用旧缺失玉拳身份'],
 [13,'pine-cloud-elder','松翁','assets/characters/motion-generated/roster-expansion/pine-cloud-elder/master.png',null,'新作实看：白眉白须、窄长慈祥老者脸、低白髻/松簪，米白玉绿道袍，右竹杖左拂尘，Q版短身'],
 [14,'jade-craft-artisan','玉匠','assets/characters/motion-generated/roster-expansion/jade-craft-artisan/master.png',null,'新作实看：黑齐刘海bob/两侧小辫、雀斑方圆脸/橄榄杏眼，玉绿米白工坊围裙，右小玉锤左云纹玉料，无技能含义'],
 [15,'paper-kite-wanderer','纸鸢','assets/characters/motion-generated/roster-expansion/paper-kite-wanderer/master.png',null,'新作实看：青黑低双辫、暖榛眼、宽圆竹笠、青米短袍，右线拐左折纸鸢；脸形仍偏幼圆，宽帽剪影明显，无飞行技能'],
 [16,'cinnabar-seal-keeper','赤砂','assets/characters/motion-generated/roster-expansion/cinnabar-seal-keeper/master.png',null,'新作实看：成年感细长铜眼/雀斑、赤褐短卷发/玉发带、赤砂围腰/米白玉绿衣，右方印左云印样纸；顶发余量待alpha核验']
];
const groups={normal:[9,22,1,2,3,4,5,6,7,8,18,19,20,21],competitive_random_extra:[10,11],purple_diamond:[13,14,15,16]};
const slots=[];
for(const[id,identityId,displayName,master,alias,visual]of selected){
 const ini=player.playerIni.find(r=>r.id===id);
 const exists=master!==null;
 const newMaster=master?.includes('/roster-expansion/')??false;
 const row=native.rows.find(r=>r.sourceRoleId===id);
 if(!row||!row.matchesCombatGo)throw new Error('Missing verified profile for '+id);
 const[vCapacity,vMaxCapacity,vPower,vMaxPower,vSpeed,vMaxSpeed]=row.decodedSixValues;
 let sourceRecord=null,sourceSha=null;
 if(master){sourceRecord=newMaster?master+'.generation.json':master.endsWith('/master.png')?master.replace('master.png','source.json'):master+'.source.json';let s=JSON.parse(await readFile(path.resolve(root,sourceRecord),'utf8'));sourceSha=s.sha256??s.sourceSha256??null;}
 slots.push({sourceRoleId:id,sourceGroup:Object.keys(groups).find(g=>groups[g].includes(id)),sourceScope:'current community v1.3.4 role-rules configuration only',legacyName:null,legacyNameStatus:'not obtained from bounded ZIP text evidence',baseAttributes:{capacity:vCapacity,maxCapacity:vMaxCapacity,range:vPower,maxRange:vMaxPower,speed:vSpeed,maxSpeed:vMaxSpeed},attributeStatus:'20/20 six-value numeric rows independently matched fixed combat.go against fixed ZIP Client.exe PE data; gameplay units/function usage not independently verified',sourceNativeProfile:{BombCapacity:vCapacity,MaxBombCapacity:vMaxCapacity,BombPower:vPower,MaxBombPower:vMaxPower,SpeedRate:vSpeed,MaxSpeedRate:vMaxSpeed},attributeEvidence:{record:'assets/characters/motion-generated/native-role-table-static-evidence.json',rowVA:row.va,dataSha256:native.dataSha256,sourceUrl:native.source.url,gitBlobSha:native.source.gitBlobSha,unitCaution:'Native slot/rate values; not pixels per second or current remake movement conversion'},sourcePlayerIni:ini,sourcePlayerPyCfgEntry:player.playerPy.assignments.playerCfg.find(r=>r.id===id)??null,
 appearance:{identityId,displayName,master,sourceRecord,recordedSourceSha256:sourceSha,isNewGeneration:newMaster,status:newMaster?'new_original_master_visually_checked_pending_alpha_client':'existing_master_visually_checked_mapping_candidate',visualObservation:visual,visualCheck:exists?{performed:true,date:'2026-10-28',method:newMaster?'Visually inspected builtin image_gen result; native1254x1254; no alpha/pixel/client QA':master.includes('roster-candidates')?'Single-file view_image; 4096 source displayed1600; no new montage/pixel QA':'Runtime identity master previously individually viewed by this worker'}:{performed:false},runtimeEnabled:false,clientApproved:false},
 existingLocalStringAlias:alias,aliasBridgeStatus:alias?'local implementation appearance alias only; numeric legacy ID bridge NOT established by this evidence':'not applicable',allocationStatus:'project-authored appearance allocation, not recovered Tencent identity or statistics'});
}
const data={schemaVersion:1,createdAt:new Date().toISOString(),source:{archiveSha256:player.expectedArchiveSha256,archiveHashEvidence:player.archiveHashEvidence,roleRulesEntry:'QQTang-Local/configs/role-rules.json',roleRulesBytes:401,roleRulesSha256:'8f9c6e0f005b96791b3f3eef463ffac4da959248f2020dda31f0488565331963',officialOriginalAuthenticity:'unverified',scope:'20 concrete IDs in current community configuration, not all Tencent versions or proof every restricted ID is directly selectable'},runtimeEnabled:false,sourceConcreteRoleCount:20,randomPlaceholder:{sourceRoleId:23,newIdentity:false,meaning:'random placeholder only; do not draw another character'},purpleDiamondIdentityMask:8192,existingOwnMasterCount:15,newOwnMasterCountCreated:5,currentStaticIdentityCandidateCount:20,missingHistoricalArtRestored:false,gameplayRulesChanged:false,sourcePropertiesChanged:false,slots};
await writeFile(path.join(import.meta.dirname,'roster-skin-mapping-20261028.json'),JSON.stringify(data,null,2)+'\n');
const lines=['# 20个社区逻辑槽位与自有外观的独立分配','','2026-10-28。这里只写本项目外观分配候选，不改src、全局manifest、Git或玩法参数。20是固定社区v1.3.4配置的具体范围，不是腾讯全部历史角色总数。','',
'证据：固定ZIP见references/qqtang-map-data/README.md；本轮不在重型资源冻结时重算288MB包。role-rules.json为401字节、SHA256 `8f9c6e0f005b96791b3f3eef463ffac4da959248f2020dda31f0488565331963`。normal共14个ID，竞技随机额外2个，紫钻4个；随机23不计独立人物。该配置是社区规则，尚未证明每个受限ID均在同一UI直接可选。','',
'player.py经有界AST只读赋值解析：25个playerCfg ID；109份编号INI共23179字节（含3614字节player.py）只有动作/分层资源引用。动作枚举1stand、2trigger、3sit、4walk、5ride、6die、7freeze、8cry、9jump、10win；playerCfg的300保留为未解释原字段，不当速度/帧率。INI另有lose/wait，不按相似名字擅自合并。','',
'小配置、GameCFG、avatarforge、propdescrip、DealProp2、itemCFG/commodityCFG未给出完整ID→旧名/基础表；旧名仍null。根另取得固定commit的combat.go，本工通过GitHub连接器实际读取，并对固定ZIP Client.exe静态读PE头16KB和数据576字节，20/20行XOR0x1234后与六值表逐值一致。数据SHA256 `'+native.dataSha256+'`；VA0x7f2680、RVA0x3f2680、文件offset'+native.fileOffset+'。见native-role-table-static-evidence.json。未执行/提取/编译/反编译客户端；六字段语义来自固定Go声明，未独立验证FUN使用/真实速度换算/官方原始身份。','',
'adventure-rules中的speed是怪物条目线索，不能挪作人物属性。player_z.cfg含NUL为二进制，不解析其值。原始数据行12/17/23即使存在数字，也不能据此越过role-rules变成可玩角色。','',
'object/body/dir.txt实际列20个.img文件名（默认body1/2及51001等stand/walk，另自列dir.txt一行）；这与根此前object.idx的body类目22条不是同一统计。109个INI、25个playerCfg和body资源文件都是不同类目，不能任一个当可选角色分母。动作资源链本轮证据止于INI引用的类别/ID；未解码pkg，不宣称图像、方向、帧数和实际选择已验收。','',
'现存15个master均已实际查看；11候选通过单图查看原4096 PNG、显示1600预览，主4位之前已查看运行身份图。未批量做新像素QA/拼接。4096是历史兼容导出画布，非已确认原生4K；源记录缺口保留。既有9条历史缺失路径没有恢复。','',
'下表数字→自有形象是本项目新分配，不代表识别出了腾讯旧名。主4位原string别名(maomao/asha/wukong/titan)只记录现有兼容入口；本轮没有静态证据把这些字符串与数字ID绑定，不迁移其旧试稿属性。根后续负责运行兼容。','',
'|源ID/当前社区组|自有展示名/身份|现存master或新设计|实看/设计差异|','|---|---|---|---|',...slots.map(s=>`|${s.sourceRoleId} / ${s.sourceGroup}|${s.appearance.displayName} / ${s.appearance.identityId}|${s.appearance.master??'待新作'}|${s.appearance.visualObservation}|`),'',
'独立完整数据：roster-skin-mapping-20261028.json。原始文本解析证据：roster-player-static-evidence.json，读取器roster-static-evidence.py仅zipfile/configparser/有界AST字面量，未import/exec/eval包内代码，未下载代码或运行客户端。','',
'五位新作原生均1254×1254、使用内置image_gen且实际model/quality未披露为null；没有放大成4096或替旧缺失图恢复。它们强调脸型/年龄/发型/器物/体态差异，但透明彩边、边界余量、全阵容对照和运行验收仍pending。器物只定义外观，不生成新技能或修改来源六属性。当前20是静态身份候选齐备，不是20人全动作/运行验收通过。','',
'## 已核实的来源六数值','',
'字段顺序：容量/容量上限/威力/威力上限/速度档/速度档上限。保持原值，不当作像素/秒。','',
'|源ID|六数值|独立PE比较|','|---|---|---|',...slots.map(s=>`|${s.sourceRoleId}|${Object.values(s.sourceNativeProfile).join(' / ')}|matched|`),'',
'## 另列额外完整模型（用途未核实）','',
'固定known.go把24–36标为full-model entity identities；本工实际读取固定commit，另与对应player24..36.ini的cloth引用一致性比对。详见additional-full-models-static-evidence.json。这13个仅确认额外完整模型、生产用途未核实；此前称变身候选是分类错误，已纠正。它们不是20常规/受限候选槽位，不能据其有完整模型就当作临时变身。真正scene→avatar变身映射见transformations/source-scene-catalog-evidence.json与独立manifest。'];
await writeFile(path.join(import.meta.dirname,'ROSTER_STATIC_EVIDENCE_20261028.md'),lines.join('\n')+'\n');
const forms=[...fixed.known.content.matchAll(/\b(Role\w+)\s+uint16\s*=\s*(\d+)\s*\/\/\s*cloth(\d+)([^\n]*)/g)].map(m=>{const id=Number(m[2]),cloth=m[3],ini=player.playerIni.find(r=>r.id===id);return{sourceRoleId:id,sourceConstant:m[1],sourceComment:m[4].trim(),expectedClothId:cloth,playerIni:ini,clothReferenceMatches:ini?.sections?.stand?.cloth===cloth&&ini?.sections?.walk?.cloth===cloth,sourceClassification:'additional complete entity model; production purpose unverified; NOT established as temporary transformation or selectable role',productionPurpose:null,temporaryTransformationEstablished:false,ownArt:null,gameplayIntegration:false};});
await writeFile(path.join(import.meta.dirname,'additional-full-models-static-evidence.json'),JSON.stringify({schemaVersion:2,source:{commit:fixed.commit,url:fixed.known.display_url,gitBlobSha:fixed.known.sha},classificationCorrection:{previousFile:'transformation-models-static-evidence.json',previousClaim:'transformation candidate',correctedClaim:'13 additional full models; production purpose unverified',reason:'known.go only identifies complete entity models. NativeTransformation scene mapping belongs to sceneelement/catalog.go and uses avatar41/42/43/44/45/46/54/55.'},count:forms.length,scope:'separate from20 concrete configured player roleIDs AND from8 statically mapped temporary transformation avatars; no source image decode/model-animation verification',forms},null,2)+'\n');
console.log(JSON.stringify({slots:slots.length,historicalOwnMasters:15,newOwnMasters:5,matchedNativeProfiles:native.matchedPlayableRows,additionalForms:forms.length,formClothMatches:forms.filter(s=>s.clothReferenceMatches).length}));
