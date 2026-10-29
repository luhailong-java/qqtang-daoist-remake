// Text metadata only after viewing the full unscaled256-per-cell contact and forge/compose individually.
import{readFile,writeFile}from'node:fs/promises';
import path from'node:path';
const base=import.meta.dirname;
const m=JSON.parse(await readFile(path.join(base,'manifest.json'),'utf8'));
const observations={
 friends:'Two original overlapping symbolic Daoist busts and gold cloud base intact.',
 'add-friend':'Single bust and clear gold plus, hair/crown/cloud silhouette intact.',
 'remove-friend':'White-haired bust and cinnabar minus intact; no clipped minus badge.',
 'private-chat':'Envelope within jade speech bubble, whisper ribbon and red tassel intact.',
 guild:'Upright banner/crest, top tip and both lower tassels intact.',
 task:'Checkmark scroll and original red tassel intact.',
 backpack:'Whole jade pouch/cloud embroidery, top cloth/cords and both tassels intact.',
 warehouse:'Closed storage chest and gold lock/latch intact.',
 forge:'Individually viewed256: anvil, complete hammer shaft/head and long red tassel are owned together; no compose bead/pot fragment.',
 compose:'Individually viewed256: both jade beads, joining glow and whole tripod vessel/legs intact; no forge handle/tassel fragment.',
 'save-replay':'Play scroll, down-arrow and red tassel intact.',
 'cancel-replay':'Matching scroll, clear stop square and tassel intact.',
 'pet-card':'Paw/bell card and cloud/tassel frame intact.',
 fullscreen:'All four chunky jade right-angle corners retained as one intended icon; centre stays transparent.',
 mute:'Whole bell, diagonal slash, bottom bead and tassel intact.',
 reconnect:'Both chain links, warm spark and cloud ends intact.'
};
for(const r of m.entries){
 r.actual256ContactViewed=true;r.individuallyViewed256=['forge','compose'].includes(r.id);r.localVisualObservation=observations[r.id];r.visibleSolidColorHaloObserved=false;r.localSliceReviewPassed=true;r.status='slice_candidate_local_cut_and_visual_review_passed_ui_client_pending';r.runtimeAdopted=false;r.clientApproved=false;
 await writeFile(path.join(base,r.id+'.png.provenance.json'),JSON.stringify(r,null,2)+'\n');
}
m.actual256PerCellContactViewed=true;m.contactReview='assets/ui/semantic-extra/SLICE_REVIEW_20261028.md';m.localSliceReviewPassed=true;m.status='16_slice_candidates_not_runtime_adopted';m.pending=['Actual UI24–48px semantic readability/contrast and interaction states','Root UI/CSS adoption and client validation after machine slot return'];
await writeFile(path.join(base,'manifest.json'),JSON.stringify(m,null,2)+'\n');
console.log(JSON.stringify({icons:m.entries.length,sourceImages:m.sourceImageCount,sourceAlpha8VisiblePixels:m.gate.visiblePixels,allSourceGates:m.gate.all16SourceChecksPassed,actualContactViewed:true,individuallyViewed:['forge','compose'],runtimeAdopted:false}));
