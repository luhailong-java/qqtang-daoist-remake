// Existing image-repository poses, exported on a shared 256px canvas.
// Every available clip is a client candidate; enabling it is an explicit caller choice.
const aliases = {
  maomao: 'daoist-child', asha: 'moon-shadow',
  wukong: 'mountain-guardian', titan: 'lotus-healer',
};
const imageCache = new Map();
const pendingClips = new Map();
const MAX_CACHED_FRAMES = 48;
let manifest = null;
let manifestPromise = null;
let manifestError = null;

export function characterMotionId(id) { return aliases[id] || id; }

export function motionDirection(facing) {
  if (typeof facing === 'string') {
    const value = facing.toUpperCase();
    return ({ UP: 'N', RIGHT: 'E', DOWN: 'S', LEFT: 'W' })[value]
      || (['N', 'E', 'S', 'W'].includes(value) ? value : null);
  }
  if (!facing || (!facing.dx && !facing.dy)) return null;
  return Math.abs(facing.dx || 0) > Math.abs(facing.dy || 0)
    ? (facing.dx < 0 ? 'W' : 'E') : (facing.dy < 0 ? 'N' : 'S');
}

export async function loadCharacterMotion() {
  if (!manifestPromise) {
    manifestPromise = (async () => {
      const response = await fetch('./assets/characters/motion/manifest.json');
      if (!response.ok) throw new Error(`人物动作清单读取失败：${response.status}`);
      const data = await response.json();
      if (data.schemaVersion !== 1 || !data.characters) throw new Error('人物动作清单格式不支持');
      manifest = data;
      return data;
    })().catch(error => { manifestError = error; throw error; });
  }
  return manifestPromise;
}

export function characterMotionStatus(id) {
  return manifest?.characters[characterMotionId(id)] || null;
}

export function characterMotionLoadError() { return manifestError; }

function clipFor(id, { action = 'run', direction = 'S', allowCandidate = false } = {}) {
  const character = characterMotionStatus(id);
  if (!character || (character.adoptionStatus === 'client_candidate' && !allowCandidate)) return null;
  const cardinal = motionDirection(direction);
  return cardinal ? character.clips[action]?.[cardinal] || null : null;
}

function touch(file, entry) {
  imageCache.delete(file);
  imageCache.set(file, entry);
  if (imageCache.size > MAX_CACHED_FRAMES) {
    for (const [key, cached] of imageCache) {
      if (imageCache.size <= MAX_CACHED_FRAMES) break;
      if (cached.ready) imageCache.delete(key);
    }
  }
}

function loadFrame(file) {
  const cached = imageCache.get(file);
  if (cached) { touch(file, cached); return cached.promise; }
  const image = new Image();
  image.decoding = 'async';
  const entry = { image, ready: false, promise: null };
  image.src = file;
  entry.promise = image.decode().then(() => {
    entry.ready = Boolean(image.naturalWidth);
    touch(file, entry);
    return entry.ready ? image : null;
  }).catch(() => { imageCache.delete(file); return null; });
  imageCache.set(file, entry);
  return entry.promise;
}

// Load only the requested action and direction. No diagonals are substituted or mirrored.
export async function preloadCharacterMotion(id, options = {}) {
  await loadCharacterMotion();
  const clip = clipFor(id, options);
  if (!clip) return null;
  const key = `${characterMotionId(id)}/${options.action || 'run'}/${motionDirection(options.direction || 'S')}`;
  if (!pendingClips.has(key)) {
    const request = (async () => {
      let cursor = 0;
      let complete = true;
      const worker = async () => {
        while (cursor < clip.frames.length) {
          const frame = clip.frames[cursor++];
          if (!await loadFrame(frame.file)) complete = false;
        }
      };
      await Promise.all(Array.from({ length: Math.min(4, clip.frames.length) }, worker));
      return complete;
    })().finally(() => pendingClips.delete(key));
    pendingClips.set(key, request);
  }
  return pendingClips.get(key);
}

// A descriptor may exist before its image is decoded. elapsedMs is supplied by the renderer;
// this module never advances gameplay or changes movement, collision or damage timing.
export function getCharacterMotionFrame(id, options = {}) {
  const clip = clipFor(id, options);
  if (!clip?.frames.length) return null;
  const elapsed = Number.isFinite(options.elapsedMs) ? Math.max(0, options.elapsedMs) : 0;
  const loop = options.loop ?? clip.loop;
  const phase = loop ? elapsed % clip.durationMs : Math.min(elapsed, clip.durationMs - 1);
  const index = Math.min(clip.frames.length - 1, Math.floor(phase / clip.frameMs));
  const frame = clip.frames[index];
  const cached = imageCache.get(frame.file);
  if (cached) touch(frame.file, cached);
  return {
    ...frame, index, image: cached?.ready ? cached.image : null,
    canvas: manifest.canvas, anchor: clip.anchor,
    durationMs: clip.durationMs, ended: !loop && elapsed >= clip.durationMs,
    sourceStatus: characterMotionStatus(id).sourceStatus,
    adoptionStatus: 'client_candidate', clientApproved: false,
  };
}

// x/y locate the fixed world root; size is the width AND height of the full source canvas.
// Return false for missing/not-yet-decoded clips so the caller can draw the original still.
export function drawCharacterMotion(ctx, id, x, y, size, options = {}) {
  if (!manifest) { void loadCharacterMotion().catch(() => {}); return false; }
  const frame = getCharacterMotionFrame(id, options);
  if (!frame || !(size > 0)) return false;
  // On a render tick load only the selected frame. Re-preloading every whole
  // clip can churn a bounded cache when several characters face different ways.
  if (!frame.image) { void loadFrame(frame.file); return false; }
  const scale = size / frame.canvas[0];
  ctx.drawImage(frame.image, x - frame.anchor[0] * scale, y - frame.anchor[1] * scale, size, size);
  return true;
}
