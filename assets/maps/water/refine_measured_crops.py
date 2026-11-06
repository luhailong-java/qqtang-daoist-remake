"""Correct four evidenced cell-boundary crops, without AI or source geometry edits."""
import copy
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def box(image):
    return image.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()

manifest = read(OUT / 'art.json')
regions = {5002: [580, 40, 950, 495], 5005: [580, 500, 960, 980], 5024: [600, 515, 970, 950]}
for i, old in enumerate(manifest['pieces']):
    identity = old['elementId']
    if identity not in regions:
        continue
    destination = OUT / f'pieces/{identity}-water-v2-crop.png'
    if destination.exists():
        raise ValueError('Refusing overwrite')
    item = copy.deepcopy(old)
    image = Image.open(ROOT / old['derivedFrom']['file']).convert('RGBA')
    region = regions[identity]
    cell = image.crop(region)
    core = box(cell)
    bounds = [max(0, core[0]-2), max(0, core[1]-2), min(cell.width, core[2]+2), min(cell.height, core[3]+2)]
    absolute = [region[0]+bounds[0], region[1]+bounds[1], region[0]+bounds[2], region[1]+bounds[3]]
    crop = image.crop(absolute)
    target = (item['worldFrameWidth']*4, item['worldFrameHeight']*4)
    scale = min(target[0]/crop.width, target[1]/crop.height)
    size = (round(crop.width*scale), round(crop.height*scale))
    placement = ((target[0]-size[0])//2, target[1]-size[1])
    canvas = Image.new('RGBA', target, (0,0,0,0))
    canvas.alpha_composite(crop.resize(size, Image.Resampling.LANCZOS), placement)
    canvas.save(destination)
    item['file'] = destination.relative_to(ROOT).as_posix()
    item['sha256'] = hashlib.sha256(destination.read_bytes()).hexdigest()
    item['operation'] = {'type': 'refined-measured-crop-uniform-fit-bottom-align', 'sourceRectLTRB': absolute, 'uniformScale': scale, 'placementPx': list(placement), 'resampled': True, 'newModelGeneration': False, 'supersedes': {'file': old['file'], 'sha256': old['sha256']}, 'reason': 'Measured object regions replace equal-row cells; avoid cutting one asset and including the previous row.'}
    gb = box(crop)
    ga = (gb[2]-gb[0])/(gb[3]-gb[1])
    deviation = abs(ga/item['qa']['sourceVisibleAspect']-1)
    edge = core[0] == 0 or core[1] == 0 or core[2] == cell.width or core[3] == cell.height
    warnings = ['source-id-lookup-and-render-anchor-unverified', 'original-map-geometry-and-in-game-validation-pending']
    if deviation > .1:
        warnings.append(f'generated-visible-aspect-deviation-{deviation:.3f}-exceeds-0.100-review-required')
    if edge:
        warnings.append('visible-core-touches-generated-cell-edge-review-required')
    item['qa'].update({'generatedVisibleAspect': ga, 'relativeAspectDeviation': deviation, 'generatedCellLTRB': region, 'coreTouchesCellEdge': edge, 'warnings': warnings})
    item['alphaExtrema'] = canvas.getchannel('A').getextrema()
    write(destination.with_suffix('.png.provenance.json'), item)
    manifest['pieces'][i] = item
    manifest.setdefault('supersededCrops', []).append({'elementId': identity, 'file': old['file'], 'replacedBy': item['file'], 'reason': item['operation']['reason'], 'retentionReason': 'May still be referenced by root global inventory until its next refresh; do not delete automatically.'})
write(OUT / 'art.json', manifest)
print(json.dumps([{'elementId': p['elementId'], 'file': p['file'], 'aspectDeviation': p['qa']['relativeAspectDeviation'], 'edge': p['qa']['coreTouchesCellEdge']} for p in manifest['pieces'] if p['elementId'] in regions]))
