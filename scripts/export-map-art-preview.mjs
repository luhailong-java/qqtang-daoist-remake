import {readFile,writeFile,mkdir} from 'node:fs/promises';
import path from 'node:path';
import {loadMapCatalog} from '../server/map-catalog.mjs';
import {createMapArtCatalog,sourceMapDrawList} from '../src/map-art.js';
const root=path.resolve(import.meta.dirname,'..');
const id=process.argv[2]||'source-201';
if(!/^source-\d+$/.test(id))throw new Error('Expected source map ID');
const directory=JSON.parse(await readFile(path.join(root,'assets/maps/runtime-manifests.json')));
const manifests=[];
for(const file of directory.manifests){try{manifests.push(JSON.parse(await readFile(path.join(root,file))));}catch(error){if(error.code!=='ENOENT')throw error;}}
const source=(await loadMapCatalog()).getRuntime(id);
const plan={id,name:source.name,width:source.width*40,height:source.height*40,
  sourceMapSha256:source.source.sha256,status:'painted-scene-candidate-not-gameplay-screenshot',
  ...sourceMapDrawList(source,createMapArtCatalog(manifests))};
await mkdir(path.join(root,'.artifacts'),{recursive:true});
await writeFile(path.join(root,'.artifacts',`map-art-plan-${id}.json`),JSON.stringify(plan,null,2)+'\n');
console.log(JSON.stringify({id,objects:plan.commands.length,missing:plan.missingElementIds}));
