"""Contact sheets of existing rasters only; never paints or changes artwork."""
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


def centre(canvas, source, box):
    left, top, right, low = box
    canvas.alpha_composite(source, (left + (right - left - source.width) // 2,
                                    top + (low - top - source.height) // 2))


out = HERE / 'previews'
out.mkdir(parents=True, exist_ok=True)
records = []
world = read(HERE / 'world-art.json')
inventory = read(HERE / 'art.json')
for theme, color, ink in [('light', (247, 243, 230, 255), 'black'), ('dark', (32, 38, 44, 255), 'white')]:
    picture = Image.new('RGBA', (768, 512), color)
    draw = ImageDraw.Draw(picture)
    inputs = []
    for slot, item in enumerate(inventory['items']):
        cape = Image.open(ROOT / item['file']).convert('RGBA')
        centre(picture, cape, [slot % 3 * 256, slot // 3 * 256 + 20,
                               slot % 3 * 256 + 256, slot // 3 * 256 + 256])
        draw.text((slot % 3 * 256 + 10, slot // 3 * 256 + 8), f'ID{item["itemId"]} / candidate-pending', fill=ink)
        inputs.append({'file': item['file'], 'sha256': item['sha256']})
    draw.text((522, 282), '5 source IDs / inventory only', fill=ink)
    draw.text((522, 304), 'Visual/attachment/timing pending', fill=ink)
    target = out / f'inventory-five-{theme}.png'
    picture.convert('RGB').save(target)
    records.append({'file': target.relative_to(ROOT).as_posix(), 'sha256': sha(target), 'inputs': inputs})
    for entry in world['items']:
        ident = entry['itemId']
        contract = read(HERE / f'references/{ident}/source-contract.json')
        picture = Image.new('RGBA', (1152, 1000), color)
        draw = ImageDraw.Draw(picture)
        draw.text((14, 10), f'ID{ident} / 12 native cropped phases / density4 / CANDIDATE PENDING', fill=ink)
        draw.text((14, 28), 'S=reference-only source at nearest4; N=new candidate at actual density4. No attachment/timing claim.', fill=ink)
        inputs = []
        for frame in entry['frames']:
            index = frame['sourceFrameIndex']
            source = contract['frames'][index]
            left, top = index % 3 * 384, index // 3 * 238 + 48
            draw.text((left + 12, top + 6), f'phase{index} native{source["nativeFrameSize"]} raw{source["frameOffsetRaw"]}', fill=ink)
            draw.text((left + 12, top + 26), f'Envelope deviation {frame["qa"]["relativeAspectDeviation"] * 100:.3f}%', fill=ink)
            old = Image.open(ROOT / source['file']).convert('RGBA')
            old = old.resize((old.width * 4, old.height * 4), Image.Resampling.NEAREST)
            new = Image.open(ROOT / frame['file']).convert('RGBA')
            centre(picture, old, [left + 10, top + 55, left + 187, top + 226])
            centre(picture, new, [left + 197, top + 55, left + 374, top + 226])
            draw.text((left + 15, top + 215), 'S', fill=ink)
            draw.text((left + 202, top + 215), 'N', fill=ink)
            inputs += [{'file': source['file'], 'sha256': source['sha256']},
                       {'file': frame['file'], 'sha256': frame['sha256']}]
        target = out / f'{ident}-source-vs-candidate-{theme}.png'
        picture.convert('RGB').save(target)
        records.append({'file': target.relative_to(ROOT).as_posix(), 'sha256': sha(target), 'inputs': inputs})
(out / 'provenance.json').write_text(json.dumps({'operation': 'Existing source/candidate montage only; no source or candidate pixel editing',
    'visualAccepted': False, 'runtimeAdopted': False, 'files': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'previewFiles': len(records), 'visualAccepted': False}))
