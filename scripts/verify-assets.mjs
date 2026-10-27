import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
for(const file of ['qqtang-world-v2.png','qqtang-characters-v2.png','game-atlas.png']){
  const bytes=await readFile(path.join(root,'assets',file));
  if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error(`${file}: invalid PNG / LFS pointer`);
  const record=JSON.parse(await readFile(path.join(root,'assets',file+'.generation.json'),'utf8'));
  if(record.sha256!==createHash('sha256').update(bytes).digest('hex'))throw new Error(`${file}: SHA256 mismatch`);
  if(record.width!==bytes.readUInt32BE(16)||record.height!==bytes.readUInt32BE(20))throw new Error(`${file}: dimensions mismatch`);
  if(record.submittedParameters.model!==null||record.actualModel!==null)throw new Error(`${file}: model evidence requires review`);
  console.log(`${file}: PNG ${record.width}x${record.height}, hash and provenance passed`);
}
