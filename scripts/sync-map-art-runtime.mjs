import {readdir,readFile,writeFile} from 'node:fs/promises';
const root=new URL('../',import.meta.url),directory=new URL('assets/maps/',root),manifests=[];
for(const entry of await readdir(directory,{withFileTypes:true})){
  if(!entry.isDirectory())continue;
  const file=`assets/maps/${entry.name}/art.json`;
  try{const data=JSON.parse(await readFile(new URL(file,root)));if(data.tilePixels===40&&Array.isArray(data.pieces))manifests.push(file);}
  catch(error){if(error.code!=='ENOENT')throw error;}
}
manifests.sort();
await writeFile(new URL('assets/maps/runtime-manifests.json',root),JSON.stringify({schemaVersion:1,status:'painted-candidates-awaiting-in-game-validation',manifests},null,2)+'\n');
console.log(JSON.stringify({runtimeManifests:manifests}));
