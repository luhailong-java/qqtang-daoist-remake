// Re-read complete current files; reveal any changed text before another image call.
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..'),imageRoot=path.resolve(root,'..','image');
const previouslyRead={
  'AGENTS.md':'b247ee3eda4d04bc367ca6c36ed220a4ca54eb4179aa573df57f357861e63d6b',
  'config/image-generation.json':'9d8a6972715aedfe56438cdbb34c375d94f06709a69cd2c1284dfba35fec66d1',
  'docs/IMAGE_MODEL_POLICY.md':'5f1ee419193e5e9ef9db5b651508f4e558523238c8ca5f49d75f5d9453b3bc02'
};
for(const [file,expected]of Object.entries(previouslyRead)){
  const bytes=await readFile(path.join(imageRoot,file)),sha256=createHash('sha256').update(bytes).digest('hex');
  console.log(JSON.stringify({file:path.join(imageRoot,file),sha256,completeBytesRead:bytes.length,contentComparedToPriorFullRead:sha256===expected?'unchanged':'changed'}));
  if(sha256!==expected)console.log(bytes.toString('utf8'));
}
const config=JSON.parse((await readFile(path.join(imageRoot,'config/image-generation.json'),'utf8')).replace(/^\uFEFF/,''));
console.log(JSON.stringify({readAt:new Date().toISOString(),configTarget:config,actualModel:null,actualQuality:null,route:'builtin image_gen; no model/quality selectors exposed'}));
