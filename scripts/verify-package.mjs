import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=path.resolve(import.meta.dirname,'..');
const {createAppServer}=await import(pathToFileURL(path.join(root,'dist/server/app.mjs')));
const app=createAppServer({port:0});
try{
  await app.start();
  const address=app.server.address();
  const base=`http://127.0.0.1:${address.port}`;
  const health=await (await fetch(base+'/api/health')).json();
  if(!health.authoritative)throw new Error('Packaged server is not authoritative');
  for(const file of ['index.html','src/app.js','src/net.js','src/art.js','src/game.js','assets/art.json','assets/qqtang-characters-v2.png']){
    const response=await fetch(base+'/'+file);
    if(!response.ok)throw new Error(`Missing packaged file: ${file}`);
    const actual=Buffer.from(await response.arrayBuffer());
    const expected=await readFile(path.join(root,'dist',file));
    if(createHash('sha256').update(actual).digest('hex')!==createHash('sha256').update(expected).digest('hex'))throw new Error(`Packaged response mismatch: ${file}`);
  }
  console.log(JSON.stringify({packagedServer:true,health:health.name,verifiedFiles:7,port:address.port}));
}finally{await app.close();}
