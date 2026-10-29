import{readFile,writeFile}from'node:fs/promises';
import{createHash}from'node:crypto';
import path from'node:path';
const root=path.resolve(import.meta.dirname,'../../..');
const spec=JSON.parse(await readFile(path.resolve(root,process.argv[2]),'utf8'));
const bytes=await readFile(path.resolve(root,spec.file));
if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error('Not a real PNG');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const refs=await Promise.all(spec.references.map(async ref=>({...ref,sha256:sha(await readFile(ref.path))})));
const config=JSON.parse(await readFile('D:/work/image/config/image-generation.json','utf8'));
const record={schemaVersion:1,file:spec.file,sha256:sha(bytes),generatedAt:new Date().toISOString(),timeEvidence:'UTC registration after builtin tool result; provider creation timestamp not exposed',
 width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),format:'PNG',tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',configSnapshot:config,
 submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:refs.map(ref=>ref.path)},actualModel:null,actualQuality:null,
 unverifiedReason:'宿主管理，工具未开放型号/质量选择器，实际返回未披露可核实版本与质量。',prompt:spec.prompt,promptSha256:sha(await readFile(path.resolve(root,spec.prompt))),references:refs,
 evidence:{hostSource:spec.hostSource,returnedFields:['image_url','output_hint'],selectorsExposed:false},editTarget:spec.editTarget||null,review:spec.review||null,
 status:spec.status||'source_pending_alpha_anchor_and_runtime_review',clientApproved:false,userAccepted:false};
await writeFile(path.resolve(root,spec.file+'.generation.json'),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({file:record.file,width:record.width,height:record.height,sha256:record.sha256,status:record.status}));
