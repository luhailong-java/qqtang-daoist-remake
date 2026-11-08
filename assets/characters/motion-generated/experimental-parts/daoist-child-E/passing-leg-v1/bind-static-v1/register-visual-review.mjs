import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const pp=path.join(base,'proposal.json');
const p=JSON.parse(fs.readFileSync(pp,'utf8'));
const status='two_passing_static_candidates_shared_offset_lift_measured';
p.actuallyViewed=true;p.actualViewedEvidence='visual-review.json';p.reviewStatus=status;
fs.writeFileSync(pp,JSON.stringify(p,null,2)+'\n');
const s=56.25/444;
const poseMeasurements=p.twoPoses.map(pose=>{
 const entries=Object.entries(pose.legMeasurements),plant=entries.find(([id])=>id.endsWith('planted')),
 raised=entries.find(([id])=>id.endsWith('raised'));
 return{pose:pose.pose,planted:plant,raised,
  actualFootBottomDifferenceBetweenLegs:plant[1].renderedLegAlpha8BBoxExclusive[3]-raised[1].renderedLegAlpha8BBoxExclusive[3],
  liftedLowestPixelBottomClearanceDesign:raised[1].clearanceToPixelBottom,
  liftedLowestPixelBottomClearanceLogicalUsingPriorFixedScale:raised[1].clearanceToPixelBottom*s};
});
const r={
 schemaVersion:1,projectDisplayName:'灵葫大作战',reviewedAtUTC:new Date().toISOString(),
 sourceProposalSha256:sha(fs.readFileSync(pp)),status,
 actuallyViewed:['two-passing-627-ivory.png','two-passing-96-ivory.png'].map(n=>({file:n,sha256:sha(fs.readFileSync(path.join(base,n)))})),
 nativeCropsIndividuallyActuallyViewed:['near_R_planted.png','near_R_raised.png','far_L_planted.png','far_L_raised.png'],
 manualSourceCapPointsVisible:true,capPixelEvidence:'Cap samples are near-opaque ivory at252–253alpha in current source. All chosen heel/toe/sole points are current visible pixels; far planted sole is threshold-edgealpha8 and remains manually uncertain.',
 sharedNewLegScale:.24,familyArtImageOffset:[0,-12.84],fixedBoneHips:{nearR:[307,439],farL:[319,438]},
 sourceCapAfterPlacement:{nearR:[307,426.16],farL:[319,425.16]},
 effectiveImagePivotIsAnatomicalClaim:false,fixedUpperArmRingMatricesUnchanged:true,
 observations:{
  posing:'P1near planted/far raised andP2near raised/far planted show actual bent knee and visible boot lift with consistent screen-right toes. Not an old whole leg rotated or source image warped.',
  hips:'White source caps mostly hide under the existing torso/hem after one common family image placement. No extra hem/gold hip ring added. Bonehip and paintedcap positions are explicitly different; do not relabel effective pivot as source anatomy.',
  scale:'Boot material/size is broadly compatible with old0.24 legs, no per-part or per-pose scale fit. This is one visual static comparison, not a measured native physical unit proof.',
  depth:'P2near raised boot obscures a substantial part of far planted ankle/lower leg; the lower far boot remains visible. Keep this overlap as a future motion/readability concern.',
  sourceMapping:'Source indices1/2/4/5 persistent anatomical identity and contact correspondence remain unconfirmed. TwoP poses do not establish six-phase source alignment or a loop.',
  small:'Whole627 square uniformly resized96; actor about68px high. Identity/gourd and a foot lift can be recognized, but overlapping ankles/boots become crowded; small view alone cannot certify limb identity.',
 },
 measurements:poseMeasurements,manualPlantedSoleY:{P1:528.88,P2:528.12},manualPlantedResidual:{P1:.38,P2:-.38},
 actualPlantedLowestPixelRowBoth:528,actualPlantedLowestPixelBottomBoth:529,
 candidateArtGroundY:528.5,sourceNativeGroundClaim:false,
 requestedRaised75SourcePxTargetMetForBoth:false,
 unchangedFixedDrawScaleRecommendation:{designToLogical:s,source:'../../passing-leg-audit-20261029/current-static-alpha-scale.json',
   noPerPoseBboxNormalization:true},
 currentActorAlpha8Bounds:p.twoPoses.map(q=>({pose:q.pose,bbox:q.actorAlpha8BBoxExclusive})),
 sourceNativeTimingMs:null,worldRoot:null,sourcePoseIdentityMappingApproved:false,sixPhaseComplete:false,
 fullStaticCoordinatorApproved:false,runtimeEnabled:false,fullAnimationAccepted:false,
 newAiImages:0,renderBatches:1,extraRenders:0,
 nextAction:'Preserve this one static batch with actual residuals/lift and depth concerns, no auto-refit, AI retry or second assembly. Coordinator decides next independent work.',
};
fs.writeFileSync(path.join(base,'visual-review.json'),JSON.stringify(r,null,2)+'\n');
console.log(JSON.stringify({file:path.join(base,'visual-review.json'),status,renderBatches:1,
 liftedClearance:poseMeasurements.map(x=>({pose:x.pose,design:x.liftedLowestPixelBottomClearanceDesign,logical:x.liftedLowestPixelBottomClearanceLogicalUsingPriorFixedScale}))}));
