// Final text-only review markers; no source-image read/decode or runtime/Git mutation.
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
const base=path.join(import.meta.dirname,'native-role9-evidence');
for(const[name,direction]of [['group0-face-direction-probe','E'],['group2-direction-probe','W'],['group0-four-phase-board','E'],['group0-six-phase-board','E']]){
 const file=path.join(base,name+'.json'),r=JSON.parse(await readFile(file,'utf8'));
 r.actualVisualViewed=true;r.observedCardinalDirection=direction;r.directionEvidence=direction==='E'?'Actual face0 and all six-phase-board noses/mouths point screen-right; no directory-order assumption.':'Actual representative face12 nose/mouth point screen-left; initial shoe-only guess discarded.';
 r.review='assets/characters/motion-generated/daoist-child/native-role9-evidence/NATIVE_E_GAIT_REVIEW_20261028.md';
 for(const p of r.records||[]){p.cardinalDirectionNotYetVerified=false;p.observedCardinalDirection=direction;}
 await writeFile(file,JSON.stringify(r,null,2)+'\n');
}
const p=path.join(base,'group0-e-lowerbody-review.json'),r=JSON.parse(await readFile(p,'utf8'));r.actualVisualViewed=true;await writeFile(p,JSON.stringify(r,null,2)+'\n');
const gp=path.join(import.meta.dirname,'east-native-reference-contact-pair-v1.png.generation.json'),g=JSON.parse(await readFile(gp,'utf8'));g.review.actualVisualViewed=true;g.review.ivoryPreviewViewed=true;g.review.poseReview='assets/characters/motion-generated/daoist-child/east-native-reference-contact-pair-v1.review.md';await writeFile(gp,JSON.stringify(g,null,2)+'\n');
console.log(JSON.stringify({updatedMetadataRecords:6,sourceImagesDecoded:0,status:'source_E_verified_new_key_pair_not_passed'}));
