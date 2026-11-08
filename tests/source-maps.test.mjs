import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileOriginalMap,canTraverseSource,sourceFlameStep} from '../src/original-maps.js';
import {createGame,movePlayer,placeBomb,tick} from '../src/game.js';
import {loadMapCatalog} from '../server/map-catalog.mjs';
import {createAppServer} from '../server/app.mjs';

const fixtureElement=(id,w=1,h=1,attrs=[0],life=-1)=>({id,className:`Test${id}`,widthCells:w,heightCells:h,gridAttr:attrs,imageOffset:[0,0],properties:{size:[w,h],GridAttr:attrs,LifeTime:life,canMove:0}});
function fixture(width=19,height=7){
  const table=entries=>({count:entries.length,entries});
  return{header:{version:4,nativeRule:1,width,height,dimensionSource:'artificial-test'},source:{sha256:'test-only-not-original',officialOriginalAuthenticity:'unverified'},
    layers:Array.from({length:3},(_,index)=>({index,values:Array(width*height).fill(0)})),
    tables:{wallItems:table([]),hiddenItems:table([]),spawnGroupA:table([{row:0,col:0},{row:height-1,col:width-1}]),spawnGroupB:table([]),objectives:table([])},
    catalogEntries:[{id:999999,name:'人工测试夹具',playerLimit:2,catalogWidth:width,catalogHeight:height}]};
}
const people=[{id:'a',team:'red',character:'maomao',isBot:false},{id:'b',team:'blue',character:'asha',isBot:false}];
const advance=(g,ms)=>{for(let n=0;n<ms&&g.status==='playing';n+=50)tick(g,Math.min(50,ms-n));};
const directory=await loadMapCatalog();

test('China Town 01 imports exact layers, footprint, source spawns and the catalog four-seat limit',async()=>{
  const raw=JSON.parse(await readFile(new URL('../references/qqtang-map-data/maps/town01_4.json',import.meta.url)));
  const compiled=directory.getRuntime('source-201');
  assert.equal(compiled.width,15);assert.equal(compiled.height,13);assert.equal(compiled.playerLimit,4);
  assert.equal(compiled.source.sha256,'10f84593742d90af379f9698d7e003111ea8c5b209f87ac27f3717afdcbec4ca');
  assert.deepEqual(compiled.layers,raw.layers);assert.deepEqual(compiled.tables,raw.tables);
  assert.equal(compiled.sceneObjects.find(o=>o.elementId===3019).width,4);
  assert.equal(compiled.sceneObjects.find(o=>o.elementId===3019).height,2);
  const a=createGame({map:'source-201',sourceMap:compiled,seed:1}),b=createGame({map:'source-201',sourceMap:compiled,seed:999});
  assert.deepEqual(a.grid,compiled.grid);assert.deepEqual(a.grid,b.grid,'source map must never be randomized');
  assert.deepEqual(a.players.map(p=>({x:p.x,y:p.y})),raw.tables.spawnGroupA.entries.map(c=>({x:c.col,y:c.row})));
  assert.deepEqual(a.originalTargets,[]);assert.equal(a.objectives.red,null);
  a.sourceMap.layers[1].values[0]=999;assert.deepEqual(compiled.layers,raw.layers,'runtime is isolated from catalog');
  assert.throws(()=>createGame({map:'source-201'}),{code:'SOURCE_DATA_REQUIRED'});
  assert.throws(()=>createGame({sourceMap:compiled,mode:'bun'}),{code:'SOURCE_RULE_UNSUPPORTED'});
  assert.throws(()=>createGame({sourceMap:compiled,participants:Array.from({length:5},(_,i)=>({id:String(i),team:i%2?'red':'blue'}))}),{code:'SOURCE_PLAYER_LIMIT'});
});

test('runtime uses actual variable width and height at edges, in movement and splash propagation',()=>{
  const raw=fixture(),map=compileOriginalMap(raw,[]),game=createGame({sourceMap:map,participants:people});
  assert.deepEqual([game.width,game.height],[19,7]);assert.equal(game.grid[0][0],0,'no synthetic border is inserted');
  const player=game.players[0];player.x=17;player.y=0;player.range=4;
  assert.equal(placeBomb(game,'a'),true);assert.equal(movePlayer(game,'a',1,0),true);
  advance(game,250);assert.equal(movePlayer(game,'a',1,0),false,'actual width bounds');
  player.x=0;player.y=0;advance(game,4750);
  assert.ok(game.blasts.some(b=>b.x===18&&b.y===0));
  assert.ok(game.blasts.every(b=>b.x>=0&&b.x<19&&b.y>=0&&b.y<7));
  assert.equal(map.pixelDimensions.width,760);assert.equal(map.pixelDimensions.status,'candidate-community-40px-constant');
  const realLarge=directory.getRuntime('source-1601');
  assert.deepEqual([realLarge.width,realLarge.height],[40,17]);
  assert.equal(realLarge.layers[2].values.length,680);
  assert.throws(()=>createGame({sourceMap:realLarge,participants:people}),{code:'SOURCE_RULE_UNSUPPORTED'},'PvE data is not relabeled ordinary combat');
});

test('full footprints, row-major last writer and directional player/flame attributes remain separate',()=>{
  const raw=fixture(6,4);raw.layers[0].values[1*6+1]=100;raw.layers[1].values[1*6+2]=101;
  const map=compileOriginalMap(raw,[fixtureElement(100,2,1,[0,0]),fixtureElement(101,1,1,[0x0f08])]);
  assert.equal(map.grid[1][1],1);assert.equal(map.grid[1][2],0,'later layer overwrites footprint summary');
  assert.equal(map.collision[8].exitAttr,0,'exit retains layer zero even after layer one overwrite');
  assert.equal(canTraverseSource(map,1,0,2,0),true);
  assert.equal(canTraverseSource(map,2,0,2,1),false,'down entry bit is closed');
  assert.equal(canTraverseSource(map,3,1,2,1),false,'left entry bit is closed');
  assert.equal(sourceFlameStep(map,2,0,2,1).enter,true,'flame has separate directional group');
  raw.layers[0].values[1*6+1]=-100;
  const ignored=compileOriginalMap(raw,[fixtureElement(101,1,1,[0x0f08])]);
  assert.equal(ignored.grid[1][1],0,'negative editor markers do not invent standalone walls');
  assert.equal(ignored.layers[0].values[7],-100,'signed source value is retained');
});

test('unknown elements, invalid footprints and malformed layer lengths fail closed',()=>{
  const unknown=fixture();unknown.layers[2].values[20]=999;
  assert.throws(()=>compileOriginalMap(unknown,[]),{code:'SOURCE_UNKNOWN_ELEMENT'});
  const overflow=fixture();overflow.layers[1].values[18]=10;
  assert.throws(()=>compileOriginalMap(overflow,[fixtureElement(10,2,1,[0,0])]),{code:'SOURCE_FOOTPRINT_BOUNDS'});
  const truncated=fixture();truncated.layers[1].values.pop();assert.throws(()=>compileOriginalMap(truncated,[]),{code:'SOURCE_LAYERS'});
});

test('source destructible instances respect durability without random replacement boxes or invented drops',()=>{
  const raw=fixture(6,4);raw.layers[1].values[2]=10;
  const map=compileOriginalMap(raw,[fixtureElement(10,1,1,[0],2)]),g=createGame({sourceMap:map,participants:people});
  const p=g.players[0];p.x=1;p.range=3;placeBomb(g,'a');p.x=0;p.y=3;advance(g,5000);
  assert.equal(g.grid[0][2],2);assert.equal(g.sourceMap.sceneObjects[0].lifeTime,1);assert.equal(g.pickups.length,0);
  advance(g,800);p.x=1;p.y=0;placeBomb(g,'a');p.x=0;p.y=3;advance(g,5000);
  assert.equal(g.grid[0][2],0);assert.equal(g.sourceMap.sceneObjects[0].destroyed,true);assert.equal(g.pickups.length,0);
  assert.equal(g.sourceMap.layers[1].values[2],10,'source layer remains an immutable provenance record');
});

test('actual map directory preserves 381 catalog rows, source authenticity and unavailable reasons',()=>{
  assert.equal(directory.maps.length,381);assert.equal(directory.get('source-201').maxSeats,4);
  assert.equal(directory.get('source-201').officialOriginalAuthenticity,'unverified');
  assert.equal(directory.get('source-0').unavailableCode,'SOURCE_FILE_MISSING');
  assert.equal(directory.maps.filter(m=>m.unavailableCode==='SOURCE_UNKNOWN_ELEMENT').length,22);
  assert.ok(directory.maps.filter(m=>m.width!==15&&m.width!==null).every(m=>m.width>15));
  assert.ok(directory.draftMaps.every(m=>m.geometryStatus==='unaccepted-custom-draft'));
});

test('server selects actual source map, returns max seats, and rejects a fifth human or incompatible mode',async t=>{
  const app=createAppServer({port:0});const address=await app.start();t.after(()=>app.close());
  const url=`http://127.0.0.1:${address.port}`;
  const request=async(path,body,token)=>{const r=await fetch(url+path,{method:body?'POST':'GET',headers:{...(body?{'content-type':'application/json'}:{}),...(token?{authorization:`Bearer ${token}`}:{})},...(body?{body:JSON.stringify(body)}:{})});return{status:r.status,data:await r.json()};};
  const listing=await request('/api/maps');assert.equal(listing.status,200);assert.equal(listing.data.maps.length,381);
  const users=[];for(let i=0;i<5;i++)users.push((await request('/api/session',{name:`原图玩家${i}`})).data);
  const owner=users[0],create=await request('/api/rooms',{name:'中国城测试',map:'source-201',mode:'classic',bots:0,duration:60},owner.token);
  assert.equal(create.status,200);assert.equal(create.data.currentRoom.max,4);const id=create.data.currentRoom.id;
  for(let i=1;i<4;i++){assert.equal((await request(`/api/rooms/${id}/join`,{},users[i].token)).status,200);await request('/api/action',{action:'ready',ready:true},users[i].token);}
  assert.equal((await request(`/api/rooms/${id}/join`,{},users[4].token)).data.code,'ROOM_FULL');
  assert.equal((await request('/api/action',{action:'seat',seat:4,locked:true},owner.token)).data.code,'MAP_SEAT_LIMIT');
  assert.equal((await request('/api/action',{action:'config',mode:'bun'},owner.token)).data.code,'SOURCE_RULE_UNSUPPORTED');
  const started=await request('/api/action',{action:'start'},owner.token);assert.equal(started.status,200);assert.equal(started.data.currentRoom.game.mapKind,'source-map');
  assert.deepEqual(started.data.currentRoom.game.grid,directory.getRuntime('source-201').grid);
  assert.equal(started.data.currentRoom.game.sourceMap.layers.length,3);
});
