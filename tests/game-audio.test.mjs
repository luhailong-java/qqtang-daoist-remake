import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createAudioEventCursor,audioCueForEvent,GameAudio} from '../src/game-audio.js';

const manifest=JSON.parse(await readFile(new URL('../assets/audio/original-v1/manifest.json',import.meta.url)));
const hash=buffer=>createHash('sha256').update(buffer).digest('hex');

test('all original audio files are real unclipped PCM with their own source and digest',async()=>{
  assert.equal(manifest.pieces.length,21);
  assert.equal(manifest.pieces.filter(p=>p.kind==='music').length,2);
  for(const piece of manifest.pieces){
    const raw=await readFile(new URL('../'+piece.file,import.meta.url));
    assert.equal(hash(raw),piece.sha256);
    assert.equal(raw.toString('ascii',0,4),'RIFF');
    assert.equal(raw.toString('ascii',8,12),'WAVE');
    assert.equal(raw.readUInt16LE(20),1);
    assert.equal(raw.readUInt16LE(22),1);
    assert.equal(raw.readUInt32LE(24),44100);
    assert.equal(raw.readUInt16LE(34),16);
    assert.equal(raw.readUInt32LE(40),raw.length-44);
    let square=0,peak=0;
    for(let at=44;at<raw.length;at+=2){const value=raw.readInt16LE(at);peak=Math.max(peak,Math.abs(value));square+=value*value;}
    assert.ok(peak>2000&&peak<25000);
    assert.ok(Math.sqrt(square/((raw.length-44)/2))/32768>.002);
    const provenance=JSON.parse(await readFile(new URL('../'+piece.provenanceRecord,import.meta.url)));
    assert.equal(provenance.sha256,piece.sha256);
    assert.equal(provenance.originalComposition,true);
    assert.equal(provenance.externalSamples,false);
    assert.equal(provenance.auditoryAccepted,false);
    assert.equal(provenance.model,null);
    const source=await readFile(new URL('../'+provenance.source.file,import.meta.url));
    assert.equal(hash(source),provenance.source.sha256);
    if(piece.loop)assert.ok(Math.abs(raw.readInt16LE(44)-raw.readInt16LE(raw.length-2))/32768<.02);
  }
});

test('events use declared cue meanings; only actual self rescue selects the needle cue',()=>{
  assert.equal(audioCueForEvent({type:'pickup',item:'shield'}),'shield');
  assert.equal(audioCueForEvent({type:'rescued',playerId:'p1',by:'p1'}),'needle');
  assert.equal(audioCueForEvent({type:'rescued',playerId:'p1',by:'p2'}),'rescued');
  assert.equal(audioCueForEvent({type:'rescued'}),'rescued');
  assert.equal(audioCueForEvent({type:'finished',winnerTeam:'red'}),null);
  assert.equal(audioCueForEvent({type:'unknown-native-event'}),null);
});

test('cursor ignores join/reconnect history, duplicates and out-of-order snapshots without changing game data',()=>{
  const cursor=createAudioEventCursor();
  const initial=Object.freeze({id:'g1',time:10,events:Object.freeze([Object.freeze({type:'start',time:0})])});
  const before=JSON.stringify(initial);
  assert.deepEqual(cursor.consume(initial),[]);
  const pickup=Object.freeze({type:'pickup',time:20,playerId:'p1',item:'needle'});
  const next=Object.freeze({id:'g1',time:20,events:Object.freeze([...initial.events,pickup])});
  assert.deepEqual(cursor.consume(next),['needle']);
  assert.deepEqual(cursor.consume(next),[]);
  assert.deepEqual(cursor.consume({id:'g1',time:15,events:[{type:'damage',time:15}]}),[]);
  assert.equal(JSON.stringify(initial),before);
  cursor.reset();
  assert.deepEqual(cursor.consume(next),[]);
  assert.deepEqual(cursor.consume({id:'g2',time:30,events:[pickup]}),[]);
});

test('a snapshot burst coalesces identical cues and caps simultaneous event presentation',()=>{
  const cursor=createAudioEventCursor();cursor.consume({id:'g',time:0,events:[]});
  const events=Array.from({length:10},(_,i)=>({type:'bubble-burst',time:10,bombId:String(i)}));
  assert.deepEqual(cursor.consume({id:'g',time:10,events}),['bubble-burst']);
});

function mockContext(){
  const nodes=[];
  return {state:'suspended',nodes,destination:{},
    async resume(){this.state='running';},
    createGain(){return{gain:{value:1},connect(){},disconnect(){}};},
    async decodeAudioData(){return{duration:.2};},
    createBufferSource(){
      const node={started:false,stopped:false,loop:false,connect(){},disconnect(){},start(){this.started=true;},
        stop(){this.stopped=true;this.onended?.();}};
      nodes.push(node);return node;
    },
  };
}
const response=piece=>({ok:true,json:async()=>piece,arrayBuffer:async()=>new ArrayBuffer(8)});
const flush=()=>new Promise(resolve=>setImmediate(resolve));

test('audio waits for a gesture, uses separate buses, and mute stops music/voices',async()=>{
  const context=mockContext();
  const audio=new GameAudio({createContext:()=>context,fetcher:async url=>response(url.endsWith('manifest.json')?manifest:null)});
  assert.equal(await audio.play('pickup'),false);
  assert.equal(context.nodes.length,0);
  await audio.unlock();await flush();
  assert.equal(context.state,'running');
  assert.equal(audio.musicBus.gain.value,.10);
  assert.equal(audio.sfxBus.gain.value,.30);
  assert.equal(await audio.play('pickup'),true);
  audio.setPreferences({sound:false,volume:.2});
  assert.equal(await audio.play('pickup'),false);
  assert.equal(audio.music,null);
  assert.equal(audio.voices.size,0);
  assert.equal(audio.master.gain.value,0);
});

test('a slow decode cannot play a stale event and hidden/pause prevent background music',async()=>{
  let now=0;
  const context=mockContext();
  const audio=new GameAudio({clock:()=>now,createContext:()=>context,fetcher:async url=>{
    if(url.endsWith('manifest.json'))return response(manifest);
    if(url.endsWith('pickup.wav'))now=600;
    return response(null);
  }});
  await audio.unlock();await flush();
  assert.equal(await audio.play('pickup'),false);
  audio.setScene('battle',{hidden:true});await flush();
  assert.equal(audio.music,null);
  audio.setScene('battle',{paused:true});await flush();
  assert.equal(audio.music,null);
});

test('unavailable audio capability or failed manifest is silent and does not throw',async()=>{
  const unavailable=new GameAudio({createContext:()=>null});
  assert.equal(await unavailable.unlock(),false);
  assert.equal(await unavailable.play('pickup'),false);
  const failed=new GameAudio({createContext:()=>mockContext(),fetcher:async()=>{throw Error('offline');}});
  assert.equal(await failed.unlock(),true);
  assert.equal(await failed.play('pickup'),false);
});

test('original PCM data is served unchanged with an audio MIME by the actual local authority HTTP server',async()=>{
  const {createAppServer}=await import('../server/app.mjs');
  const server=createAppServer({port:0});
  const address=await server.start();
  try{
    const base='http://127.0.0.1:'+address.port;
    const piece=manifest.pieces[0];
    const res=await fetch(base+'/'+piece.file);
    assert.equal(res.status,200);
    assert.match(res.headers.get('content-type'),/^audio\/wav/);
    assert.equal(hash(Buffer.from(await res.arrayBuffer())),piece.sha256);
  }finally{await server.close();}
});
