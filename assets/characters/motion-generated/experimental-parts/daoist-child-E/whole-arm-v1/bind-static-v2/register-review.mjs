import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const pp=path.join(base,'proposal.json');
const p=JSON.parse(fs.readFileSync(pp,'utf8'));
const status='preferred_static_candidate_near_shoulder_transition_improved';
p.actuallyViewed=true;p.actualViewedEvidence='visual-review.json';p.reviewStatus=status;
fs.writeFileSync(pp,JSON.stringify(p,null,2)+'\n');
const r={
 schemaVersion:1,projectDisplayName:'灵葫大作战',reviewedAtUTC:new Date().toISOString(),
 sourceProposalSha256:sha(fs.readFileSync(pp)),status,
 actuallyViewed:['torso-shoulder-inspection-4x.png','torso-shoulder-ring-ivory-4x.png','two-contacts-627-ivory.png','two-contacts-96-ivory.png'].map(n=>({file:n,sha256:sha(fs.readFileSync(path.join(base,n)))})),
 comparisonBasis:'Previously actually viewed v1 native627/96; no v1 re-render or bulk source review.',
 preferredOverV1:true,preferenceScope:'Local shoulder construction / final authorized single correction; coordinator adoption still pending.',
 observations:{
  ownership:'Manual compound-polygon ring cutout looks green/gold only in the actually viewed4x inspection. Old white sleeve interior and lower draped cloth are absent from the foreground cutout.',
  nearShoulder:'The v1 short horizontal rectangle transition aroundY393 is no longer visible. The new continuous white sleeve connects through the old green/gold port more naturally, rather than restoring the closed white stub as a front patch.',
  farShoulder:'Moving the whole far arm from340,355 to334,360 reduces white-cap exposure at the front shoulder edge. A small amount of white sleeve volume remains visible; no break observed. Full hidden overlap has not been pixel-certified.',
  material:'Original own head, band, jade/ivory/gold torso, continuous sleeves and boots preserved. New near empty fist and far gourd grip remain legible.',
  scale:'Both arm transforms remain0.18, all v3 head/torso/leg matrices unchanged. This is authored static art registration, not a source-native skeleton/offset recovery.',
  small:'Whole627 canvas downsized96square; person remains about68px high. Character and gourd recognizable, joint detail too small to independently certify from96.',
 },
 manualRingSourceROI:[22,35,130,174],ringNativeCropSize:[108,139],ringAlpha8VisiblePixels:3273,
 originalTorsoMatrix:[.48,0,0,.48,225.18,310.76],ringImageMatrix:[.48,0,0,.48,235.74,327.56],
 oldRectanglePassUsed:false,whiteInteriorRestoredAsForeground:false,sourcePngOrArmAlphaEdited:false,
 nearShoulder:[262.5,359.5],farShoulder:[334,360],commonArmScale:.18,
 fixedV3HeadTorsoLegMatricesUnchanged:true,nearFarLogicalIdentitiesFixed:true,
 anatomicalLeftGripIndependentlyConfirmed:false,
 residual:['Small white sleeve volume still visible at far shoulder edge; do not claim pixel-proved full cap hiding','Prior crotch gold tip remains unassigned/unresolved','Grip thumb mostly occluded; handedness follows fixed own source/chain but not independent anatomical proof','Same arm bind inA/B is static-only, not alternating arm gait','No game-size dynamic/slow/dark-background or runtime review'],
 sourceNativeTimingMs:null,worldRoot:null,gameCallerRootModified:false,nativeFrameOffsetModified:false,
 newAiImages:0,renderBatchCount:1,additionalRenderAttempts:0,finalSamePointRepair:true,
 fullStaticCoordinatorApproved:false,completeAnimation:false,runtimeAdopted:false,
 nextAction:'Preserve v2 as preferred static candidate for coordinator review, stop same-point correction. No further masking/binding/image generation without a new independent assignment.',
};
fs.writeFileSync(path.join(base,'visual-review.json'),JSON.stringify(r,null,2)+'\n');
console.log(JSON.stringify({file:path.join(base,'visual-review.json'),status,preferredOverV1:true,renderBatchCount:1}));
