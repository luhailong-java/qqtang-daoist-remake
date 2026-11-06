import test from 'node:test';
import assert from 'node:assert/strict';
import {resultPresentation} from '../src/result-art.js';

test('both teams receive their own authoritative victory/defeat artwork',()=>{
  for(const winner of ['red','blue']){
    assert.equal(resultPresentation(winner,winner).id,'victory');
    assert.equal(resultPresentation(winner,winner==='red'?'blue':'red').id,'defeat');
  }
});
test('a draw uses the balanced crest for both teams',()=>{
  assert.equal(resultPresentation('draw','red'),resultPresentation('draw','blue'));
  assert.equal(resultPresentation('draw','red').label,'平局');
});
test('pending results and absent participants cannot be displayed or recorded as defeats',()=>{
  for(const winner of [null,undefined,'','pending','<img src=x>'])assert.equal(resultPresentation(winner,'red'),null);
  assert.equal(resultPresentation('red',null),null);
  assert.equal(resultPresentation('draw','spectator'),null);
});
test('outcome presentation is immutable and asset paths are fixed local PNGs',()=>{
  const states=[resultPresentation('red','red'),resultPresentation('draw','red'),resultPresentation('blue','red')];
  assert.equal(new Set(states.map(state=>state.file)).size,3);
  for(const state of states){assert.ok(Object.isFrozen(state));assert.match(state.file,/^assets\/ui\/results\/(victory|draw|defeat)\.png$/);}
});
