// Five explicit current portrait source JSONs only; no image reads or shared manifest/Git mutation.
import{readFile,writeFile}from'node:fs/promises';
import path from'node:path';
const base=import.meta.dirname,root=path.resolve(base,'../../..');
const current=JSON.parse(await readFile(path.join(base,'manifest.json'),'utf8').catch(()=>'{"counts":{"portraits":0}}'));
if((current.counts?.portraits??0)>5)throw Error('This initial-five writer cannot replace the completed20-slot registry; use finalize-roster20.py.');
const map=JSON.parse(await readFile(path.join(root,'assets/characters/motion-generated/roster-skin-mapping-20261028.json'),'utf8'));
const defs=[
 ['cloud-tortoise-warden',11,'Broad warm-tan face/thick dark brows, charcoal short hair and turtle clasp/ribbons remain clear. Lower-right original turtle tally edge remains in the single crop.'],
 ['pine-cloud-elder',13,'White bun/pine pin/brows, elder face and full long beard remain clear. Tiny original hand/whisk edges remain at the lower shoulder crop; no part moved.'],
 ['jade-craft-artisan',14,'Full black bob/short braids, LEFT cloud clip/beads, olive eyes and freckles remain clear. Natural mallet/cloud edges remain at bottom sides.'],
 ['paper-kite-wanderer',15,'Complete broad bamboo hat/cloud pin/ribbons and both braids retained. Face is smaller because full hat and hair share one uniform crop scale;256 eyes readable, smaller UI sizes unverified.'],
 ['cinnabar-seal-keeper',16,'Full auburn curls/jade band/seal pin and adult almond eyes/freckles remain clear. Source stamp edge remains naturally at lower-left; no hair top was reconstructed.']
];
const entries=[];
for(const[id,role,observation]of defs){
 const file=id+'-256.png',recordPath=path.join(base,file+'.source.json'),r=JSON.parse(await readFile(recordPath,'utf8'));
 const slot=map.slots.find(s=>s.sourceRoleId===role);if(!slot||slot.appearance.identityId!==id||r.sourceRoleId!==role||r.identityId!==id||r.source.file!==slot.appearance.master)throw Error('Exact20-slot source mapping mismatch '+id);
 r.output.actual256Viewed=true;r.output.visualObservation=observation;r.output.visibleSolidHaloObserved=false;r.output.fullHeadHairHeadwearFacePreserved=true;r.output.smallUIReadabilityBelow256Verified=false;r.status='portrait_candidate_actual256_viewed_pending_ui_adoption';r.runtimeAdopted=false;r.clientApproved=false;
 await writeFile(recordPath,JSON.stringify(r,null,2)+'\n');
 entries.push({sourceRoleId:role,identityId:id,name:r.name,file:r.file,sha256:r.sha256,sourceRecord:r.file+'.source.json',sourceMaster:r.source.file,sourceMasterSha256:r.source.sha256,sourceMasterNativeSize:r.source.nativeGenerationSizeFromRecord,sourceGenerationRecord:r.source.sourceGenerationRecord,sourceActualModel:r.source.actualModel,sourceActualQuality:r.source.actualQuality,sourceCropLTRB:r.operation.sourceCropLTRB,sourceCropSize:r.operation.sourceCropSize,uniformScale:r.operation.uniformScale,resampledCropSize:r.operation.resampledCropSize,placementXY:r.operation.placementXY,canvas:[256,256],alphaExtrema:r.output.alphaExtrema,alpha8MarginsLTRB:r.output.alpha8MarginsLTRB,alpha8OuterEdges:r.output.alpha8OuterEdges,preview:r.output.preview,visualObservation:observation,status:r.status,runtimeAdopted:false,clientApproved:false});
}
const manifest={schemaVersion:1,updatedAt:new Date().toISOString(),scope:'Only five existing new-own-identity masters in20-slot mapping: IDs11/13/14/15/16. UI portrait derivatives, not five new characters or new generations.',sourceMapping:'assets/characters/motion-generated/roster-skin-mapping-20261028.json',counts:{existingIdentitiesCovered:5,portraits:5,newCharacters:0,newImageGenerations:0,runtimeAdoptions:0},processing:'Manual one-piece complete head/hair/headwear/face/short-shoulder rectangular ROI; uniform premultiplied-alpha LANCZOS downscale, all crop dimension ratios exact after integer rasterization; centered256 transparent canvas with at least14px visible-edge margins. No component movement, mirroring or AI redraw.',entries,runtimeAdopted:false,clientApproved:false,machineScope:'Only explicit five masters read/hashed/decoded individually and five256px portraits viewed. No sweep of20 old characters, tests/browser/build/src/global runtime or Git changes.'};
await writeFile(path.join(base,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({manifest:'assets/characters/portraits-candidates/manifest.json',...manifest.counts,sourceRoleIds:entries.map(e=>e.sourceRoleId)}));
