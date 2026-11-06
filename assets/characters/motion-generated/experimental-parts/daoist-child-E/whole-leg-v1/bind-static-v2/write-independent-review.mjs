import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url));
const source=path.resolve(out,'../root-contact-diagnostic/proposal.json');
const bytes=fs.readFileSync(source);
const p=JSON.parse(bytes);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const transformed=[];
for(const pose of p.twoContacts){
 const solePoints={};
 for(const id of [pose.nearPart,pose.farPart]){
  const node=pose.nodes.find(n=>n.id===id),xy=p.parts[id].soleCandidate;
  const [a,b,c,d,e,f]=node.imageMatrix;
  solePoints[id]=[a*xy[0]+c*xy[1]+e,b*xy[0]+d*xy[1]+f];
 }
 transformed.push({contact:pose.contact,solePoints});
}
const registerProposal={};
for(const [id,part] of Object.entries(p.parts)){
 const near=id.startsWith('near_');
 const hipPos=near?p.nearHipPosition:p.farHipPosition;
 registerProposal[id]={
   currentVisualHipCandidate:part.hip,
   proposedAuthoredAttachment:[part.hip[0],part.soleCandidate[1]-(p.diagnosticGroundY-hipPos[1])/p.wholeLegUniformScale],
   purpose:'Unexecuted artistic attachment inside hidden cap to register the existing manual sole landmark to one diagnostic line; not a corrected anatomical measurement',
   fixedHipPosition:hipPos,scale:p.wholeLegUniformScale,approved:false,
 };
}
const r={
 schemaVersion:1,projectDisplayName:'灵葫大作战',reviewedAt:new Date().toISOString(),
 reviewScope:'Read existing coordinator contact images and proposal/code only. No second crop/render, pixel decode sweep, AI generation, browser, build or test.',
 sourceProposal:'../root-contact-diagnostic/proposal.json',sourceProposalSha256:hash(bytes),
 actuallyViewed:['../root-contact-diagnostic/two-contacts-ivory.png','../root-contact-diagnostic/contact-A-ivory.png','../root-contact-diagnostic/contact-B-ivory.png'],
 viewedFilesEvidence:['two-contacts-ivory.png','contact-A-ivory.png','contact-B-ivory.png'].map(n=>({file:'../root-contact-diagnostic/'+n,sha256:hash(fs.readFileSync(path.resolve(out,'../root-contact-diagnostic',n)))})),
 nearFarAssignmentAndLayerOrderCoherent:true,trueScreenRightFacingVisible:true,
 segmentedKneeCuffProblemRemoved:true,oldAdditionalHemAbsent:true,
 hipCapsMostlyOccluded:true,allHipFinishedGoldEdgesFullyOccludedApproved:false,
 soleLandmarkEvidence:'Root manual unapproved soleCandidate points, transformed numerically from existing recorded matrices. No independent anatomical/pixel-ground approval.',
 transformedSolePoints:transformed,withinPoseSoleYDifference:0.04,betweenPoseSoleYShift:2.4,
 diagnosticGroundY:529,rootMoved:false,commonWholeLegScale:0.24,
 status:'leg_foundation_viable_static_registration_and_caps_pending',
 minimalUnexecutedRegistrationProposal:registerProposal,
 upperBodyOffsetProposal:null,
 arms:'absent; old shoulder/arm issues remain pending, no claim of complete character',
 newImagegenCalls:0,newPngOutputs:0,newAssemblies:0,
 completeAnimation:false,sourceNativeTimingMs:null,worldRoot:null,
 staticBindAccepted:false,runtimeAdopted:false,
 document:'INDEPENDENT_REVIEW_20261028.md',
};
fs.writeFileSync(path.join(out,'independent-review.json'),JSON.stringify(r,null,2)+'\n');
console.log(JSON.stringify({file:path.join(out,'independent-review.json'),status:r.status,newAssemblies:0,transformedSolePoints:transformed}));
