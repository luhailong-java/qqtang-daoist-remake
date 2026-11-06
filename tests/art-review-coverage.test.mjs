import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {headWorldSequences,sequenceFrameLabel} from '../src/art-review-data.js';
const read=name=>JSON.parse(fs.readFileSync(new URL(`../assets/items/head-adornments/${name}`,import.meta.url),'utf8'));

test('partial basket review shows22 available positions and24 declared, preserving raw source order',()=>{
  const full=read('world-39-art.json').items[0];
  const item={...full,frames:full.frames.slice(0,22)},clip=headWorldSequences({items:[item]})[0];
  assert.equal(clip.frameCount,22);assert.equal(clip.sourceDeclaredFrameCount,24);
  assert.equal(sequenceFrameLabel(clip),'22 / 源24帧');
  assert.deepEqual(clip.frames.map(frame=>frame.frameIndex),item.frames.map(frame=>frame.sourceFrameIndex));
});
test('completed basket frame coverage displays all 24 source positions',()=>{
  const item=read('world-39-art.json').items[0],clip=headWorldSequences({items:[item]})[0];
  assert.equal(sequenceFrameLabel(clip),'24 帧');
  assert.deepEqual(clip.frames.map(frame=>frame.frameIndex),Array.from({length:24},(_,index)=>index));
  assert.deepEqual(clip.frames.slice(22).map(frame=>frame.sourceFrame.frameOffset),[[29,-6],[31,7]]);
});
test('fully represented garland remains24 of24 with native logical geometry',()=>{
  const item=read('world-114-art.json').items[0],clip=headWorldSequences({items:[item]})[0];
  assert.equal(clip.frameCount,24);assert.equal(sequenceFrameLabel(clip),'24 帧');
  for(let i=0;i<item.frames.length;i++){
    assert.equal(clip.frames[i].sourceFrame.width,item.frames[i].logicalFrameSize[0]);
    assert.deepEqual(clip.frames[i].sourceFrame.frameOffset,item.frames[i].frameOffsetRaw);
  }
});
test('review uses own display identity while retaining original source fields',()=>{
  const item=read('world-39-art.json').items[0],clip=headWorldSequences({items:[item]})[0];
  assert.equal(clip.projectEffectName,'云玩珍藏篮');assert.equal(clip.sourceName,'杂物帽');
});
