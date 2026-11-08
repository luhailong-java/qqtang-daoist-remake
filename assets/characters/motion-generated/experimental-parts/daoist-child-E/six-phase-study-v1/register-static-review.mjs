import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const mp=path.join(base,'manifest.json'),manifest=JSON.parse(fs.readFileSync(mp,'utf8'));
const status='inspection_only_six_assembled_slots_not_native_six_frames';
manifest.actuallyViewedContactSheets=true;manifest.actualViewedEvidence='static-review.json';manifest.reviewStatus=status;
fs.writeFileSync(mp,JSON.stringify(manifest,null,2)+'\n');
const review={
 schemaVersion:1,projectDisplayName:'灵葫大作战',reviewedAtUTC:new Date().toISOString(),
 manifestSha256:sha(fs.readFileSync(mp)),status,
 actuallyViewed:['six-poses-627-contact.png','six-poses-96-contact.png'].map(n=>({file:n,sha256:sha(fs.readFileSync(path.join(base,n)))})),
 renderCounts:{exactByteReused627:4,exactByteReused96:4,new627Combinations:2,newModelGenerations:0},
 byteReuseEvidence:manifest.frames.filter(f=>f.sources.byteIdenticalReuse).map(f=>({slot:f.index,studyFile:f.file,studySha256:f.sha256,
   originalFile:f.sources.source,originalSha256:f.sources.sourceSha256,byteCopyNotReRender:true})),
 observations:{
  newSlot2:'NearRIGHT backward support from oldContactB plus farLEFT raised fromP1 is readable as a rear-support/raised-forward static combination. No obvious new trouser break or source edge clipping observed.',
  newSlot5:'NearRIGHT raised fromP2 plus farLEFT backward support from oldContactA remains readable. Near raised boot partly overlaps lower far leg/boot area, without relabelling layers.',
  fixedUpper:'Head, torso, both arms and shoulder ring remain identical in all6slots. This intentionally contains no arm swing, body weight shift or hair motion.',
  heldLegs:'FarRaised is the same piece/matrix in slots1/2; nearRaised the same piece/matrix in4/5. One leg therefore holds while the other switches source shape.',
  inferredTransitionRisk:'Static differences suggest hold/pop risk under hard120ms cuts; this is an inference from the contact sheets and inherited matrices, not a watched client loop or motion-quality acceptance.',
  small:'All six96 canvases preserve the same full627 scale. Character/gourd and raised-foot differences are visible, ankle layering remains crowded; actor is about68px high.',
 },
 gif:{file:'six-poses-inspection-120ms.gif',exported:true,canvas:[96,96],sharedPaletteColors:256,
   durationMsPerFrame:120,inspectionTimingOnly:true,nativeTimingMs:null,loopExtension:null,playsOnce:true,
   dynamicallyViewedInClientOrBrowser:false,doNotClaimGIFMotionQA:true},
 matrixOrPivotOrOffsetRefit:false,newNearFarSwap:false,sourceAlphaModified:false,
 sourceCorrespondence:false,nativeTimingMs:null,worldRoot:null,loop:false,runtimeAccepted:false,
 fullWalkAccepted:false,formalRigCreated:false,testsBuildBrowserExecuted:false,
 nextAction:'Preserve this one assembly study and explicit hard-cut/depth risks; no retry, new imagegen, runtime integration or native timing/source-match claim.',
};
fs.writeFileSync(path.join(base,'static-review.json'),JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify({file:path.join(base,'static-review.json'),status,byteReused:4,newCombinations:2,gifLoop:false,runtimeAccepted:false}));
