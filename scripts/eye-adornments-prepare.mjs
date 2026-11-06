import fs from 'node:fs';
const batch=process.argv[2],brief=JSON.parse(fs.readFileSync(`docs/eye-adornments-${batch}.brief.json`,'utf8'));
const slots=['TOP LEFT','TOP MIDDLE','TOP RIGHT','BOTTOM LEFT','BOTTOM MIDDLE','BOTTOM RIGHT'];
if(brief.items.length!==6)throw new Error('One atlas requires exactly six explicit items');
const prompt=`Create one genuinely transparent RGBA inventory-art atlas for our original Daoist chibi game《灵葫大作战》. Requested1536x1024 landscape, exactly SIX independent complete ornaments,3columns×2rows. Inventory objects only, no full character or UI screen. No text/IDs, labels, blue inventory frames, stands, shadows, aura backgrounds or ground rings. Every complete item must be well inside its own cell with at least40px empty transparent gap. No touching/overlap between items or canvas edges. Fine high-definition hand-painted finish, rounded polished forms, restrained warm-gold and jade highlights, clean readable silhouette, not plastic3D or pixel texture.

ACTUAL INPUTS: Image1 contains the six actual source appearance references in this row order, STRUCTURE/CONTENT ONLY; inventory/stand exceptions are explicitly described below. The old pixel art is not our style or identity; ignore all blue square UI frames/ground shadows. Do not copy QQ faces, source game logos, anime/film/partner characters, Olympic or licensed symbols. Images2/3 are our confirmed primary mail/team Daoist Q style: jade/teal, warm ivory, gold filigree, soft finely painted material; source colors that distinguish individual objects may remain as accents. No UI/background/people from these references in final atlas.

${brief.sourceVisualNotes??''}
Exact six-grid order:
${brief.items.map((x,i)=>`${slots[i]} item${x.itemId} / ${x.displayName}: ${x.designBrief}`).join('\n')}

Redraw these actual source concepts as independent original Daoist Q accessories, with complete edges, handles, petals, dangles and transparent holes. Do not repeat one generic crown in all six cells. No additional duplicate objects. One6-object atlas is ONE image generation; later crops are derivatives, not6 new images. Inventory candidate only, not equipped world animation. Highest host-provided image quality target.`;
fs.writeFileSync(`docs/eye-adornments-${batch}.prompt.txt`,prompt+'\n');
console.log(prompt);
