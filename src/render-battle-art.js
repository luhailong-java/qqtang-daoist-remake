// Presentation-only candidates. This module never advances an animation or mutates game state.
const MANIFESTS = Object.freeze({
  pickups: 'assets/items/battlefield/art.json',
  creatures: 'assets/maps/exploration/creatures/art.json',
  bubbles: 'assets/effects/bubbles/manifest.json',
  flames: 'assets/effects/flames/manifest.json',
  states: 'assets/effects/states/manifest.json',
  props: 'assets/runtime/battle-props-20261112/manifest.json',
});
const PICKUP_SCENES = Object.freeze({capacity: 1, range: 2, speed: 3});
// These are original appearances for the synthetic draft waves, not native wave/entity assignments.
const DRAFT_SKINS = Object.freeze({ordinary: 30000, boss: 30006});
const CONTENT_RECTS = Object.freeze({
  30000: Object.freeze([247, 84, 823, 1041]),
  30006: Object.freeze([57, 138, 1181, 1014]),
});
const safePath = value => typeof value === 'string' && value.startsWith('assets/')
  && !value.includes('..') && !/[\\?#:\u0000-\u001f]/.test(value);

function asset(entry, manifest, extra = {}) {
  if (!safePath(entry.file) || !entry.file.endsWith('.png') || !/^[a-f0-9]{64}$/.test(entry.sha256 || '')
      || ![entry.width, entry.height].every(n => Number.isInteger(n) && n > 0 && n <= 8192)) {
    throw new Error(`Invalid painted candidate in ${manifest}`);
  }
  const rect = extra.rect || [0, 0, entry.width, entry.height];
  if (rect.some(n => !Number.isFinite(n)) || rect[0] < 0 || rect[1] < 0 || rect[2] <= 0 || rect[3] <= 0
      || rect[0] + rect[2] > entry.width || rect[1] + rect[3] > entry.height) throw new Error('Invalid content rectangle');
  return Object.freeze({file: entry.file, sha256: entry.sha256, width: entry.width, height: entry.height,
    manifest, generationRecord: entry.generationRecord || entry.derivedFrom?.generationRecord || null,
    provenanceRecord: entry.provenanceRecord || (entry.derivedFrom ? entry.file + '.provenance.json' : null),
    sourceRecord: entry.sourceRecord || entry.sourceReferenceRecord || entry.identityMappingRecord || null,
    sourceFrame: entry.sourceFirstFrame || entry.sourceFrame || null,
    representation: 'static-painted-client-candidate', sourceTimingMs: null, visualAccepted: false,
    ...extra, rect: Object.freeze([...rect])});
}

export function createBattleArtRuntime({fetchImpl = globalThis.fetch,
  createImage = () => new globalThis.Image()} = {}) {
  const pickups = new Map(), creatures = new Map(), props = new Map(), images = new Map(), errors = [];
  let bubble = null, blast = null, heldShield = null, loading;

  async function read(manifest, apply) {
    try {
      const response = await fetchImpl('./' + manifest);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (data.schemaVersion !== 1) throw new Error('Unsupported schema');
      apply(data);
    } catch (error) { errors.push({manifest, message: String(error.message || error)}); }
  }
  function load() {
    loading ??= Promise.all([
      read(MANIFESTS.pickups, data => {
        const entries = new Map();
        for (const entry of data.pieces) {
          if (!Number.isInteger(entry.sceneId) || entries.has(entry.sceneId)) throw new Error('Invalid scene ID');
          entries.set(entry.sceneId, asset(entry, MANIFESTS.pickups, {sceneId: entry.sceneId}));
        }
        for (const [id, entry] of entries) pickups.set(id, entry);
      }),
      read(MANIFESTS.creatures, data => {
        const entries = new Map();
        for (const entry of data.masters) {
          if (!Number.isInteger(entry.entityId) || entries.has(entry.entityId)) throw new Error('Invalid entity ID');
          entries.set(entry.entityId, asset(entry, MANIFESTS.creatures,
            {artworkCatalogEntityId: entry.entityId, rect: CONTENT_RECTS[entry.entityId],
              displayName: entry.projectOriginalChineseIdentityName}));
        }
        for (const [id, entry] of entries) creatures.set(id, entry);
      }),
      read(MANIFESTS.bubbles, data => {
        const frame = data.clips.find(entry => entry.sourceResource === 'bomb1_stand')?.frames
          .find(entry => entry.frameIndex === 0 && !entry.empty);
        bubble = asset(frame || {}, MANIFESTS.bubbles, {artworkResource: 'bomb1_stand', selectedFrameIndex: 0});
      }),
      read(MANIFESTS.flames, data => {
        // A transparent, newly painted cloud-fire burst is a generic danger-cell appearance.
        // Native flame1-9 directional/endpoint associations remain unverified and are not guessed here.
        const frame = data.resources.find(entry => entry.sourceResource === 'flame10_stand')?.frames
          .find(entry => entry.frameIndex === 0 && !entry.empty);
        blast = asset(frame || {}, MANIFESTS.flames, {artworkResource: 'flame10_stand', selectedFrameIndex: 0});
      }),
      read(MANIFESTS.states, data => {
        // A static own painting for the existing shield flag. The original lookup, anchor and pace remain unknown.
        const frame = data.resources.find(entry => entry.sourceResource === 'magic3')?.frames
          .find(entry => entry.frameIndex === 2 && !entry.empty);
        heldShield = asset(frame || {}, MANIFESTS.states, {artworkResource: 'magic3', selectedFrameIndex: 2});
      }),
      read(MANIFESTS.props, data => {
        const entries = new Map();
        for (const entry of data.pieces) {
          if (!['needle', 'shield', 'bun'].includes(entry.slot) || entries.has(entry.slot)
              || entry.sceneId != null || entry.sourceEntityId != null) throw new Error('Invalid temporary prop slot');
          entries.set(entry.slot, asset(entry, MANIFESTS.props, {slot: entry.slot, sceneId: null,
            sourceEntityId: null, appearanceMapping: 'original-temporary-skin-for-technical-role'}));
        }
        for (const [slot, entry] of entries) props.set(slot, entry);
      }),
    ]).then(() => status());
    return loading;
  }
  function pickupDescriptor(pickup) {
    const typeScene = PICKUP_SCENES[pickup?.type];
    if (pickup?.sceneId !== undefined && pickup.sceneId !== null) {
      if (!Number.isInteger(pickup.sceneId) || (typeScene !== undefined && pickup.sceneId !== typeScene)) return null;
      return pickups.get(pickup.sceneId) || null;
    }
    // Account inventory itemId is deliberately not a scene-factory ID.
    return typeScene === undefined ? props.get(pickup?.type) || null : pickups.get(typeScene) || null;
  }
  function monsterDescriptor(monster, game) {
    if (!monster || typeof monster !== 'object') return null;
    const sourceId = monster?.entityId ?? monster?.sourceEntityId;
    if (sourceId !== undefined && sourceId !== null) {
      if (!Number.isInteger(sourceId)) return null;
      const selected = creatures.get(sourceId);
      return selected ? Object.freeze({asset: selected, sourceEntityId: sourceId,
        appearanceMapping: 'explicit-entity-id'}) : null;
    }
    if (game?.mapKind !== 'draft-map' || game?.mode !== 'adventure') return null;
    const selected = creatures.get(DRAFT_SKINS[monster?.boss ? 'boss' : 'ordinary']);
    return selected ? Object.freeze({asset: selected, sourceEntityId: null,
      appearanceMapping: 'original-temporary-skin-for-synthetic-draft-role'}) : null;
  }
  function requestImage(descriptor) {
    if (!descriptor) return null;
    if (images.has(descriptor.file)) return images.get(descriptor.file);
    const entry = {ready: false, failed: false, image: null, promise: null};
    images.set(descriptor.file, entry);
    entry.promise = (async () => {
      try {
        const image = createImage();
        image.decoding = 'async'; image.src = './' + descriptor.file;
        await image.decode();
        if (image.naturalWidth !== descriptor.width || image.naturalHeight !== descriptor.height) {
          throw new Error('Decoded PNG dimensions differ from its manifest');
        }
        entry.image = image; entry.ready = true;
      } catch (error) { entry.failed = true; errors.push({file: descriptor.file, message: String(error.message || error)}); }
      return entry.ready;
    })();
    return entry;
  }
  function draw(ctx, descriptor, x, y, width, height) {
    if (!descriptor) { void load(); return false; }
    if (![x, y, width, height].every(Number.isFinite) || width <= 0 || height <= 0) return false;
    const entry = requestImage(descriptor);
    if (!entry.ready) return false;
    const [sx, sy, sw, sh] = descriptor.rect, scale = Math.min(width / sw, height / sh);
    const w = sw * scale, h = sh * scale;
    ctx.drawImage(entry.image, sx, sy, sw, sh, x + (width - w) / 2, y + (height - h) / 2, w, h);
    return true;
  }
  async function preloadDefaults() {
    await load();
    await Promise.all([pickups.get(1), pickups.get(2), pickups.get(3), bubble, blast, heldShield, ...props.values()]
      .filter(Boolean).map(descriptor => requestImage(descriptor).promise));
    return status();
  }
  function status() {
    return {representation: 'static-painted-client-candidates', visualAccepted: false,
      sourceTimingMs: null, pickupScenes: [...pickups.keys()], temporaryPropSlots: [...props.keys()],
      creatureEntityIds: [...creatures.keys()],
      loadedImages: [...images].filter(([, entry]) => entry.ready).map(([file]) => file), errors: [...errors]};
  }
  return Object.freeze({load, preloadDefaults, status, pickupDescriptor, monsterDescriptor,
    propDescriptor: slot => props.get(slot) || null,
    bubbleDescriptor: () => bubble, blastDescriptor: () => blast,
    heldShieldDescriptor: () => heldShield,
    drawPickup: (ctx, pickup, ...bounds) => draw(ctx, pickupDescriptor(pickup), ...bounds),
    drawProp: (ctx, slot, ...bounds) => draw(ctx, props.get(slot), ...bounds),
    drawMonster: (ctx, monster, game, ...bounds) => draw(ctx, monsterDescriptor(monster, game)?.asset, ...bounds),
    drawBubble: (ctx, ...bounds) => draw(ctx, bubble, ...bounds),
    drawBlast: (ctx, ...bounds) => draw(ctx, blast, ...bounds),
    drawHeldShield: (ctx, player, ...bounds) => player?.alive === true && player.shield === true
      && player.trappedUntil == null && draw(ctx, heldShield, ...bounds)});
}

const runtime = createBattleArtRuntime();
export const loadBattleArt = () => runtime.preloadDefaults();
export const drawBattlePickup = (...args) => runtime.drawPickup(...args);
export const drawBattleProp = (...args) => runtime.drawProp(...args);
export const drawBattleMonster = (...args) => runtime.drawMonster(...args);
export const drawBattleBubble = (...args) => runtime.drawBubble(...args);
export const drawBattleBlast = (...args) => runtime.drawBlast(...args);
export const drawHeldShield = (...args) => runtime.drawHeldShield(...args);
export const battleArtStatus = () => runtime.status();
