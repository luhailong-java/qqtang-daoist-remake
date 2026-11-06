import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root=process.cwd(),folder=path.join(root,'assets/items/eye-adornments');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const catalogFile=path.join(root,'references/qqtang-item-data/catalog.json'),catalogBytes=fs.readFileSync(catalogFile),catalog=JSON.parse(catalogBytes);
const items=catalog.items.filter(i=>i.category==='eye').sort((a,b)=>a.item_id-b.item_id);
if(items.length!==72||new Set(items.map(i=>i.item_id)).size!==72)throw new Error('Actual eye scope changed');
fs.mkdirSync(folder,{recursive:true});
const batches=Array.from({length:12},(_,i)=>({batch:String.fromCharCode(97+i),ids:items.slice(i*6,i*6+6).map(x=>x.item_id)}));
fs.writeFileSync(path.join(folder,'source-contract.json'),JSON.stringify({schemaVersion:1,projectDisplayName:'灵葫大作战',sourceCategory:'eye',
 categoryDisplayName:'冠饰与趣味装饰',actualScope:'Crowns/helmets/hair ornaments/goggles and flowers, balls, shields, handheld signs and playful visual props; English eye is not a reliable semantic description.',
 sourceCatalog:{file:'references/qqtang-item-data/catalog.json',sha256:hash(catalogBytes),sourceArchiveSha256:catalog.sourceArchiveSha256,
  sourceMember:catalog.sourceMember,sourceMemberSha256:catalog.sourceMemberSha256,officialOriginalAuthenticity:catalog.officialOriginalAuthenticity},
 actualCount:items.length,batches,items,scope:'Inventory icon candidates only, no world/state/main-game contract adoption',
 worldAccepted:false,stateAccepted:false,runtimeAccepted:false},null,2)+'\n');
if(!fs.existsSync(path.join(folder,'art.json')))fs.writeFileSync(path.join(folder,'art.json'),JSON.stringify({schemaVersion:1,status:'original-painted-candidates',
 sourceCategory:'eye',categoryDisplayName:'冠饰与趣味装饰',items:[],worldAccepted:false,stateAccepted:false,runtimeAccepted:false},null,2)+'\n');
const examples=[];
for(const letter of 'abcdefghi'){
 const gp=`assets/items/surroundings/surroundings-${letter}-v1.png.generation.json`,ep=`docs/surroundings-${letter}-export.json`;
 const gb=fs.readFileSync(gp),eb=fs.readFileSync(ep),g=JSON.parse(gb),e=JSON.parse(eb);
 examples.push({batch:letter,generation:{file:gp,sha256:hash(gb),native:[g.width,g.height],actualModel:g.actualModel,actualQuality:g.actualQuality},
  export:{file:ep,sha256:hash(eb),assetDirectory:e.assetDirectory,items:e.items.map(i=>({itemId:i.itemId,rect:i.rect}))}});
}
fs.writeFileSync('docs/eye-adornments-source-read.json',JSON.stringify({readAtUTC:new Date().toISOString(),actualCatalogCount:72,
 actualCategoryContent:'冠饰/头盔/发带/护目镜以及球花盾灯标牌等趣味装饰',surroundingsReadmeActuallyRead:true,examplesAtoIRead:examples,
 genericScriptsReadOnly:['scripts/extract-item-art-reference.py','scripts/make-item-structure-board.py','scripts/export-item-art.py'],
 extractionLimit:'1–6 explicit inventory IDs per call',worldStateRuntimeAccepted:false},null,2)+'\n');
console.log(JSON.stringify({actualCategory:'eye',count:72,batches}));
