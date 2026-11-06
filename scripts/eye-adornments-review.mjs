import fs from 'node:fs';
const [batch,note]=process.argv.slice(2),folder='assets/items/eye-adornments';
const file=`${folder}/qa/eye-adornments-${batch}-contact-256.png.source.json`;
const contact=JSON.parse(fs.readFileSync(file,'utf8'));
contact.actualVisualViewed=true;contact.actualVisualViewedAtUTC=new Date().toISOString();contact.visualNote=note;contact.inventoryCandidateOnly=true;
fs.writeFileSync(file,JSON.stringify(contact,null,2)+'\n');
const artFile=`${folder}/art.json`,art=JSON.parse(fs.readFileSync(artFile,'utf8'));
for(const item of art.items.filter(x=>x.batch===batch)){item.current256ContactActuallyViewed=true;item.currentVisualNote=note;item.accepted=false;item.worldAccepted=false;item.stateAccepted=false;item.runtimeAccepted=false;fs.writeFileSync(item.file+'.provenance.json',JSON.stringify(item,null,2)+'\n');}
fs.writeFileSync(artFile,JSON.stringify(art,null,2)+'\n');
const readme=`${folder}/README.md`;let text=fs.readFileSync(readme,'utf8');text=text.replace(/当前\d+\/72库存候选已导出。/,`当前${art.items.length}/72库存候选已导出。`);
const marker='\n## 当前批次记录\n';text=text.split(marker)[0]+marker+'\n'+[...new Set(art.items.map(x=>x.batch))].sort().map(b=>`- ${b.toUpperCase()}：6项，原生图/真实alpha裁切/256联系图均有记录，候选未接入。`).join('\n')+'\n';fs.writeFileSync(readme,text);
console.log(JSON.stringify({batch,inventoryCandidates:art.items.length,accepted:false}));
