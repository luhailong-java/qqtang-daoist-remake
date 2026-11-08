// Existing JSON/text and encoded-file hashes only; no image decode/render/module execution.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url));
const root='D:/work/qqtang-ui';
const native=path.join(root,'assets/characters/motion-generated/daoist-child/native-role9-evidence');
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const save=(n,r)=>fs.writeFileSync(path.join(base,n),JSON.stringify(r,null,2)+'\n');
const sixPath=path.join(native,'group0-six-phase-board.json'),six=read(sixPath);
const lowerPath=path.join(native,'group0-e-lowerbody-review.json'),lower=read(lowerPath);
const scale=read(path.join(base,'current-static-alpha-scale.json'));
const ownV2Path=path.resolve(base,'../whole-arm-v1/bind-static-v2/proposal.json'),own=read(ownV2Path);
const viewedPngs=[path.join(native,'group0-six-phase-board-5x.png'),path.join(native,'group0-e-lowerbody-12x.png'),
 path.resolve(base,'../whole-leg-v1/registered-contact-v3/two-contacts-ivory.png'),
 path.resolve(base,'../whole-arm-v1/bind-static-v2/two-contacts-627-ivory.png')].map(p=>({file:rel(p),sha256:sha(fs.readFileSync(p)),actuallyViewed:true}));
const zero=six.records.find(r=>r.frameIndex===0),three=six.records.find(r=>r.frameIndex===3);
const repeated=zero.layers.map(a=>{
 const b=three.layers.find(x=>x.layer===a.layer);
 const equal={encodedPixelSha256:a.encodedPixelSha256===b.encodedPixelSha256,
  nativeSize:JSON.stringify(a.nativeSize)===JSON.stringify(b.nativeSize),frameOffset:JSON.stringify(a.frameOffset)===JSON.stringify(b.frameOffset),pixelMode:a.pixelMode===b.pixelMode};
 return {layer:a.layer,frame0:{encodedPixelSha256:a.encodedPixelSha256,nativeSize:a.nativeSize,frameOffset:a.frameOffset,sourceByteOffset:a.sourceByteOffset},
  frame3:{encodedPixelSha256:b.encodedPixelSha256,nativeSize:b.nativeSize,frameOffset:b.frameOffset,sourceByteOffset:b.sourceByteOffset},
  equal,sameEncodedSignatureSizeOffset:Object.values(equal).every(Boolean)};
});
const observations={
 0:'Narrow/overlapping lower silhouette, foot and leg each11x6 at45,75. No independently labelled anatomical leg chain.',
 1:'Wide left/right shoe separation; screen-left leg-component bottom79, screen-right81. Screen-left outline is shallower. This is a visible level difference, not a proved ground-contact label.',
 2:'Screen-left component moves up to72..78, right remains76..81. Left shoe is raised relative to right by the lower-boundary evidence.',
 3:'Same recorded body/foot/leg/cloth/hair signature,size,offset as0, but face bytes differ. Whole pose must not be aliased.',
 4:'Opposite visible lift envelope: screen-left76..81, screen-right72..78. Screen-right component is higher; anatomical side unknown.',
 5:'Both leg-component lower bounds80, but left starts73 and right75 with different shoe forms. Equal lower bounds do not prove both planted or prove phase equivalence.',
};
const facts={
 schemaVersion:1,projectDisplayName:'灵葫大作战',createdAtUTC:new Date().toISOString(),sourceRoleId:9,ownIdentity:'daoist-child',
 sourceMetadata:[{file:rel(sixPath),sha256:sha(fs.readFileSync(sixPath))},{file:rel(lowerPath),sha256:sha(fs.readFileSync(lowerPath))}],
 reusedSourceScope:'Previously decoded selected six source objects only, current task reuses existingPNG/metadata; no package/client/object decompression or code execution.',
 actualViewedBoards:viewedPngs,alphaOnlyDecodedImages:scale.records.map(r=>({file:r.file,sha256:r.sha256})),
 totalUniqueExistingPngsReadOrViewed:6,newPngs:0,newAiCalls:0,newRendererExecutions:0,
 direction:'E',directionEvidence:'Actually viewed six-board face noses/mouths screen-right; earlier group0 source proof reused, not directory order.',
 nativeCanvas:[100,100],declaredDirections:4,declaredFramesPerDirection:6,observedNativeIndices:[0,1,2,3,4,5],
 diagnosticLayerOrder:six.compositeOrder,nativeRendererOrderIndependentlyProven:false,head1Read:false,
 frame0vs3:repeated,wholePoseAliasApproved:false,anatomicalNearFarChainProven:false,
 phaseFacts:six.records.map(r=>({frameIndex:r.frameIndex,phaseIndex:r.phaseIndex,directionGroupIndex:r.directionGroupIndex,
  layers:r.layers.map(l=>({layer:l.layer,sourceResource:l.sourceResource,nativeSize:l.nativeSize,frameOffset:l.frameOffset,
   encodedPixelSha256:l.encodedPixelSha256,pixelMode:l.pixelMode,sourceByteOffset:l.sourceByteOffset})),
  legComponents:lower.records.find(x=>x.frameIndex===r.frameIndex)?.legAlpha8Components??null,
  observation:observations[r.frameIndex],nativePhysicalContactConfirmed:false,nativeSupportLegAnatomicalSide:null,timingMs:null})),
 preservedUnknowns:['Native time unit/duration; old[4,300] remains uninterpreted','Original complete render order/head1 contribution','Original actor world root/collision anchor','Persistent source nearRIGHT/farLEFT leg identities','Exact physical heel/toe ground contacts'],
 nativeTimingMs:null,worldRoot:null,runtimeEnabled:false,
};
save('native-phase-facts.json',facts);
const parts=[
 {id:'near_R_passing_planted',side:'RIGHT',depth:'near',state:'planted-under-hip',bootSurface:'Own near outer boot/cloud detail, not a mirrored far boot'},
 {id:'near_R_passing_raised',side:'RIGHT',depth:'near',state:'bent-knee-raised-passing',bootSurface:'Same RIGHT boot/cloth identity; independently painted bend/sole orientation'},
 {id:'far_L_passing_planted',side:'LEFT',depth:'far',state:'planted-under-hip',bootSurface:'Own far inner boot view; preserve left identity independently'},
 {id:'far_L_passing_raised',side:'LEFT',depth:'far',state:'bent-knee-raised-passing',bootSurface:'Same LEFT identity, independently painted bend; never mirror nearRIGHT'},
].map(p=>({...p,completeSinglePart:'Plain hidden ivory hip cap -> uninterrupted trouser leg -> one ankle gold cuff -> entire jade boot, no segmented knee cuff',
 status:'missing_not_generated',commonScaleIntent:'Same native boot/cloth pixel scale as existing whole-leg-v1, future source-to627 bind0.24 retained only after actual art proportion check; no per-item fit.',
 plannedAcceptance:p.state==='planted-under-hip'?[
  'Ankle/sole center near beneath own hip instead of a wide-stride planted pair; complete flat sole and screen-right toe',
  'Artistic contact sole near the existing diagnostic art-ground528.5 within1 designpx; this is not native/world ground',
  'Hidden cap attachment follows unchanged torso art contract; actual source pivot/ankle/toe/sole must be measured after a future image']:[
  'Genuine bent-knee silhouette, heel/ankle tucked and foot passing under/near hip; not translating a straight contact leg upward',
  'Visible sole clearance provisional12–20 designpx above diagnostic art-ground, boot toe remains screen-right',
  'New paint must show knee bend/boot pitch coherently; no code move of source leg or mirrored other side'],
 futureRuntimeOrLoopApproved:false}));
const phases=[
 {nativeIndex:0,ownCandidateRole:'narrow passing before A',near:'near_R_passing_raised',far:'far_L_passing_planted',
  sourceToOwnEvidence:'Source narrow silhouette only; assignment near swing/far support is an explicit own art choice, not source anatomical recovery.',confidence:'artistic_proposal_only'},
 {nativeIndex:1,ownCandidateRole:'wide contact A reference',near:'near_R_forward',far:'far_L_backward',
  sourceToOwnEvidence:'Existing A supplies the wide opposite reach. Native screen-left bottom79/right81 does not prove the current two planted art soles are exact native contacts.',confidence:'outline_reference_candidate_not_native_contact_proof'},
 {nativeIndex:2,ownCandidateRole:'A-side lift / transition',near:'near_R_forward',far:'far_L_passing_raised',
  sourceToOwnEvidence:'Source screen-left foot lifts while screen-right stays lower. Assigning rear swing to own farLEFT is provisional; use future art/chain review, not X-sort.',confidence:'support_side_unconfirmed'},
 {nativeIndex:3,ownCandidateRole:'opposite narrow passing before B',near:'near_R_passing_planted',far:'far_L_passing_raised',
  sourceToOwnEvidence:'Source lower layers repeat0 but do not expose persistent identity. Own inverse support/swing must remain distinct; do not alias own0/3.',confidence:'artistic_proposal_only'},
 {nativeIndex:4,ownCandidateRole:'wide B silhouette placeholder, physical contact conflict pending',near:'near_R_backward',far:'far_L_forward',
  sourceToOwnEvidence:'Native screen-right is higher(bottom78) while left reaches81. Treating B front/farLEFT as planted would conflict with that visible envelope; do not call native contactB matched. A different timing/phase-role interpretation may be necessary.',confidence:'explicit_contact_mapping_conflict'},
 {nativeIndex:5,ownCandidateRole:'B-side recovery / transition placeholder',near:'near_R_passing_raised',far:'far_L_forward',
  sourceToOwnEvidence:'Equal bottom80 with differing shoe forms; not enough to prove which side is physically planted. Own near swing/far support remains unconfirmed.',confidence:'contact_state_unconfirmed'},
].map(p=>({...p,sourceObservation:observations[p.nativeIndex],nativeFrameTimingMs:null,worldRoot:null,
 currentCandidateAlreadyAvailable:[p.near,p.far].filter(x=>!x.includes('passing')),
 missingParts:[p.near,p.far].filter(x=>x.includes('passing')),registration:null,approved:false}));
const req={
 schemaVersion:1,projectDisplayName:'灵葫大作战',createdAtUTC:new Date().toISOString(),
 sourceFacts:'native-phase-facts.json',currentStaticProposal:{file:rel(ownV2Path),sha256:sha(fs.readFileSync(ownV2Path))},
 scope:'Minimum new passing-leg source requirements and provisional six-slot correspondence only; not a generated set, animation or native phase recovery.',
 minimumIndependentPassingParts:4,parts,
 whyNotTwoPartsOrRotation:'Existing front/back whole-leg pieces bind hip-to-ankle diagonal and entire boot together. Rotating a wide stride ankle under hip also tilts the sole; shifting it keeps a straight wide leg and floating cap. Neither supplies a natural flat-sole under-hip support plus a genuine bent-knee passing silhouette. Need both support and swing for each anatomical side.',
 conditionalAdditionalParts:'If future fixed-scale registration cannot use the bent passing sources for early toe-off at source2/5, an additional near/far toe-off pair may be needed. Four is a minimum independent passing experiment, not proof that a full six-phase loop needs exactly four new images.',
 sixPhaseCandidates:phases,phaseRolesRecoveredFromNative:false,sourceAnatomicalNearFarConfirmed:false,
 nativeTimingMs:null,worldRoot:null,drawScaleRecommendation:'current-static-alpha-scale.json',
 sourceIdentityPolicy:'Original source shape only informs functional pose/camera. New art keeps own Daoist material/character; no original QQ hair/clothing/face copied.',
 noNewGuideOrArtworkProduced:true,noRigOrAnimationAuthored:true,runtimeEnabled:false,staticAccepted:false,fullAnimationAccepted:false,
 nextStep:'Coordinator reviews phase4 conflict and minimum source-piece plan before any new art. No generation/render/runtime work begun by this task.',
};
save('passing-leg-requirements-and-six-phase-candidates.json',req);
const appPath=path.join(root,'src/app.js'),app=fs.readFileSync(appPath,'utf8');
const artPath=path.join(root,'assets/art.json'),art=read(artPath);
save('audit-delivery.json',{
 schemaVersion:1,createdAtUTC:new Date().toISOString(),scope:'Existing sixPNG maximum plus text/metadata and arithmetic, no new visual outputs.',
 sourceFacts:'native-phase-facts.json',requirements:'passing-leg-requirements-and-six-phase-candidates.json',scale:'current-static-alpha-scale.json',
 exactPngBudget:{actuallyViewedBoards:4,alphaOnlyDecodedStaticRgba:2,totalUnique:6,additionalClientPackageDecodes:0,newPngOutputs:0},
 codeEvidence:{app:{file:rel(appPath),sha256:sha(Buffer.from(app)),
   sourceMapCell:40,legacyDrawSpaceCell:64,unit:40/64,
   actorFallbackDrawBox:[82,90],actorFallbackLogicalVisibleHeight:90*40/64,
   sourceLines:app.split(/\r?\n/).filter(l=>l.includes('cell=g.sourceMap?40:64')||l.includes('const drawScaled=')||l.includes('if(!animated)drawSprite'))},
  art:{file:rel(artPath),sha256:sha(fs.readFileSync(artPath)),daoistFallbackSource:art.characters.assets[0]},
  fallbackScaleMath:'drawSprite min(82/633,90/907) is height-limited, then sourceMap unit40/64 =>56.25logical px; renderer source read only.'},
 drawScaleRecommendation:{fixedReferenceSpanH:scale.fixedReferenceSpan[1],oneSharedScale:scale.recommendedOneSharedDesignPixelToLogicalPixelScale,
  full627CanvasLogicalSize:scale.recommendedFull627DesignCanvasLogicalSize,
  full627CanvasSizeInExisting64DrawSpace:scale.recommendedFull627CanvasSizeInExisting64DrawSpace,
  mapCellChanged:false,nativeOneToOneClaim:false},
 preservedUnknowns:facts.preservedUnknowns,runtimeEnabled:false,newImagegenCalls:0,rendererOrTestsOrBrowserExecuted:false,
});
console.log(JSON.stringify({minimumPassingParts:4,native0vs3:repeated.map(x=>({layer:x.layer,equal:x.sameEncodedSignatureSizeOffset})),
 pngBudget:6,newPngs:0,oneSharedDesignToLogicalScale:scale.recommendedOneSharedDesignPixelToLogicalPixelScale,phase4ConflictRetained:true}));
