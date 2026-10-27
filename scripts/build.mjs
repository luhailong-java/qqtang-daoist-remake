import {cp,mkdir,rm} from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..'); const out=path.join(root,'dist');
if(out!==path.join(root,'dist'))throw new Error('Invalid output directory');
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
for(const name of ['index.html','maps.html','src','assets','server','scripts','docs','references','tests','package.json','README.md','.gitignore','启动本地预览.cmd'])await cp(path.join(root,name),path.join(out,name),{recursive:true});
console.log(`QQ堂 client + local authority server ready: ${out}`);
