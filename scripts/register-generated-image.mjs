import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const [file,prompt,hostSource,...references]=process.argv.slice(2);
if(!file||!prompt||!hostSource)throw new Error('Usage: node register-generated-image.mjs asset prompt host-source [reference ...]');
const bytes=await readFile(path.join(root,file));
if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error('Expected real PNG');
const cfg=JSON.parse(await readFile('D:/work/image/config/image-generation.json','utf8'));
const record={file,sha256:createHash('sha256').update(bytes).digest('hex'),generatedAt:new Date().toISOString(),
  timeEvidence:'registration immediately after tool return; UTC',width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),format:'PNG',
  tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',configSnapshot:cfg,
  submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:references},
  actualModel:null,actualQuality:null,unverifiedReason:'宿主管理，工具未开放型号/质量选择器，返回未披露可核实型号或质量。',
  prompt,references:await Promise.all(references.map(async p=>({path:p,purpose:p.replaceAll('\\','/').includes('/visual-reference/')?'structure and geometry reference only':p.replaceAll('\\','/').includes('/characters/')?'original character identity reference':'style reference',sha256:createHash('sha256').update(await readFile(p)).digest('hex')}))),
  evidence:{hostSource,returnedFields:['image_url','output_hint'],selectorsExposed:false},
  operation:'built-in generated source; no resampling or pixel editing',nativeDimensions:true};
await writeFile(path.join(root,file+'.generation.json'),JSON.stringify(record,null,2)+'\n');
console.log(`${file}: ${record.width}x${record.height} source registered`);
