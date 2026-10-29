import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url));
const proposalPath=path.join(out,'proposal.json');
const p=JSON.parse(fs.readFileSync(proposalPath,'utf8'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const status='static_bind_candidate_shoulder_transition_pending';
p.actuallyViewed=true;p.actualViewedEvidence='visual-review.json';p.reviewStatus=status;
fs.writeFileSync(proposalPath,JSON.stringify(p,null,2)+'\n');
const r={
 schemaVersion:1,projectDisplayName:'灵葫大作战',reviewedAtUTC:new Date().toISOString(),
 sourceProposalSha256:hash(fs.readFileSync(proposalPath)),
 actuallyViewed:['two-contacts-627-ivory.png','two-contacts-96-ivory.png'].map(n=>({file:n,sha256:hash(fs.readFileSync(path.join(out,n)))})),
 status,fullStaticAccepted:false,runtimeAdopted:false,completeAnimation:false,
 commonArmScale:.18,sameArmBindBothContacts:true,headTorsoLegV3MatricesPreserved:true,
 sourceAlpha8OwnedOnce:p.sourceAlpha8OwnedOnce,unassignedVisiblePixels:p.unassignedVisiblePixels,duplicateOwnership:p.duplicateOwnership,
 observations:{
  identity:'Own Daoist child hair/band, jade-ivory-gold costume, nearRIGHT empty fist and farLEFT assigned Taiji gourd retained. No old standalone hand/gourd added.',
  continuousArms:'Both sleeves remain continuous shoulder/elbow/wrist; old repeated finished elbow ring is absent. Each wrist has one natural embroidered cuff.',
  scale:'Uniform0.18 arm transform looks broadly compatible with unchanged old head/torso and whole legs; hands/gourd are not grossly enlarged. This is a single manual bind-scale choice, not native anatomy proof.',
  nearShoulder:'Existing torso port still reads as a closed white sleeve stub. The new sleeve emerges under the vest with a short straight occlusion transition around designY393. Current shoulder joint is not naturally seamless enough for full-static approval.',
  farShoulder:'Part of the rounded far white cap peeks outside the front/chest shoulder edge. This may be sleeve volume, but attachment coverage is not yet approved.',
  gourdOcclusion:'Far arm is behind torso in the body area; forearm/hand/complete gourd extend into open area in front of the face direction, rather than being lost behind torso. Near fist crosses lower-front torso. No gourd/tassel edge clipping observed in the627 composition.',
  handedness:'FarLEFT anatomical assignment and chain are fixed in metadata; thumb largely occluded in painted grip, so isolated anatomical left-hand proof remains unconfirmed.',
  feet:'Copied v3 art registration intact; no new hip/leg motion or caller/root adjustment. Existing small crotch gold tip remains unresolved.',
  small:'Whole627 square scaled uniformly to96square. Identity/fist/gourd can be recognized at this size, but shoulder joint detail is too small to approve from this view. Visible person is about68px high, not a96px-high body.',
 },
 nearShoulderOcclusionPass:{sourceROI:[20,25,132,172],sameTorsoMatrix:[.48,0,0,.48,225.18,310.76],
   localLowerBoundaryDesignY:393.32,sourcePixelEdit:false,armAlphaRepair:false},
 nativeSourceLandmarks:'proposal.json armParts, visual estimates only; pivots not claimed anatomical/native recovered',
 holdingHandAnatomicallyConfirmed:false,sourceNativeTimingMs:null,worldRoot:null,
 newAiImageCount:0,oneAssemblyBatch:true,additionalAdjustments:0,
 nextAction:'Keep this one result and source records; coordinator decides whether a future occlusion/attachment change is warranted. Do not auto-repeat assembly or AI repair.',
};
fs.writeFileSync(path.join(out,'visual-review.json'),JSON.stringify(r,null,2)+'\n');
console.log(JSON.stringify({file:path.join(out,'visual-review.json'),status,armCrops:Object.values(p.armParts).map(x=>({id:x.partId,sourceROI:x.sourceCropRect,size:x.nativeCropSize,pivot:x.pivot}))}));
