import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import os from 'node:os';
const root=path.resolve(import.meta.dirname,'..');
const [file,prompt,hostSource,...references]=process.argv.slice(2);
if(!file||!prompt||!hostSource)throw new Error('Usage: node register-generated-image.mjs asset prompt host-source [reference ...]');
const bytes=await readFile(path.join(root,file));
if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error('Expected real PNG');
const candidates=[process.env.GPT_IMAGE_CONFIG,path.resolve(root,'..','image','config','image-generation.json')].filter(Boolean);
let cfg,configSource;
async function readConfiguration(candidate){const raw=await readFile(candidate);cfg=JSON.parse(raw.toString('utf8').replace(/^\uFEFF/,''));configSource={path:candidate,sha256:createHash('sha256').update(raw).digest('hex')};}
for(const candidate of candidates){try{await readConfiguration(candidate);break;}catch(error){if(error.code!=='ENOENT')throw error;}}
if(!cfg){try{const pointer=JSON.parse((await readFile(path.join(os.homedir(),'.codex','image-generation-config.json'),'utf8')).replace(/^\uFEFF/,''));if(pointer.config_path)await readConfiguration(pointer.config_path);}catch(error){if(error.code!=='ENOENT')throw error;}}
if(!cfg||typeof cfg.model!=='string'||typeof cfg.quality!=='string')throw new Error('Cannot locate current unified image configuration. Set GPT_IMAGE_CONFIG or install the image repository beside this project; do not silently reuse a historical snapshot.');
const record={file,sha256:createHash('sha256').update(bytes).digest('hex'),generatedAt:new Date().toISOString(),
  timeEvidence:'UTC registration after tool return; provider creation timestamp not exposed',width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),format:'PNG',
  tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',configSnapshot:cfg,configSource,
  submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:references},
  actualModel:null,actualQuality:null,unverifiedReason:'宿主管理，工具未开放型号/质量选择器，返回未披露可核实型号或质量。',
  prompt,references:await Promise.all(references.map(async p=>({path:p,purpose:(p.replaceAll('\\','/').includes('/visual-reference/')||p.replaceAll('\\','/').includes('/references/qqtang-')||p.replaceAll('\\','/').includes('/references/world/')||p.replaceAll('\\','/').includes('/references/inventory'))?'structure and functional content reference only':(p.replaceAll('\\','/').includes('/characters/')||p.includes('own-four-characters-contact'))?'original character identity reference':'style reference',sha256:createHash('sha256').update(await readFile(p)).digest('hex')}))),
  evidence:{hostSource,returnedFields:['image_url','output_hint'],selectorsExposed:false},
  operation:'built-in generated source; no resampling or pixel editing',nativeDimensions:true};
await writeFile(path.join(root,file+'.generation.json'),JSON.stringify(record,null,2)+'\n');
console.log(`${file}: ${record.width}x${record.height} source registered`);
