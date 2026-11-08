// Lightweight, bounded source JSON and exact-path audit only. Never recurse PNG directories or bulk decode/import.
import{readFile,writeFile,stat,open}from'node:fs/promises';
import{createHash}from'node:crypto';
import path from'node:path';
const sourceRoot='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters';
const picks={
 '01_ice_sword_girl':['manifest.json'],
 '02_fire_talisman_boy':['inventory.json','animation-timing.json','animation-events.json'],
 '05_celestial_musician_girl':['final-selection.json','STATUS.json','registration.json','animation-timing.json'],
 '06_thunder_caster_boy':['STATUS.json','animation-timing.json'],
 '08_alchemy_prodigy_boy':['manifest.json','selection-run-N.json','selection-run-S.json','selection-run-W-grounded.json','selection-combat-W.json'],
 '09_bamboo_archer_girl':['manifest.json','accepted-version.json','status.json','animation-timing.json'],
 '10_crimson_spear_girl':['delivery-current.json','source-selection.json','validation.json','runtime-export-report.json','animation-timing.json'],
 '14_short_hair_snow_summoner_girl':['manifest.json','run-timing.json'],
 '15_water_dragon_scholar_boy':['manifest.json'],
 '17_ghost_script_calligrapher_boy':['manifest.json','animation-timing.json'],
 '20_star_formation_master_girl':['merge-manifest.json']
};
let total=0;const loaded=[];
for(const[id,files]of Object.entries(picks))for(const file of files){const loc=path.join(sourceRoot,id,file);let s;try{s=await stat(loc);}catch(e){if(e.code==='ENOENT'){loaded.push({id,file,missing:true});continue;}throw e;}if(s.size>3_000_000||(total+=s.size)>9_000_000)throw new Error('Text size bound exceeded');const bytes=await readFile(loc);loaded.push({id,file,bytes:s.size,sha256:createHash('sha256').update(bytes).digest('hex'),modifiedAt:s.mtime.toISOString(),value:JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/,''))});}
function shape(v,d=0){if(v===null)return null;if(typeof v==='string')return v.length>170?v.slice(0,170)+'…':v;if(typeof v!=='object')return v;if(Array.isArray(v))return{arrayLength:v.length,first:d<3&&v.length?shape(v[0],d+1):undefined};const keys=Object.keys(v);if(d>=3)return{keys:keys.slice(0,18),keyCount:keys.length};return Object.fromEntries(keys.slice(0,d?10:24).map(k=>[k,shape(v[k],d+1)]).concat(keys.length>(d?10:24)?[['__otherKeys',keys.slice(d?10:24,(d?10:24)+12)],['__keyCount',keys.length]]:[]));}
if(process.argv[2]==='inspect'){for(const r of loaded.filter(r=>!process.argv[3]||process.argv[3].split(',').some(x=>r.id.startsWith(x))))console.log(JSON.stringify({...r,value:undefined,shape:shape(r.value)}));}
else if(process.argv[2]==='first-frames'){for(const r of loaded.filter(r=>!process.argv[3]||process.argv[3].split(',').some(x=>r.id.startsWith(x)))){const v=r.value;let found;if(Array.isArray(v))found=v[0];else found=v?.frames?.[0]??v?.files?.[0]??v?.sequences?.[0]?.frames?.[0]??v?.groups?.[0]?.frames?.[0];if(found)console.log(JSON.stringify({id:r.id,file:r.file,keys:Object.keys(v),first:found}));}}
else if(process.argv[2]==='audit'){
 const primary={'01_ice_sword_girl':'manifest.json','02_fire_talisman_boy':'inventory.json','05_celestial_musician_girl':'final-selection.json','06_thunder_caster_boy':'STATUS.json','08_alchemy_prodigy_boy':'manifest.json','09_bamboo_archer_girl':'manifest.json','10_crimson_spear_girl':'delivery-current.json','14_short_hair_snow_summoner_girl':'manifest.json','15_water_dragon_scholar_boy':'manifest.json','17_ghost_script_calligrapher_boy':'manifest.json','20_star_formation_master_girl':'merge-manifest.json'};
 const report={schemaVersion:1,checkedAt:new Date().toISOString(),scope:'11 existing own identities, current declared exact frame paths only. No recursive image scan, full decode, pixel/hash sweep, copy/import, client execution or Git mutation.',sourceRoot,sourceJsonBytesRead:total,hashesReverified:'source JSON only; PNG expected hashes retained but not rehashed',characters:[]};
 const exists=async loc=>{try{const s=await stat(loc);return s.isFile();}catch(e){if(e.code==='ENOENT')return false;throw e;}};
 const bounded=(dir,p)=>{const loc=path.resolve(dir,p);if(loc!==dir&&!loc.startsWith(dir+path.sep))throw new Error('Outside character scope: '+p);return loc;};
 for(const[id,file]of Object.entries(primary)){
  const entry=loaded.find(r=>r.id===id&&r.file===file),v=entry.value,dir=path.resolve(sourceRoot,id),frames=[];
  const add=(f,group={})=>{if(typeof f==='string')f={file:f};const action=f.action??group.action??String(f.slot??'').split(/[/-]/)[0];const direction=f.direction??group.direction??String(f.slot??'').split(/[/-]/)[1];const raw=f.output??f.runtime??f.path??f.file??f.source;const numbered=String(f.slot??raw??'').match(/(?:^|[\/\\-])(\d+)(?:\.png)?$/);frames.push({action,direction,frame:f.frame??(numbered?Number(numbered[1]):frames.length+1),sourceFrame:f.sourceFrame??null,relativePath:raw,expectedSha256:f.sha256??null,declaredFrameMs:f.durationMs??f.previewDurationMs??group.ms??group.frameMs??group.durationMs??null,recordHint:typeof f.generationRecord==='string'?f.generationRecord:f.generationRecord?.file??f.derivedRecord??f.native_evidence??null,manifestDeclaredSize:f.size??f.native_size??(f.width&&f.height?[f.width,f.height]:null)});};
  if(Array.isArray(v))v.forEach(f=>add(f));
  else if(Array.isArray(v.frames))v.frames.forEach(f=>add(f));
  else if(Array.isArray(v.files))v.files.forEach(f=>add(f));
  else if(Array.isArray(v.sequences))v.sequences.forEach(g=>g.frames.forEach(f=>add(f,g)));
  else if(v.groups&&!Array.isArray(v.groups))Object.entries(v.groups).forEach(([key,list])=>list.forEach(f=>add(f,{action:key.split('/')[0],direction:key.split('/')[1]})));
  else throw new Error('No active frame list found '+id);
  if(frames.length>250)throw new Error('Frame path count cap exceeded');
  for(const f of frames){
   if(typeof f.relativePath!=='string'||!f.relativePath.endsWith('.png'))throw new Error('No exact active PNG path '+id+' '+JSON.stringify(f));
   const loc=bounded(dir,f.relativePath);f.absolutePath=loc;
   try{const s=await stat(loc);f.exists=s.isFile();f.bytes=s.size;if(f.exists){const handle=await open(loc,'r');try{const b=Buffer.alloc(26),r=await handle.read(b,0,26,0);f.realPngHeader=r.bytesRead===26&&b.subarray(0,8).toString('hex')==='89504e470d0a1a0a';f.lfsPointerPrefix=b.subarray(0,r.bytesRead).toString('utf8').startsWith('version https://git-lfs');if(f.realPngHeader){f.pngHeaderSize=[b.readUInt32BE(16),b.readUInt32BE(20)];f.pngColorType=b[25];}}finally{await handle.close();}}}catch(e){if(e.code==='ENOENT')f.exists=false;else throw e;}
   let recordCandidates=[f.relativePath+'.generation.json'];if(typeof f.recordHint==='string')recordCandidates.push(f.recordHint);
   f.sourceRecord=null;for(const r of recordCandidates){try{if(await exists(bounded(dir,r))){f.sourceRecord=r;break;}}catch(e){if(!String(e.message).startsWith('Outside'))throw e;}}
  }
  const groups={};for(const f of frames){const k=f.action+'/'+f.direction;const g=groups[k]??={declaredSlots:0,pngHeadersPresent:0,missing:[],notPng:[],recordPathsPresent:0,headerSizes:{},declaredFrameMs:{}};g.declaredSlots++;if(!f.exists)g.missing.push(f.frame);else if(!f.realPngHeader)g.notPng.push(f.frame);else g.pngHeadersPresent++;if(f.sourceRecord)g.recordPathsPresent++;if(f.pngHeaderSize){const k=f.pngHeaderSize.join('x');g.headerSizes[k]=(g.headerSizes[k]??0)+1;}if(f.declaredFrameMs!=null)g.declaredFrameMs[f.declaredFrameMs]=(g.declaredFrameMs[f.declaredFrameMs]??0)+1;}
  const timingFile=loaded.find(r=>r.id===id&&r.file==='animation-timing.json');
  const notes=[];if(id.startsWith('09'))notes.push('Current manifest says changed_after_user_feedback; accepted-version snapshot no longer matches current images. Its45ms/720ms must not override current75ms/1200ms. E/W/NW same-leg support/dynamics still limited.');
  if(id.startsWith('10'))notes.push('Current delivery/timing says60ms/960ms; runtime-export-report and older requirement text retain75ms/1200ms. Preserve conflict; do not replay historic sourceFrame reorder.');
  if(id.startsWith('15'))notes.push('Source manifest explicitly retracts old final-review and leaves complete latest dynamic review pending; source paths/inventory may be historical removed files; use frames[].output as active targets.');
  if(id.startsWith('17'))notes.push('Source acceptance says7 of14 dynamic groups incomplete; client not integrated.');
  if(id.startsWith('20'))notes.push('Some row width/nativeSize fields describe1254 source while active PNG header may be1024; actual header kept separately. Historical grounding/timing fields not current timing.');
  const eligible=frames.filter(f=>f.realPngHeader&&((f.action==='run'&&['N','E','S','W'].includes(f.direction))||f.action==='hit'));
  const preview=frames.find(f=>f.action==='run'&&f.direction==='S'&&f.realPngHeader)??frames.find(f=>f.action==='run'&&f.realPngHeader)??frames.find(f=>f.realPngHeader);
  report.characters.push({id,sourceEntry:file,sourceEntrySha256:entry.sha256,sourceEntryModifiedAt:entry.modifiedAt,expectedSlots:frames.length,actualExactPathPngHeaders:frames.filter(f=>f.realPngHeader).length,missingPaths:frames.filter(f=>!f.exists).map(f=>f.relativePath),nonPngPaths:frames.filter(f=>f.exists&&!f.realPngHeader).map(f=>f.relativePath),sidecarOrExplicitRecordPathsPresent:frames.filter(f=>f.sourceRecord).length,orthogonalRunAndHitSourceCandidates:eligible.length,sourceStatus:v.status??v.visualAcceptanceScope??'declared_selection',sourceClientApproval:false,qqtangClientApproval:false,rootOrTransformDeclaration:v.rootPx??v.root_anchor??v.coordinateSystem??v.anchor??v.alignment??v.exportTransform??null,animationTiming:timingFile?.value??v.timing??v.runTiming??null,notes,groups,suggestedSingleVisualSample:preview?.absolutePath??null,frames});
 }
 report.totals={identities:report.characters.length,declaredSlots:report.characters.reduce((a,c)=>a+c.expectedSlots,0),actualExactPathPngHeaders:report.characters.reduce((a,c)=>a+c.actualExactPathPngHeaders,0),orthogonalRunAndHitSourceCandidates:report.characters.reduce((a,c)=>a+c.orthogonalRunAndHitSourceCandidates,0),missingPaths:report.characters.reduce((a,c)=>a+c.missingPaths.length,0),copiedImages:0,fullImageDecodes:0,qqtangClientApproved:0};
 await writeFile(path.join(import.meta.dirname,'EXISTING_ACTION_SOURCE_AUDIT_20261028.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report.totals));for(const c of report.characters)console.log(JSON.stringify({id:c.id,declared:c.expectedSlots,png:c.actualExactPathPngHeaders,records:c.sidecarOrExplicitRecordPathsPresent,orthogonalRunHit:c.orthogonalRunAndHitSourceCandidates,missing:c.missingPaths.length,availableGroups:Object.entries(c.groups).filter(([_,g])=>g.pngHeadersPresent).map(([k,g])=>({clip:k,png:g.pngHeadersPresent,expected:g.declaredSlots,missing:g.missing,sizes:g.headerSizes,ms:g.declaredFrameMs})),sample:c.suggestedSingleVisualSample}));
}
else throw new Error('Use inspect while selecting bounded active source fields');
