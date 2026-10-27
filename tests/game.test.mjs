import test from 'node:test';
import assert from 'node:assert/strict';
import {CHARACTERS,MODES,createGame,movePlayer,placeBomb,useItem,tick} from '../src/game.js';
const participants=[{id:'you',name:'毛毛',character:'maomao',team:'red',isBot:false},{id:'friend',name:'阿莎',character:'asha',team:'red',isBot:false},{id:'enemy',name:'泰坦',character:'titan',team:'blue',isBot:false}];
const gameFor=mode=>createGame({mode,participants,seed:42,duration:180});
function advance(g,ms){for(let n=0;n<ms&&g.status==='playing';n+=50)tick(g,Math.min(50,ms-n));}
function openGrid(g){for(let y=1;y<12;y++)for(let x=1;x<14;x++)g.grid[y][x]=0;}
function pos(g,id,x,y){const p=g.players.find(p=>p.id===id);Object.assign(p,{x,y,_moveAt:g.time});return p;}
test('historical character baselines, six modes and eight unique spawn points',()=>{
  assert.deepEqual(CHARACTERS.map(c=>[c.id,c.capacity,c.maxCapacity,c.range,c.maxRange,c.speed,c.maxSpeed]),[['maomao',2,6,2,7,5,8],['asha',2,6,2,7,5,8],['wukong',2,7,1,8,4,7],['titan',2,6,3,9,3,6]]);
  assert.deepEqual(MODES.map(m=>m.id),['classic','brawl','bun','soccer','push','adventure']);
  const g=createGame({seed:9});assert.equal(g.width,15);assert.equal(g.height,13);assert.deepEqual(g.grid,createGame({seed:9}).grid);assert.doesNotThrow(()=>JSON.stringify(g));
  const eight=createGame({participants:Array.from({length:8},(_,i)=>({id:String(i),team:i%2?'blue':'red',character:CHARACTERS[i%4].id}))});assert.equal(new Set(eight.players.map(p=>`${p.x},${p.y}`)).size,8);
  const sameTeam=createGame({participants:Array.from({length:8},(_,i)=>({id:String(i),team:'red'}))});assert.equal(new Set(sameTeam.players.map(p=>`${p.x},${p.y}`)).size,8);
});
test('authoritative movement rejects flooding, walls and bomb re-entry',()=>{
  const g=gameFor('classic');assert.equal(movePlayer(g,'you',-1,0),false);assert.equal(movePlayer(g,'you',1,1),false);assert.equal(placeBomb(g,'you'),true);
  assert.equal(movePlayer(g,'you',1,0),true);assert.equal(movePlayer(g,'you',1,0),false);advance(g,220);assert.equal(movePlayer(g,'you',-1,0),false);assert.equal(movePlayer(g,'you',1,0),true);
});
test('five-second fuse, stopping at first box and chained bubbles',()=>{
  const g=gameFor('classic');openGrid(g);const p=pos(g,'you',3,3);p.range=4;g.grid[3][4]=2;g.grid[3][5]=2;
  placeBomb(g,'you');pos(g,'you',3,5);advance(g,1000);placeBomb(g,'you');pos(g,'you',1,1);advance(g,3950);assert.equal(g.bombs.length,2);
  advance(g,50);assert.equal(g.bombs.length,0);assert.equal(g.grid[3][4],0);assert.equal(g.grid[3][5],2);assert.ok(!g.blasts.some(b=>b.x===5&&b.y===3));
});
test('five-second trap requires a collected needle for self-rescue',()=>{
  const g=gameFor('classic');placeBomb(g,'you');advance(g,5000);const p=g.players[0];assert.equal(p.trappedUntil,10000);assert.equal(useItem(g,'you'),false);
  p.inventory.needle=1;assert.equal(useItem(g,'you'),true);assert.equal(p.inventory.needle,0);assert.equal(p.trappedUntil,null);assert.ok(p.invulnerableUntil>g.time);
});
test('adjacent teammate rescues; adjacent enemy eliminates the trapped opponent',()=>{
  const g=gameFor('classic');openGrid(g);const p=pos(g,'you',3,3);p.trappedUntil=5000;pos(g,'friend',3,5);pos(g,'enemy',11,11);movePlayer(g,'friend',0,-1);assert.equal(p.trappedUntil,null);assert.equal(p.alive,true);
  p.trappedUntil=5000;p.invulnerableUntil=0;pos(g,'friend',1,1);pos(g,'enemy',5,3);movePlayer(g,'enemy',-1,0);assert.equal(p.alive,false);assert.equal(g.players[2].score,100);
});
test('ordinary team knockout waits for mutually trapped survivors',()=>{
  const g=createGame({participants:[participants[0],participants[2]]});g.players[0].trappedUntil=100;g.players[1].trappedUntil=200;advance(g,100);assert.equal(g.status,'playing');advance(g,100);assert.equal(g.winnerTeam,'draw');
  const knockout=gameFor('classic');knockout.players[2].alive=false;tick(knockout,50);assert.equal(knockout.winnerTeam,'red');
});
test('brawl scores eliminations and respawns after three seconds',()=>{
  const g=gameFor('brawl');openGrid(g);const enemy=pos(g,'enemy',3,3);enemy.trappedUntil=5000;pos(g,'you',3,5);movePlayer(g,'you',0,-1);assert.equal(g.scores.red,1);assert.equal(enemy.respawnAt,3000);
  advance(g,2950);assert.equal(enemy.alive,false);advance(g,50);assert.equal(enemy.alive,true);g.scores.red=10;tick(g,50);assert.equal(g.winnerTeam,'red');
});
test('bun hauling changes stock, slows movement, drops on defeat and respawns at ten seconds',()=>{
  const g=gameFor('bun');openGrid(g);const p=pos(g,'you',13,5);movePlayer(g,'you',0,1);assert.equal(p.carrying,'blue');assert.equal(g.objectives.blue.buns,2);assert.ok(p._moveAt-g.time>220);
  pos(g,'you',1,5);movePlayer(g,'you',0,1);assert.equal(g.scores.red,1);assert.equal(p.carrying,null);
  p.carrying='blue';p.trappedUntil=1;tick(g,50);assert.equal(p.alive,false);assert.equal(p.respawnAt,10050);assert.ok(g.pickups.some(item=>item.type==='bun'&&item.team==='blue'));
  advance(g,10000);assert.equal(p.alive,true);g.scores.red=3;tick(g,50);assert.equal(g.winnerTeam,'red');
});
test('soccer uses sky bubbles and space kicks a rolling bubble',()=>{
  const g=gameFor('soccer');openGrid(g);assert.equal(placeBomb(g,'you'),false);assert.equal(g.bombs.length,0);advance(g,800);assert.equal(g.bombs.length,1);
  const p=pos(g,'you',3,3);p.facing={dx:1,dy:0};Object.assign(g.bombs[0],{x:4,y:3});assert.equal(placeBomb(g,'you'),true);advance(g,100);assert.equal(g.bombs[0].x,5);assert.equal(g.bombs[0].ownerId,'you');
});
test('push has four HP, movement pushes, shooting damages and idle space breaks boxes',()=>{
  const g=gameFor('push');openGrid(g);const p=pos(g,'you',3,3),enemy=pos(g,'enemy',7,3);assert.equal(p.hp,4);g.grid[3][4]=2;
  assert.equal(movePlayer(g,'you',1,0),true);assert.equal(g.grid[3][5],2);assert.equal(placeBomb(g,'you'),true);assert.equal(enemy.hp,3);assert.equal(g.bombs.length,0);
  advance(g,450);p.facing={dx:1,dy:0};g.grid[3][5]=2;assert.equal(placeBomb(g,'you'),true);assert.equal(g.grid[3][5],0);
  enemy.hp=1;enemy.invulnerableUntil=0;g.grid[3][5]=2;g.grid[3][6]=0;advance(g,400);p._directionAt=g.time;placeBomb(g,'you');tick(g,50);assert.equal(enemy.alive,false);assert.equal(g.winnerTeam,'red');
});
test('adventure advances three waves with a boss, clear win and party-wipe loss',()=>{
  const g=gameFor('adventure');assert.ok(g.players.every(p=>p.team==='red'));assert.equal(g.wave,1);
  for(let wave=1;wave<=3;wave++){
    assert.equal(g.wave,wave);
    if(wave===3){
      const boss=g.monsters.find(m=>m.boss);assert.equal(boss.maxHp,6);boss._nextMove=Infinity;
      g.blasts.push(...['one','two'].map(sourceId=>({x:boss.x,y:boss.y,sourceId,expiresAt:g.time+500,ownerId:'you'})));
      advance(g,250);assert.equal(boss.hp,4,'each source can damage a monster only once');
    }
    g.monsters.forEach(m=>{m.alive=false;m.hp=0;});advance(g,wave===3?50:1550);
  }
  assert.equal(g.winnerTeam,'red');const lost=gameFor('adventure');lost.players.forEach(p=>p.alive=false);tick(lost,50);assert.equal(lost.winnerTeam,'monsters');
});
test('all modes terminate at time limit and reject invalid deltas',()=>{
  for(const mode of MODES){const g=createGame({mode:mode.id,duration:1});assert.equal(tick(g,NaN),false);tick(g,10000);assert.equal(g.time,100);advance(g,900);assert.equal(g.status,'finished',mode.id);assert.ok(['red','blue','draw','monsters'].includes(g.winnerTeam));assert.ok(g.events.length<=20);}
});
