// Independent static transformation-source/art registry. Never executes client/source.
import{readFile,writeFile,stat}from'node:fs/promises';
import path from'node:path';
const here=import.meta.dirname,root=path.resolve(here,'../../../..');
const source=JSON.parse(await readFile(path.join(here,'source-scene-catalog-evidence.json'),'utf8'));
const player=JSON.parse(await readFile(path.join(here,'../roster-player-static-evidence.json'),'utf8'));
const rows=[
 [104,41,'qingyu-cloud-duck','青羽云鸭','duck','玉绿羽冠、象牙鸭身、青金短道袍、云纹帽与圆短翅，蹼足；自有鸭形，不新增飞行表现',{TraverseStaticTerrain:true,CanCollectItems:false,RecoverOnlyOnOpenCell:true}],
 [110,42,'ink-horn-fox','墨角灵狸','demon','墨青大头灵狸、玉色小角/尖耳、象牙口鼻、短道袍、云卷单尾；圆润自有兽形',{SpeedRate:8,BombCapacity:8,ReverseDirection:true}],
 [101,43,'ruyi-lingzhi-spirit','如意芝灵',null,'如意云瓣青玉灵芝冠、象牙圆脸短身、米白玉绿短袍、两手两脚；来源43原名不作猜测',{}],
 [109,44,'jade-palm-bamboo-bear','玉掌竹熊','panda','象牙圆大头熊、深玉耳/眼斑、青竹小髻、玉掌套、米白青绿短袍；敦实掌部剪影',{CanKickBomb:true,CanPushBreakable:true}],
 [107,45,'cloud-lantern-spirit','轻云灯灵','fast ghost','圆玉框米白纸灯脸、轻云冠、短玉绿袍/小云足、单流苏尾；光只在灯内，不烘焙外光晕',{SpeedRate:8}],
 [108,46,'golden-gourd-sage','金葫胖仙','candy king','金玉葫芦双圆身、上圆憨笑脸、小叶冠、下圆短袍、短手圆足；不复制现存道童',{BombCapacity:8}],
 [114,54,'jade-shell-crab','碧甲灵蟹','crab','青玉如意云纹圆甲、象牙面、短眼柄、两大玉钳与紧凑小蟹足、朱砂绳结；自有蟹形',{HorizontalSpeedRate:5,VerticalSpeedRate:2}],
 [115,55,'jade-stone-axe-child','青岩钺童','axe gang','青灰玉石方圆大头、平顶石纹短发块、杏眼、米白包布和玉绿短甲、短腿双小钺；自有石偶',{GrantedActionID:46,GrantedActionCount:9}]
];
const entries=[];
for(const[scene,avatar,id,name,alias,design,changes]of rows){
 const rel=`assets/characters/motion-generated/transformations/avatar-${avatar}-${id}/master.png`;
 let generation=null;
 try{generation=JSON.parse(await readFile(path.resolve(root,rel+'.generation.json'),'utf8'));await stat(path.resolve(root,rel));}catch(e){if(e.code!=='ENOENT')throw e;}
 let alpha=null;
 if(generation){try{alpha=JSON.parse(await readFile(path.resolve(root,path.dirname(rel),'qa/alpha-review.json'),'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}}
 const sourceDefinition={SceneID:scene,AvatarRoleID:avatar,DurationMS:30000,TraverseStaticTerrain:false,CanCollectItems:true,RecoverOnlyOnOpenCell:false,ReverseDirection:false,CanKickBomb:false,CanPushBreakable:false,SpeedRate:0,HorizontalSpeedRate:0,VerticalSpeedRate:0,BombCapacity:0,GrantedActionID:0,GrantedActionCount:0,...changes};
 entries.push({sourceSceneId:scene,sourceAvatarRoleId:avatar,namespace:'temporary battlefield avatar, separate from account role IDs',communityCommentAlias:alias,legacyNameVerified:false,sourceDefinition,sourceDefinitionStatus:'Transcribed literal assignments/default zero values from fixed community NativeTransformation source. Function semantics/callback use/runtime behavior not independently verified.',zeroValueCaution:'Zero is retained as source default field; do not infer zero movement/capacity or invent fallback semantics.',nativePlayerIni:player.playerIni.find(r=>r.id===avatar)??null,ownIdentity:{id,name,design,master:generation?rel:null,plannedMaster:rel,staticMasterStatus:generation?'static_source_candidate_single_ivory_alpha_reviewed_pending_anchor_client':'planned',nativeSize:generation?[generation.width,generation.height]:null,sha256:generation?.sha256??null,generationRecord:generation?rel+'.generation.json':null,actualModel:generation?.actualModel??null,actualQuality:generation?.actualQuality??null,singleSourceAlpha:alpha?{record:path.dirname(rel)+'/qa/alpha-review.json',ivoryPreview:path.dirname(rel)+'/qa/master-ivory.jpg',alphaExtrema:alpha.alphaExtrema,alpha8BBoxLTRB:alpha.alpha8BBoxLTRB,outerEdgeAlpha8Counts:alpha.outerEdgeAlpha8Counts,minimumMarginPixels:Math.min(alpha.alpha8BBoxLTRB[0],alpha.alpha8BBoxLTRB[1],alpha.width-alpha.alpha8BBoxLTRB[2],alpha.height-alpha.alpha8BBoxLTRB[3]),ivoryPreviewActuallyViewed:true,previewObservation:'No obvious colored aura in the actually viewed900px ivory composite; not pixel-perfect or client approval. Alpha0 hidden RGB not treated as failure.'}:null,runtimeEnabled:false,clientApproved:false,fullAnimationComplete:false}});
}
const actualPairs=[...source.source.content.matchAll(/case (\d+):\s*avatarRoleID = (\d+)/g)].map(m=>[Number(m[1]),Number(m[2])]);
if(actualPairs.length!==8||entries.some(e=>!actualPairs.some(([s,a])=>s===e.sourceSceneId&&a===e.sourceAvatarRoleId)))throw new Error('Source transformation pairs do not match registry');
const out={schemaVersion:1,createdAt:new Date().toISOString(),source:{repository:source.repository,commit:source.commit,url:source.source.display_url,gitBlobSha:source.source.sha,evidenceRecord:'assets/characters/motion-generated/transformations/source-scene-catalog-evidence.json',semanticsIndependentlyVerified:false},scope:'Eight scene-to-avatar mappings declared by fixed community NativeTransformation; not20 account-role candidates and not13 additional full models24–36',runtimeEnabled:false,fullAnimationComplete:false,totalMappedAvatars:8,staticMasterCandidates:entries.filter(e=>e.ownIdentity.master).length,entries};
await writeFile(path.join(here,'manifest.json'),JSON.stringify(out,null,2)+'\n');
const md=['# 八个真实来源映射的原创临时形态静态候选','','2026-10-28。独立于常规20个逻辑人物，亦独立于24–36那13个用途未核实的额外完整模型。该13项已改名additional-full-models-static-evidence.json；不能因存在完整模型就叫临时变身。','',
'实际读取固定commit的internal/clientdata/sceneelement/catalog.go，Git blob SHA `'+source.source.sha+'`，链接：'+source.source.display_url+'。返回文本与来源字段见source-scene-catalog-evidence.json。8/8 scene→avatar赋值已与独立清单逐项匹配；函数语义/回调实际行为仍仅社区声明，本批没有独立核验客户端函数或运行。','',
'## 原始映射、参数与自有身份','',
'DurationMS原声明30000，默认CanCollectItems=true；未赋值字段保持Go零值0/false，不能把0自行解释为真实零速度/容量或猜fallback。下列别名仅来自社区注释，不作为本项目展示名。avatar43原名/物种未知，保持null，不凭目录猜。','',
'|scene→avatar|社区注释别名|自有展示名|区别于默认的来源赋值|静态源|','|---|---|---|---|---|',...entries.map(e=>{const row=rows.find(r=>r[1]===e.sourceAvatarRoleId);return `|${e.sourceSceneId}→${e.sourceAvatarRoleId}|${e.communityCommentAlias??'未知/null'}|${e.ownIdentity.name}|${Object.entries(row[6]).map(([k,v])=>k+'='+v).join('；')||'无额外赋值'}|${e.ownIdentity.master??'待生成'}|`;}),'',
'## 原画、逐图记录与单件检查','',
'8张当前候选均由内置image_gen新画，灵蟹另外做1次AI下脸修正/整幅reframe，共9个模型结果。每次生成前实际重读image/AGENTS.md、config/image-generation.json及IMAGE_MODEL_POLICY；每次实际附邮件/组队两主风格和自有道童比例参考。灵蟹AI编辑还实际附master-v1编辑目标。实际提交model/quality均null（无选择器），返回实际型号/质量未披露为null。每张旁保存prompt/register/generation记录，失败/修正版分别对应，不倒填旧图。','',
'本批请求1536方图、原生均返回1254方图，保存原字节；没有放大为4096、切运行帧或改源像素。qa/master-ivory.jpg只是单件米白合成并整体缩到900上限的检查图，有derivedFrom记录，不是新生成原画。只检查刚生成单件，未恢复历史全量QA/批量解码/构建测试。','',
'|avatar|原生|真实Alpha|alpha≥8外四边(左/右/上/下)|最小余量px|检查说明|','|---|---|---|---|---|---|',...entries.map(e=>{const a=e.ownIdentity.singleSourceAlpha;return `|${e.sourceAvatarRoleId}|${e.ownIdentity.nativeSize?.join('×')??'待生成'}|${a?.alphaExtrema.join('–')??'待查'}|${a?Object.values(a.outerEdgeAlpha8Counts).join('/'):'待查'}|${a?.minimumMarginPixels??'待查'}|${a?'实际查看米白底，未见明显彩晕；根点/比例/动画/客户端待验':'待查'}|`;}),'',
'灵蟹v1下脸两棕弧像额外闭眼，未采用；master.png为AI修正版，只保留两根眼柄上的眼睛，下脸仅嘴与腮红。修正版左右余量约72/76像素，未达到提示词100像素目标，但alpha≥8不触边；是否加共享透明边/按原版尺度导出须后续合同和客户端核验，不把请求目标当成已达。墨角灵狸/青岩钺童最小余量也较紧，仍未触边。所有形态相对体积、地面根点、方向、待机/移动/受击/困泡/离场/恢复动画和状态转换都未因静态master齐备而完成。','',
'本批不写src、不改全局资源manifest或Git，不把绘制的器物/形状变成新规则，runtimeEnabled/clientApproved/fullAnimationComplete均false。'];
await writeFile(path.join(here,'README.md'),md.join('\n')+'\n');
console.log(JSON.stringify({mapped:8,sourcePairsMatched:actualPairs.length,staticMasterCandidates:out.staticMasterCandidates,runtimeEnabled:false}));
