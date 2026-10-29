import{writeFile}from'node:fs/promises';
import{spawnSync}from'node:child_process';
import path from'node:path';
const[id,host,observation]=process.argv.slice(2);
if(!/^(41|42|43|44|45|46|54|55)-[a-z-]+$/.test(id))throw new Error('Unexpected transformation identity path');
const root=path.resolve(import.meta.dirname,'../../../..'),rel='assets/characters/motion-generated/transformations/avatar-'+id+'/master';
const spec={file:rel+'.png',prompt:rel+'.prompt.txt',hostSource:host,review:{type:'new original temporary transformation static master candidate; not full animation or runtime approval',identity:observation,pending:['single-source real alpha/edge/ivory inspection','relative scale/root/directions/animation/client integration'],runtimeEnabled:false},references:[{path:'D:/work/qqtang-ui/references/image/01-mail-event.png',role:'primary confirmed Daoist Q hand-painted style'},{path:'D:/work/qqtang-ui/references/image/team-ui-v2.png',role:'primary confirmed Daoist Q hand-painted style'},{path:'D:/work/qqtang-ui/assets/characters/runtime/daoist-child.png',role:'own big-head short-body proportions and hand-painted finish only, not source creature identity'}]};
await writeFile(path.resolve(root,rel+'.register.json'),JSON.stringify(spec,null,2)+'\n');
const result=spawnSync(process.execPath,[path.resolve(import.meta.dirname,'../register-source.mjs'),rel+'.register.json'],{encoding:'utf8'});process.stdout.write(result.stdout);process.stderr.write(result.stderr);if(result.status)process.exit(result.status);
