// One new blink edit only; no runtime/Git mutations.
import{readFile,writeFile,copyFile}from'node:fs/promises';
import{spawnSync}from'node:child_process';
import path from'node:path';
const[id,hostSource]=process.argv.slice(2);if(!['daoist-child','moon-shadow','mountain-guardian','lotus-healer'].includes(id))throw Error('Explicit own identity required');
const base=import.meta.dirname,root=path.resolve(base,'../../../..'),prefix='assets/characters/motion-generated/idle-blinks/'+id;
const source=JSON.parse(await readFile(path.join(root,prefix+'/open-S.png.source.json'),'utf8'));
await copyFile(hostSource,path.join(root,prefix+'/closed-S-v1.png'));
const spec={file:prefix+'/closed-S-v1.png',prompt:prefix+'/closed-S-v1.prompt.txt',hostSource,editTarget:prefix+'/open-S.png',references:[{path:path.join(root,prefix+'/open-S.png').replaceAll('\\','/'),role:'exact own SOUTH/front open-eye edit target; same whole canvas/body/hands/props/boots; source record '+prefix+'/open-S.png.source.json'},{path:'D:/work/qqtang-ui/references/image/01-mail-event.png',role:'primary Daoist Q style'},{path:'D:/work/qqtang-ui/references/image/team-ui-v2.png',role:'primary Daoist Q style'}],status:'closed_eye_idle_key_candidate_pending_source_canvas_and_foot_comparison',review:{kind:'one_S_closed_eye_idle_key_not_walk_or_full_animation',character:id,direction:'S',sourceCanvas:[768,768],sourceOpen:prefix+'/open-S.png',sourceOpenSha256:source.sha256,editOfSourceRecord:prefix+'/open-S.png.source.json',wholeCanvasOnly:true,borrowedRoot:false,root:null,runtimeEnabled:false,clientApproved:false,oneEditOnly:true}};
const specFile=prefix+'/closed-S-v1.register.json';await writeFile(path.join(root,specFile),JSON.stringify(spec,null,2)+'\n');
const p=spawnSync(process.execPath,[path.join(root,'assets/characters/motion-generated/register-source.mjs'),specFile],{cwd:root,encoding:'utf8'});if(p.status)throw Error(p.stderr||p.stdout);console.log(p.stdout.trim());
