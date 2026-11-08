import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [batch,host]=process.argv.slice(2),root=process.cwd();
if(!/^[a-l]$/.test(batch)||!host)throw new Error('batch a–l and explicit host output path required');
const base=`assets/items/eye-adornments/eye-adornments-${batch}-v1.png`,prompt=`docs/eye-adornments-${batch}.prompt.txt`;
if(fs.existsSync(base))throw new Error('Do not overwrite an existing source');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const bytes=fs.readFileSync(host);fs.copyFileSync(host,base);
const refs=[`assets/items/eye-adornments/references/eye-adornments-${batch}-structure.png`,'references/image/01-mail-event.png','references/image/team-ui-v2.png'];
const p=fs.readFileSync(prompt,'utf8');
const result={schemaVersion:1,projectDisplayName:'灵葫大作战',file:base,sha256:hash(bytes),generatedAt:new Date().toISOString(),
 timeEvidence:'UTC registration after builtin return; provider creation timestamp not disclosed',width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),format:'PNG',
 tool:'image_gen.imagegen',route:'builtin',art_source:'host_image',configSnapshot:JSON.parse(fs.readFileSync('D:/work/image/config/image-generation.json','utf8')),
 submittedParameters:{model:null,quality:null,transparent_background:true,referenced_image_paths:refs.map(x=>path.join(root,x).replaceAll('\\','/'))},
 actualModel:null,actualQuality:null,unverifiedReason:'宿主管理，工具未开放型号/质量选择器，返回未披露可核实版本/质量。',
 prompt,promptFileSha256:hash(Buffer.from(p)),submittedPromptSha256:hash(Buffer.from(p.trim())),promptSubmission:'File text trimmed at beginning/end only',
 references:refs.map((file,i)=>({file,sha256:hash(fs.readFileSync(file)),role:i===0?'Actual item structure references; board source records distinguish inventory/stand and format limits, not style/QQ face adoption':'Confirmed primary Daoist Q hand-painted style'})),
 sourceVisualNotes:JSON.parse(fs.readFileSync(`docs/eye-adornments-${batch}.brief.json`,'utf8')).sourceVisualNotes??null,
 evidence:{hostSource:host.replaceAll('\\','/'),returnedFields:['image_url','output_hint'],selectorsExposed:false},
 requestedCanvasInPrompt:[1536,1024],generationCount:1,requestedItemCount:6,
 sourceAndOutputScope:'One six-object atlas is one model generation; each later256 icon is a crop/PMA resize, not six model calls.',
 accepted:false,worldAccepted:false,stateAccepted:false,runtimeAdopted:false};
fs.writeFileSync(base+'.generation.json',JSON.stringify(result,null,2)+'\n');
fs.writeFileSync(base+'.tool-result.json',JSON.stringify({returnedFields:['image_url','output_hint'],
 output_hint:`Generated image saved to ${host}; original left in host cache.`,actualModel:null,actualQuality:null},null,2)+'\n');
console.log(JSON.stringify({file:base,sha256:result.sha256,native:[result.width,result.height],actualModel:null,actualQuality:null}));
