import{loadMapArt,prepareMapArt,paintSourceMap}from'./map-art.js';
const $=id=>document.getElementById(id),canvas=$('gallery-canvas'),status=$('gallery-status');
const names={town:'中国城',desert:'沙漠',snow:'冰雪',mine:'矿洞',water:'水面',field:'田野',bomb:'足球场景',bun:'抢包山',pig:'集市',treasure:'寻宝',match:'比武',sculpture:'雕塑',machine:'机械',box:'推箱子',practice:'练习',pve:'探险关卡',tank:'坦克场景',rand:'随机目录占位'};
let maps=[],selected=null,source=null,revision=0;
function setStatus(message,failed=false){status.textContent=message;status.classList.toggle('gallery-failed',failed);}
function renderList(){
  const query=$('gallery-search').value.trim().toLowerCase(),family=$('gallery-family').value;
  const list=maps.filter(map=>(!family||map.family===family)&&(!query||`${map.name} ${map.catalogId} ${map.mapFileName}`.toLowerCase().includes(query)));
  $('gallery-count').textContent=`${list.length} 张地图`;$('gallery-list').replaceChildren();
  if(!list.length){const empty=document.createElement('p');empty.textContent='没有符合条件的地图。';$('gallery-list').append(empty);}
  for(const map of list){const button=document.createElement('button');button.type='button';button.className='gallery-map';button.setAttribute('aria-pressed',String(map.id===selected?.id));
    const title=document.createElement('strong'),details=document.createElement('small');title.textContent=map.name;
    details.textContent=`${map.width??'?'}×${map.height??'?'} · ${map.maxSeats}人 · ${map.artCoverage?`${map.artCoverage.paintedCandidateCount}/${map.artCoverage.requiredCount}类新画候选`:'数据待核对'}`;
    button.append(title,details);button.addEventListener('click',()=>void selectMap(map));$('gallery-list').append(button);}
}
function paint(){
  if(!source)return;
  const width=source.width*40,height=source.height*40;canvas.width=width*2;canvas.height=height*2;canvas.hidden=false;
  const ctx=canvas.getContext('2d');ctx.setTransform(2,0,0,2,0,0);ctx.clearRect(0,0,width,height);
  const result=paintSourceMap(ctx,source);
  if($('gallery-footprints').checked){ctx.lineWidth=.8;ctx.strokeStyle='#b24f3b';for(const object of source.sceneObjects){if(object.layer!==2&&!object.destroyed)ctx.strokeRect(object.x*40+.4,object.y*40+.4,object.width*40-.8,object.height*40-.8);}}
  canvas.setAttribute('aria-label',`${selected.name}，${source.width}列${source.height}行，${result.missingElementIds.length}类素材待制作。`);
  setStatus(result.missingElementIds.length?`已显示当前候选；${result.missingElementIds.length}类尚未制作：${result.missingElementIds.join('、')}`:'场景素材已覆盖，仍待视觉与运行验收。');
}
async function selectMap(map){
  const ticket=++revision;selected=map;source=null;canvas.hidden=true;$('gallery-retry').hidden=true;$('gallery-title').textContent=map.name;renderList();
  const link=new URL(location.href);link.searchParams.set('map',map.id);history.replaceState(null,'',link);
  $('gallery-facts').textContent=`编号${map.catalogId} · ${map.width??'?'}列×${map.height??'?'}行 · 最多${map.maxSeats}人 · ${map.mapFileName}`;
  setStatus('正在载入地图与新画素材…');
  try{const response=await fetch(`./api/maps/${encodeURIComponent(map.id)}`);if(!response.ok)throw new Error(`地图读取失败（${response.status}）`);const data=await response.json();
    if(ticket!==revision)return;
    if(!data.sourceMap)throw new Error(map.unavailableReason||'源地图尚未能完整解析，不能用其他布局替代。');
    const candidate=data.sourceMap;const art=await prepareMapArt(candidate,{retry:true});if(ticket!==revision)return;
    source=candidate;paint();if(art.failed){setStatus(`${art.failed}张素材未能读取，请重试。`,true);$('gallery-retry').hidden=false;}
  }catch(error){if(ticket!==revision)return;setStatus(error.message,true);$('gallery-retry').hidden=false;}
}
$('gallery-search').addEventListener('input',renderList);$('gallery-family').addEventListener('change',renderList);$('gallery-footprints').addEventListener('change',paint);$('gallery-retry').addEventListener('click',()=>selected?void selectMap(selected):void initialize());
async function initialize(){try{const response=await fetch('./api/maps');if(!response.ok)throw new Error(`目录读取失败（${response.status}）`);const data=await response.json();maps=data.maps;
  for(const family of [...new Set(maps.map(map=>map.family))].sort()){const option=document.createElement('option');option.value=family;option.textContent=names[family]||family;$('gallery-family').append(option);}
  await loadMapArt();renderList();const initial=new URL(location.href).searchParams.get('map')||'source-201';await selectMap(maps.find(map=>map.id===initial)||maps[0]);
}catch(error){setStatus(error.message,true);$('gallery-count').textContent='目录未能载入';$('gallery-retry').hidden=false;}}
void initialize();
