// Data serialization and encoded-file SHA reads only. Does not import/run the renderer.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const base=path.dirname(fileURLToPath(import.meta.url));
const root='D:/work/qqtang-ui';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const readJson=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const save=(p,r)=>fs.writeFileSync(p,JSON.stringify(r,null,2)+'\n');
const proposalPath=path.join(base,'proposal.json'),proposalBytes=fs.readFileSync(proposalPath),proposal=JSON.parse(proposalBytes);
const legacyRootPath=path.resolve(base,'../../bind-static-v1.proposal.json'),legacyRootBytes=fs.readFileSync(legacyRootPath),legacyRoot=JSON.parse(legacyRootBytes);
const partsManifestPath=path.resolve(base,'../../parts-v1/manifest.json'),partsManifest=readJson(partsManifestPath);
const modulePath=path.join(root,'src/cutout-rig.js'),moduleBytes=fs.readFileSync(modulePath);
const sourceFiles=new Map();
function sourceFile(file,expectedSha){
  if(!/^assets\/[A-Za-z0-9_/-]+\.png$/.test(file)||file.includes('..'))throw new Error('Invalid candidate asset path: '+file);
  if(sourceFiles.has(file)){
    if(sourceFiles.get(file).expectedSha256!==expectedSha)throw new Error('Conflicting source SHA: '+file);
    return sourceFiles.get(file);
  }
  const p=path.join(root,file),exists=fs.existsSync(p)&&fs.statSync(p).isFile();
  if(!exists)throw new Error('Missing candidate source: '+file);
  // Encoded bytes only; no PNG header parsing or image decode.
  const b=fs.readFileSync(p),actualSha=hash(b);
  if(actualSha!==expectedSha)throw new Error('Current candidate source SHA differs: '+file);
  const result={file,exists:true,encodedByteLength:b.length,expectedSha256:expectedSha,actualSha256:actualSha,imageDecoded:false};
  sourceFiles.set(file,result);return result;
}
const sourceRecordFor=n=>{
 if(n.sourceGenerationRecord)return n.sourceGenerationRecord;
 if(n.paintedSourceGenerationRecord)return n.paintedSourceGenerationRecord;
 return null;
};
const candidateFiles=[];
let largestSerializationRoundoff=0;
for(const pose of proposal.twoContacts){
  const torso=pose.nodes.find(n=>n.id==='torso_pelvis');
  if(!torso)throw new Error('Torso source node absent');
  const topPos=torso.position,landmarks={};
  const nodes=pose.nodes.map(n=>{
    sourceFile(n.file,n.sha256);
    const originalPart=partsManifest.parts.find(p=>p.partId===n.id);
    const node={id:n.id,parent:n.id==='torso_pelvis'?null:'torso_pelvis',file:n.file,
      sourceSha256:n.sha256,pivot:[...n.pivot],
      bindPosition:n.id==='torso_pelvis'?[...n.position]:[n.position[0]-topPos[0],n.position[1]-topPos[1]],
      imageScale:n.scale,layer:n.layer,bindRotationDegrees:0,imageRotationDegrees:0,
      anatomicalSide:n.anatomicalSide??(n.id.startsWith('near_')?'RIGHT':n.id.startsWith('far_')?'LEFT':null),
      holdingIdentity:n.holdingIdentity??null,
      expectedStaticBoneMatrix:[1,0,0,1,...n.position],expectedStaticImageMatrix:[...n.imageMatrix],
      sourceNativeCropSize:n.sourceCropSize,sourceROI:n.sourceCropRect??n.originalNativeCrop?.sourceCropRect??originalPart?.sourceCropRect??null,
      sourceGenerationRecord:sourceRecordFor(n),
      sourceProposalNodeId:n.id,manualLandmarksApproved:false,
      derivation:'With zero rotations: child bone=T(torso position)*T(source absolute position minus torso position). imageScale affects image pixels only, not child bind translations.',
    };
    const points=n.manualLocalLandmarks??(n.originalNativeCrop?{
      hip:n.originalNativeCrop.hip,ankle:n.originalNativeCrop.ankle,toe:n.originalNativeCrop.toe,soleCandidate:n.originalNativeCrop.soleCandidate}:null);
    if(points){
      node.manualCropLocalLandmarks=points;
      node.sourceLandmarkEvidence='Existing hand-authored candidate landmarks preserved; not recovered native joints/root.';
      for(const [name,xy]of Object.entries(points))landmarks[n.id+'_'+name]={node:n.id,space:'image',point:xy,approved:false};
    }
    return node;
  });
  const ring=pose.newShoulderOcclusion;
  sourceFile(ring.file,ring.sha256);
  const roi=ring.sourceROI;
  nodes.push({id:'near_shoulder_ring',parent:'torso_pelvis',file:ring.file,sourceSha256:ring.sha256,
    pivot:[torso.pivot[0]-roi[0],torso.pivot[1]-roi[1]],bindPosition:[0,0],imageScale:torso.scale,
    layer:ring.layer,bindRotationDegrees:0,imageRotationDegrees:0,anatomicalSide:'RIGHT',
    expectedStaticBoneMatrix:[1,0,0,1,...topPos],expectedStaticImageMatrix:[...ring.cutoutImageMatrix],
    sourceNativeCropSize:[roi[2]-roi[0],roi[3]-roi[1]],
    sourceROI:roi,sourceTorso:ring.sourceTorso,sourceTorsoSha256:ring.sourceTorsoSha256,
    sourceRecord:ring.sourceRecord,sourceOwnershipRecord:proposal.sourceRingOwnership,
    sourceOwnership:{outerPolygonSource:ring.outerPolygonSource,excludedInnerHoleSource:ring.excludedInnerHoleSource,
      operation:'Existing same-source ring-only PNG, white sleeve and lower cloth already excluded by manual ownership cut; ordinary renderer node, no runtime mask feature required.'},
    contentRole:'same_source_torso_shoulder_occlusion',
    derivation:'Shares torso bone. Crop pivot=torso pivot minus sourceROI origin, so image matrix is exactly the torso matrix shifted by scale*ROI origin. Pivot may lie outside this cropped image; schema only requires a finite pair.',
    manualLandmarksApproved:false,
  });
  const arithmetic=[];
  for(const n of nodes){
    const pos=n.parent?[topPos[0]+n.bindPosition[0],topPos[1]+n.bindPosition[1]]:n.bindPosition;
    const m=[n.imageScale,0,0,n.imageScale,pos[0]-n.pivot[0]*n.imageScale,pos[1]-n.pivot[1]*n.imageScale];
    const roundoff=Math.max(...m.map((x,i)=>Math.abs(x-n.expectedStaticImageMatrix[i])));
    largestSerializationRoundoff=Math.max(largestSerializationRoundoff,roundoff);
    arithmetic.push({node:n.id,derivedOnlyByTranslationScaleAlgebra:m,expectedFromRenderedProposal:n.expectedStaticImageMatrix,maxAbsoluteDoubleRoundoff:roundoff});
  }
  const rig={
    schemaVersion:1,projectDisplayName:'灵葫大作战',identity:'daoist-child',direction:'E',contact:pose.contact,
    animationSource:'procedural_skeletal_animation',
    animationSourceScope:'Required cutout-rig.js renderer/schema classification only. No motion/animation was generated or authored in this file.',
    contentMotionKind:'static_painted_parts_assembly',renderedMotion:false,
    designCanvas:[...legacyRoot.designCanvas],referenceRoot:[...legacyRoot.referenceRoot],
    referenceRootEvidence:{file:rel(legacyRootPath),sha256:hash(legacyRootBytes),field:'referenceRoot',
      scope:legacyRoot.rootEvidence,notNativeOrWorldRoot:true},
    worldRoot:null,nativeTiming:null,sourceNativeTimingMs:null,
    nodes,actions:{static:{loop:false,tracks:{},contentMotionKind:'static_painted_parts_assembly'}},defaultAction:'static',
    landmarks,landmarksApproved:false,
    sourceProposal:{file:rel(proposalPath),sha256:hash(proposalBytes),contact:pose.contact},
    sourceRenderedReference:{file:pose.output,sha256:pose.sha256,record:pose.output+'.source.json'},
    sourceModule:{file:rel(modulePath),sha256:hash(moduleBytes),readAsTextOnly:true,moduleImportedOrExecuted:false},
    expectedStaticMatrixScope:'Design-plane image matrices before caller/root/size wrapper; copied exactly from the already rendered v2 proposal. No renderer execution during this data delivery.',
    futureDesignPlaneComparisonSetup:{root:[...legacyRoot.referenceRoot],size:legacyRoot.designCanvas[0],action:'static',pose:{},
      scope:'To cancel drawCutoutRig caller placement for a future independent comparison only; not an actual call or new gameplay root.'},
    serializationAlgebraOnly:arithmetic,futureComparisonSuggestedTolerance:1e-10,
    schemaRepresentation:{ordinaryPaintedNodes:true,emptyTrackStaticAction:true,ringAsOrdinaryPng:true,requiresModuleChange:false,
      method:'Read actual cutout-rig.js schema and transform code; no validateCutoutRig/sample/draw/import/test/image decode invoked.'},
    runtimeEnabled:false,runtimeAdopted:false,staticAccepted:false,fullAnimationAccepted:false,clientApproved:false,
    candidateStatus:'data_prepared_for_future_independent_acceptance',
  };
  const file=path.join(base,`rig-contact-${pose.contact}.candidate.json`);save(file,rig);
  candidateFiles.push({file:rel(file),sha256:hash(fs.readFileSync(file)),contact:pose.contact,nodes:nodes.length,
    actions:{static:{loop:false,trackCount:0}},referenceRoot:rig.referenceRoot});
}
save(path.join(base,'rig-candidates.delivery.json'),{
  schemaVersion:1,createdAtUTC:new Date().toISOString(),operation:'Static JSON data serialization, source path existence and encoded-byte SHA only. No image decode, model call, renderer import, rendering, test, browser or runtime.',
  candidates:candidateFiles,sourceFiles:[...sourceFiles.values()],uniqueEncodedSources:sourceFiles.size,
  serializationAlgebraMaximumDoubleRoundoff:largestSerializationRoundoff,
  note:'Roundoff is ordinary arithmetic while serializing relative translations, not a module/renderer test or adoption gate.',
  runtimeEnabled:false,staticAccepted:false,fullAnimationAccepted:false,worldRoot:null,nativeTiming:null,
});
console.log(JSON.stringify({candidates:candidateFiles.map(x=>({file:x.file,nodes:x.nodes})),uniqueEncodedSources:sourceFiles.size,
  maximumSerializationRoundoff:largestSerializationRoundoff,imageDecodes:0,rendererExecutions:0,runtimeEnabled:false}));
