import http from 'node:http';
import {readFile, stat, realpath} from 'node:fs/promises';
import path from 'node:path';
import {randomBytes, randomUUID} from 'node:crypto';
import * as engine from '../src/game.js';
import {loadMapCatalog} from './map-catalog.mjs';

const ROOT=path.resolve(import.meta.dirname,'..');
const MAX_BODY=8192, MAX_ROOMS=30, MAX_SESSIONS=100;
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
  '.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8',
  '.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml',
  '.webp':'image/webp','.woff2':'font/woff2','.md':'text/plain; charset=utf-8'};
class ApiError extends Error {
  constructor(status,message,code='BAD_REQUEST'){super(message);this.status=status;this.code=code;}
}
function requireValue(condition,status,message,code){if(!condition)throw new ApiError(status,message,code);}
const cleanText=(value,max)=>String(value??'').replace(/[\u0000-\u001f\u007f]/g,'').trim().slice(0,max);
const publicSession=s=>({id:s.id,name:s.name,character:s.character});
const publicMember=m=>({id:m.id,name:m.name,character:m.character,team:m.team,isBot:m.isBot,ready:m.ready,seat:m.seat});
const copyGame=g=>g?JSON.parse(JSON.stringify(g,(k,v)=>k.startsWith('_')?undefined:v)):null;

/** Original reconstruction transport; this is not Tencent's historic wire protocol. */
export function createAppServer({port=4387,host='127.0.0.1',tickMs=50}={}){
  const sessions=new Map(),rooms=new Map(),streams=new Map();
  let loop,heartbeat,cleanup,startedAt=null,closed=false,lastBroadcast=0,gameCache=new Map(),mapCatalog=null;
  const characters=()=>engine.CHARACTERS,modes=()=>engine.MODES;
  const validCharacter=id=>characters().some(c=>c.id===id),validMode=id=>modes().some(m=>m.id===id);
  const roomStatus=r=>r.game?r.game.status:'waiting';
  const roomList=()=>[...rooms.values()].map(r=>({id:r.id,name:r.name,mode:r.mode,map:r.map,
    count:r.members.length,max:r.maxSeats,mapInfo:mapCatalog.get(r.map),status:roomStatus(r),channel:r.channel,
    botCount:r.members.filter(m=>m.isBot).length,ownerId:r.ownerId,template:r.template}));
  function snapshot(session){
    const r=rooms.get(session.roomId);let currentRoom=null;
    if(r){
      if(!gameCache.has(r.id))gameCache.set(r.id,copyGame(r.game));
      currentRoom={id:r.id,name:r.name,mode:r.mode,map:r.map,mapInfo:mapCatalog.get(r.map),max:r.maxSeats,maxSeats:r.maxSeats,duration:r.duration,channel:r.channel,
        ownerId:r.ownerId,members:r.members.map(publicMember),lockedSeats:[...r.lockedSeats],
        chat:r.chat.map(m=>({...m})),game:gameCache.get(r.id),paused:r.paused};
    }
    return {session:publicSession(session),rooms:roomList(),currentRoom,characters:characters(),modes:modes(),
      mapDirectory:{url:'/api/maps',sourceMapCount:mapCatalog.maps.length,candidatePlayableCount:mapCatalog.maps.filter(m=>m.playable).length,defaultMap:'source-201'},
      server:{name:'QQ堂重制本地服务',version:'0.2.0',transport:'HTTP + SSE',authoritative:true,startedAt,
        note:'独立重制开发服务，不连接腾讯原运营服务器'}};
  }
  function event(res,data){if(!res.destroyed&&!res.writableEnded)res.write(`event: data\ndata: ${JSON.stringify(data)}\n\n`);}
  function broadcast(){
    gameCache.clear();
    for(const [token,clients] of streams){const session=sessions.get(token);if(!session||!clients.size)continue;
      const data=snapshot(session);session.lastSeen=Date.now();for(const res of clients)event(res,data);}
    lastBroadcast=Date.now();
  }
  function json(res,status,data){const bytes=Buffer.from(JSON.stringify(data));
    res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',
      'Content-Length':bytes.length,'X-Content-Type-Options':'nosniff'});res.end(bytes);}
  function authenticate(req,url){
    const token=/^Bearer\s+(.+)$/i.exec(req.headers.authorization||'')?.[1]||url.searchParams.get('token');
    const session=token&&sessions.get(token);
    requireValue(session,401,'本地身份已失效，请重新进入。','UNAUTHORIZED');
    session.lastSeen=Date.now();session.disconnectedAt=null;return session;
  }
  function roomOf(session){const room=rooms.get(session.roomId);requireValue(room,409,'请先进入一个房间。','NO_ROOM');return room;}
  function owner(room,session){requireValue(room.ownerId===session.id,403,'只有房主可以执行此操作。','OWNER_REQUIRED');}
  function waiting(room){requireValue(!room.game,409,'请先结束对局并返回房间。','ROOM_BUSY');}
  function chooseMap(id,mode){
    const selected=mapCatalog.get(id);requireValue(selected,400,'地图标识不在实际目录中。','UNKNOWN_MAP');
    requireValue(selected.playable,409,selected.unavailableReason||'此图尚不能启动。',selected.unavailableCode||'MAP_UNAVAILABLE');
    requireValue(selected.playableModes.includes(mode),409,'此源地图尚未核验支持所选模式，不能编造目标或关卡。','SOURCE_RULE_UNSUPPORTED');
    return selected;
  }
  function setBots(room,count){
    requireValue(Number.isInteger(count)&&count>=0&&count<room.maxSeats,400,`此图AI数量应为0至${room.maxSeats-1}。`,'MAP_SEAT_LIMIT');
    const humans=room.members.filter(m=>!m.isBot),old=room.members.filter(m=>m.isBot);
    requireValue(humans.length<=room.maxSeats&&humans.every(m=>m.seat<room.maxSeats),409,'当前玩家席位超出目标地图人数上限，请先腾出高位席。','MAP_SEAT_LIMIT');
    const seats=Array.from({length:room.maxSeats},(_,i)=>i).filter(s=>!room.lockedSeats.includes(s)&&!humans.some(m=>m.seat===s));
    requireValue(count<=seats.length,409,'可用席位不足，请先开放空席。','ROOM_FULL');
    room.members=[...humans,...seats.slice(0,count).map((seat,index)=>{
      const previous=old.find(m=>m.seat===seat),character=characters()[(seat+index)%characters().length];
      return previous||{id:`ai-${room.id}-${seat}`,name:`${character.name} · AI`,character:character.id,
        team:seat%2?'blue':'red',isBot:true,ready:true,seat};
    })].sort((a,b)=>a.seat-b.seat);
  }
  function makeRoom({name,mode='classic',map='source-201',bots=3,duration=180,channel='free',template=false},session=null){
    requireValue(rooms.size<MAX_ROOMS,429,'本地房间数量已达上限。','ROOM_LIMIT');
    requireValue(validMode(mode),400,'未知游戏模式。');
    const selectedMap=chooseMap(map,mode);
    requireValue(Number.isInteger(duration)&&[60,120,180,300].includes(duration),400,'时长应为60、120、180或300秒。');
    const roomName=cleanText(name,24);requireValue(roomName.length,400,'房间名称不能为空。');
    const room={id:randomUUID().slice(0,8),name:roomName,mode,map,maxSeats:selectedMap.maxSeats,duration,channel:cleanText(channel,20)||'free',
      ownerId:session?.id||null,members:[],lockedSeats:[],chat:[],game:null,paused:false,template,lastActivity:Date.now()};
    if(session)room.members.push({id:session.id,name:session.name,character:session.character,
      team:'red',isBot:false,ready:true,seat:0});else room.lockedSeats=[0];
    setBots(room,bots);if(!session)room.lockedSeats=[];
    rooms.set(room.id,room);if(session)session.roomId=room.id;return room;
  }
  function chat(room,name,text){room.chat.push({id:randomUUID().slice(0,8),name,text,at:new Date().toISOString()});room.chat=room.chat.slice(-50);}
  function leave(session,reason='离开了房间'){
    const room=rooms.get(session.roomId);session.roomId=null;if(!room)return;
    room.members=room.members.filter(m=>m.id!==session.id);
    const player=room.game?.players.find(p=>p.id===session.id);
    if(player){player.alive=false;player.trappedUntil=null;player.respawnAt=null;}
    chat(room,'系统',`${session.name}${reason}`);
    const humans=room.members.filter(m=>!m.isBot);
    if(!humans.length){
      if(room.template){room.ownerId=null;room.game=null;room.paused=false;room.chat=[];room.lockedSeats=[];setBots(room,3);}
      else rooms.delete(room.id);
    }else if(room.ownerId===session.id){room.ownerId=humans[0].id;humans[0].ready=true;room.paused=false;chat(room,'系统',`${humans[0].name}成为房主`);}
    gameCache.clear();
  }
  function join(room,session){
    waiting(room);if(session.roomId===room.id)return;
    requireValue(!session.roomId,409,'请先离开当前房间。','ALREADY_IN_ROOM');
    let seat=Array.from({length:room.maxSeats},(_,i)=>i).find(i=>!room.lockedSeats.includes(i)&&!room.members.some(m=>m.seat===i));
    if(seat===undefined){const bot=[...room.members].reverse().find(m=>m.isBot&&!room.lockedSeats.includes(m.seat));
      requireValue(bot,409,'房间已满。','ROOM_FULL');seat=bot.seat;room.members=room.members.filter(m=>m.id!==bot.id);}
    if(!room.ownerId)room.ownerId=session.id;
    room.members.push({id:session.id,name:session.name,character:session.character,team:room.mode==='adventure'?'red':seat%2?'blue':'red',
      isBot:false,ready:room.ownerId===session.id,seat});room.members.sort((a,b)=>a.seat-b.seat);
    session.roomId=room.id;room.lastActivity=Date.now();chat(room,'系统',`${session.name}进入房间`);
  }
  function action(session,body){
    if(body.action==='character'&&!session.roomId){requireValue(validCharacter(body.character),400,'未知角色。');session.character=body.character;return;}
    const room=roomOf(session),member=room.members.find(m=>m.id===session.id);
    requireValue(member,409,'当前身份不在此房间。');room.lastActivity=Date.now();
    switch(body.action){
      case 'leave':leave(session);break;
      case 'ready':waiting(room);member.ready=room.ownerId===session.id?true:Boolean(body.ready);break;
      case 'character':waiting(room);requireValue(validCharacter(body.character),400,'未知角色。');member.character=body.character;session.character=body.character;break;
      case 'team':waiting(room);requireValue(['red','blue'].includes(body.team),400,'未知队伍。');
        requireValue(room.mode!=='adventure'||body.team==='red',400,'合作探险的玩家在同一队。');member.team=body.team;break;
      case 'config':{
        owner(room,session);waiting(room);const patch=body.config&&typeof body.config==='object'?body.config:body;
        const name=patch.name===undefined?room.name:cleanText(patch.name,24),mode=patch.mode??room.mode,
          map=patch.map??room.map,duration=patch.duration??room.duration,bots=patch.bots??room.members.filter(m=>m.isBot).length;
        requireValue(name.length,400,'房间名称不能为空。');requireValue(validMode(mode),400,'未知游戏模式。');
        const selectedMap=chooseMap(map,mode);
        requireValue(Number.isInteger(duration)&&[60,120,180,300].includes(duration),400,'时长应为60、120、180或300秒。');
        const candidate={...room,maxSeats:selectedMap.maxSeats,lockedSeats:room.lockedSeats.filter(seat=>seat<selectedMap.maxSeats)};
        setBots(candidate,bots);Object.assign(room,{name,mode,map,duration,maxSeats:candidate.maxSeats,members:candidate.members,lockedSeats:candidate.lockedSeats});
        for(const m of room.members){if(mode==='adventure')m.team='red';if(!m.isBot&&m.id!==room.ownerId)m.ready=false;}break;
      }
      case 'seat':{
        owner(room,session);waiting(room);const seat=body.seat;
        requireValue(Number.isInteger(seat)&&seat>=0&&seat<room.maxSeats,400,`此图席位编号应为0至${room.maxSeats-1}。`,'MAP_SEAT_LIMIT');
        requireValue(!room.members.some(m=>m.seat===seat),409,'只能开关空闲席位。');
        room.lockedSeats=room.lockedSeats.filter(n=>n!==seat);if(body.locked)room.lockedSeats.push(seat);room.lockedSeats.sort((a,b)=>a-b);break;
      }
      case 'start':{
        owner(room,session);waiting(room);requireValue(room.members.length>=2,409,'至少需要两位玩家或AI。','TOO_FEW_PLAYERS');
        requireValue(room.members.every(m=>m.isBot||m.id===room.ownerId||m.ready),409,'请等待所有玩家准备。','NOT_READY');
        if(room.mode==='adventure')for(const m of room.members)m.team='red';
        else if(new Set(room.members.map(m=>m.team)).size<2){const bot=room.members.find(m=>m.isBot);
          requireValue(bot,409,'竞技至少需要红蓝两队。','NEED_TWO_TEAMS');bot.team=room.members[0].team==='red'?'blue':'red';}
        chooseMap(room.map,room.mode);
        room.game=engine.createGame({mode:room.mode,map:room.map,sourceMap:mapCatalog.getRuntime(room.map),duration:room.duration,seed:randomBytes(4).readUInt32BE(),participants:room.members.map(publicMember)});
        room.game.id??=randomUUID();room.paused=false;chat(room,'系统','对局开始');break;
      }
      case 'return':requireValue(room.game?.status==='finished',409,'当前对局尚未结束。');room.game=null;room.paused=false;
        for(const m of room.members)m.ready=m.isBot||m.id===room.ownerId;break;
      case 'pause':owner(room,session);requireValue(room.game?.status==='playing',409,'当前没有进行中的对局。');room.paused=Boolean(body.paused);break;
      case 'chat':{
        const text=cleanText(body.text,200);requireValue(text.length,400,'消息不能为空。');
        requireValue(Date.now()-(session.lastChatAt||0)>=400,429,'消息发送太快，请稍候。','RATE_LIMIT');
        session.lastChatAt=Date.now();chat(room,session.name,text);break;
      }
      default:throw new ApiError(400,'未知房间操作。');
    }
  }
  function input(session,body){
    const room=roomOf(session);requireValue(room.game?.status==='playing',409,'当前没有进行中的对局。');
    requireValue(!room.paused,409,'对局已暂停。','PAUSED');
    requireValue(room.members.some(m=>m.id===session.id),403,'没有对局操作权限。');
    const now=Date.now();session.inputTimes=(session.inputTimes||[]).filter(t=>now-t<1000);
    requireValue(session.inputTimes.length<60,429,'操作过于频繁。','RATE_LIMIT');session.inputTimes.push(now);
    if(body.type==='move'){requireValue(Number.isInteger(body.dx)&&Number.isInteger(body.dy)&&Math.abs(body.dx)+Math.abs(body.dy)===1,400,'移动方向不正确。');
      return Boolean(engine.movePlayer(room.game,session.id,body.dx,body.dy));}
    if(body.type==='bomb')return Boolean(engine.placeBomb(room.game,session.id));
    if(body.type==='item')return Boolean(engine.useItem(room.game,session.id));
    throw new ApiError(400,'未知对战输入。');
  }
  async function bodyJSON(req){
    requireValue((req.headers['content-type']||'').toLowerCase().startsWith('application/json'),415,'请使用JSON请求。');
    const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;requireValue(size<=MAX_BODY,413,'请求内容过大。','BODY_TOO_LARGE');chunks.push(chunk);}
    let body;try{body=JSON.parse(Buffer.concat(chunks).toString('utf8')||'{}');}catch{throw new ApiError(400,'JSON格式不正确。');}
    requireValue(body&&typeof body==='object'&&!Array.isArray(body),400,'请求应为JSON对象。');return body;
  }
  async function staticFile(req,res,url){
    let rel;try{rel=decodeURIComponent(url.pathname);}catch{throw new ApiError(400,'路径编码不正确。');}
    requireValue(!rel.split('/').some(p=>p.startsWith('.')&&p!==''),403,'不可读取此路径。');
    let file=path.resolve(ROOT,'.'+rel);requireValue(file===ROOT||file.startsWith(ROOT+path.sep),403,'不可读取此路径。');
    requireValue(!['server','tests','scripts'].includes(path.relative(ROOT,file).split(path.sep)[0].toLowerCase()),403,'此目录不是网页资源。');
    if((await stat(file)).isDirectory())file=path.join(file,'index.html');const resolved=await realpath(file);
    requireValue(resolved.toLowerCase().startsWith((ROOT+path.sep).toLowerCase()),403,'不可读取外部资源。');
    const bytes=await readFile(resolved);res.writeHead(200,{'Content-Type':MIME[path.extname(file).toLowerCase()]||'application/octet-stream',
      'Content-Length':bytes.length,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});res.end(req.method==='HEAD'?undefined:bytes);
  }
  const server=http.createServer(async(req,res)=>{
    try{
      const url=new URL(req.url,'http://localhost');
      if(url.pathname==='/favicon.ico'){res.writeHead(204);res.end();return;}
      if(!url.pathname.startsWith('/api/')){requireValue(['GET','HEAD'].includes(req.method),405,'请求方式不支持。');await staticFile(req,res,url);return;}
      if(['127.0.0.1','localhost','::1'].includes(host)){
        let requestHost;try{requestHost=new URL(`http://${req.headers.host}`).hostname;}catch{}
        requireValue(['127.0.0.1','localhost','[::1]'].includes(requestHost),403,'仅允许本机开发地址。','ORIGIN_REJECTED');
      }
      if(req.method==='POST'&&req.headers.origin){let origin;try{origin=new URL(req.headers.origin);}catch{}
        requireValue(origin&&origin.host===req.headers.host&&['http:','https:'].includes(origin.protocol),403,'请求来源不匹配。','ORIGIN_REJECTED');}
      if(req.method==='GET'&&url.pathname==='/api/health'){json(res,200,{ok:true,name:'QQ堂重制本地服务',version:'0.2.0',authoritative:true});return;}
      if(req.method==='GET'&&url.pathname==='/api/maps'){json(res,200,{ok:true,...mapCatalog.publicDirectory()});return;}
      if(req.method==='GET'&&/^\/api\/maps\/[^/]+$/.test(url.pathname)){
        const id=url.pathname.split('/')[3],descriptor=mapCatalog.get(id);requireValue(descriptor,404,'地图目录中不存在此标识。','UNKNOWN_MAP');
        json(res,200,{ok:true,map:descriptor,sourceMap:mapCatalog.getRuntime(id)});return;
      }
      if(req.method==='POST'&&url.pathname==='/api/session'){
        const body=await bodyJSON(req);requireValue(sessions.size<MAX_SESSIONS,429,'本地身份数量已达上限。','SESSION_LIMIT');
        const name=cleanText(body.name,12);requireValue(name.length,400,'昵称不能为空。');
        const character=body.character||characters()[0].id;requireValue(validCharacter(character),400,'未知角色。');
        const token=randomBytes(24).toString('hex'),session={token,id:randomUUID(),name,character,roomId:null,lastSeen:Date.now(),disconnectedAt:null};
        sessions.set(token,session);json(res,201,{token,session:publicSession(session)});return;
      }
      const session=authenticate(req,url);
      if(req.method==='GET'&&url.pathname==='/api/state'){gameCache.clear();json(res,200,snapshot(session));return;}
      if(req.method==='GET'&&url.pathname==='/api/events'){
        res.writeHead(200,{'Content-Type':'text/event-stream; charset=utf-8','Cache-Control':'no-cache, no-transform',Connection:'keep-alive','X-Accel-Buffering':'no'});res.flushHeaders();
        let clients=streams.get(session.token);if(!clients){clients=new Set();streams.set(session.token,clients);}clients.add(res);session.disconnectedAt=null;
        gameCache.clear();event(res,snapshot(session));res.on('close',()=>{clients.delete(res);if(!clients.size){streams.delete(session.token);session.disconnectedAt=Date.now();}});return;
      }
      requireValue(req.method==='POST',405,'请求方式不支持。');const body=await bodyJSON(req);let accepted;
      if(url.pathname==='/api/rooms'){requireValue(!session.roomId,409,'请先离开当前房间。','ALREADY_IN_ROOM');makeRoom(body,session);}
      else if(/^\/api\/rooms\/[^/]+\/join$/.test(url.pathname)){const room=rooms.get(url.pathname.split('/')[3]);requireValue(room,404,'房间不存在。','ROOM_NOT_FOUND');join(room,session);}
      else if(url.pathname==='/api/action')action(session,body);
      else if(url.pathname==='/api/input')accepted=input(session,body);
      else throw new ApiError(404,'接口不存在。','NOT_FOUND');
      gameCache.clear();json(res,200,{ok:true,...(accepted===undefined?{}:{accepted}),...snapshot(session)});broadcast();
    }catch(error){
      if(res.headersSent){res.end();return;}
      const status=error instanceof ApiError?error.status:error.code==='ENOENT'?404:500;
      if(status===500)console.error('QQ堂本地服务错误:',error);
      json(res,status,{ok:false,error:status===500?'本地服务发生错误。':error.message,code:error.code||'INTERNAL_ERROR'});
    }
  });
  server.keepAliveTimeout=5000;server.headersTimeout=10_000;
  async function start(){
    requireValue(!closed,500,'服务已经关闭。');
    for(const name of ['createGame','movePlayer','placeBomb','useItem','tick'])requireValue(typeof engine[name]==='function',500,`游戏引擎缺少${name}接口。`);
    requireValue(Array.isArray(characters())&&characters().length&&Array.isArray(modes())&&modes().length,500,'游戏引擎目录尚未就绪。');
    if(server.listening)return server.address();
    mapCatalog??=await loadMapCatalog();
    if(!rooms.size)for(const template of [{name:'中国城01 · 源数据候选',mode:'classic',map:'source-201'},
      {name:'抢包山 · 自定义技术试稿',mode:'bun',map:'town'},{name:'合作探险 · 自定义技术试稿',mode:'adventure',map:'factory'}]){
      if(validMode(template.mode))makeRoom({...template,template:true,bots:3,duration:180});}
    await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,host,()=>{server.off('error',reject);resolve();});});startedAt=new Date().toISOString();
    loop=setInterval(()=>{for(const room of rooms.values())if(room.game?.status==='playing'&&!room.paused)engine.tick(room.game,Math.min(100,Math.max(10,tickMs)));
      if(Date.now()-lastBroadcast>=100)broadcast();},Math.min(100,Math.max(10,tickMs)));
    heartbeat=setInterval(()=>{for(const clients of streams.values())for(const res of clients)if(!res.destroyed)res.write(': heartbeat\n\n');},15_000);
    cleanup=setInterval(()=>{const now=Date.now();let changed=false;for(const [token,session] of sessions){
      if(session.roomId&&session.disconnectedAt&&now-session.disconnectedAt>30_000){leave(session,'断开连接');changed=true;}
      if(now-session.lastSeen>30*60_000&&!streams.has(token)){leave(session,'已离线');sessions.delete(token);changed=true;}}
      if(changed)broadcast();},1000);
    return server.address();
  }
  async function close(){
    if(closed)return;closed=true;clearInterval(loop);clearInterval(heartbeat);clearInterval(cleanup);
    for(const clients of streams.values())for(const res of clients)res.end();streams.clear();
    if(server.listening)await new Promise((resolve,reject)=>{server.close(e=>e?reject(e):resolve());server.closeIdleConnections?.();});
  }
  return {server,start,close};
}
