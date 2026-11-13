"""Compose existing inventory/mobile/source rasters only, no artwork painting."""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


items = read(HERE / 'art.json')['items']
out = HERE / 'previews'
out.mkdir(parents=True, exist_ok=True)
records = []
for theme, color, ink in [('light', (247, 243, 230, 255), 'black'), ('dark', (32, 38, 44, 255), 'white')]:
    normal = Image.new('RGBA', (768, 572), color)
    mobile = Image.new('RGBA', (768, 360), color)
    comparison = Image.new('RGBA', (1536, 600), color)
    nd, md, cd = ImageDraw.Draw(normal), ImageDraw.Draw(mobile), ImageDraw.Draw(comparison)
    normal_inputs, mobile_inputs, source_inputs = [], [], []
    for slot, item in enumerate(items):
        ident = item['itemId']
        cx, cy = slot % 3 * 256, slot // 3 * 286
        nd.text((cx + 10, cy + 8), f'ID{ident} / inventory256 / PENDING', fill=ink)
        normal.alpha_composite(Image.open(ROOT / item['file']).convert('RGBA'), (cx, cy + 26))
        normal_inputs.append({'file': item['file'], 'sha256': item['sha256']})
        mx, my = slot % 3 * 256, slot // 3 * 180
        md.text((mx + 10, my + 8), f'ID{ident} / actual mobile pixels', fill=ink)
        for variant in item['mobileVariants']:
            size = variant['width']
            pos = (mx + 18, my + 58) if size == 64 else (mx + 128, my + 42)
            mobile.alpha_composite(Image.open(ROOT / variant['file']).convert('RGBA'), pos)
            md.text((pos[0], my + 146), f'{size}px / pending', fill=ink)
            mobile_inputs.append({'file': variant['file'], 'sha256': variant['sha256']})
        sx, sy = slot % 3 * 512, slot // 3 * 300
        cd.text((sx + 10, sy + 8), f'ID{ident} / S=source physical reference; N=own candidate pending', fill=ink)
        source_path = HERE / f'references/{ident}/inventory-physical-reference.png'
        source = Image.open(source_path).convert('RGBA')
        enlarged = source.resize((source.width * 4, source.height * 4), Image.Resampling.NEAREST)
        comparison.alpha_composite(enlarged, (sx + (256 - enlarged.width) // 2, sy + 40 + (240 - enlarged.height) // 2))
        comparison.alpha_composite(Image.open(ROOT / item['file']).convert('RGBA'), (sx + 256, sy + 32))
        cd.text((sx + 10, sy + 276), 'S / blue UI pixels are reference-only', fill=ink)
        cd.text((sx + 270, sy + 276), 'N / no world phases claimed', fill=ink)
        source_inputs += [{'file': rel(source_path), 'sha256': sha(source_path)},
                          {'file': item['file'], 'sha256': item['sha256']}]
    for name, picture, inputs in [('inventory-six', normal, normal_inputs), ('mobile-six', mobile, mobile_inputs),
                                   ('source-vs-candidate', comparison, source_inputs)]:
        target = out / f'{name}-{theme}.png'
        picture.convert('RGB').save(target)
        records.append({'file': rel(target), 'sha256': sha(target), 'inputs': inputs})
(out / 'provenance.json').write_text(json.dumps({'operation': 'existing raster composition only; mobile sprites displayed at actual64/96',
    'files': records, 'worldCandidatePositions': 0, 'visualAccepted': False, 'runtimeAdopted': False},
    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'previews': len(records), 'selectedInventoryIds': [i['itemId'] for i in items], 'worldCandidatePositions': 0}))
