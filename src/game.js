import {canTraverseSource,sourceFlameStep,projectSourceCollision,SourceMapError} from './original-maps.js';

/** QQ堂规则重制原型：历史候选基线见 docs/QQTANG_ORIGINAL_RESEARCH.md。
 * 角色档位、5秒糖泡/困泡尚未经原客户端逐帧复测；地图为本轮布局。
 * 重制约定：速度n=max(110,370-30*n)ms/格，携包乘1.45；每家3包；
 * 比武10分/3秒复活；抢包10秒复活；相邻格即接触、敌方补刀优先；
 * 推箱空格击碎、方向输入400ms内空格推射，箱击/火焰扣1HP；
 * 探险3波含末波Boss；破箱4%掉针，没有免费自救。非腾讯最终版保证。
 * 本模块内置权威动作节流；状态JSON可序列化，无浏览器依赖。
 */
export const CHARACTERS=[
  {id:'maomao',name:'道童',identity:'金发带道童',capacity:2,maxCapacity:6,range:2,maxRange:7,speed:5,maxSpeed:8,sprite:0,description:'金发带、太极葫芦与玉绿短袍，笑迎每一场相逢。'},
  {id:'asha',name:'月影',identity:'月影少女',capacity:2,maxCapacity:6,range:2,maxRange:7,speed:5,maxSpeed:8,sprite:1,description:'银发月饰、蓝色围巾与双弯刃，清朗灵秀的月下行者。'},
  {id:'wukong',name:'山岳',identity:'山岳守卫',capacity:2,maxCapacity:7,range:1,maxRange:8,speed:4,maxSpeed:7,sprite:2,description:'木珠、环首法杖与金绿圆盾，守望伙伴的山岳少年。'},
  {id:'titan',name:'莲花',identity:'莲花医者',capacity:2,maxCapacity:6,range:3,maxRange:9,speed:3,maxSpeed:6,sprite:3,description:'莲冠粉穗、粉白长衣与莲灯药瓶，温暖明亮的莲花医者。'},
];
export const MODES=[
  {id:'classic',name:'普通竞技',description:'团队对抗，同伴接触救援，敌人接触淘汰；全队离场判负。'},
  {id:'brawl',name:'比武',description:'淘汰累计团队分数，离场3秒后复活；先到10分获胜。'},
  {id:'bun',name:'抢包山',description:'搬走对方包子回己家，携包减速，离场掉包、10秒复活。'},
  {id:'soccer',name:'热血足球',description:'糖泡从天而降，空格把身边糖泡沿面朝方向踢向对方。'},
  {id:'push',name:'推箱子',description:'4点生命，移动推箱，空格击碎，方向配合空格推射箱子。'},
  {id:'adventure',name:'合作探险',description:'全员合作迎战3波怪物及Boss，清关获胜，全员离场失败。'},
];
const DRAFT_WIDTH=15,DRAFT_HEIGHT=13,DIRS=[[0,-1],[1,0],[0,1],[-1,0]];
const key=(x,y)=>`${x},${y}`,distance=(a,b)=>Math.abs(a.x-b.x)+Math.abs(a.y-b.y);
const byId=(g,id)=>g.players.find(p=>p.id===id),active=(g,p)=>g.status==='playing'&&p?.alive;
const specFor=id=>CHARACTERS.find(c=>c.id===id)||CHARACTERS[0];
const interval=p=>Math.max(110,370-30*p.speed)*(p.carrying?1.45:1);
function random(g){g._randomState=(Math.imul(g._randomState,1664525)+1013904223)>>>0;return g._randomState/4294967296;}
function emit(g,type,detail={}){
  const text=({start:'对局开始',eliminated:'角色离场',rescued:'同伴已获救',trapped:'角色被困',respawn:'角色重新入场',pickup:'拾取道具','bun-taken':'取得包子','bun-dropped':'包子掉落','bun-returned':'包子已夺回','bun-delivered':'包子送达','box-pushed':'推动箱子','box-shot':'推射箱子','box-broken':'箱子破碎','bubble-placed':'放置糖泡','bubble-kicked':'踢出糖泡','bubble-burst':'糖泡爆开','sky-bubble':'天降糖泡','fire-row':'火焰出现',wave:'怪物来袭','monster-defeated':'怪物被击败',finished:'对局结束',damage:'受到伤害'})[type]||type;
  g.events.push({type,time:g.time,text,...detail});if(g.events.length>20)g.events.splice(0,g.events.length-20);
}
function inside(g,x,y){return Number.isInteger(x)&&Number.isInteger(y)&&x>=0&&y>=0&&x<g.width&&y<g.height;}
function occupied(g,x,y,except=null){return g.players.some(p=>p!==except&&p.alive&&p.x===x&&p.y===y);}
function walkable(g,p,x,y){return inside(g,x,y)&&g.grid[y][x]===0&&!g.bombs.some(b=>b.x===x&&b.y===y)&&!occupied(g,x,y,p)&&!g.monsters.some(m=>m.alive&&m.x===x&&m.y===y);}
function rays(g,b){
  const cells=[{x:b.x,y:b.y}];for(const[dx,dy]of DIRS)for(let n=1;n<=b.range;n++){
    const x=b.x+dx*n,y=b.y+dy*n;if(!inside(g,x,y))break;
    if(g.sourceMap){const step=sourceFlameStep(g.sourceMap,x-dx,y-dy,x,y);if(!step.enter)break;cells.push({x,y});if(!step.continue)break;}
    else{if(g.grid[y][x]===1)break;cells.push({x,y});if(g.grid[y][x]===2)break;}
  }return cells;
}
function dangers(g,extra=null){const set=new Set(g.blasts.map(b=>key(b.x,b.y)));for(const b of extra?[...g.bombs,extra]:g.bombs)for(const c of rays(g,b))set.add(key(c.x,c.y));return set;}
function route(g,p,goal,{danger=null,max=28}={}){
  const queue=[{x:p.x,y:p.y,path:[]}],seen=new Set([key(p.x,p.y)]);
  for(let i=0;i<queue.length;i++){
    const node=queue[i];if(node.path.length&&goal(node))return node.path;if(node.path.length>=max)continue;
    for(const[dx,dy]of DIRS){const x=node.x+dx,y=node.y+dy,k=key(x,y);if(seen.has(k)||!walkable(g,p,x,y)||danger?.has(k)||(g.sourceMap&&!canTraverseSource(g.sourceMap,node.x,node.y,x,y)))continue;seen.add(k);queue.push({x,y,path:[...node.path,[dx,dy]]});}
  }return null;
}
const escape=(g,p,danger,max=10)=>route(g,p,n=>!danger.has(key(n.x,n.y)),{max});

export function createGame({mode='classic',map='courtyard',duration=180,seed=42,participants,sourceMap=null}={}){
  const chosenMode=MODES.some(m=>m.id===mode)?mode:'classic';
  if(String(map).startsWith('source-')&&!sourceMap)throw new SourceMapError('SOURCE_DATA_REQUIRED','源地图必须由本地目录加载，不能退回随机试稿。');
  if(sourceMap&&(!sourceMap.playableModes?.includes(chosenMode)||sourceMap.kind!=='source-map'))throw new SourceMapError('SOURCE_RULE_UNSUPPORTED','此源地图未核验支持所选模式，不能编造目标点或关卡。');
  if(sourceMap&&Array.isArray(participants)&&participants.length>sourceMap.playerLimit)throw new SourceMapError('SOURCE_PLAYER_LIMIT',`此图最多${sourceMap.playerLimit}人。`);
  const source=Array.isArray(participants)&&participants.length?participants.slice(0,8):[
    {id:'you',name:'你',character:'maomao',team:'red',isBot:false},{id:'bot-1',name:'月影 · AI',character:'asha',team:'blue',isBot:true},
    {id:'bot-2',name:'山岳 · AI',character:'wukong',team:'red',isBot:true},{id:'bot-3',name:'莲花 · AI',character:'titan',team:'blue',isBot:true},
  ];
  if(sourceMap&&source.length>sourceMap.playerLimit)throw new SourceMapError('SOURCE_PLAYER_LIMIT',`此图最多${sourceMap.playerLimit}人。`);
  const g={id:`qqt-${chosenMode}-${(Number(seed)>>>0).toString(36)}`,width:sourceMap?.width??DRAFT_WIDTH,height:sourceMap?.height??DRAFT_HEIGHT,grid:[],time:0,
    duration:Number.isFinite(duration)?Math.max(1,duration):180,status:'playing',winnerTeam:null,mode:chosenMode,map:String(map),
    players:[],bombs:[],blasts:[],pickups:[],objectives:{red:{x:1,y:6,buns:3},blue:{x:13,y:6,buns:3}},monsters:[],scores:{red:0,blue:0},events:[],
    wave:chosenMode==='adventure'?1:0,totalWaves:3,targetScore:chosenMode==='bun'?3:10,endReason:null,
    _randomState:(Number(seed)>>>0)||42,_bombId:0,_eventId:0,_nextSkyAt:800,_nextFireAt:8000,_waveReadyAt:null};
  g.mapKind=sourceMap?'source-map':'draft-map';g.geometryStatus=sourceMap?.geometryStatus||'unaccepted-custom-draft';g.maxSeats=sourceMap?.playerLimit??8;
  const spawn={red:[[1,1],[1,11],[1,5],[5,1]],blue:[[13,11],[13,1],[13,7],[9,11]]},all=[...spawn.red,...spawn.blue],protectedCells=new Set();
  for(const[x,y]of all)for(const[dx,dy]of[[0,0],...DIRS])protectedCells.add(key(x+dx,y+dy));
  const density=chosenMode==='push'?0.48:map==='town'?0.46:map==='factory'?0.28:0.35;
  if(sourceMap){
    g.sourceMap=structuredClone(sourceMap);g.map=sourceMap.id;g.grid=g.sourceMap.grid.map(row=>[...row]);
    g.objectives={red:null,blue:null};g.originalTargets=structuredClone(sourceMap.targets);
    g.originalSpawnGroups=structuredClone(sourceMap.spawnGroups);
  }else for(let y=0;y<g.height;y++){const row=[];for(let x=0;x<g.width;x++){
    const wall=x===0||y===0||x===g.width-1||y===g.height-1||(x%2===0&&y%2===0),corridor=x===1||x===13||y===1||y===11||x===7||y===5||y===7;
    row.push(wall?1:!corridor&&!protectedCells.has(key(x,y))&&random(g)<density?2:0);
  }g.grid.push(row);}
  const ids=new Set(),usedSpawns=new Set(),indices={red:0,blue:0};
  const sourceSpawns=sourceMap?[...sourceMap.spawnGroups.A,...sourceMap.spawnGroups.B].filter((point,index,list)=>list.findIndex(other=>other.x===point.x&&other.y===point.y)===index):null;
  source.forEach((entry,i)=>{
    const spec=specFor(entry.character),team=chosenMode==='adventure'?'red':entry.team==='blue'?'blue':'red',base=String(entry.id??`player-${i+1}`),id=ids.has(base)?`${base}-${i+1}`:base;ids.add(id);
    let point=sourceSpawns?[sourceSpawns[i].x,sourceSpawns[i].y]:chosenMode==='adventure'?all[i]:spawn[team][indices[team]++%4];
    if(usedSpawns.has(key(...point)))point=all.find(candidate=>!usedSpawns.has(key(...candidate)));
    const[x,y]=point;usedSpawns.add(key(x,y));
    g.players.push({id,name:String(entry.name||spec.name).slice(0,24),character:spec.id,team,isBot:!!entry.isBot,x,y,alive:true,trappedUntil:null,score:0,
      capacity:spec.capacity,range:spec.range,speed:spec.speed,hp:chosenMode==='push'?4:chosenMode==='adventure'?3:1,inventory:{needle:0},respawnAt:null,
      invulnerableUntil:0,carrying:null,shield:false,facing:{dx:team==='red'?1:-1,dy:0},_spawn:{x,y},_moveAt:0,_actionAt:0,_nextAction:400+i*100,_directionAt:-1000,_trappedBy:null});
  });
  g._competitiveTeams=[...new Set(g.players.map(p=>p.team))];if(chosenMode==='adventure')spawnWave(g);emit(g,'start',{mode:chosenMode});return g;
}
function dropBun(g,p){if(!p.carrying)return;g.pickups.push({x:p.x,y:p.y,type:'bun',team:p.carrying,availableAt:g.time});emit(g,'bun-dropped',{playerId:p.id,team:p.carrying,x:p.x,y:p.y});p.carrying=null;}
function eliminate(g,p,killerId=null){
  if(!p.alive)return;const killer=byId(g,killerId||p._trappedBy);p.alive=false;p.trappedUntil=null;p._trappedBy=null;dropBun(g,p);
  p.respawnAt=g.mode==='brawl'?g.time+3000:g.mode==='bun'?g.time+10000:null;
  if(killer&&killer!==p&&killer.team!==p.team){killer.score+=100;if(g.mode==='brawl')g.scores[killer.team]++;}
  emit(g,'eliminated',{playerId:p.id,by:killer?.id||null,respawnAt:p.respawnAt});
}
function rescue(g,p,rescuerId){p.trappedUntil=null;p._trappedBy=null;p.invulnerableUntil=g.time+1000;const rescuer=byId(g,rescuerId);if(rescuer&&rescuer!==p)rescuer.score+=30;emit(g,'rescued',{playerId:p.id,by:rescuerId});}
function contacts(g){
  const free=g.players.filter(p=>p.alive&&p.trappedUntil===null);
  for(const p of g.players.filter(p=>p.alive&&p.trappedUntil!==null)){
    const nearby=free.filter(other=>other.alive&&distance(other,p)<=1),enemy=nearby.find(other=>other.team!==p.team);
    if(enemy){eliminate(g,p,enemy.id);continue;}const friend=nearby.find(other=>other.team===p.team);if(friend)rescue(g,p,friend.id);
  }
}
function damage(g,p,ownerId=null){if(!p.alive||p.invulnerableUntil>g.time)return;p.hp=Math.max(0,p.hp-1);p.invulnerableUntil=g.time+1000;emit(g,'damage',{playerId:p.id,hp:p.hp,by:ownerId});if(p.hp<=0)eliminate(g,p,ownerId);}
function hitPlayer(g,p){
  if(!p.alive||p.trappedUntil!==null||p.invulnerableUntil>g.time)return;const blast=g.blasts.find(b=>b.x===p.x&&b.y===p.y);if(!blast)return;
  if(p.shield){p.shield=false;p.invulnerableUntil=g.time+1000;return;}
  if(g.mode==='push'||g.mode==='adventure'){damage(g,p,blast.ownerId);return;}
  p.trappedUntil=g.time+5000;p._trappedBy=blast.ownerId||null;emit(g,'trapped',{playerId:p.id,by:blast.ownerId||null,until:p.trappedUntil});
}
function collect(g,p){
  if(!p.alive||p.trappedUntil!==null)return;const spec=specFor(p.character);
  for(let i=g.pickups.length-1;i>=0;i--){const item=g.pickups[i];if(item.x!==p.x||item.y!==p.y||item.availableAt>g.time)continue;
    if(item.type==='bun'){
      if(g.mode!=='bun')continue;
      if(item.team===p.team){g.objectives[item.team].buns++;emit(g,'bun-returned',{team:item.team,playerId:p.id});}
      else if(!p.carrying){p.carrying=item.team;emit(g,'bun-taken',{team:item.team,playerId:p.id});}else continue;
    }else{
      if(item.type==='capacity')p.capacity=Math.min(spec.maxCapacity,p.capacity+1);if(item.type==='range')p.range=Math.min(spec.maxRange,p.range+1);if(item.type==='speed')p.speed=Math.min(spec.maxSpeed,p.speed+1);
      if(item.type==='needle')p.inventory.needle++;if(item.type==='shield')p.shield=true;p.score+=20;emit(g,'pickup',{playerId:p.id,item:item.type});
    }g.pickups.splice(i,1);
  }
  if(g.mode!=='bun')return;
  const home=g.objectives[p.team],other=p.team==='red'?'blue':'red',enemy=g.objectives[other];
  if(p.carrying&&p.x===home.x&&p.y===home.y){g.scores[p.team]++;p.score+=200;p.carrying=null;emit(g,'bun-delivered',{playerId:p.id,team:p.team,score:g.scores[p.team]});}
  else if(!p.carrying&&p.x===enemy.x&&p.y===enemy.y&&enemy.buns>0){enemy.buns--;p.carrying=other;emit(g,'bun-taken',{playerId:p.id,team:other});}
}
export function movePlayer(g,id,dx,dy){
  const p=byId(g,id);if(!active(g,p)||!Number.isInteger(dx)||!Number.isInteger(dy)||Math.abs(dx)+Math.abs(dy)!==1)return false;
  p.facing={dx,dy};p._directionAt=g.time;if(p.trappedUntil!==null||g.time<p._moveAt)return false;
  const x=p.x+dx,y=p.y+dy;
  if(g.sourceMap&&!canTraverseSource(g.sourceMap,p.x,p.y,x,y))return false;
  if(g.mode==='push'&&inside(g,x,y)&&g.grid[y][x]===2){const nx=x+dx,ny=y+dy;if(!walkable(g,p,nx,ny))return false;g.grid[y][x]=0;g.grid[ny][nx]=2;emit(g,'box-pushed',{playerId:id,from:{x,y},to:{x:nx,y:ny}});}
  if(!walkable(g,p,x,y))return false;p.x=x;p.y=y;collect(g,p);p._moveAt=g.time+interval(p);hitPlayer(g,p);contacts(g);return true;
}
function destroyBox(g,x,y,ownerId,withDrop=true){
  if(g.sourceMap){
    const cell=g.sourceMap.collision[y*g.width+x];if(!cell||cell.durability<=0)return;
    const object=g.sourceMap.sceneObjects.find(item=>item.id===cell.instanceId);if(!object||object.destroyed)return;
    object.lifeTime--;if(object.lifeTime<=0){object.destroyed=true;const owner=byId(g,ownerId);if(owner)owner.score+=10;emit(g,'box-broken',{x,y,elementId:object.elementId,playerId:ownerId});}
    const projected=projectSourceCollision(g.sourceMap);g.sourceMap.collision=projected.cells;g.sourceMap.grid=projected.grid;g.grid=projected.grid.map(row=>[...row]);return;
  }
  if(g.grid[y]?.[x]!==2)return;g.grid[y][x]=0;const owner=byId(g,ownerId);if(owner)owner.score+=10;
  if(withDrop){const roll=random(g),type=roll<0.04?'needle':roll<0.20?'capacity':roll<0.36?'range':roll<0.50?'speed':roll<0.55?'shield':null;if(type)g.pickups.push({x,y,type,availableAt:g.time+(g.mode==='push'?0:700)});}
  emit(g,'box-broken',{x,y,playerId:ownerId});
}
function kick(g,p){const{dx,dy}=p.facing,b=g.bombs.find(b=>(b.x===p.x+dx&&b.y===p.y+dy)||(b.x===p.x&&b.y===p.y));if(!b)return false;b.dx=dx;b.dy=dy;b.ownerId=p.id;b._nextRollAt=g.time+100;emit(g,'bubble-kicked',{playerId:p.id,bombId:b.id,dx,dy});return true;}
function shoot(g,p){
  const{dx,dy}=p.facing,x=p.x+dx,y=p.y+dy;if(g.grid[y]?.[x]!==2)return false;
  if(g.time-p._directionAt>400){destroyBox(g,x,y,p.id);return true;}
  g.grid[y][x]=0;let last={x,y};for(let n=1;n<=Math.max(g.width,g.height);n++){
    const nx=x+dx*n,ny=y+dy*n;if(!inside(g,nx,ny)||g.grid[ny][nx]!==0||g.bombs.some(b=>b.x===nx&&b.y===ny))break;
    const target=g.players.find(other=>other.alive&&other.x===nx&&other.y===ny);if(target){damage(g,target,p.id);break;}last={x:nx,y:ny};
  }g.grid[last.y][last.x]=2;emit(g,'box-shot',{playerId:p.id,from:{x,y},to:last});return true;
}
export function placeBomb(g,id){
  const p=byId(g,id);if(!active(g,p)||p.trappedUntil!==null||g.time<p._actionAt)return false;
  if(g.mode==='soccer'){if(!kick(g,p))return false;p._actionAt=g.time+250;return true;}
  if(g.mode==='push'){if(!shoot(g,p))return false;p._actionAt=g.time+400;return true;}
  if(g.sourceMap?.collision[p.y*g.width+p.x]?.occupied)return false;
  if(g.bombs.filter(b=>b.ownerId===id).length>=p.capacity||g.bombs.some(b=>b.x===p.x&&b.y===p.y))return false;
  g.bombs.push({id:`bubble-${++g._bombId}`,x:p.x,y:p.y,ownerId:id,explodeAt:g.time+5000,range:p.range});p._actionAt=g.time+160;emit(g,'bubble-placed',{playerId:id,x:p.x,y:p.y});return true;
}
export function useItem(g,id){const p=byId(g,id);if(!active(g,p)||p.trappedUntil===null||p.inventory.needle<1||g.time>=p.trappedUntil)return false;p.inventory.needle--;rescue(g,p,id);return true;}
function explode(g,b,queue,queued){
  const index=g.bombs.findIndex(other=>other.id===b.id);if(index<0)return;g.bombs.splice(index,1);const hitInstances=new Set();
  for(const{x,y}of rays(g,b)){
    g.blasts.push({x,y,expiresAt:g.time+700,ownerId:b.ownerId,sourceId:b.id});g.pickups=g.pickups.filter(item=>item.type==='bun'||item.x!==x||item.y!==y);
    if(g.sourceMap){
      const cell=g.sourceMap.collision[y*g.width+x];
      if(cell?.durability>0&&!hitInstances.has(cell.instanceId)){hitInstances.add(cell.instanceId);destroyBox(g,x,y,b.ownerId);}
    }else if(g.grid[y][x]===2)destroyBox(g,x,y,b.ownerId);
    for(const next of g.bombs)if(next.x===x&&next.y===y&&!queued.has(next.id)){queued.add(next.id);queue.push(next);}
  }emit(g,'bubble-burst',{bombId:b.id,x:b.x,y:b.y});
}
function roll(g){for(const b of g.bombs){if((!b.dx&&!b.dy)||g.time<(b._nextRollAt||0))continue;b._nextRollAt=g.time+130;const x=b.x+b.dx,y=b.y+b.dy;if(!inside(g,x,y)||g.grid[y][x]!==0||g.bombs.some(other=>other!==b&&other.x===x&&other.y===y)){b.dx=0;b.dy=0;}else{b.x=x;b.y=y;}}}
function sky(g){
  const cells=[];for(let y=0;y<g.height;y++)for(let x=0;x<g.width;x++)if(g.grid[y][x]===0&&!g.bombs.some(b=>b.x===x&&b.y===y))cells.push({x,y});if(!cells.length)return;
  const cell=cells[Math.floor(random(g)*cells.length)];g.bombs.push({id:`bubble-${++g._bombId}`,...cell,ownerId:null,explodeAt:g.time+5000,range:3,dx:0,dy:0});emit(g,'sky-bubble',cell);
}
function fire(g){const y=Math.floor(random(g)*g.height),sourceId=`fire-${++g._eventId}`;for(let x=0;x<g.width;x++)if(g.grid[y][x]===0)g.blasts.push({x,y,expiresAt:g.time+850,ownerId:null,sourceId,type:'fire'});emit(g,'fire-row',{y});}
function respawn(g,p){
  let point=p._spawn;if(!walkable(g,p,point.x,point.y)){const options=[];for(let y=0;y<g.height;y++)for(let x=0;x<g.width;x++)if(walkable(g,p,x,y))options.push({x,y});options.sort((a,b)=>distance(a,p._spawn)-distance(b,p._spawn));if(!options.length){p.respawnAt=g.time+200;return;}point=options[0];}
  p.x=point.x;p.y=point.y;p.alive=true;p.trappedUntil=null;p.respawnAt=null;p.invulnerableUntil=g.time+2000;p.hp=1;p._moveAt=g.time;emit(g,'respawn',{playerId:p.id});
}
function spawnWave(g){
  const count=g.wave===1?2:3,cells=[{x:7,y:6},{x:7,y:3},{x:7,y:9}],monsters=[];
  for(let i=0;i<count;i++){const boss=g.wave===3&&i===0,hp=boss?6:g.wave===1?1:2,point=cells[i];g.grid[point.y][point.x]=0;monsters.push({id:`wave-${g.wave}-monster-${i+1}`,...point,hp,maxHp:hp,boss,alive:true,_nextMove:g.time+700+i*130,_attackAt:g.time+1500,_blastHits:[]});}
  g.monsters=monsters;g._waveReadyAt=null;emit(g,'wave',{wave:g.wave,monsters:count});
}
function monsters(g){
  for(const m of g.monsters){if(!m.alive)continue;
    const hit=g.blasts.find(b=>b.x===m.x&&b.y===m.y&&!m._blastHits.includes(b.sourceId));
    if(hit){m._blastHits.push(hit.sourceId);m.hp--;const owner=byId(g,hit.ownerId);if(owner)owner.score+=40;if(m.hp<=0){m.alive=false;if(owner)owner.score+=m.boss?400:100;emit(g,'monster-defeated',{monsterId:m.id,boss:m.boss});continue;}}
    const target=g.players.filter(p=>p.alive).sort((a,b)=>distance(a,m)-distance(b,m))[0];if(!target)continue;
    if(distance(target,m)<=1&&g.time>=m._attackAt){m._attackAt=g.time+(m.boss?1000:1400);damage(g,target,m.id);}
    if(g.time<m._nextMove)continue;m._nextMove=g.time+(m.boss?600:750);
    const choices=DIRS.map(([dx,dy])=>({x:m.x+dx,y:m.y+dy})).filter(p=>inside(g,p.x,p.y)&&g.grid[p.y][p.x]===0&&!g.bombs.some(b=>b.x===p.x&&b.y===p.y)&&!occupied(g,p.x,p.y)&&!g.monsters.some(other=>other!==m&&other.alive&&other.x===p.x&&other.y===p.y));
    choices.sort((a,b)=>distance(a,target)-distance(b,target));if(choices.length){const point=random(g)<0.8?choices[0]:choices[Math.floor(random(g)*choices.length)];m.x=point.x;m.y=point.y;}
  }
  if(g.monsters.every(m=>!m.alive)&&g.wave<3){if(g._waveReadyAt===null)g._waveReadyAt=g.time+1500;if(g.time>=g._waveReadyAt){g.wave++;spawnWave(g);}}
}
function goalFor(g,p){
  const closest=items=>items.sort((a,b)=>distance(a,p)-distance(b,p))[0];
  const friend=closest(g.players.filter(other=>other!==p&&other.alive&&other.team===p.team&&other.trappedUntil!==null));if(friend)return{target:friend,adjacent:true};
  const trapped=closest(g.players.filter(other=>other.alive&&other.team!==p.team&&other.trappedUntil!==null));if(trapped)return{target:trapped,adjacent:true};
  if(g.mode==='bun'){
    if(p.carrying)return{target:g.objectives[p.team],adjacent:false};const dropped=closest(g.pickups.filter(item=>item.type==='bun'));if(dropped)return{target:dropped,adjacent:false};
    const enemy=p.team==='red'?'blue':'red';if(g.objectives[enemy].buns>0)return{target:g.objectives[enemy],adjacent:false};
  }
  const pickup=closest(g.pickups.filter(item=>item.type!=='bun'&&item.availableAt<=g.time&&distance(item,p)<=5));if(pickup)return{target:pickup,adjacent:false};
  const target=closest(g.mode==='adventure'?g.monsters.filter(m=>m.alive):g.players.filter(other=>other.alive&&other.team!==p.team));return target?{target,adjacent:true}:null;
}
function bot(g,p){
  if(!p.alive)return;if(p.trappedUntil!==null){if(p.inventory.needle>0&&p.trappedUntil-g.time<4000)useItem(g,p.id);return;}
  if(g.time<p._nextAction)return;p._nextAction=g.time+interval(p)+random(g)*80;
  if(g.mode==='soccer')for(const[dx,dy]of DIRS)if(g.bombs.some(b=>b.x===p.x+dx&&b.y===p.y+dy)){p.facing={dx,dy};if(placeBomb(g,p.id))break;}
  const danger=dangers(g);if(danger.has(key(p.x,p.y))){const path=escape(g,p,danger);if(path?.length)movePlayer(g,p.id,...path[0]);return;}
  const goal=goalFor(g,p);
  if(g.mode==='push'){const box=DIRS.find(([dx,dy])=>g.grid[p.y+dy]?.[p.x+dx]===2);if(box){p.facing={dx:box[0],dy:box[1]};p._directionAt=g.time;placeBomb(g,p.id);}}
  else if(g.mode!=='soccer'){
    const proposed={x:p.x,y:p.y,range:p.range},cells=rays(g,proposed),crate=cells.some(c=>g.grid[c.y][c.x]===2),target=goal&&cells.some(c=>c.x===goal.target.x&&c.y===goal.target.y);
    if((crate||target)&&random(g)<0.65){const path=escape(g,p,dangers(g,proposed),6);if(path&&placeBomb(g,p.id)){movePlayer(g,p.id,...path[0]);return;}}
  }
  if(goal){const near=goal.adjacent?distance(p,goal.target)<=1:distance(p,goal.target)===0;if(!near){const path=route(g,p,n=>goal.adjacent?distance(n,goal.target)<=1:distance(n,goal.target)===0,{danger});if(path?.length){movePlayer(g,p.id,...path[0]);return;}}}
  const choices=DIRS.filter(([dx,dy])=>walkable(g,p,p.x+dx,p.y+dy)&&!danger.has(key(p.x+dx,p.y+dy)));if(choices.length)movePlayer(g,p.id,...choices[Math.floor(random(g)*choices.length)]);
}
function finish(g,team,reason){if(g.status!=='playing')return;g.status='finished';g.winnerTeam=team;g.endReason=reason;emit(g,'finished',{winnerTeam:team,reason});}
function evaluate(g){
  if(g.mode==='adventure'){
    if(!g.players.some(p=>p.alive)){finish(g,'monsters','all-players-out');return;}if(g.wave===3&&g.monsters.every(m=>!m.alive)){finish(g,'red','all-waves-cleared');return;}if(g.time>=g.duration*1000)finish(g,'monsters','time-limit');return;
  }
  if(g.mode==='brawl'||g.mode==='bun'){
    if(Math.max(g.scores.red,g.scores.blue)>=g.targetScore){finish(g,g.scores.red===g.scores.blue?'draw':g.scores.red>g.scores.blue?'red':'blue','objective');return;}
  }else if(g._competitiveTeams.length>1){
    const survivors=g.players.filter(p=>p.alive),teams=[...new Set(survivors.map(p=>p.team))];if(!survivors.length){finish(g,'draw','all-players-out');return;}if(teams.length===1&&survivors.some(p=>p.trappedUntil===null)){finish(g,teams[0],'team-eliminated');return;}
  }
  if(g.time<g.duration*1000)return;
  if(g.mode==='brawl'||g.mode==='bun'){finish(g,g.scores.red===g.scores.blue?'draw':g.scores.red>g.scores.blue?'red':'blue','time-limit');return;}
  const rank={red:{alive:0,score:0,hp:0},blue:{alive:0,score:0,hp:0}};for(const p of g.players){rank[p.team].alive+=Number(p.alive);rank[p.team].score+=p.score;rank[p.team].hp+=p.alive?p.hp:0;}
  const a=rank.red,b=rank.blue,diff=a.alive-b.alive||(g.mode==='push'?a.hp-b.hp:0)||a.score-b.score;finish(g,diff===0?'draw':diff>0?'red':'blue','time-limit');
}
export function tick(g,dt){
  if(g.status!=='playing'||!Number.isFinite(dt)||dt<=0)return false;g.time=Math.min(g.duration*1000,g.time+Math.min(100,dt));g.blasts=g.blasts.filter(b=>b.expiresAt>g.time);
  if(g.mode==='soccer'){roll(g);if(g.time>=g._nextSkyAt){sky(g);g._nextSkyAt=g.time+1800;}}
  if(g.mode==='push'&&g.time>=g._nextFireAt){fire(g);g._nextFireAt=g.time+6000;}
  const queue=g.bombs.filter(b=>b.explodeAt<=g.time),queued=new Set(queue.map(b=>b.id));for(let i=0;i<queue.length;i++)explode(g,queue[i],queue,queued);
  for(const p of g.players){hitPlayer(g,p);if(p.alive&&p.trappedUntil!==null&&g.time>=p.trappedUntil)eliminate(g,p);if(!p.alive&&p.respawnAt!==null&&g.time>=p.respawnAt)respawn(g,p);collect(g,p);}
  contacts(g);for(const p of g.players)if(p.isBot)bot(g,p);if(g.mode==='adventure')monsters(g);contacts(g);for(const p of g.players)collect(g,p);evaluate(g);return true;
}
