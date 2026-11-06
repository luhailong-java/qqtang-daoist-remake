import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const out=path.dirname(fileURLToPath(import.meta.url));
const root='D:/work/qqtang-ui';
const relative=(p)=>path.relative(root,p).replaceAll('\\','/');
const hash=(b)=>crypto.createHash('sha256').update(b).digest('hex');
const save=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n');
const file=path.join(out,'whole-leg-v1.png');
const png=fs.readFileSync(file);
const prompt=fs.readFileSync(path.join(out,'whole-leg-v1.prompt.txt'),'utf8');
const alpha=JSON.parse(fs.readFileSync(path.join(out,'whole-leg-v1.alpha-review.json'),'utf8'));
const referenceSpecs=[
 ['synthetic-structural-pose-guide.png','synthetic pose intention only; internal engineering diagram; not original game evidence','synthetic-structural-pose-guide.png.source.json'],
 ['../parts-master-v1.png','own previous parts material identity only; not separated cuffs/layout/poses','../parts-master-v1.png.generation.json'],
 ['../../../../../../../references/image/01-mail-event.png','confirmed primary Daoist Q hand-painted style',null],
 ['../../../../../../../references/image/team-ui-v2.png','confirmed primary Daoist Q hand-painted style',null],
];
// Explicit project paths avoid ambiguous traversal for the two style references.
const references=referenceSpecs.map(([p,role,rec],i)=>{
 const absolute=i<2?path.resolve(out,p):path.join(root,'references/image',i===2?'01-mail-event.png':'team-ui-v2.png');
 return {path:absolute.replaceAll('\\','/'),role,sha256:hash(fs.readFileSync(absolute)),
   sourceRecord:rec?relative(path.resolve(out,rec)):null};
});
const review={
 schemaVersion:1,file:relative(file),sha256:hash(png),reviewedAt:new Date().toISOString(),
 sourceCanvasSize:[png.readUInt32BE(16),png.readUInt32BE(20)],sourceAndIvoryActuallyViewed:true,
 status:'not_passed_hip_cap_finished_trim_and_far_side_unproven',
 imagegenAttemptCount:1,staticNewPaintedPartCount:4,
 requestedOrder:['near_RIGHT_forward','near_RIGHT_backward','far_LEFT_forward','far_LEFT_backward'],
 observations:{
   chainReach:'Both left-column pieces visibly extend down/right from hip; both right-column pieces extend down/left. The right-column foremost toe is left of its own hip-cap center while still pointing screen right.',
   frontBackReachSignsVisible:true,allBootsPointScreenRight:true,
   allFourConnectedHipToBoot:true,noIntermediateKneeGoldCuffVisible:true,
   oneAnkleFinishedGoldCuffPerLeg:true,
   material:'Own ivory cloth, lower cloud embroidery, teal/jade boots, ivory toe and thin warm gold sole are retained.',
   hipCap:'All four hip ends contain overlapping finished flap/curved gold edging rather than the requested plain white hidden rounded cloth cap. This is not approved joint overlap.',
   nearFar:'Four cells retain the requested labels only in metadata. Boot trim differences, especially bottom-right inner instep, are visible, but a dependable anatomical inner/outer-side identity for near RIGHT vs far LEFT is not yet proven.',
   commonScale:'No deliberate post-generation per-cell normalization. Similar visible lengths are not a calibrated common bind scale.',
   alpha:'Full native ivory composite has no visible brown outer glow. The raw viewer brown/black RGB outside the four parts is hidden at alpha zero and is not a transparency failure.',
 },
 alphaEvidence:relative(path.join(out,'whole-leg-v1.alpha-review.json')),
 alpha8OuterEdges:alpha.alpha.alpha8OuterEdges,
 diagnosticNativeHipAnkleToePoints:null,
 measurementReason:'Full hidden-cap / side-identity contract did not pass, so no accepted anatomical pivots are assigned from visible finished cap shapes.',
 bindScale:null,worldRoot:null,timing:null,sliced:false,assembled:false,
 runtimeAdopted:false,clientApproved:false,
 nextAction:'Stop this one-attempt branch; coordinator may review source evidence before any new task. No slicing, repair, assembly or animation attempted.',
};
save('whole-leg-v1.review.json',review);
const toolResult={
 returnedFields:['image_url','output_hint'],
 output_hint:'Generated images are saved to C:\\Users\\luyua\\.codex\\generated_images\\01a18186-b8cc-7422-8ae3-98b8ffad899f as C:\\Users\\luyua\\.codex\\generated_images\\01a18186-b8cc-7422-8ae3-98b8ffad899f\\exec-e568a80a-cbfc-43b8-8d9d-361a2009aaee.png by default.',
 providerCreationTimestamp:null,model:null,quality:null,
};
save('whole-leg-v1.tool-result.json',toolResult);
save('whole-leg-v1.png.generation.json',{
 schemaVersion:1,file:relative(file),sha256:hash(png),generatedAt:new Date().toISOString(),
 timeEvidence:'UTC registration after builtin tool return; provider timestamp not exposed',
 width:png.readUInt32BE(16),height:png.readUInt32BE(20),format:'PNG',
 tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',
 configSnapshot:JSON.parse(fs.readFileSync('D:/work/image/config/image-generation.json','utf8')),
 batchConfigVerification:'docs/IMAGE_CONFIG_VERIFICATION_20261028.md',
 submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:references.map(r=>r.path)},
 actualModel:null,actualQuality:null,
 unverifiedReason:'宿主管理，工具未开放型号/质量选择器，实际返回未披露可核实型号及质量。',
 requestedCanvasSizeInPrompt:[1536,1024],sizeSelectorExposed:false,
 prompt:relative(path.join(out,'whole-leg-v1.prompt.txt')),promptFileSha256:hash(Buffer.from(prompt)),
 submittedPromptSha256:hash(Buffer.from(prompt.trim())),promptSubmission:'file text trimmed at beginning/end; no other alteration',
 references,
 evidence:{hostSource:'C:/Users/luyua/.codex/generated_images/01a18186-b8cc-7422-8ae3-98b8ffad899f/exec-e568a80a-cbfc-43b8-8d9d-361a2009aaee.png',
   returnedFields:['image_url','output_hint'],toolResult:relative(path.join(out,'whole-leg-v1.tool-result.json')),selectorsExposed:false},
 newImageNotEditingFailedCharacterFrames:true,
 excludedReferences:['failed whole-character E poses','failed static bind','old native QQ character appearance'],
 review:relative(path.join(out,'whole-leg-v1.review.json')),
 status:review.status,runtimeAdopted:false,clientApproved:false,
});
console.log(JSON.stringify({file:relative(file),sha256:hash(png),status:review.status,size:review.sourceCanvasSize}));
