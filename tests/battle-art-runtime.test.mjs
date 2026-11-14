import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {setImmediate} from 'node:timers/promises';
import test from 'node:test';
import {createBattleArtRuntime} from '../src/render-battle-art.js';
import {createGame} from '../src/game.js';
import {createAppServer} from '../server/app.mjs';
import {ART_RUNTIME_FALLBACK, PICKUP_FALLBACK_SLOTS} from '../src/battle-art-fallback-data.js';
import {loadArt, drawSprite, sprite, art} from '../src/art.js';

const rootFile = file => new URL('../' + file.replace(/^\.\//, ''), import.meta.url);
const manifestFiles = [
  'assets/items/battlefield/art.json', 'assets/maps/exploration/creatures/art.json',
  'assets/effects/bubbles/manifest.json', 'assets/effects/flames/manifest.json',
  'assets/runtime/battle-props-20261112/manifest.json',
  'assets/effects/states/manifest.json',
];
const manifests = new Map(await Promise.all(manifestFiles.map(async file =>
  [file, JSON.parse(await readFile(rootFile(file), 'utf8'))])));
const dimensions = new Map();
for (const data of manifests.values()) {
  const entries = data.pieces || data.masters || (data.clips || data.resources).flatMap(clip => clip.frames);
  for (const entry of entries) if (entry.file) dimensions.set(entry.file, [entry.width, entry.height]);
}
function fixture({missingManifest, rejectImage, wrongDimensions = false} = {}) {
  const fetches = [], decoded = [];
  const runtime = createBattleArtRuntime({
    fetchImpl: async path => {
      const file = path.replace(/^\.\//, ''); fetches.push(file);
      return file === missingManifest ? {ok: false, status: 404} :
        {ok: true, json: async () => structuredClone(manifests.get(file))};
    },
    createImage: () => ({
      async decode() {
        const file = this.src.replace(/^\.\//, ''); decoded.push(file);
        if (file === rejectImage) throw new Error('Missing PNG');
        [this.naturalWidth, this.naturalHeight] = dimensions.get(file);
        if (wrongDimensions) this.naturalWidth++;
      },
    }),
  });
  return {runtime, fetches, decoded};
}
function selectedCandidates(runtime) {
  const game = {mode: 'adventure', mapKind: 'draft-map'};
  return [...['capacity', 'range', 'speed'].map(type => runtime.pickupDescriptor({type})),
    ...['needle', 'shield', 'bun'].map(slot => runtime.propDescriptor(slot)),
    runtime.monsterDescriptor({boss: false}, game).asset, runtime.monsterDescriptor({boss: true}, game).asset,
    runtime.bubbleDescriptor(), runtime.blastDescriptor(), runtime.heldShieldDescriptor(), ...runtime.rescueDescriptors()];
}

test('capacity, range and speed use separate scene-factory paintings, without inventory-ID confusion', async () => {
  const {runtime, fetches, decoded} = fixture();
  await runtime.load();
  assert.equal(fetches.length, manifestFiles.length);
  assert.equal(decoded.length, 0);
  assert.deepEqual(['capacity', 'range', 'speed'].map(type => runtime.pickupDescriptor({type}).sceneId), [1, 2, 3]);
  assert.equal(new Set(['capacity', 'range', 'speed'].map(type => runtime.pickupDescriptor({type}).file)).size, 3);
  assert.equal(runtime.pickupDescriptor({type: 'unknown', itemId: 1}), null);
  assert.equal(runtime.pickupDescriptor({type: 'capacity', sceneId: 2}), null);
  assert.equal(runtime.pickupDescriptor({sceneId: 999999}), null);
});

test('synthetic normal/Boss appearances remain distinct from exact native entity identity', async () => {
  const {runtime} = fixture(); await runtime.load();
  const game = createGame({mode: 'adventure'}), before = structuredClone(game), monster = game.monsters[0];
  const normal = runtime.monsterDescriptor(monster, game);
  const boss = runtime.monsterDescriptor({...monster, boss: true}, game);
  assert.equal(normal.sourceEntityId, null); assert.equal(boss.sourceEntityId, null);
  assert.equal(normal.asset.artworkCatalogEntityId, 30000);
  assert.equal(boss.asset.artworkCatalogEntityId, 30006);
  assert.notEqual(normal.asset.file, boss.asset.file);
  assert.equal(runtime.monsterDescriptor(monster, {...game, mapKind: 'source-map'}), null);
  assert.equal(runtime.monsterDescriptor({...monster, entityId: 999999}, game), null);
  const exact = runtime.monsterDescriptor({...monster, entityId: 30006}, {...game, mapKind: 'source-map'});
  assert.equal(exact.sourceEntityId, 30006); assert.equal(exact.appearanceMapping, 'explicit-entity-id');
  assert.deepEqual(game, before);
});

test('currently used paintings have exact PNG hashes, dimensions and a present generation/provenance chain', async () => {
  const {runtime} = fixture(); await runtime.load();
  const selected = selectedCandidates(runtime);
  assert.equal(new Set(selected.map(entry => entry.file)).size, 13);
  for (const entry of selected) {
    const bytes = await readFile(rootFile(entry.file));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.sha256);
    assert.deepEqual([bytes.readUInt32BE(16), bytes.readUInt32BE(20), bytes[25]], [entry.width, entry.height, 6]);
    assert.ok(entry.generationRecord);
    JSON.parse(await readFile(rootFile(entry.generationRecord), 'utf8'));
    if (entry.provenanceRecord) JSON.parse(await readFile(rootFile(entry.provenanceRecord), 'utf8'));
    assert.equal(entry.visualAccepted, false); assert.equal(entry.sourceTimingMs, null);
  }
});

test('static effect painting and uniform fitting do not advance clocks, add cells or mutate game state', async () => {
  const {runtime} = fixture(); await runtime.preloadDefaults();
  const game = createGame(), before = structuredClone(game), draws = [];
  const ctx = {drawImage: (image, ...bounds) => draws.push({file: image.src, bounds})};
  assert.equal(runtime.drawPickup(ctx, {type: 'range'}, 133, 197, 54, 54), true);
  assert.equal(runtime.drawBubble(ctx, 123, 187, 74, 74), true);
  assert.equal(runtime.drawBlast(ctx, 118, 182, 84, 84), true);
  assert.equal(runtime.drawBubble(ctx, 123, 187, 74, 74), true);
  assert.equal(draws.length, 4);
  assert.deepEqual(draws[1], draws[3]);
  for (const draw of draws) {
    const [, , sourceWidth, sourceHeight, , , targetWidth, targetHeight] = draw.bounds;
    assert.ok(Math.abs(sourceWidth / sourceHeight - targetWidth / targetHeight) < 1e-9);
  }
  assert.equal(runtime.bubbleDescriptor().selectedFrameIndex, 0);
  assert.equal(runtime.blastDescriptor().selectedFrameIndex, 0);
  assert.deepEqual(game, before);
});

test('shield painting follows only the live held flag, separately from the pickup and invulnerability timer', async () => {
  const {runtime} = fixture(); await runtime.preloadDefaults();
  const player = {alive: true, shield: true, trappedUntil: null, invulnerableUntil: 0};
  const draws = [], ctx = {drawImage: image => draws.push(image.src)};
  const render = state => runtime.drawHeldShield(ctx, state, 0, 0, 108, 108);
  assert.equal(render(player), true);
  assert.equal(render({...player, alive: false}), false);
  assert.equal(render({...player, trappedUntil: 4000}), false);
  assert.equal(render({...player, shield: false, invulnerableUntil: 1000}), false);
  assert.deepEqual(draws, ['./' + runtime.heldShieldDescriptor().file]);
  assert.notEqual(runtime.heldShieldDescriptor().file, runtime.pickupDescriptor({type: 'shield'}).file);
});

test('rescue cue restores alpha and does not draw a partial pair or expired event', async () => {
  const {runtime} = fixture(); await runtime.preloadDefaults();
  const calls = [];
  const ctx = {globalAlpha: 0.8, save() { this.previous = this.globalAlpha; },
    restore() { this.globalAlpha = this.previous; }, drawImage(image) { calls.push([image.src, this.globalAlpha]); }};
  assert.equal(runtime.drawRescueCue(ctx, -1, 32, 52), false);
  assert.equal(runtime.drawRescueCue(ctx, 320, 32, 52), false);
  assert.equal(runtime.drawRescueCue(ctx, 240, 32, 52), true);
  assert.equal(ctx.globalAlpha, 0.8);
  assert.deepEqual(calls, runtime.rescueDescriptors().reverse().map(entry => ['./' + entry.file, 0.4]));
  const missing = fixture({rejectImage: runtime.rescueDescriptors()[0].file}).runtime;
  await missing.preloadDefaults();
  assert.equal(missing.drawRescueCue({drawImage() { assert.fail('Partial rescue art'); }}, 0, 32, 52), false);
});

test('unavailable/not-decoded art returns false for the existing caller fallback, with one decode attempt', async () => {
  const missing = manifests.get(manifestFiles[0]).pieces.find(entry => entry.sceneId === 1).file;
  const {runtime, decoded} = fixture({rejectImage: missing}); await runtime.load();
  const ctx = {drawImage() { assert.fail('A missing painting must not draw'); }};
  assert.equal(runtime.drawPickup(ctx, {type: 'capacity'}, 0, 0, 54, 54), false);
  await setImmediate();
  assert.equal(runtime.drawPickup(ctx, {type: 'capacity'}, 0, 0, 54, 54), false);
  assert.equal(decoded.filter(file => file === missing).length, 1);
  assert.equal(runtime.drawPickup(ctx, {type: 'unknown'}, 0, 0, 54, 54), false);
  assert.ok(runtime.status().errors.some(error => error.file === missing));
});

test('one missing manifest or wrong PNG dimensions cannot disable unrelated candidate groups', async () => {
  const {runtime} = fixture({missingManifest: manifestFiles[1]}); await runtime.preloadDefaults();
  assert.equal(runtime.monsterDescriptor({boss: true}, {mode: 'adventure', mapKind: 'draft-map'}), null);
  assert.ok(runtime.pickupDescriptor({type: 'speed'}));
  assert.ok(runtime.bubbleDescriptor());
  assert.ok(runtime.status().errors.some(error => error.manifest === manifestFiles[1]));
  const broken = fixture({wrongDimensions: true}); await broken.runtime.preloadDefaults();
  assert.equal(broken.runtime.drawBubble({drawImage() { assert.fail('Wrong-size PNG must not draw'); }}, 0, 0, 74, 74), false);
  assert.equal(broken.runtime.status().loadedImages.length, 0);
});

test('adventure painting decodes only the two selected skins and keeps the existing caller rectangles', async () => {
  const {runtime, decoded} = fixture(); await runtime.load();
  const game = createGame({mode: 'adventure'}), before = structuredClone(game), draws = [];
  const ctx = {drawImage: (image, ...bounds) => draws.push({file: image.src, bounds})};
  for (const boss of [false, true]) {
    assert.equal(runtime.drawMonster(ctx, {boss}, game, 438, 364, 84, 84), false);
    await setImmediate();
    assert.equal(runtime.drawMonster(ctx, {boss}, game, 438, 364, 84, 84), true);
  }
  assert.equal(decoded.length, 2); assert.equal(draws.length, 2);
  for (const {bounds: [sx, sy, sw, sh, x, y, w, h]} of draws) {
    assert.ok(sx >= 0 && sy >= 0 && sw > 0 && sh > 0);
    assert.ok(x >= 438 && y >= 364 && x + w <= 522 && y + h <= 448);
    assert.ok(Math.abs(sw / sh - w / h) < 1e-9);
  }
  assert.deepEqual(game, before);
});

test('the project HTTP server serves the new runtime module and every selected original PNG unchanged', async t => {
  const server = createAppServer({port: 0}); const address = await server.start();
  t.after(() => server.close());
  const {runtime} = fixture(); await runtime.load();
  const selected = selectedCandidates(runtime);
  const origin = `http://127.0.0.1:${address.port}/`;
  await Promise.all(selected.map(async entry => {
    const response = await fetch(origin + entry.file);
    assert.equal(response.status, 200); assert.equal(response.headers.get('content-type'), 'image/png');
    assert.equal(createHash('sha256').update(Buffer.from(await response.arrayBuffer())).digest('hex'), entry.sha256);
  }));
  const response = await fetch(origin + 'src/render-battle-art.js');
  assert.equal(response.status, 200);
  assert.equal(await response.text(), await readFile(rootFile('src/render-battle-art.js'), 'utf8'));
});

test('needle, shield and bun are explicit original temporary slots with null native IDs and unchanged old display bounds', async () => {
  const {runtime} = fixture(); await runtime.preloadDefaults();
  const draws = [], ctx = {drawImage: (image, ...bounds) => draws.push({file: image.src, bounds})};
  for (const type of ['needle', 'shield', 'bun']) {
    const entry = runtime.pickupDescriptor({type});
    assert.equal(entry.slot, type); assert.equal(entry.sceneId, null); assert.equal(entry.sourceEntityId, null);
    assert.equal(runtime.drawPickup(ctx, {type}, 69, 133, type === 'bun' ? 64 : 54, type === 'bun' ? 64 : 54), true);
  }
  for (const bounds of [[56, 118, 80, 80], [95, 112, 35, 35]]) assert.equal(runtime.drawProp(ctx, 'bun', ...bounds), true);
  assert.deepEqual(draws.slice(-2).map(draw => draw.bounds.slice(4)), [[56, 118, 80, 80], [95, 112, 35, 35]]);
  assert.equal(new Set(draws.filter(draw => draw.file.endsWith('/bun.png')).map(draw => draw.file)).size, 1);
});

test('default tables match byte-reviewed originals, preserve the four identities and contain no legacy atlas paths', async () => {
  assert.deepEqual(JSON.parse(await readFile(rootFile('assets/art.json'), 'utf8')), ART_RUNTIME_FALLBACK);
  assert.doesNotMatch(JSON.stringify(ART_RUNTIME_FALLBACK), /qqtang-characters-v2\.png|game-atlas\.png/);
  assert.deepEqual(ART_RUNTIME_FALLBACK.characters.assets.slice(0, 4).map(({file, width, height, rect}) => ({file, width, height, rect})), [
    {file:'./assets/characters/runtime/daoist-child.png',width:1024,height:1024,rect:[195,59,633,907]},
    {file:'./assets/characters/runtime/moon-shadow.png',width:1024,height:1024,rect:[124,59,775,906]},
    {file:'./assets/characters/runtime/mountain-guardian.png',width:1024,height:1024,rect:[161,59,701,906]},
    {file:'./assets/characters/runtime/lotus-healer.png',width:1024,height:1024,rect:[142,59,740,906]},
  ]);
  assert.deepEqual(ART_RUNTIME_FALLBACK.tiles.assets.slice(0, 3), [null, null, null]);
  const entries = ['characters','tiles','pickups','effects'].flatMap(sheet => ART_RUNTIME_FALLBACK[sheet].assets).filter(Boolean);
  for (const entry of entries) {
    const bytes = await readFile(rootFile(entry.file));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.sha256);
    assert.deepEqual([bytes.readUInt32BE(16), bytes.readUInt32BE(20)], [entry.width, entry.height]);
    if (entry.provenanceRecord) JSON.parse(await readFile(rootFile(entry.provenanceRecord), 'utf8'));
  }
});

test('JSON fetch failure or a stale legacy table still preloads own fallbacks; unknown slots stay unmapped', async () => {
  const dimensions = new Map(['characters','tiles','pickups','effects']
    .flatMap(sheet => ART_RUNTIME_FALLBACK[sheet].assets).filter(Boolean).map(entry => [entry.file, [entry.width, entry.height]]));
  for (const fetchImpl of [async () => { throw new Error('Offline'); },
    async () => ({ok: true, json: async () => ({tiles: {file:'./assets/game-atlas.png'}})})]) {
    const loaded = [];
    const result = await loadArt({fetchImpl, createImage: () => ({async decode() {
      loaded.push(this.src); [this.naturalWidth, this.naturalHeight] = dimensions.get(this.src);
    }})});
    assert.ok(result.errors.length); assert.ok(loaded.length > 0);
    assert.ok(loaded.every(file => !/qqtang-characters-v2|game-atlas/.test(file)));
    assert.deepEqual(art, ART_RUNTIME_FALLBACK);
    const draws = [], ctx = {drawImage: (...args) => draws.push(args)};
    assert.equal(drawSprite(ctx, 0, 0, 0, 64, 64, 'tiles'), false);
    assert.equal(drawSprite(ctx, 999, 0, 0, 64, 64), false);
    assert.equal(sprite(999).includes('<image'), false);
    assert.equal(draws.length, 0);
    assert.equal(drawSprite(ctx, 6, 0, 0, 84, 84), true);
    assert.equal(drawSprite(ctx, PICKUP_FALLBACK_SLOTS.needle, 0, 0, 54, 54, 'pickups'), true);
  }
});
