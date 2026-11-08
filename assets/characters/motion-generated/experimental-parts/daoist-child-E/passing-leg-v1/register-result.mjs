import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url)),root='D:/work/qqtang-ui';
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const save=(n,r)=>fs.writeFileSync(path.join(base,n),JSON.stringify(r,null,2)+'\n');
const pngPath=path.join(base,'passing-leg-v1.png'),png=fs.readFileSync(pngPath);
const prompt=fs.readFileSync(path.join(base,'passing-leg-v1.prompt.txt'),'utf8');
const alpha=JSON.parse(fs.readFileSync(path.join(base,'passing-leg-v1.alpha-review.json'),'utf8'));
const refs=[
 [path.join(base,'synthetic-passing-guide.png'),'project-authored synthetic structure/75px lift intention, not native anatomy',rel(path.join(base,'synthetic-passing-guide.png.source.json'))],
 [path.resolve(base,'../whole-leg-v1/whole-leg-v1.png'),'own continuous trouser/boot material only; old wide strides and gold hip rims excluded',rel(path.resolve(base,'../whole-leg-v1/whole-leg-v1.png.generation.json'))],
 [path.join(root,'assets/characters/motion-generated/daoist-child/native-role9-evidence/group0-six-phase-board-5x.png'),'actual sourceE functional narrow/lift reference only; original character identity not adopted; anatomical contact/timing unverified','assets/characters/motion-generated/daoist-child/native-role9-evidence/group0-six-phase-board.json'],
 [path.join(root,'references/image/01-mail-event.png'),'confirmed primary Daoist Q hand-painted style',null],
 [path.join(root,'references/image/team-ui-v2.png'),'confirmed primary Daoist Q hand-painted style',null],
].map(([file,role,sourceRecord])=>({path:file.replaceAll('\\','/'),role,sourceRecord,sha256:hash(fs.readFileSync(file))}));
const review={
 schemaVersion:1,projectDisplayName:'灵葫大作战',file:rel(pngPath),sha256:hash(png),reviewedAtUTC:new Date().toISOString(),
 nativeAndIvoryActuallyViewed:true,actualNativeSize:[1536,1024],
 status:'four_passing_leg_parts_candidate_hip_scale_and_lift_unconfirmed',
 gridOrder:['near_R_planted','near_R_raised','far_L_planted','far_L_raised'],
 observations:{
  visibleWholeParts:4,allBootToesScreenRight:true,continuousTrouserBoot:true,
  plainClosedWhiteHipCaps:true,oldGoldHipRimAbsent:true,repeatedKneeGoldCuffAbsent:true,
  planted:'Left-column legs are substantially narrower/more vertical than old wide-stride legs. Boots look level; ankle-under-hip exact coordinate contract has not been measured/approved.',
  raised:'Right-column knees visibly bend forward and shins fold back toward ankles. Entire raised boot has a coherent pitched sole; this is not a wide-stride source translated or rotated by code.',
  material:'Own ivory cloth, lower warm-gold clouds, single ankle cuff, jade-green boot, ivory toe and thin gold sole retained.',
  sideIdentity:'Near/far cells assigned from guide; independent boot surface differences are visible but anatomical side continuity is not yet approved from isolated parts.',
  transparency:'Actual ivory view has no brown outer glow; raw viewer coloredRGB at alpha0 is hidden and not an alpha defect.',
 },
 cellCoordinateContract:{commonRequestedHipCellPoint:[330,86],actualHipPoints:null,approved:false,
  issue:'Model moved the cap positions independently relative to nominal cells. Source mother must not be treated as a registered fixed-root animation grid.'},
 lift:{requestedNativeSoleDifference:75,requestedRange:[70,80],actualRegisteredSoleDifference:null,
  nominalCellLowestVisiblePixelDifference:alpha.nominalCellLowestVisiblePixelLiftProxy,
  proxyScope:'Both62px are raw alpha lower-bound differences before hip alignment, not anatomical sole measurements or an accepted70–80px lift.',
  requestedLiftPassed:false},
 clearance:{requestedOuterPx:30,actualAlpha8OuterMargins:{left:358,top:22,right:260,bottom:41},
  outerEdgesAllAlpha8Zero:true,requestedMarginPassed:false,
  nominalCellTopMargins:[22,27,8,14],nominalCellBoundarySafetyIsNotSlicingApproval:true},
 alphaEvidence:'passing-leg-v1.alpha-review.json',actualCommonPhysicalScaleApproved:false,
 sourceAnatomicalNearFarConfirmed:false,nativeSourcePhase4MappingConflictUnresolved:true,
 sourceNativeTimingMs:null,worldRoot:null,localPivots:null,bindScale:null,
 newImagegenCalls:1,retries:0,sliced:false,bound:false,animationProduced:false,
 runtimeEnabled:false,runtimeAdopted:false,clientApproved:false,fullAnimationAccepted:false,
 pending:['Hip registration and actual shared source scale','Registered sole lift versus70–80px intent','Top22px versus30px clearance','Source phase4 support-side interpretation','Independent fixed nearRIGHT/farLEFT boot continuity and full static assembly'],
 nextAction:'Stop at source candidate after this single call. No cropping, binding, retry or runtime adoption; coordinator reviews first.',
};
save('passing-leg-v1.review.json',review);
save('passing-leg-v1.tool-result.json',{
 returnedFields:['image_url','output_hint'],actualModel:null,actualQuality:null,providerCreationTimestamp:null,
 output_hint:'Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a18186-b8cc-7422-8ae3-98b8ffad899f as C:\\Users\\luyua\\.codex\\generated_images\\01a18186-b8cc-7422-8ae3-98b8ffad899f\\exec-9abf0d22-d0c7-4135-953c-22faf28d0f62.png by default.',
});
save('passing-leg-v1.png.generation.json',{
 schemaVersion:1,projectDisplayName:'灵葫大作战',file:rel(pngPath),sha256:hash(png),generatedAt:new Date().toISOString(),
 timeEvidence:'UTC registration after builtin result; provider creation time not exposed',width:png.readUInt32BE(16),height:png.readUInt32BE(20),format:'PNG',
 tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',creationKind:'new_independent_painted_rig_parts_from_references',
 configSnapshot:JSON.parse(fs.readFileSync('D:/work/image/config/image-generation.json','utf8')),
 officialVerification:rel(path.join(base,'MODEL_VERIFICATION_20261029.md')),
 submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:refs.map(r=>r.path)},
 actualModel:null,actualQuality:null,unverifiedReason:'宿主管理，工具没有型号/质量选择器，返回结果未披露可核实型号或质量。',
 requestedCanvasSizeInPrompt:[1536,1024],sizeSelectorExposed:false,
 prompt:rel(path.join(base,'passing-leg-v1.prompt.txt')),promptFileSha256:hash(Buffer.from(prompt)),submittedPromptSha256:hash(Buffer.from(prompt.trim())),
 promptSubmission:'File text trimmed only at start/end',references:refs,
 evidence:{hostSource:'C:/Users/luyua/.codex/generated_images/01a18186-b8cc-7422-8ae3-98b8ffad899f/exec-9abf0d22-d0c7-4135-953c-22faf28d0f62.png',
  returnedFields:['image_url','output_hint'],toolResult:rel(path.join(base,'passing-leg-v1.tool-result.json')),selectorsExposed:false},
 editTarget:null,originalQQCharacterAppearanceAdopted:false,
 review:rel(path.join(base,'passing-leg-v1.review.json')),status:review.status,runtimeAdopted:false,
});
console.log(JSON.stringify({file:rel(pngPath),sha256:hash(png),nativeSize:[1536,1024],status:review.status,modelCalls:1,retries:0}));
