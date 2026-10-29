// One new form source only. No runtime/index/Git mutations.
import{readFile,writeFile}from'node:fs/promises';
import{spawnSync}from'node:child_process';
import path from'node:path';
const[idText,hostSource,order='N,E,S,W']=process.argv.slice(2),id=Number(idText);
const base=import.meta.dirname,root=path.resolve(base,'../../../..');
const catalog=JSON.parse(await readFile(path.join(base,'manifest.json'),'utf8'));
const item=catalog.entries.find(e=>e.sourceAvatarRoleId===id);if(!item||id===54)throw Error('Use explicit4-direction form only;54 is single-direction');
const prefix=path.posix.dirname(item.ownIdentity.master),name='idle-four-directions-v1';
const actual=order.split(',');if(actual.length!==4||actual.some(d=>!['N','E','S','W'].includes(d)))throw Error('Actual observed4 cells required');
const spec={file:prefix+'/'+name+'.png',prompt:prefix+'/'+name+'.prompt.txt',hostSource,editTarget:item.ownIdentity.master,references:[{path:'D:/work/qqtang-ui/'+item.ownIdentity.master,role:'selected own form identity master'},{path:'D:/work/qqtang-ui/references/image/01-mail-event.png',role:'primary Daoist Q style'},{path:'D:/work/qqtang-ui/references/image/team-ui-v2.png',role:'primary Daoist Q style'}],status:new Set(actual).size===4?'four_direction_static_candidate_pending_single_source_qa':'not_passed_missing_cardinal_direction',review:{kind:'temporary_form_four_direction_idle_stills_not_animation',avatarRoleId:id,requestedOrder:['N','E','S','W'],actualVisualOrder:actual,missingDirections:['N','E','S','W'].filter(d=>!actual.includes(d)),runtimeEnabled:false,pending:['single-source alpha/ownership','identity asymmetric attachments/true directions','shared scale/root and client'],sourceDirectionEvidence:'assets/characters/motion-generated/transformations/native-body-direction-evidence.json',sourceDirectionCount:4,sourceDirectionIndexOrder:null}};
const specPath=prefix+'/'+name+'.register.json';await writeFile(path.join(root,specPath),JSON.stringify(spec,null,2)+'\n');
const p=spawnSync(process.execPath,[path.join(root,'assets/characters/motion-generated/register-source.mjs'),specPath],{cwd:root,encoding:'utf8'});if(p.status)throw Error(p.stderr||p.stdout);console.log(p.stdout.trim());
