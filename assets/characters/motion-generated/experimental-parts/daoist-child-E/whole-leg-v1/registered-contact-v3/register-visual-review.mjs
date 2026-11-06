import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const proposalPath=path.join(out,'proposal.json');
const proposal=JSON.parse(fs.readFileSync(proposalPath,'utf8'));
proposal.actuallyViewed=true;
proposal.actualViewedEvidence='visual-review.json';
proposal.reviewStatus='registered_sole_points_matched_small_crotch_gold_edge_unresolved';
fs.writeFileSync(proposalPath,JSON.stringify(proposal,null,2)+'\n');
const review={
 schemaVersion:1,projectDisplayName:'灵葫大作战',reviewedAtUTC:new Date().toISOString(),
 sourceProposalSha256:hash(fs.readFileSync(proposalPath)),
 actuallyViewed:['two-contacts-ivory.png','contact-B-ivory.png'].map(name=>({file:name,sha256:hash(fs.readFileSync(path.join(out,name)))})),
 contactAScope:'Actually viewed unscaled627px contact A inside the1254px side-by-side diagnostic; no separately reopened A source required.',
 status:'registered_sole_points_matched_small_crotch_gold_edge_unresolved',
 continuousLegsNaturalEnoughForFurtherStaticReview:true,
 headTorsoRelativeAlignmentPreserved:true,newNeckGapObserved:false,
 newSegmentedKneeGoldRingObserved:false,oldExtraHemUsed:false,
 visibleSmallGoldTip:{contact:'B',locationApproxCanvas:[315,453,324,460],
   evidence:'Manual visual estimate from actually viewed contact B. Not a pixel measurement or proof of source ownership between torso trim and cap.',
   allHipGoldEdgesFullyHiddenApproved:false},
 transformedUnapprovedManualSoleY:{A:{nearRight:528.52,farLeft:528.48},B:{nearRight:528.52,farLeft:528.48}},
 candidateArtGroundY:528.5,candidatePointDeviation:0.02,
 soleEvidence:'Existing hand-authored unapproved soleCandidate transformed by recorded matrices; no pixel-ground or native-root proof.',
 actualPixelGroundApproved:false,sourceNativeAnchorRecovered:false,
 sourceNativeTimingMs:null,worldRoot:null,callerRootModified:false,nativeFrameOffsetModified:false,
 newModelGenerations:0,additionalAdjustmentsAfterThisRender:0,
 fullArmsPresent:false,staticFullCharacterApproved:false,completeAnimation:false,
 runtimeAdopted:false,clientApproved:false,
 pending:['Small crotch gold tip unresolved; do not keep translating this take','All shoulder/arm/held-gourd art absent','No small-game-size or dynamic review under machine hold'],
};
fs.writeFileSync(path.join(out,'visual-review.json'),JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify({file:path.join(out,'visual-review.json'),status:review.status,newModelGenerations:0}));
