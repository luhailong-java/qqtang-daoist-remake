import {ART_RUNTIME_FALLBACK} from './battle-art-fallback-data.js';

export let art = structuredClone(ART_RUNTIME_FALLBACK);
const images = new Map();
let loadErrors = [];

function sourceFor(index, sheet) {
  if (!Number.isInteger(index) || index < 0) return null;
  return art[sheet]?.assets?.[index] || null;
}

export async function loadArt({fetchImpl = globalThis.fetch, createImage = () => new globalThis.Image()} = {}) {
  art = structuredClone(ART_RUNTIME_FALLBACK); images.clear(); loadErrors = [];
  try {
    const response = await fetchImpl('./assets/art.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const candidate = await response.json();
    // A stale/failed JSON fetch cannot reintroduce an old atlas.
    if (JSON.stringify(candidate) !== JSON.stringify(ART_RUNTIME_FALLBACK)) throw new Error('Runtime art table differs from its checked default');
    art = candidate;
  } catch (error) { loadErrors.push({file: 'assets/art.json', message: String(error.message || error)}); }
  const sources = new Map();
  for (const sheet of ['characters', 'tiles', 'pickups', 'effects']) {
    for (const source of art[sheet].assets) if (source) sources.set(source.file, source);
  }
  await Promise.all([...sources].map(async ([file, source]) => {
    try {
      const image = createImage(); image.decoding = 'async'; image.src = file;
      await image.decode();
      if (image.naturalWidth !== source.width || image.naturalHeight !== source.height) throw new Error('PNG dimensions differ from default table');
      images.set(file, image);
    } catch (error) { loadErrors.push({file, message: String(error.message || error)}); }
  }));
  return {loadedFiles: [...images.keys()], errors: [...loadErrors]};
}

export function sprite(index, cls = '', sheet = 'characters') {
  const source = sourceFor(index, sheet);
  if (!source) return `<span class="sprite ${cls} missing-sprite" aria-hidden="true"></span>`;
  return `<span class="sprite ${cls}" aria-hidden="true"><svg class="atlas-sprite" viewBox="${source.rect.join(' ')}" preserveAspectRatio="xMidYMid meet"><image href="${source.file}" width="${source.width}" height="${source.height}"/></svg></span>`;
}

export function drawSprite(ctx, index, x, y, width, height, sheet = 'characters') {
  const source = sourceFor(index, sheet), image = source && images.get(source.file);
  if (!source || !image || ![x, y, width, height].every(Number.isFinite) || width <= 0 || height <= 0) return false;
  const [sx, sy, sw, sh] = source.rect, scale = Math.min(width / sw, height / sh);
  const w = sw * scale, h = sh * scale;
  ctx.drawImage(image, sx, sy, sw, sh, x + (width - w) / 2, y + (height - h) / 2, w, h);
  return true;
}
