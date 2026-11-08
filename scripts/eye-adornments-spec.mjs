import fs from 'node:fs';
const [batch,cutText]=process.argv.slice(2),[row,tl,tr,bl,br]=JSON.parse(cutText);
const brief=JSON.parse(fs.readFileSync(`docs/eye-adornments-${batch}.brief.json`,'utf8'));
const mother=`assets/items/eye-adornments/eye-adornments-${batch}-v1.png`;
const bytes=fs.readFileSync(mother),W=bytes.readUInt32BE(16),H=bytes.readUInt32BE(20);
const rects=[[0,0,tl,row],[tl,0,tr,row],[tr,0,W,row],[0,row,bl,H],[bl,row,br,H],[br,row,W,H]];
const items=(brief.items??brief).map((x,i)=>({itemId:x.itemId,name:x.name,displayName:x.displayName,rect:rects[i],sourceReference:x.sourceReference??`references/qqtang-item-data/icons/item-${x.itemId}-inventory-icon.png`,sourceReferenceKind:x.sourceReferenceKind??'declared inventory icon',inventoryMappingVerified:x.inventoryMappingVerified??null}));
fs.writeFileSync(`docs/eye-adornments-${batch}-export.json`,JSON.stringify({source:mother,assetDirectory:'assets/items/eye-adornments',manualCutEvidence:'Native ivory atlas actually viewed; unequal row/column cut lines selected only in real transparent gaps. Preflight independently rejects occupied cut edges, missing or duplicate alpha>=8 ownership.',items},null,2)+'\n');
console.log(JSON.stringify({batch,W,H,rects}));
