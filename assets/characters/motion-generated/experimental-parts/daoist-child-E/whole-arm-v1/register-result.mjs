import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url));
const root='D:/work/qqtang-ui';
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const write=(name,r)=>fs.writeFileSync(path.join(out,name),JSON.stringify(r,null,2)+'\n');
const p=path.join(out,'whole-arm-v1.png'),png=fs.readFileSync(p);
const prompt=fs.readFileSync(path.join(out,'whole-arm-v1.prompt.txt'),'utf8');
const refs=[
 [path.join(out,'synthetic-structural-guide.png'),'project-authored synthetic structure and equal-arm-length intent; not source game anatomy',rel(path.join(out,'synthetic-structural-guide.png.source.json'))],
 [path.join(out,'own-material-reference-board.png'),'seven own native crop materials, hand and gourd identity; old joint rims excluded',rel(path.join(out,'own-material-reference-board.png.source.json'))],
 [path.join(root,'references/image/01-mail-event.png'),'confirmed primary Daoist Q hand-painted style',null],
 [path.join(root,'references/image/team-ui-v2.png'),'confirmed primary Daoist Q hand-painted style',null],
].map(([file,role,sourceRecord])=>({path:file.replaceAll('\\','/'),role,sourceRecord,sha256:hash(fs.readFileSync(file))}));
const review={
 schemaVersion:1,projectDisplayName:'灵葫大作战',file:rel(p),sha256:hash(png),reviewedAtUTC:new Date().toISOString(),
 actuallyViewedNativeAndIvory:true,nativeSize:[1536,1024],
 status:'continuous_two_arm_candidates_clearance_and_bind_pending',
 visibleCompleteMainParts:2,nearPart:'RIGHT empty fist',farPart:'LEFT hand plus entire own Taiji gourd',
 construction:{bothContinuousShoulderToHand:true,plainClosedWhiteShoulderCapsVisible:true,
  shoulderGoldCupAbsent:true,midElbowFinishedCuffAbsent:true,oneNaturalWristCuffPerArm:true,
  gourdHandConnectedToSleeve:true,wholeBodyOrExtraPartsAbsent:true,
  material:'Ivory silk, warm-gold cloud wrist embroidery and chibi peach hands; gold two-lobed Taiji gourd, green collar, jade beads and red tassel retained. Gourd has additional small cloud decoration.',
  contactOrMotion:'No opposite-contact arm set or walk was requested/generated; two neutral/bent static part sources only.'},
 actualHoldingHandEvidence:'Assigned LEFT/far by project and source material provenance. Visible curled fingers/grip resemble own far-hand source; thumb mostly occluded, so anatomical handedness not independently proved by this isolated image.',
 anatomicalHoldingHandConfirmed:false,programmaticMirroring:false,
 clearance:{requested:60,actualAlpha8Margins:{left:65,top:238,right:10,bottom:208},
  requestedClearancePassed:false,actualOuterAlpha8EdgesAllZero:true,tasselVisuallyComplete:true,
  issue:'Right tassel tip is close to canvas edge at10px margin, no current visible truncation; do not call60px clearance satisfied.'},
 alphaEvidence:'whole-arm-v1.alpha-review.json',
 transparency:'Native ivory composite has no visible brown outer glow; raw viewer brown RGB at alpha0 is hidden data, not a transparency failure.',
 commonPhysicalScaleApproved:false,localPivots:null,bindScale:null,worldRoot:null,timingMs:null,
 sliced:false,assembled:false,additionalImagegenAttempts:0,
 runtimeAdopted:false,clientApproved:false,completeAnimation:false,
 pending:['Requested60px right tassel clearance not met','Exact ownership crop not yet authored or approved','One common source-to-torso scale and hidden shoulder coverage not bound','LEFT grip anatomical chain/near-far occlusion needs independent full-figure static review'],
 nextAction:'Stop after single generation and necessary source inspection. Coordinator decides whether to crop or bind; no automatic retry.',
};
write('whole-arm-v1.review.json',review);
write('whole-arm-v1.tool-result.json',{
 returnedFields:['image_url','output_hint'],model:null,quality:null,providerCreationTimestamp:null,
 output_hint:'Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a18186-b8cc-7422-8ae3-98b8ffad899f as C:\\Users\\luyua\\.codex\\generated_images\\01a18186-b8cc-7422-8ae3-98b8ffad899f\\exec-d3080643-c3b8-4167-a4fc-3affba5461f8.png by default.',
});
write('whole-arm-v1.png.generation.json',{
 schemaVersion:1,projectDisplayName:'灵葫大作战',file:rel(p),sha256:hash(png),generatedAt:new Date().toISOString(),
 timeEvidence:'UTC registration after builtin tool return; no provider timestamp exposed',
 width:png.readUInt32BE(16),height:png.readUInt32BE(20),format:'PNG',
 tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',
 configSnapshot:JSON.parse(fs.readFileSync('D:/work/image/config/image-generation.json','utf8')),
 batchOfficialVerification:'docs/IMAGE_CONFIG_VERIFICATION_20261028.md',
 submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:refs.map(r=>r.path)},
 actualModel:null,actualQuality:null,unverifiedReason:'宿主管理，工具未开放型号/质量选择器，实际返回未披露可核实型号和质量。',
 requestedCanvasSizeInPrompt:[1536,1024],sizeSelectorExposed:false,
 prompt:rel(path.join(out,'whole-arm-v1.prompt.txt')),promptFileSha256:hash(Buffer.from(prompt)),
 submittedPromptSha256:hash(Buffer.from(prompt.trim())),promptSubmission:'File text trimmed at start/end, no other alteration',
 references:refs,
 evidence:{hostSource:'C:/Users/luyua/.codex/generated_images/01a18186-b8cc-7422-8ae3-98b8ffad899f/exec-d3080643-c3b8-4167-a4fc-3affba5461f8.png',
   returnedFields:['image_url','output_hint'],selectorsExposed:false,toolResult:rel(path.join(out,'whole-arm-v1.tool-result.json'))},
 newIndependentPaintedArms:true,editTarget:null,
 excludedReferences:['failed whole-character E gait images','whole-leg sources','failed16-part static bind'],
 review:rel(path.join(out,'whole-arm-v1.review.json')),status:review.status,runtimeAdopted:false,
});
console.log(JSON.stringify({file:rel(p),sha256:hash(png),nativeSize:[png.readUInt32BE(16),png.readUInt32BE(20)],status:review.status}));
