import test from 'node:test';
import assert from 'node:assert/strict';
import {setTimeout as delay} from 'node:timers/promises';
import {createAppServer} from '../server/app.mjs';

async function harness(t){
  const app=createAppServer({port:0,tickMs:25});const address=await app.start();
  const base=`http://127.0.0.1:${address.port}`;t.after(()=>app.close());
  const request=async(route,body,token,extra={})=>{
    const headers={...(body===undefined?{}:{'content-type':'application/json'}),...(token?{authorization:`Bearer ${token}`}:{})};
    const res=await fetch(base+route,{method:body===undefined?'GET':'POST',headers:{...headers,...extra},body:body===undefined?undefined:JSON.stringify(body)});
    return {status:res.status,data:await res.json()};
  };
  const session=async(name='测试玩家',character='maomao')=>{
    const res=await request('/api/session',{name,character});assert.equal(res.status,201);return res.data;
  };
  const create=async(user,patch={})=>{
    const res=await request('/api/rooms',{name:'集成测试房间',mode:'classic',map:'courtyard',bots:0,duration:60,...patch},user.token);
    assert.equal(res.status,200,JSON.stringify(res.data));return res.data;
  };
  return {app,base,request,session,create};
}

test('health and real assets are served while unauthenticated and cross-origin API mutations are rejected',async t=>{
  const h=await harness(t);
  assert.equal((await h.request('/api/health')).data.authoritative,true);
  assert.equal((await h.request('/api/state')).status,401);
  const cross=await h.request('/api/session',{name:'外部页面'},null,{origin:'https://example.invalid'});
  assert.equal(cross.status,403);assert.equal(cross.data.code,'ORIGIN_REJECTED');
  const asset=await fetch(h.base+'/assets/game-atlas.png');assert.equal(asset.status,200);
  assert.match(asset.headers.get('content-type'),/^image\/png/);
  assert.equal(Buffer.from(await asset.arrayBuffer()).subarray(0,8).toString('hex'),'89504e470d0a1a0a');
  assert.equal((await fetch(h.base+'/server/app.mjs')).status,403);
  assert.equal((await fetch(h.base+'/.git/config')).status,403);
});

test('two independent sessions share one room; owner cannot start before peer ready and peers cannot change owner settings',async t=>{
  const h=await harness(t),a=await h.session('房主','maomao'),b=await h.session('队友','asha');
  assert.notEqual(a.token,b.token);assert.notEqual(a.session.id,b.session.id);
  const created=await h.create(a);const roomId=created.currentRoom.id;
  const joined=await h.request(`/api/rooms/${roomId}/join`,{},b.token);assert.equal(joined.status,200);
  assert.equal(joined.data.currentRoom.members.length,2);
  assert.equal((await h.request('/api/action',{action:'start'},a.token)).data.code,'NOT_READY');
  assert.equal((await h.request('/api/action',{action:'config',mode:'bun'},b.token)).status,403);
  assert.equal((await h.request('/api/action',{action:'ready',ready:true},b.token)).status,200);
  const started=await h.request('/api/action',{action:'start'},a.token);assert.equal(started.status,200);
  assert.equal(started.data.currentRoom.game.players.length,2);
  assert.deepEqual(new Set(started.data.currentRoom.game.players.map(p=>p.id)),new Set([a.session.id,b.session.id]));
  assert.equal((await h.request('/api/action',{action:'character',character:'titan'},b.token)).data.code,'ROOM_BUSY');
  assert.equal((await h.request('/api/action',{action:'pause',paused:true},b.token)).status,403);
});

test('server chooses the authenticated player, ignores spoofed player ids and prevents diagonal moves',async t=>{
  const h=await harness(t),a=await h.session('甲'),b=await h.session('乙','titan');
  const r=await h.create(a);await h.request(`/api/rooms/${r.currentRoom.id}/join`,{},b.token);
  await h.request('/api/action',{action:'ready',ready:true},b.token);
  let s=(await h.request('/api/action',{action:'start'},a.token)).data;
  const original=s.currentRoom.game.players.find(p=>p.id===b.session.id);
  const me=s.currentRoom.game.players.find(p=>p.id===a.session.id);
  const dir=[[1,0],[0,1],[-1,0],[0,-1]].find(([dx,dy])=>s.currentRoom.game.grid[me.y+dy]?.[me.x+dx]===0);
  assert.ok(dir,'spawn has a legal neighbor');
  const moved=await h.request('/api/input',{type:'move',id:b.session.id,dx:dir[0],dy:dir[1]},a.token);
  assert.equal(moved.status,200);assert.equal(moved.data.accepted,true);
  const peer=moved.data.currentRoom.game.players.find(p=>p.id===b.session.id);
  assert.deepEqual([peer.x,peer.y],[original.x,original.y]);
  const mover=moved.data.currentRoom.game.players.find(p=>p.id===a.session.id);
  assert.deepEqual([mover.x,mover.y],[me.x+dir[0],me.y+dir[1]]);
  assert.equal((await h.request('/api/input',{type:'move',dx:1,dy:1},a.token)).status,400);
  const bomb=await h.request('/api/input',{type:'bomb',ownerId:b.session.id},a.token);
  assert.equal(bomb.status,200);assert.equal(bomb.data.accepted,true);
  assert.ok(bomb.data.currentRoom.game.bombs.every(item=>item.ownerId===a.session.id));
});

test('owner pause freezes authoritative time, blocks inputs, then resumes the same game',async t=>{
  const h=await harness(t),a=await h.session('暂停房主');await h.create(a,{bots:1});
  await h.request('/api/action',{action:'start'},a.token);
  const paused=await h.request('/api/action',{action:'pause',paused:true},a.token);
  const time=paused.data.currentRoom.game.time,id=paused.data.currentRoom.game.id;
  await delay(180);
  assert.equal((await h.request('/api/state',undefined,a.token)).data.currentRoom.game.time,time);
  assert.equal((await h.request('/api/input',{type:'bomb'},a.token)).data.code,'PAUSED');
  await h.request('/api/action',{action:'pause',paused:false},a.token);await delay(100);
  const resumed=(await h.request('/api/state',undefined,a.token)).data.currentRoom.game;
  assert.equal(resumed.id,id);assert.ok(resumed.time>time);
});

test('eight human seats are enforced and joining a full AI room replaces one AI',async t=>{
  const h=await harness(t),owner=await h.session('第一席');const created=await h.create(owner);
  for(let i=1;i<8;i++){
    const peer=await h.session(`席位${i+1}`);
    assert.equal((await h.request(`/api/rooms/${created.currentRoom.id}/join`,{},peer.token)).status,200);
  }
  const ninth=await h.session('第九席');
  assert.equal((await h.request(`/api/rooms/${created.currentRoom.id}/join`,{},ninth.token)).data.code,'ROOM_FULL');
  const other=await h.session('AI房主'),full=await h.create(other,{bots:7});
  const replacement=await h.request(`/api/rooms/${full.currentRoom.id}/join`,{},ninth.token);
  assert.equal(replacement.status,200);assert.equal(replacement.data.currentRoom.members.length,8);
  assert.equal(replacement.data.currentRoom.members.filter(m=>m.isBot).length,6);
});

test('empty seat locks, lobby character updates, team selection and owner transfer persist in snapshots',async t=>{
  const h=await harness(t),a=await h.session('旧房主'),b=await h.session('新房主');
  const character=await h.request('/api/action',{action:'character',character:'wukong'},a.token);
  assert.equal(character.status,200);assert.equal(character.data.session.character,'wukong');
  const created=await h.create(a);
  const locked=await h.request('/api/action',{action:'seat',seat:7,locked:true},a.token);
  assert.deepEqual(locked.data.currentRoom.lockedSeats,[7]);
  assert.equal((await h.request('/api/action',{action:'config',bots:7,name:'不应写入'},a.token)).status,409);
  assert.equal((await h.request('/api/state',undefined,a.token)).data.currentRoom.name,'集成测试房间');
  await h.request(`/api/rooms/${created.currentRoom.id}/join`,{},b.token);
  const team=await h.request('/api/action',{action:'team',team:'red'},b.token);assert.equal(team.status,200);
  assert.equal(team.data.currentRoom.members.find(m=>m.id===b.session.id).team,'red');
  await h.request('/api/action',{action:'leave'},a.token);
  const transferred=(await h.request('/api/state',undefined,b.token)).data;
  assert.equal(transferred.currentRoom.ownerId,b.session.id);
  assert.equal(transferred.currentRoom.members.find(m=>m.id===b.session.id).ready,true);
});

test('SSE sends actual shared state without token leakage and reconnect retains the current room',async t=>{
  const h=await harness(t),a=await h.session('实时玩家');const created=await h.create(a,{bots:1});
  const abort=new AbortController();
  const res=await fetch(`${h.base}/api/events?token=${a.token}`,{signal:abort.signal});
  assert.equal(res.status,200);assert.match(res.headers.get('content-type'),/^text\/event-stream/);
  const reader=res.body.getReader();let text='';
  while(!text.includes('\n\n'))text+=new TextDecoder().decode((await reader.read()).value);
  assert.match(text,/^event: data\ndata: /);const data=JSON.parse(text.split('data: ')[1].split('\n\n')[0]);
  assert.equal(data.currentRoom.id,created.currentRoom.id);assert.equal(data.session.id,a.session.id);
  assert.equal(JSON.stringify(data).includes(a.token),false);
  await reader.cancel();abort.abort();
  const reconnect=await h.request('/api/state',undefined,a.token);
  assert.equal(reconnect.status,200);assert.equal(reconnect.data.currentRoom.id,created.currentRoom.id);
  const chat=await h.request('/api/action',{action:'chat',text:'重连后消息'},a.token);
  assert.equal(chat.status,200);assert.equal(chat.data.currentRoom.chat.at(-1).text,'重连后消息');
});

test('invalid bodies and malformed roles are rejected with bounded JSON errors',async t=>{
  const h=await harness(t);
  assert.equal((await h.request('/api/session',{name:'',character:'maomao'})).status,400);
  assert.equal((await h.request('/api/session',{name:'名字',character:'unknown'})).status,400);
  const big=await h.request('/api/session',{name:'a'.repeat(9000)});assert.equal(big.status,413);
  const nonJSON=await fetch(h.base+'/api/session',{method:'POST',headers:{'content-type':'text/plain'},body:'name=foo'});
  assert.equal(nonJSON.status,415);
  const malformed=await fetch(h.base+'/api/session',{method:'POST',headers:{'content-type':'application/json'},body:'{oops'});
  assert.equal(malformed.status,400);assert.equal(typeof(await malformed.json()).error,'string');
});
