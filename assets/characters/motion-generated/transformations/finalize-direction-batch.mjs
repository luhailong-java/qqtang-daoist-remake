// Explicit nine metadata records only. No PNG decode/hash, scan, crop, runtime or Git change.
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
const base=import.meta.dirname,root=path.resolve(base,'../../../..');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
const save=(file,value)=>writeFile(file,JSON.stringify(value,null,2)+'\n');
const catalog=await json(path.join(base,'manifest.json'));
const native=await json(path.join(base,'native-body-direction-evidence.json'));
const defs=[
 [41,'idle-four-directions-v1',['N','E','S','W'],'four_direction_static_candidate_margin_and_root_pending',['E nominal cell bottom margin is only1px; requested60px margins/common450px body height/common foot baseline not met','Asymmetric cloud-cap attachments and common physical root/scale still pending']],
 [42,'idle-four-directions-v1',['N','E','S','W'],'not_passed_nominal_cell_crossing',['Alpha>=8 crosses both nominal vertical and horizontal cuts; equal627px cell crop is unsafe','Horn/tail near/far identity and common scale/root pending']],
 [43,'idle-four-directions-v1',['N','E','S','W'],'not_passed_nominal_row_crossing',['Alpha>=8 crosses nominal row cut','Red cap ornament near/far side and common scale/root pending']],
 [44,'idle-four-directions-v1',['N','W','S','E'],'not_passed_nominal_row_crossing',['Actual order differs from requested N/E/S/W: N/W/S/E','Alpha>=8 crosses nominal row cut','Physical LEFT ear leaf occlusion and common scale/root pending']],
 [45,'idle-four-directions-v1',['N','E','S','W'],'not_passed_nominal_row_crossing',['Alpha>=8 crosses nominal row cut','Single tail attachment/physical side through profile turns and common scale/root pending']],
 [46,'idle-four-directions-v1',['N','E','S','W'],'not_passed_nominal_row_crossing',['Alpha>=8 crosses nominal row cut','Head-stem leaf physical side and common scale/root pending']],
 [54,'walk-single-direction-keys-v1',['front-key-A','front-key-B'],'not_passed_insufficient_leg_contact_alternation',['Two front-facing keys have only small leg-shape shifts; alternating six-leg support is not demonstrated','No complete walk sequence/timing/root approval; source header really has only1direction','Actual alpha maximum254 retained; no opaque-alpha or root rewrite']],
 [55,'idle-four-directions-v2',['N','E','S','W'],'corrected_two_axes_four_direction_static_candidate_root_pending',['Extra posterior blade removed in E/W; visible total now2 single-headed axes in each view; hand/shaft chains still subject to client-scale inspection','E nominal cell bottom margin is only1px; common physical scale/root and requested margins not met']]
];
const entries=[];
for(const[id,name,order,status,issues]of defs){
 const item=catalog.entries.find(e=>e.sourceAvatarRoleId===id), prefix=path.posix.dirname(item.ownIdentity.master),file=prefix+'/'+name+'.png';
 const generation=await json(path.join(root,file+'.generation.json'));
 const qaRel=prefix+'/qa/'+name+'.alpha-review.json',qa=await json(path.join(root,qaRel));
 generation.status=status;generation.review??={};Object.assign(generation.review,{actualVisualViewed:true,actualVisualOrder:order,issues,sharedPhysicalRoot:null,sharedPhysicalScale:null,runtimeEnabled:false,clientApproved:false,fullAnimationComplete:false});
 if(id===55)generation.review.visibleBladeHeadCounts={N:2,E:2,S:2,W:2};
 await save(path.join(root,file+'.generation.json'),generation);
 qa.actualVisualViewed=true;qa.visualReview={ivoryViewed:true,visibleSolidColorHaloObserved:false,interpretation:'No obvious solid colored halo on this ivory preview; alpha0 hiddenRGB is not treated as visible dirt. This does not approve edges at client size.',issues};
 if(id===55)qa.visualReview.visibleBladeHeadCounts={N:2,E:2,S:2,W:2};
 await save(path.join(root,qaRel),qa);
 const source=native.resources.find(e=>e.avatarRoleId===id);
 entries.push({sourceSceneId:item.sourceSceneId,sourceAvatarRoleId:id,ownIdentityId:item.ownIdentity.id,ownName:item.ownIdentity.name,identityMaster:item.ownIdentity.master,sourceActionHeaders:source.actions.map(a=>({action:a.action,body:a.body,path:a.path,directions:a.directions,totalFrames:a.frameCount,framesPerDirection:a.declaredFramesPerDirection,semanticDirectionOrder:a.semanticDirectionOrder,playbackTimingMs:a.playbackTimingMs})),candidate:{file,sha256:generation.sha256,nativeSize:[generation.width,generation.height],generationRecord:file+'.generation.json',actualModel:generation.actualModel,actualQuality:generation.actualQuality,actualVisualOrder:order,uniqueDirectionCoverage:id===54?['front-only']:order,posePositions:order.length,qa:qaRel,ivoryPreview:prefix+'/qa/'+name+'-ivory.jpg',alphaExtrema:qa.alphaExtrema,alpha8BBoxLTRB:qa.alpha8BBoxLTRB,alpha8OuterEdges:qa.alpha8OuterEdges,nominalAtlas:qa.atlas??{columns:2,rows:1,cellSize:[1024,768],actualObservedOrder:order,nominalSeamNotMeasured:true},cells:qa.cells??null,status,issues},sharedPhysicalRoot:null,sharedPhysicalScale:null,staticBindApproved:false,runtimeEnabled:false,clientApproved:false,fullAnimationComplete:false});
}
const old55=catalog.entries.find(e=>e.sourceAvatarRoleId===55),oldPrefix=path.posix.dirname(old55.ownIdentity.master),oldFile=oldPrefix+'/idle-four-directions-v1.png';
const oldGen=await json(path.join(root,oldFile+'.generation.json'));
oldGen.status='not_passed_extra_axe_blade_heads_in_E_W';oldGen.supersededCandidate=oldPrefix+'/idle-four-directions-v2.png';await save(path.join(root,oldFile+'.generation.json'),oldGen);
const result={schemaVersion:1,updatedAt:new Date().toISOString(),scope:'Eight true scene→avatar temporary-form identities only. Seven4direction idle-still foundations and one1direction two-walk-key candidate. Static source candidates, not approved animation.',sourceMappingManifest:'assets/characters/motion-generated/transformations/manifest.json',nativeDirectionEvidence:'assets/characters/motion-generated/transformations/native-body-direction-evidence.json',sourceSemanticsIndependentlyVerified:false,sourceDirectionIndexOrderVerified:false,metadataOnlyIndex:true,counts:{identities:8,sourceImagesThisBatch:9,currentCandidates:8,cardinalDirectionStillPositions:28,singleDirectionWalkKeyPositions:2,totalPosePositions:30,uniqueIdentityDirectionPairs:29,completeWalkAnimations:0,newRuntimeApprovals:0},runtimeEnabled:false,fullAnimationComplete:false,entries,supersededCandidates:[{file:oldFile,generationRecord:oldFile+'.generation.json',reason:'E/W each showed3 blade heads; AI v2 removes posterior extra head without changing actual directions',replacement:oldPrefix+'/idle-four-directions-v2.png'}],pending:['Nominal boundary crossing in42/43/44/45/46 requires actual alpha ownership or regenerated source; never blindly split equal cells','Common physical scale/root not established for any form; do not independently bbox-fit every view','54 six-leg phase/contact alternation not passed; source1direction retained','Source cardinal index order and timing semantics not independently proven','96px/dark background/client-state/continuous-motion checks wait for machine slot to be returned'],machineScope:'Remote builtin imagegen plus necessary individual new-source alpha/ivory QA and small metadata only; no family decode/import/build/test/browser/runtime/Git.'};
await save(path.join(base,'direction-action-foundations-20261028.manifest.json'),result);
console.log(JSON.stringify({written:'direction-action-foundations-20261028.manifest.json',...result.counts}));
