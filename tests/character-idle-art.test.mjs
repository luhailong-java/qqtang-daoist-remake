import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {setImmediate} from 'node:timers/promises';
import test from 'node:test';
import {drawCharacterIdle,loadCharacterIdle} from '../src/character-motion.js';
import {CHARACTERS} from '../src/game.js';

const fromRoot = file => new URL('../' + file, import.meta.url);
const manifest = JSON.parse(await readFile(fromRoot('assets/characters/idle/v1/manifest.json'), 'utf8'));

test('four exact cardinal stills per identity have verified RGBA files and the same foot root', async () => {
  const expected = CHARACTERS.flatMap(character => ['N', 'E', 'S', 'W'].map(direction => `${character.id}/${direction}`));
  assert.deepEqual(manifest.frames.map(frame => `${frame.characterId}/${frame.direction}`).sort(), expected.sort());
  assert.equal(new Set(manifest.frames.map(frame => frame.sha256)).size, 16);
  for (const frame of manifest.frames) {
    const png = await readFile(fromRoot(frame.file));
    assert.deepEqual([png.readUInt32BE(16), png.readUInt32BE(20), png[25]], [256, 256, 6]);
    assert.deepEqual(frame.anchor, [128, 232]);
    assert.equal(createHash('sha256').update(png).digest('hex'), frame.sha256);
  }
});

test('directional stills are decoded lazily and use the same root without mirroring', async t => {
  t.mock.method(globalThis, 'fetch', async () => ({ok: true, json: async () => manifest}));
  globalThis.Image = class { async decode() { this.naturalWidth = 256; } };
  t.after(() => { delete globalThis.Image; });
  const draws = [];
  const ctx = {drawImage: (image, ...bounds) => draws.push([image.src, ...bounds])};
  await loadCharacterIdle();
  assert.equal(drawCharacterIdle(ctx, 'maomao', {dx:1,dy:0}, 55, 100, 110), false);
  await setImmediate();
  assert.equal(drawCharacterIdle(ctx, 'maomao', {dx:1,dy:0}, 55, 100, 110), true);
  assert.equal(drawCharacterIdle(ctx, 'maomao', {dx:-1,dy:0}, 55, 100, 110), false);
  await setImmediate();
  assert.equal(drawCharacterIdle(ctx, 'maomao', {dx:-1,dy:0}, 55, 100, 110), true);
  assert.equal(drawCharacterIdle(ctx, 'unknown', 'E', 55, 100, 110), false);
  assert.deepEqual(draws, [
    ['assets/characters/idle/v1/daoist-child-E.png', 0, 0.3125, 110, 110],
    ['assets/characters/idle/v1/daoist-child-W.png', 0, 0.3125, 110, 110],
  ]);
});
