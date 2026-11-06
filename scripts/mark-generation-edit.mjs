import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
const root=path.resolve(import.meta.dirname,'..');const [image,target]=process.argv.slice(2);
if(!image||!target)throw new Error('Usage: node mark-generation-edit.mjs image-file actual-edit-target');
const recordPath=path.join(root,image+'.generation.json'),record=JSON.parse(await readFile(recordPath,'utf8'));
const targetPath=path.resolve(root,target),sha=createHash('sha256').update(await readFile(targetPath)).digest('hex');
const reference=record.references.find(r=>path.resolve(root,r.path)===targetPath&&r.sha256===sha);
if(!reference)throw new Error('Edit target is not an actual recorded reference with the same bytes');
let previousRecord=null;try{await readFile(targetPath+'.generation.json');previousRecord=target+'.generation.json';}catch(error){if(error.code!=='ENOENT')throw error;}
reference.purpose='actual edit target; preserve useful design while correcting requested geometry';
record.operation='built-in AI image edit conditioned on the actual target reference; no program pixel editing';
record.editOf={file:target,sha256:sha,generationRecord:previousRecord};
for(const suffix of ['.provenance.json','.source.json']){try{await readFile(targetPath+suffix);record.editOf.derivationRecord=target+suffix;break;}catch(error){if(error.code!=='ENOENT')throw error;}}
record.annotationNote='Edit relationship clarified from the actual submitted target reference and prompt; original model, quality, timestamp and submission fields unchanged.';
await writeFile(recordPath,JSON.stringify(record,null,2)+'\n');console.log(`Recorded actual edit relationship: ${image} <- ${target}`);
