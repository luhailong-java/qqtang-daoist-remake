// Current new-sheet JSON only. No image decode/scan/import or runtime change.
import{readFile,writeFile}from'node:fs/promises';
import path from'node:path';
const selected=[['cloud-tortoise-warden','玄龟','v2'],['pine-cloud-elder','松翁','v1'],['jade-craft-artisan','玉匠','v2'],['paper-kite-wanderer','纸鸢','v2'],['cinnabar-seal-keeper','赤砂','v1']];
const availableVersions={ 'cloud-tortoise-warden':['v1','v2'],'pine-cloud-elder':['v1'],'jade-craft-artisan':['v1','v2'],'paper-kite-wanderer':['v1','v2'],'cinnabar-seal-keeper':['v1']};
const base=import.meta.dirname;
const report={schemaVersion:1,createdAt:new Date().toISOString(),scope:'Five new own identities: current2x2 orthogonal idle STILL sources only, not movement clips or runtime adoption.',runtimeEnabled:false,clientApproved:false,characters:[],sourceResults:[]};
for(const[id,name,version]of selected){
 for(const v of availableVersions[id]){
  const file=id+'/idle-four-directions-'+v+'.png';
  const record=JSON.parse(await readFile(path.join(base,file+'.generation.json'),'utf8'));
  const qaFile=id+'/qa/idle-four-directions-'+v+'.alpha-review.json';
  const qa=JSON.parse(await readFile(path.join(base,qaFile),'utf8'));
  const selectedCurrent=v===version;
  const actualOrder=record.review.actualVisualOrder;
  const missing=['N','E','S','W'].filter(d=>!actualOrder.includes(d));
  const clearSeams=Object.values(qa.atlas.alpha8SeamCounts).every(n=>n===0);
  const clearEdges=Object.values(qa.alpha8OuterEdges).every(n=>n===0);
  qa.atlas.requestedOrder=record.review.requestedOrder??['N','E','S','W'];
  qa.actualVisualViewed=selectedCurrent||id==='paper-kite-wanderer';
  if(qa.actualVisualViewed)qa.visualObservation='Ivory diagnostic actually viewed; no obvious solid color halo. Direction/prop/face evidence is a static candidate review, not runtime approval.';
  await writeFile(path.join(base,qaFile),JSON.stringify(qa,null,2)+'\n');
  let status=missing.length?'not_passed_missing_east_after_two_attempts':!clearSeams?'not_passed_cell_boundary_crossing':'direction_still_candidate_shared_root_margin_identity_details_pending';
  record.status=status;record.review.qa=qaFile;record.review.actualAlphaEvidence={extrema:qa.alphaExtrema,outerEdges:qa.alpha8OuterEdges,seams:qa.atlas.alpha8SeamCounts};record.review.ivoryViewed=qa.actualVisualViewed;record.review.sharedRootApproved=false;record.review.runtimeEnabled=false;record.review.pending=['requested per-cell margins/450px height/shared foot-root not strictly achieved','asymmetric hair-clip/equipment near-far occlusion and cross-direction scale','source ownership/registration and actual client'];
  if(missing.length)record.review.pending.unshift('TrueE absent; duplicateW must not be relabeled or mirrored');
  await writeFile(path.join(base,file+'.generation.json'),JSON.stringify(record,null,2)+'\n');
  const entry={id,name,file:'assets/characters/motion-generated/roster-expansion/'+file,selectedCurrent,sha256:record.sha256,generationRecord:file+'.generation.json',nativeSize:[record.width,record.height],actualModel:record.actualModel??null,actualQuality:record.actualQuality??null,actualOrder,missingDirections:missing,status,sourceAlphaEvidence:qaFile,seamAlpha8Clear:clearSeams,outerEdgeAlpha8Clear:clearEdges,cellSize:qa.atlas.cellSize,nominalCells:qa.cells,sourceOwnershipApproved:false,sharedRoot:null,uniformScaleToRuntime:null,runtimeEnabled:false,clientApproved:false};
  report.sourceResults.push(entry);
  if(selectedCurrent)report.characters.push({...entry,master:id+'/master.png',completeFourDirectionPresence:missing.length===0,staticDirectionPairCount:new Set(actualOrder).size,contract:'Use one common canvas/scale for all directions, fixed per-direction artist-landmark root for future whole sequences, never per-frame bbox/lowest-foot fit. No registration has been applied in this batch.',next:missing.length?'Future focusedE missing-view work after two unsuccessful sheet attempts; current same-point stopped.':clearSeams?'Physical ownership/root/margin/asymmetric-equipment checks and one-source registration review before slicing/adoption.':'AI reframe or exact ownership repair before any equal-cell slice.'});
 }
}
report.totals={identities:5,sourceResults:report.sourceResults.length,currentSelectedSheets:5,currentSelectedPosePositions:20,currentUniqueIdentityDirectionPairs:report.characters.reduce((s,c)=>s+c.staticDirectionPairCount,0),completeFourDirectionPresence:report.characters.filter(c=>c.completeFourDirectionPresence).length,currentSheetsClearAlpha8EdgesAndSeams:report.characters.filter(c=>c.outerEdgeAlpha8Clear&&c.seamAlpha8Clear).length,sharedRootApproved:0,runtimeApproved:0,importedFrames:0};
await writeFile(path.join(base,'idle-directions-candidates-20261028.manifest.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.totals));for(const c of report.characters)console.log(JSON.stringify({id:c.id,version:c.file,actualOrder:c.actualOrder,missing:c.missingDirections,seamClear:c.seamAlpha8Clear,root:c.sharedRoot}));
