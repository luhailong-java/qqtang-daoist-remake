import fs from 'node:fs';
import path from 'node:path';
const [rawId,ownAppearance]=process.argv.slice(2),id=Number(rawId),root=process.cwd();
if(!Number.isSafeInteger(id)||!/^assets\/[\w/.-]+\.png$/.test(ownAppearance??'')||ownAppearance.includes('..'))throw Error('Explicit item ID and project own appearance PNG required');
const folder='assets/items/head-adornments',contract=JSON.parse(fs.readFileSync(`${folder}/references/world/${id}/source-contract.json`,'utf8'));
if(contract.itemId!==id||!fs.existsSync(ownAppearance))throw Error('Actual source contract or appearance absent');
const indices=contract.encodedRasterGroups.map(group=>group[0]);
const batches=Array.from({length:Math.ceil(indices.length/6)},(_,n)=>({key:String.fromCharCode(97+n),indices:indices.slice(n*6,n*6+6)}));
for(const batch of batches){const file=`${folder}/exports/world-${id}-${batch.key}.json`;if(fs.existsSync(file))throw Error(`Keep current crop specification: ${file}`);}
for(const batch of batches){
  const refs=[`${folder}/references/world/${id}/source-phases-${batch.key}.png`,'references/image/01-mail-event.png','references/image/team-ui-v2.png',ownAppearance];
  if(refs.some(file=>!fs.existsSync(file)))throw Error('Actual reference input absent');
  const spec={source:`${folder}/world/world-${id}-${batch.key}-v1.png`,version:`${id}-${batch.key}-v1`,referencePaths:refs.map(file=>path.join(root,file).replaceAll('\\','/')),
    frames:batch.indices.map(index=>{const source=contract.frames[index];if(!source.file)throw Error('Explicit source pixels absent');return{itemId:id,sourceFrameIndex:index,sourceReference:source.file,nativeFrameSize:source.nativeFrameSize,frameOffsetRaw:source.frameOffsetRaw};})};
  fs.writeFileSync(`${folder}/exports/world-${id}-${batch.key}.json`,JSON.stringify(spec,null,2)+'\n');
}
console.log(JSON.stringify({itemId:id,sourcePositions:contract.frames.length,uniqueRasters:indices.length,batches,worldAccepted:false}));
