// Original audio presentation only. This module never changes authoritative game state.
export const AUDIO_EVENT_CUES = Object.freeze({
  start:'wave', 'bubble-placed':'bubble-place', 'sky-bubble':'bubble-place',
  'bubble-burst':'bubble-burst', 'fire-row':'bubble-burst', trapped:'trapped',
  rescued:'rescued', eliminated:'eliminated', respawn:'respawn', damage:'damage',
  'box-pushed':'wood-push', 'box-shot':'wood-push', 'box-broken':'wood-break',
  'bubble-kicked':'bubble-kick', 'bun-taken':'pickup', 'bun-dropped':'wood-push',
  'bun-returned':'pickup', 'bun-delivered':'bun-delivery', wave:'wave',
  'monster-defeated':'pickup',
});

export function audioCueForEvent(event) {
  if (!event || typeof event.type !== 'string') return null;
  if (event.type === 'pickup') return event.item === 'shield' ? 'shield'
    : event.item === 'needle' ? 'needle' : 'pickup';
  if (event.type === 'rescued' && event.playerId != null && event.by === event.playerId) return 'needle';
  // A local player's result is presented separately; never infer victory from an unknown winner.
  return Object.hasOwn(AUDIO_EVENT_CUES, event.type) ? AUDIO_EVENT_CUES[event.type] : null;
}

export function createAudioEventCursor() {
  let gameId = null, latestGameTime = -Infinity;
  const seen = new Set();
  const keyFor = event => JSON.stringify(Object.keys(event).sort().map(key => [key,event[key]]));
  return {
    consume(game) {
      if (!game?.id || !Array.isArray(game.events)) { gameId=null; latestGameTime=-Infinity; seen.clear(); return []; }
      if (game.id !== gameId) {
        gameId=game.id; latestGameTime=Number.isFinite(game.time)?game.time:-Infinity; seen.clear();
        // Joining/reconnecting must not replay the retained event history.
        for (const event of game.events) seen.add(keyFor(event));
        return [];
      }
      if(Number.isFinite(game.time) && game.time<latestGameTime)return [];
      if(Number.isFinite(game.time))latestGameTime=game.time;
      const cues = [];
      for (const event of game.events) {
        const key=keyFor(event);
        if (seen.has(key)) continue;
        seen.add(key);
        const cue=audioCueForEvent(event);
        if (cue && !cues.includes(cue)) cues.push(cue);
      }
      while(seen.size>128) seen.delete(seen.values().next().value);
      return cues.slice(0,6);
    },
    reset() { gameId=null; latestGameTime=-Infinity; seen.clear(); },
  };
}

function browserAudioContext() {
  const Constructor=globalThis.AudioContext || globalThis.webkitAudioContext;
  return Constructor ? new Constructor() : null;
}

export class GameAudio {
  constructor({fetcher=(...args)=>globalThis.fetch(...args),createContext=browserAudioContext,clock=()=>Date.now()}={}) {
    this.fetcher=fetcher; this.createContext=createContext; this.clock=clock;
    this.context=null; this.master=null; this.musicBus=null; this.sfxBus=null;
    this.prefs={sound:true,volume:.2}; this.scene='lobby'; this.paused=false; this.hidden=false;
    this.unlocked=false; this.manifestPromise=null; this.pieces=new Map(); this.buffers=new Map();
    this.voices=new Set(); this.music=null; this.musicRequest=0; this.cursor=createAudioEventCursor();
    this.sfxContext = 0;
  }
  async loadManifest() {
    this.manifestPromise ??= (async()=>{
      const response=await this.fetcher('./assets/audio/original-v1/manifest.json');
      if(!response.ok)throw Error('Audio manifest unavailable');
      const data=await response.json();
      if(data.schemaVersion!==1 || !Array.isArray(data.pieces))throw Error('Unsupported audio manifest');
      for(const piece of data.pieces){
        if(typeof piece.cue!=='string'||!/^assets\/audio\/original-v1\/[a-z0-9-]+\.wav$/.test(piece.file))continue;
        this.pieces.set(piece.cue,piece);
      }
      return data;
    })().catch(()=>null);
    return this.manifestPromise;
  }
  setPreferences(prefs) {
    this.prefs={sound:Boolean(prefs.sound),volume:Math.max(0,Math.min(1,Number(prefs.volume)||0))};
    if(this.master)this.master.gain.value=this.prefs.sound?this.prefs.volume:0;
    if(!this.prefs.sound || !this.prefs.volume)this.stopSfx();
    void this.syncMusic();
  }
  setScene(scene,{paused=false,hidden=false}={}) {
    const nextScene = scene === 'battle' ? 'battle' : 'lobby';
    if (this.scene !== nextScene || (hidden && !this.hidden)) this.stopSfx();
    this.scene=nextScene;this.paused=Boolean(paused);this.hidden=Boolean(hidden);
    void this.syncMusic();
  }
  async unlock() {
    try {
      this.context ??= this.createContext();
      if(!this.context)return false;
      if(!this.master){
        this.master=this.context.createGain();this.master.connect(this.context.destination);
        this.musicBus=this.context.createGain();this.musicBus.gain.value=.10;this.musicBus.connect(this.master);
        this.sfxBus=this.context.createGain();this.sfxBus.gain.value=.30;this.sfxBus.connect(this.master);
        this.master.gain.value=this.prefs.sound?this.prefs.volume:0;
      }
      await this.context.resume();
      this.unlocked=this.context.state==='running';
      if(this.unlocked){void this.loadManifest();void this.syncMusic();}
      return this.unlocked;
    }catch{return false;}
  }
  async bufferFor(cue) {
    await this.loadManifest();
    const piece=this.pieces.get(cue);
    if(!piece || !this.context)return null;
    if(!this.buffers.has(cue)){
      const promise=(async()=>{
        const response=await this.fetcher('./'+piece.file);
        if(!response.ok)return null;
        return await this.context.decodeAudioData(await response.arrayBuffer());
      })().catch(()=>null);
      this.buffers.set(cue,promise);
    }
    return this.buffers.get(cue);
  }
  async play(cue) {
    const requested=this.clock();
    const sfxContext = this.sfxContext;
    if(!this.unlocked || !this.prefs.sound || !this.prefs.volume || this.hidden)return false;
    const buffer=await this.bufferFor(cue);
    // A delayed asset must not make a stale event audible after mute/view changes.
    if(!buffer || !this.unlocked || !this.prefs.sound || !this.prefs.volume || this.hidden ||
       this.clock()-requested>500 || this.sfxContext !== sfxContext)return false;
    try{
      while(this.voices.size>=6){
        const oldest=this.voices.values().next().value;try{oldest.stop();}catch{}
        this.voices.delete(oldest);
      }
      const node=this.context.createBufferSource();node.buffer=buffer;node.connect(this.sfxBus);
      node.onended=()=>{this.voices.delete(node);node.disconnect();};
      this.voices.add(node);node.start();return true;
    }catch{return false;}
  }
  stopSfx(){
    this.sfxContext++;
    for (const voice of this.voices) {
      try { voice.stop(); voice.disconnect(); } catch {}
    }
    this.voices.clear();
  }
  stopMusic(){
    this.musicRequest++;
    if(this.music){try{this.music.node.stop();this.music.node.disconnect();}catch{}this.music=null;}
  }
  async syncMusic(){
    const wanted=this.unlocked&&this.prefs.sound&&this.prefs.volume&&!this.hidden&&!this.paused
      ?'music-'+this.scene:null;
    if(!wanted){this.stopMusic();return false;}
    if(this.music?.cue===wanted)return true;
    const token=++this.musicRequest;
    const buffer=await this.bufferFor(wanted);
    if(!buffer || token!==this.musicRequest || !this.prefs.sound || !this.prefs.volume ||
       this.hidden || this.paused)return false;
    try{
      if(this.music){try{this.music.node.stop();this.music.node.disconnect();}catch{}}
      const node=this.context.createBufferSource();node.buffer=buffer;node.loop=true;node.connect(this.musicBus);
      node.start();this.music={cue:wanted,node};return true;
    }catch{return false;}
  }
  consumeGame(game){
    for(const cue of this.cursor.consume(game))void this.play(cue);
  }
  resetEvents(){this.cursor.reset();}
}
