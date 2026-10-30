import {sequenceCategories,headWorldSequences,mapSequence} from './art-review-data.js';
const $=id=>document.getElementById(id);
const grid=$('review-grid'),status=$('review-status'),kind=$('review-kind'),search=$('review-search');
const panel=$('effect-panel'),canvas=$('effect-canvas'),ctx=canvas.getContext('2d');
const cache=new Map(),images=new Map();let requestVersion=0,entries=[],clips=[],selectedClip=null,frameIndex=0,playing=false,raf=0,lastFrameAt=0,page=0;
const paths={items:'assets/items/art.json',battlefield:'assets/items/battlefield/art.json',skills:'assets/items/skills/art.json',food:'assets/items/food/art.json',forge:'assets/items/forge/art.json',petcards:'assets/items/petcards/art.json',transformations:'assets/characters/motion-generated/transformations/manifest.json',roster:'assets/characters/motion-generated/roster-skin-mapping-20261028.json',characters:'assets/characters/motion-generated/source-candidates-20261028.manifest.json',creatures:'assets/maps/exploration/creatures/art.json'};
Object.assign(paths,{cards:'assets/items/cards-currency/art.json',platform:'assets/items/platform/art.json',nameplates:'assets/items/namecard-borders/art.json',shortNameplates:'assets/items/namecard-borders/walk/art.json',nameplateIcons:'assets/items/namecard-borders/inventory/art.json'});
Object.assign(paths,{headAdornments:'assets/items/head-adornments/art.json'});
Object.assign(paths,{surroundings:'assets/items/surroundings/art.json'});
Object.assign(paths,{eyeAdornments:'assets/items/eye-adornments/art.json'});
Object.assign(paths,{footprints:'assets/items/footprints/art.json'});
Object.assign(paths,{portraits:'assets/characters/portraits-candidates/manifest.json',uiExtra:'assets/ui/semantic-extra/manifest.json'});
const uiNames={friends:'好友','add-friend':'添加好友','remove-friend':'删除好友','private-chat':'私聊',guild:'仙盟',task:'任务',backpack:'背包',warehouse:'仓库',forge:'锻造',compose:'合成','save-replay':'保存回放','cancel-replay':'取消回放','pet-card':'仙灵卡',fullscreen:'全屏',mute:'静音',reconnect:'重连'};
const requestedKind=new URLSearchParams(location.search).get('kind');
if([...kind.options].some(option=>option.value===requestedKind))kind.value=requestedKind;
const safeAssetPath=file=>typeof file==='string'&&file.startsWith('assets/')&&!file.includes('..')&&!file.includes('\\')&&!/[?#:\u0000-\u001f]/.test(file);
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
async function readJson(file){if(!cache.has(file))cache.set(file,fetch(file,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`${file}：${r.status}`);return r.json();}).catch(e=>{cache.delete(file);throw e;}));return cache.get(file);}
async function readSequences(category){
  if(category==='headWorld')return headWorldSequences(await readJson('assets/items/head-adornments/world-art.json'));
  if(category==='pickupSequences')return(await readJson('assets/items/battlefield/animation/manifest.json')).resources;
  if(category==='mapSequences'){
    const index=await readJson('assets/maps/animation-candidates-index.json');
    const results=await Promise.allSettled(index.entries.map(async e=>{if(!safeAssetPath(e.manifest))throw new Error('非法序列路径');return mapSequence({...await readJson(e.manifest),family:e.family});}));
    const failed=results.filter(r=>r.status==='rejected');if(failed.length)throw new Error(`${failed.length}组地图序列记录未载入`);
    return results.map(r=>r.value);
  }
  const results=await Promise.allSettled(['bubbles','flames','states'].map(group=>readJson(`assets/effects/${group}/manifest.json`)));
  if(results.some(r=>r.status==='rejected'))throw new Error('部分特效清单未载入');
  return results.flatMap((r,i)=>(i===0?r.value.clips:r.value.resources).map(c=>({...c,group:['糖泡','火焰','状态'][i]})));
}
function background(){const value=$('review-background').value;document.querySelectorAll('.asset-picture,.effect-stage').forEach(e=>e.dataset.background=value);}
function card(entry){const card=element('article',undefined,`asset-card${entry.longFrame?' long-frame-card':''}`);const stage=element('div',undefined,`asset-picture${entry.wide?' wide':''}${entry.longFrame?' long-frame':''}`);stage.dataset.background=$('review-background').value;const dimensions=element('p');dimensions.hidden=true;
  if(safeAssetPath(entry.file)){const image=element('img');image.src=entry.file;image.alt=entry.name;image.loading='lazy';image.decoding='async';image.addEventListener('load',()=>{if(!entry.size){dimensions.textContent=`图片画布 ${image.naturalWidth} × ${image.naturalHeight} 像素；原生／兼容导出见来源记录`;dimensions.hidden=false;}});image.addEventListener('error',()=>{stage.replaceChildren(element('p','图片载入失败','load-error'));});stage.append(image);}else stage.append(element('p','没有可显示的候选文件'));
  const info=element('div',undefined,'asset-info');info.append(element('h2',entry.name),element('span',entry.failed?'未通过':'待验候选',`candidate-tag${entry.failed?' failed':''}`));
  if(entry.id!==undefined)info.append(element('p',`编号 ${entry.id}`));if(entry.size)info.append(element('p',`${entry.native?'原生':'导出'} ${entry.size.join(' × ')} 像素`));else info.append(dimensions);
  if(entry.note)info.append(element('p',entry.note));const details=element('details');details.append(element('summary','来源与规格'),element('pre',JSON.stringify(entry.record,null,2)));info.append(details);card.append(stage,info);return card;}
function renderCards(){const query=search.value.trim().toLocaleLowerCase();const visible=entries.filter(e=>`${e.name} ${e.id??''}`.toLocaleLowerCase().includes(query)),size=['roster','characters','creatures','transformations'].includes(kind.value)?4:24,pages=Math.max(1,Math.ceil(visible.length/size));page=Math.max(0,Math.min(page,pages-1));const current=visible.slice(page*size,(page+1)*size);grid.replaceChildren(...current.map(card));$('review-page').textContent=`${page+1} / ${pages}`;$('review-previous').disabled=page===0;$('review-next').disabled=page>=pages-1;status.textContent=`本页 ${current.length} 个，匹配 ${visible.length} / ${entries.length} 个候选。已验收数量不由此页推定。`;}
function stop(){playing=false;cancelAnimationFrame(raf);raf=0;$('effect-play').textContent='播放';$('effect-play').setAttribute('aria-pressed','false');}
async function showCategory(){stop();selectedClip=null;const version=++requestVersion;page=0;status.textContent='正在载入…';grid.replaceChildren();entries=[];panel.hidden=true;search.disabled=sequenceCategories.has(kind.value);$('review-pagination').hidden=sequenceCategories.has(kind.value);
  try{if(sequenceCategories.has(kind.value)){clips=await readSequences(kind.value);if(version!==requestVersion)return;if(!clips.length)throw new Error('没有载入候选序列');
      $('effect-select').replaceChildren(...clips.map((c,i)=>{const option=element('option',`${c.group?c.group+' · ':''}${c.projectEffectName??c.sourceResource} · ${c.frameCount} 帧`);option.value=String(i);return option;}));panel.hidden=false;selectedClip=clips[0];frameIndex=0;status.textContent=`${clips.length} 组候选序列。仅按原始frameOffset作诊断包络预览，未确认绑定、方向语义或时序。`;$('effect-details').textContent=JSON.stringify(selectedClip,null,2);await drawFrame();return;}
    const data=await readJson(paths[kind.value]);if(version!==requestVersion)return;
    if(kind.value==='roster')entries=data.slots.map(s=>({name:s.appearance.displayName,id:s.sourceRoleId,file:s.appearance.master,note:`静态身份与来源槽位待验。容量 ${s.baseAttributes.capacity}/${s.baseAttributes.maxCapacity} · 威力 ${s.baseAttributes.range}/${s.baseAttributes.maxRange} · 速度档 ${s.baseAttributes.speed}/${s.baseAttributes.maxSpeed}；速度档单位另待核实。`,record:s}));
    else if(kind.value==='characters')entries=data.entries.map(e=>({name:e.name,file:e.file,size:e.nativeSize,native:true,wide:true,failed:e.gate==='not_passed',note:'原画或关键姿态；不代表连续动作已经完成。',record:e}));
    else if(kind.value==='portraits')entries=data.entries.map(e=>({name:e.name,id:e.sourceRoleId,file:e.file,size:e.canvas,note:'从现有20个自有身份等比裁出的头像；未增加角色数量，尚未接入角色槽位。',record:e}));
    else if(kind.value==='uiExtra')entries=data.entries.map(e=>({name:uiNames[e.id]??e.id,id:e.id,file:e.file,size:e.outputCanvas,note:'一张母图裁出16个语义图标；小尺寸辨识、状态和实际控件接入待验。',record:e}));
    else if(kind.value==='creatures')entries=data.masters.map(e=>({name:e.projectOriginalChineseIdentityName,id:e.entityId,file:e.file,size:[e.width,e.height],native:true,note:'本项目原创外观；源参数另存，完整动作待制作。',record:e}));
    else if(kind.value==='transformations')entries=data.entries.map(e=>({name:e.ownIdentity.name,id:e.sourceSceneId,file:e.ownIdentity.master,size:e.ownIdentity.nativeSize,native:true,note:`临时模型编号 ${e.sourceAvatarRoleId}；静态原画，完整动作与运行待验。`,record:e}));
    else if(kind.value==='battlefield')entries=data.pieces.map(e=>({name:e.displayName,id:e.sceneId,file:e.file,size:[e.width,e.height],note:'场景拾取物编号，与账号库存ID分开；当前首帧不代表完整动画。',record:e}));
    else if(['nameplates','shortNameplates'].includes(kind.value))entries=data.items.map(e=>({name:e.sourceName,id:e.itemId,file:e.file,size:[e.width,e.height],longFrame:true,failed:Boolean(e.warnings?.length),note:`${kind.value==='nameplates'?'长版':'短版'}首态；比例偏差 ${((e.visibleAspectRatioRelativeError??0)*100).toFixed(1)}%。完整状态、文字区与实际用途待验。`,record:e}));
    else entries=data.items.map(e=>({name:e.projectDisplayName??e.sourceName,id:e.itemId,file:e.file,size:[e.width,e.height],note:'透明、辨识、状态与运行仍待验收。',record:e}));renderCards();
  }catch(error){if(version!==requestVersion)return;status.textContent=`载入未完成：${error.message}。该类别可能仍在制作，可切换其他类别。`;}}
function loadImage(file){if(!safeAssetPath(file))return Promise.reject(new Error('不合法素材路径'));if(!images.has(file))images.set(file,new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>{images.delete(file);reject(new Error('图片载入失败'));};im.src=file;}));return images.get(file);}
async function drawFrame(){const clip=selectedClip,index=frameIndex;if(!clip)return;const frame=clip.frames[index];ctx.clearRect(0,0,canvas.width,canvas.height);$('effect-state').textContent=`${index+1} / ${clip.frames.length}${frame.empty?' · 原始空帧':''}${frame.reuseOfFrameIndex!==undefined?` · 复用第 ${frame.reuseOfFrameIndex+1} 帧`:''}`;
  if(frame.empty||!frame.file)return;try{const image=await loadImage(frame.file);if(selectedClip!==clip||frameIndex!==index)return;
    const visible=clip.frames.filter(f=>!f.empty),bounds=visible.map(f=>{const s=f.sourceFrame;if(!s||!Array.isArray(s.frameOffset)||![...s.frameOffset,s.width,s.height].every(Number.isFinite)||s.width<=0||s.height<=0)throw new Error('缺少有效原始帧尺寸或偏移');return[s.frameOffset[0],s.frameOffset[1],s.frameOffset[0]+s.width,s.frameOffset[1]+s.height];});
    const minX=Math.min(...bounds.map(b=>b[0])),minY=Math.min(...bounds.map(b=>b[1])),maxX=Math.max(...bounds.map(b=>b[2])),maxY=Math.max(...bounds.map(b=>b[3]));
    const scale=Math.min(560/(maxX-minX),560/(maxY-minY)),left=(640-(maxX-minX)*scale)/2,top=(640-(maxY-minY)*scale)/2,s=frame.sourceFrame;
    ctx.drawImage(image,left+(s.frameOffset[0]-minX)*scale,top+(s.frameOffset[1]-minY)*scale,s.width*scale,s.height*scale);
  }catch(error){if(selectedClip===clip)$('effect-state').textContent+=` · ${error.message}`;}}
function animate(now){if(!playing)return;if(!lastFrameAt)lastFrameAt=now;if(now-lastFrameAt>=Number($('effect-pace').value)){frameIndex=(frameIndex+1)%selectedClip.frames.length;lastFrameAt=now;void drawFrame();}raf=requestAnimationFrame(animate);}
kind.addEventListener('change',showCategory);search.addEventListener('input',()=>{page=0;renderCards();});$('review-background').addEventListener('change',background);
$('review-previous').addEventListener('click',()=>{page--;renderCards();});$('review-next').addEventListener('click',()=>{page++;renderCards();});
$('effect-select').addEventListener('change',()=>{stop();selectedClip=clips[Number($('effect-select').value)];frameIndex=0;$('effect-details').textContent=JSON.stringify(selectedClip,null,2);void drawFrame();});
$('effect-step').addEventListener('click',()=>{stop();if(selectedClip){frameIndex=(frameIndex+1)%selectedClip.frames.length;void drawFrame();}});
$('effect-play').addEventListener('click',()=>{if(playing){stop();return;}if(!selectedClip)return;playing=true;lastFrameAt=0;$('effect-play').textContent='暂停';$('effect-play').setAttribute('aria-pressed','true');raf=requestAnimationFrame(animate);});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});window.addEventListener('pagehide',stop);void showCategory();
