const frames = new Map();
let pending;

export function loadTrappedArt() {
  pending ??= fetch('./assets/characters/trapped/v2/manifest.json').then(async response => {
    if (!response.ok) return;
    const manifest = await response.json();
    if (manifest.schemaVersion !== 1 || manifest.state !== 'trapped' || !Array.isArray(manifest.frames)) return;

    await Promise.allSettled(manifest.frames.map(async frame => {
      const image = new Image();
      image.src = './' + frame.file;
      await image.decode();
      if (image.naturalWidth === 256 && image.naturalHeight === 256) frames.set(frame.characterId, image);
    }));
  }).catch(() => {});
  return pending;
}

export function drawTrappedArt(ctx, characterId, centerX, centerY) {
  const image = frames.get(characterId);
  if (!image) return false;
  ctx.drawImage(image, centerX - 38, centerY - 38, 76, 76);
  return true;
}
