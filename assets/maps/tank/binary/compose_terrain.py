"""Assemble at most three terrain IDs from exact source geometry and new painted RGB."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import numpy as np
import hashlib, json, sys

OUT = Path(__file__).resolve().parent
FAMILY = OUT.parent
ROOT = OUT.parents[3]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

ids = [int(n) for n in sys.argv[1:]]
assert 1 <= len(ids) <= 3 and all(19048 <= n <= 19054 for n in ids)
index_path = ROOT / 'references/qqtang-map-data/visual-reference/binary-supplement/art-reference-index.json'
entries = {p['elementId']: p for p in read(index_path)['elements']}
master_path = OUT / 'props-e-v1.png'
grass_path = OUT / 'props-d-v1.png'
master = Image.open(master_path).convert('RGBA')
grass_master = Image.open(grass_path).convert('RGBA')
materials, records = {}, []
for name, img, path, rect in [
    ('water', master, master_path, [10, 10, 877, 877]),
    ('earth', master, master_path, [897, 10, 1764, 877]),
    ('grass', grass_master, grass_path, [10, 10, 877, 877]),
]:
    crop = img.crop(rect)
    assert crop.size == (867, 867) and crop.getchannel('A').getextrema() == (255, 255)
    materials[name] = crop.resize((160, 160), Image.Resampling.LANCZOS)
    records.append({'material': name, 'file': path.relative_to(ROOT).as_posix(),
                    'sha256': sha(path), 'generationRecord': path.relative_to(ROOT).as_posix()+'.generation.json',
                    'sourceRectLTRB': rect, 'nativeCropSize': [867, 867],
                    'sourceAlphaExtrema': [255, 255], 'alphaNormalization': None,
                    'uniformScale': 160/867, 'resampler': 'LANCZOS',
                    'purpose': 'new original-painted RGB texture only'})

manifest = FAMILY / 'art.json'
art = read(manifest)
art['pieces'] = [p for p in art['pieces'] if p['elementId'] not in ids]
rows = []
for ident in ids:
    e = entries[ident]
    ref = ROOT / e['referencePng']['file']
    source = Image.open(ref).convert('RGBA')
    assert source.size == (40, 40) and source.getchannel('A').getextrema() == (255, 255)
    a = np.asarray(source)
    water = (a[:, :, 2] > a[:, :, 0]) & (a[:, :, 2] >= a[:, :, 1])
    grass = (a[:, :, 1] > a[:, :, 0]) & (a[:, :, 1] > a[:, :, 2])
    earth = ~(water | grass)
    labels = np.where(water, 0, np.where(grass, 1, 2)).astype(np.uint8)
    final = materials['earth'].copy()
    for name, mask in [('water', water), ('grass', grass)]:
        m = Image.fromarray(mask.astype(np.uint8)*255).resize((160, 160), Image.Resampling.NEAREST)
        final = Image.composite(materials[name], final, m)
    final.putalpha(255)
    target = FAMILY / 'pieces' / f'{ident}-painted-water-shore-v1.png'
    final.save(target)
    binary = {k: e[k] for k in ['binaryPropertyRecord', 'binaryPropertySourceSha256', 'familyMappingStatus',
                                'canDoSpecial', 'canHide', 'unserializedFieldsUnknown']}
    binary['sourceInspection'] = 'references/qqtang-map-data/binary-properties-inspection.json'
    warnings = ['source-image-id-and-client-anchor-unverified',
                'source stepped region boundaries preserved, no artistic smoothing',
                'water-caustic and ground texture joins await validation',
                'soil master warm ochre tone versus source brown requires visual review']
    piece = {'elementId': ident, 'idMapping': 'candidate-filename-inference',
             'file': target.relative_to(ROOT).as_posix(), 'sha256': sha(target),
             'width': 160, 'height': 160, 'worldFrameWidth': 40, 'worldFrameHeight': 40, 'exportDensity': 4,
             'sourceFootprintCells': e['footprintCells'], 'footprintCells': e['footprintCells'],
             'sourceGridAttr': e['gridAttr'], 'sourceMapElemOffset': e['mapElemOffsetRaw'],
             'sourceMapElemOffsetRaw': e['mapElemOffsetRaw'], 'sourceFrameOffsetRaw': e['selectedFrameOffset'],
             'sourceReference': e['referencePng'], 'canHide': None, 'canDoSpecial': None,
             'binaryPropertyEvidence': binary,
             'derivedFrom': records + [{'file': e['referencePng']['file'], 'sha256': sha(ref),
                                       'purpose': 'material-region geometry and alpha only; original RGB never copied'}],
             'operation': {'type': 'source-region-mask-new-texture-image-assembly', 'newModelGeneration': False,
                           'resampled': True, 'sourcePixelColoursReused': False, 'materialSources': records,
                           'sourceLogicalMaskSize': [40, 40], 'sourceMaskResampler': 'NEAREST4x',
                           'maskClassifier': 'water B>R and B>=G; grass G>R and G>B; earth complement',
                           'logicalMaskSha256': hashlib.sha256(labels.tobytes()).hexdigest(),
                           'regionPixels': {'water': int(water.sum()), 'grass': int(grass.sum()), 'earth': int(earth.sum())},
                           'sourceAlphaExtrema': [255, 255]},
             'alphaExtrema': [255, 255], 'terrainOpaqueCanvasVerified': True,
             'geometryAccepted': False, 'visualAccepted': False, 'runtimeAdopted': False,
             'accepted': False, 'inGameAccepted': False, 'seamlessVerified': False,
             'status': 'painted-terrain-composite-awaiting-region-edge-and-runtime-validation', 'warnings': warnings}
    save(Path(str(target)+'.provenance.json'), piece)
    art['pieces'].append(piece)
    rows.append({'elementId': ident, 'file': piece['file'], 'regionPixels': piece['operation']['regionPixels'],
                 'alphaExtrema': [255, 255], 'accepted': False})
art['pieces'].sort(key=lambda p: p['elementId'])
save(manifest, art)
save(OUT / 'exports' / ('terrain-'+'-'.join(map(str, ids))+'.json'),
     {'createdAtUTC': datetime.now(timezone.utc).isoformat(), 'scope': 'current small batch only, no full QA',
      'newGenerations': 0, 'sourceRgbCopied': False, 'materialSources': records, 'items': rows})
print(json.dumps({'family': 'tank', 'candidateCount': len(art['pieces']), 'current': rows, 'accepted': 0}))
