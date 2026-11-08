// One newly generated identity sheet registration only; never import/runtime/Git.
import{writeFile}from'node:fs/promises';
import{spawnSync}from'node:child_process';
import path from'node:path';
const[id,hostSource,order='N,E,S,W']=process.argv.slice(2);
if(!['cloud-tortoise-warden','pine-cloud-elder','jade-craft-artisan','paper-kite-wanderer','cinnabar-seal-keeper'].includes(id))throw Error('Unknown owned identity');
const actualDirections=order.split(',');if(actualDirections.length!==4||actualDirections.some(d=>!['N','E','S','W'].includes(d)))throw Error('Four actual observed cardinal direction cells required');
const prefix='assets/characters/motion-generated/roster-expansion/'+id;
const spec={file:prefix+'/idle-four-directions-v1.png',prompt:prefix+'/idle-four-directions-v1.prompt.txt',hostSource,editTarget:prefix+'/master.png',references:[{path:'D:/work/qqtang-ui/'+prefix+'/master.png',role:'own approved identity candidate master; exact face/hair/props'},{path:'D:/work/qqtang-ui/references/image/01-mail-event.png',role:'primary Daoist chibi style'},{path:'D:/work/qqtang-ui/references/image/team-ui-v2.png',role:'primary Daoist chibi style'}],status:'four_direction_static_candidate_pending_single_source_qa',review:{kind:'four_direction_idle_stills_not_animation',requestedOrder:['N','E','S','W'],actualVisualOrder:actualDirections,orderMatchesRequest:order==='N,E,S,W',runtimeEnabled:false,pending:['single-sheet alpha/seams','identity/hand/root/cell continuity','actual map/client integration'],ownership:'No equal cell crop approved until alpha boundary checked.'}};
if(new Set(actualDirections).size!==4){spec.status='not_passed_missing_cardinal_direction';spec.review.missingDirections=['N','E','S','W'].filter(d=>!actualDirections.includes(d));}
const root=path.resolve(import.meta.dirname,'../../../..');
await writeFile(path.join(root,prefix+'/idle-four-directions-v1.register.json'),JSON.stringify(spec,null,2)+'\n');
const proc=spawnSync(process.execPath,[path.join(root,'assets/characters/motion-generated/register-source.mjs'),prefix+'/idle-four-directions-v1.register.json'],{cwd:root,encoding:'utf8'});if(proc.status!==0)throw Error(proc.stderr||proc.stdout);console.log(proc.stdout.trim());
