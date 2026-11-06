import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {CHARACTERS} from '../src/game.js';
import {drawTrappedArt,loadTrappedArt} from '../src/trapped-art.js';

const fromRoot = file => new URL('../' + file, import.meta.url);
const manifest = JSON.parse(await readFile(fromRoot('assets/characters/trapped/v2/manifest.json'), 'utf8'));

test('all playable identities have distinct painted trapped-state RGBA assets', async () => {
  assert.deepEqual(manifest.frames.map(frame => frame.characterId).sort(), CHARACTERS.map(character => character.id).sort());
  assert.equal(new Set(manifest.frames.map(frame => frame.sha256)).size, 4);
  for (const frame of manifest.frames) {
    const png = await readFile(fromRoot(frame.file));
    assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    assert.deepEqual([png.readUInt32BE(16), png.readUInt32BE(20), png[25]], [256, 256, 6]);
    assert.equal(createHash('sha256').update(png).digest('hex'), frame.sha256);
  }
});

test('draws a decoded matching identity and leaves unavailable images to the fallback', async t => {
  t.mock.method(globalThis, 'fetch', async () => ({ok: true, json: async () => manifest}));
  class TestImage {
    async decode() {
      if (this.src.endsWith('/lotus-healer.png')) throw new Error('Test missing image');
      this.naturalWidth = 256;
      this.naturalHeight = 256;
    }
  }
  globalThis.Image = TestImage;
  t.after(() => { delete globalThis.Image; });
  const draws = [];
  const context = {drawImage: (image, ...bounds) => draws.push([image.src, ...bounds])};
  assert.equal(drawTrappedArt(context, 'maomao', 32, 26), false);
  await loadTrappedArt();
  assert.equal(drawTrappedArt(context, 'maomao', 32, 26), true);
  assert.equal(drawTrappedArt(context, 'titan', 32, 26), false);
  assert.equal(drawTrappedArt(context, 'unknown', 32, 26), false);
  assert.deepEqual(draws, [['./assets/characters/trapped/v2/daoist-child.png', -6, -12, 76, 76]]);
});
