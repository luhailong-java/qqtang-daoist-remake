"""Original deterministic plucked/wind/bell compositions and event sounds; no sampled audio."""
from pathlib import Path
import datetime,hashlib,json,wave
import numpy as np
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
SR=44100
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_bytes((json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode())
def hz(midi):return 440*2**((midi-69)/12)
def voice(midi,duration,kind='pluck',seed=0):
 n=max(1,round(duration*SR));t=np.arange(n)/SR;f=hz(midi);rng=np.random.default_rng(seed);out=np.zeros(n)
 if kind=='wind':
  for k,amp in enumerate([1,.20,.18,.07,.055],1):out+=amp*np.sin(2*np.pi*f*k*t+.004*np.sin(2*np.pi*5*t))
  noise=rng.normal(0,1,n);out+=.10*np.convolve(noise,np.ones(12)/12,mode='same')
  env=(1-np.exp(-t/.035))*np.minimum(1,(duration-t)/.09)
 elif kind=='bell':
  for k,amp in [(1,1),(2.01,.28),(3.98,.13),(5.43,.045)]:
   out+=amp*np.sin(2*np.pi*f*k*t)*np.exp(-t*(2.5+.5*k))
  env=(1-np.exp(-t/.002))*np.minimum(1,(duration-t)/.025)
 else:
  for k in range(1,9):
   if f*k>=SR/2:continue
   out+=np.sin(2*np.pi*f*k*t+.035*k)*np.exp(-t*(3+.8*k))/(k**1.25)
  env=(1-np.exp(-t/.0015))*np.minimum(1,(duration-t)/.025)
 return out*env
def add(dst,signal,start,level=1,wrap=False):
 pos=round(start*SR);signal=signal*level
 if wrap:
  indices=(np.arange(len(signal))+pos)%len(dst);np.add.at(dst,indices,signal)
 else:
  left=max(0,pos);right=min(len(dst),pos+len(signal))
  if right>left:dst[left:right]+=signal[left-pos:right-pos]
def music(bpm,seed):
 beat=60/bpm;out=np.zeros(round(32*beat*SR));rng=np.random.default_rng(seed)
 # Original 8-bar D pentatonic melody; both instruments are synthesized from math, never samples.
 phrases=[[74,78,81,78,76,74,69,71],[74,76,78,81,83,81,78,76],
          [71,74,78,76,74,71,69,66],[69,71,74,78,76,74,71,69],
          [74,78,81,83,86,83,81,78],[76,78,81,78,76,74,71,69],
          [71,74,76,78,81,78,76,71],[69,71,74,78,76,74,69,74]]
 roots=[50,55,47,57,50,55,47,50]
 for bar,notes in enumerate(phrases):
  for step,note in enumerate(notes):
   start=(bar*4+step*.5)*beat
   add(out,voice(note,beat*.85,'pluck',seed+bar*8+step),start,.19 if bpm==96 else .23,True)
   if step in [0,3,6]:
    add(out,voice(note+12,beat*.70,'wind',seed+100+bar*8+step),start+.03,.045,True)
  for pulse,interval in [(0,0),(1,7),(2,12),(3,7)]:
   add(out,voice(roots[bar]+interval,beat*1.5,'pluck',seed+300+bar*4+pulse),(bar*4+pulse)*beat,.17,True)
  add(out,voice(roots[bar]+24,beat*3.6,'wind',seed+500+bar),bar*4*beat,.025,True)
  if bar%2==0:add(out,voice(86,beat*2.8,'bell',seed+600+bar),bar*4*beat,.025,True)
  # Quiet rounded wood pulse, never an explosive sound.
  for pulse in range(4):
   t=np.arange(round(.07*SR))/SR
   wood=(np.sin(2*np.pi*170*t)*np.exp(-t*65)+rng.normal(0,.12,len(t))*np.exp(-t*100))*.045
   add(out,wood,(bar*4+pulse)*beat,1,True)
 return out,{'tempoBPM':bpm,'beats':32,'scale':'D major pentatonic','composition':'original 8-bar melody, paired plucked patterns, synthesized wind, jade-bell and quiet wood pulse','seed':seed}
def sfx(name,seed):
 durations={'ui-click':.12,'bubble-place':.25,'bubble-burst':.50,'pickup':.42,'trapped':.55,'rescued':.80,
 'eliminated':.62,'respawn':.80,'damage':.18,'wood-push':.25,'wood-break':.32,'bubble-kick':.22,
 'bun-delivery':.9,'wave':.8,'victory':1.8,'draw':1.2,'defeat':1.5,'shield':.65,'needle':.3}
 duration=durations[name];out=np.zeros(round(duration*SR));t=np.arange(len(out))/SR;rng=np.random.default_rng(seed)
 phrases={'ui-click':[86],'pickup':[78,81,86],'rescued':[74,78,81,86],'respawn':[69,74,78,81],
 'eliminated':[74,71,66],'bun-delivery':[74,78,81,86],'wave':[62,69,74],
 'victory':[74,78,81,83,86,81,86],'draw':[74,78,81,78],'defeat':[78,76,74,71,69],
 'shield':[74,81,86],'needle':[93,86]}
 if name in phrases:
  notes=phrases[name];spacing=duration/(len(notes)+1.6)
  for index,note in enumerate(notes):
   add(out,voice(note,duration-index*spacing,'bell'if name in ['ui-click','pickup','shield','needle']else'pluck',seed+index),index*spacing,.5)
 elif name in ['bubble-place','trapped','bubble-kick']:
  f0,f1=(480,160)if name=='bubble-place'else((650,210)if name=='trapped'else(230,100))
  phase=2*np.pi*(f0*t+(f1-f0)*t*t/(2*duration))
  out=(np.sin(phase)+.18*np.sin(2*phase))*np.exp(-t*8)
 elif name=='bubble-burst':
  noise=rng.normal(0,1,len(out));soft=np.convolve(noise,np.ones(24)/24,mode='same')
  out=.70*soft*np.exp(-t*9)+.22*np.sin(2*np.pi*(110*t-35*t*t))*np.exp(-t*12)
 elif name in ['wood-push','wood-break','damage']:
  noise=np.convolve(rng.normal(0,1,len(out)),np.ones(10)/10,mode='same')
  out=.25*noise*np.exp(-t*(25 if name!='wood-push'else 10))+.3*np.sin(2*np.pi*155*t)*np.exp(-t*25)
  if name=='wood-break':add(out,voice(57,.2,'pluck',seed),.06,.12)
 ramp=min(round(.008*SR),len(out)//2);out[:ramp]*=np.linspace(0,1,ramp);out[-ramp:]*=np.linspace(1,0,ramp)
 return out,{'originalSoundDesign':name,'seed':seed,'durationTargetSeconds':duration}
def publish(cue,kind,signal,design):
 signal=signal-signal.mean();peak=float(np.max(np.abs(signal)));signal*= (.58 if kind=='music'else .62)/max(peak,1e-9)
 if kind!='music':signal[0]=signal[-1]=0
 pcm=np.rint(signal*32767).astype('<i2');target=BASE/(cue+'.wav')
 with wave.open(str(target),'wb')as out:out.setnchannels(1);out.setsampwidth(2);out.setframerate(SR);out.writeframes(pcm.tobytes())
 stats={'durationSeconds':len(pcm)/SR,'sampleRate':SR,'channels':1,'bitsPerSample':16,'frames':len(pcm),
 'peak':float(np.max(np.abs(pcm.astype(np.int32))))/32768,'rms':float(np.sqrt(np.mean((pcm.astype(float)/32768)**2))),
 'clippedSamples':int(np.sum(np.abs(pcm.astype(np.int32))>=32767)),'loopBoundaryDelta':float(abs(int(pcm[0])-int(pcm[-1])))/32768}
 assert stats['clippedSamples']==0 and stats['rms']>0.002
 record={'cue':cue,'kind':kind,'file':rel(target),'sha256':sha(target),'format':'PCM WAV','loop':kind=='music','design':design,'qa':stats,
 'art_source':'original_code_audio','route':'deterministic-local-synthesis','originalComposition':True,'externalSamples':False,
 'model':None,'generatedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source':{'file':rel(Path(__file__)),'sha256':sha(Path(__file__))},'sourceGameTiming':'none; cue is presented on existing event, not a timing authority',
 'auditoryAccepted':False,'runtimeApproved':False,'userReviewStatus':'pending'}
 sidecar=Path(str(target)+'.provenance.json');save(sidecar,record)
 return {k:record[k]for k in ['cue','kind','file','sha256','format','loop','qa','art_source','auditoryAccepted','runtimeApproved','userReviewStatus']}|{'provenanceRecord':rel(sidecar)}
pieces=[]
for cue,bpm,seed in [('music-lobby',96,20261112),('music-battle',120,20261113)]:
 signal,design=music(bpm,seed);pieces.append(publish(cue,'music',signal,design))
names=['ui-click','bubble-place','bubble-burst','pickup','trapped','rescued','eliminated','respawn','damage','wood-push','wood-break','bubble-kick','bun-delivery','wave','victory','draw','defeat','shield','needle']
for index,name in enumerate(names):
 signal,design=sfx(name,1000+index);pieces.append(publish(name,'sfx',signal,design))
save(BASE/'manifest.json',{'schemaVersion':1,'scope':'original sounds for currently implemented UI and event cues; not full native QQTang audio coverage',
 'pieces':pieces,'auditoryAccepted':False,'runtimeApproved':False,'userReviewStatus':'pending',
 'nativeAudioMapping':None,'musicGain':.10,'sfxGain':.30})
print(json.dumps({'pieces':len(pieces),'music':2,'sfx':len(names),'totalBytes':sum((ROOT/p['file']).stat().st_size for p in pieces),'clipSamples':sum(p['qa']['clippedSamples']for p in pieces)}))
