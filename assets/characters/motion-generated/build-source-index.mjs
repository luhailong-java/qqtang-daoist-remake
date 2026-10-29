// Lightweight text-only registry. Reads generation JSON, never decodes PNGs.
import{readFile,writeFile}from'node:fs/promises';
import path from'node:path';
const root=path.resolve(import.meta.dirname,'../../..');
const prefix='assets/characters/motion-generated/';
const own=['daoist-child','moon-shadow','mountain-guardian','lotus-healer'];
const stateNames=['trapped-four-v2','victory-four-v1','defeat-four-v1','place-bubble-four-v1','carry-bun-four-v1','hurt-four-v1','rescue-four-v1','self-rescue-needle-four-v1','revive-four-v1','kick-bubble-four-v1','push-box-four-v1','place-bubble-windup-four-v1','place-bubble-recovery-four-v1','eliminated-four-v1'];
const entries=[
 ...['walk-north-v3','walk-north-v4','walk-east-v3','walk-east-v4'].map(n=>({name:'moon-shadow/'+n,kind:'motion_repair',gate:'not_passed',posePositions:4,adoptable:false})),
 {name:'moon-shadow/walk-west-v3',kind:'motion_repair',gate:'pending_alpha_identity_gait_review',posePositions:4,adoptable:false},
 {name:'moon-shadow/east-frame3-v5',kind:'single_frame_motion_repair',gate:'pending_occluded_near_far_chain_review',posePositions:1,adoptable:false,poseReview:prefix+'moon-shadow/east-frame3-v5.pose-review.md'},
 {name:'moon-shadow/east-contact-pair-v6',kind:'two_key_contact_motion_repair',gate:'not_passed_near_far_support_reversal',posePositions:2,adoptable:false,poseReview:prefix+'moon-shadow/east-contact-pair-v6.review.md'},
 {name:'daoist-child/east-native-reference-contact-pair-v1',kind:'two_key_contact_new_native_reference_attempt',gate:'not_passed_same_near_leg_forward_both_keys',posePositions:2,adoptable:false,poseReview:prefix+'daoist-child/east-native-reference-contact-pair-v1.review.md'},
 {name:'mountain-guardian/west-frame13-edge-v1',kind:'single_frame_edge_repair',gate:'candidate_edge_contact_removed_margin_short_root_pending',posePositions:1,adoptable:false,poseReview:prefix+'mountain-guardian/west-frame13-edge-v1.review.md'},
 {name:'moon-shadow/place-bubble-windup-single-v2',kind:'single_character_phase_repair',gate:'crescent_identity_visually_restored_pending_alpha_anchor_sequence',posePositions:1,character:'moon-shadow',adoptable:false},
 {name:'trapped-four-v1',kind:'superseded_state_candidate',gate:'superseded_by_v2_pending_qa',posePositions:4,adoptable:false},
 ...own.map(id=>({name:id+'/idle-four-directions-v1',kind:'four_direction_idle_stills',gate:'pending_alpha_identity_anchor_client_review',posePositions:4,directions:['N','E','S','W'],character:id,adoptable:false})),
 ...stateNames.map(n=>({name:n,kind:n.includes('windup')||n.includes('recovery')?'action_phase_stills':'four_character_state_key_stills',gate:n.includes('windup')?'moon_identity_failed_other_three_pending':n.startsWith('kick-')?'direction_inconsistent_pending_repair':'pending_alpha_identity_anchor_client_review',posePositions:4,characters:own,atlas:{columns:2,rows:2,order:'row-major',ownership:'not_verified_do_not_naively_equal_split'},adoptable:false}))
];
for(const e of entries){e.file=prefix+e.name+'.png';e.generationRecord=e.file+'.generation.json'; const r=JSON.parse(await readFile(path.resolve(root,e.generationRecord),'utf8'));e.sha256=r.sha256;e.nativeSize=[r.width,r.height];e.generatedAt=r.generatedAt;e.actualModel=r.actualModel??null;e.actualQuality=r.actualQuality??null;e.review=r.review??null;e.runtimeEnabled=false;e.clientApproved=false;e.userAccepted=false;}
const result={schemaVersion:1,createdAt:new Date().toISOString(),scope:'2026-10-28 character worker source candidates only',runtimeEnabled:false,clientApproved:false,userAccepted:false,notRuntimeManifest:true,notice:'Original images and key poses are not finished clips. Do not adopt before alpha/identity/anchor/direction/sequence/client gates. Heavy local QA remains explicitly paused by parent until returned.',nativeSourceCount:entries.length,sourceStatePosePositions:stateNames.length*4,singlePhaseRepairPositions:1,idleDirectionPosePositions:own.length*4,approvedNewRuntimeStates:0,entries};
await writeFile(path.join(import.meta.dirname,'source-candidates-20261028.manifest.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({nativeSourceCount:entries.length,statePosePositions:result.sourceStatePosePositions,idleDirectionPosePositions:result.idleDirectionPosePositions,approvedNewRuntimeStates:0}));
