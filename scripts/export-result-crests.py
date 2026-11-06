"""Inspect or export manually separated outcome crests; no new image generation."""
from pathlib import Path
from PIL import Image, ImageDraw
import argparse
import hashlib
import json

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--cuts', nargs=2, type=int)
args = parser.parse_args()
folder = root / 'assets/ui/results'
source = folder / 'result-crests-v1.png'
image = Image.open(source).convert('RGBA')
alpha = image.getchannel('A')
mask = alpha.point(lambda value: 255 if value >= 8 else 0)
w, h = image.size
ivory = Image.new('RGBA', image.size, '#f8f2df')
ivory.alpha_composite(image)
qa = root / 'qa'
qa.mkdir(exist_ok=True)
ivory.convert('RGB').save(qa / 'result-crests-native-ivory.png')
blank = [x for x in range(w) if not mask.crop((x, 0, x + 1, h)).getbbox()]
runs = []
for x in blank:
    if runs and runs[-1][1] == x - 1:
        runs[-1][1] = x
    else:
        runs.append([x, x])
print(json.dumps({'nativeSize': [w, h], 'alphaExtrema': alpha.getextrema(), 'alpha8BBox': mask.getbbox(), 'blankColumns': runs}))
if args.cuts is None:
    raise SystemExit()
edges = [0, *args.cuts, w]
if edges != sorted(set(edges)):
    raise ValueError('Invalid manual cuts')
entries = []
for index, (ident, label) in enumerate((('victory', '胜利'), ('draw', '平局'), ('defeat', '再接再厉'))):
    rect = [edges[index], 0, edges[index + 1], h]
    piece = image.crop(rect)
    a = piece.getchannel('A').point(lambda value: 255 if value >= 8 else 0)
    pw, ph = piece.size
    if any(a.crop(edge).getbbox() for edge in ((0, 0, 1, ph), (pw - 1, 0, pw, ph), (0, 0, pw, 1), (0, ph - 1, pw, ph))):
        raise ValueError('Visible pixels cut: ' + ident)
    box = a.getbbox()
    crop = piece.crop(box)
    scale = min(448 / crop.width, 448 / crop.height)
    size = tuple(round(v * scale) for v in crop.size)
    resized = crop.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
    output = Image.new('RGBA', (512, 512))
    output.alpha_composite(resized, ((512 - size[0]) // 2, (512 - size[1]) // 2))
    target = folder / (ident + '.png')
    output.save(target)
    entries.append({'id': ident, 'label': label, 'file': target.relative_to(root).as_posix(),
                    'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'width': 512, 'height': 512,
                    'sourceCellRect': rect, 'contentBoxInCell': list(box), 'uniformScale': scale,
                    'operation': 'crop and premultiplied-alpha LANCZOS uniform fit',
                    'newModelGeneration': False, 'visualAccepted': False, 'runtimeVisualAccepted': False})
manifest = {'schemaVersion': 1, 'source': source.relative_to(root).as_posix(),
            'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'nativeSize': [w, h],
            'generationRecord': 'assets/ui/results/result-crests-v1.png.generation.json',
            'manualColumnCuts': args.cuts, 'sourceVisiblePixelsCrossingCuts': 0, 'entries': entries,
            'runtimeUse': 'src/result-art.js and showResult in src/app.js; server outcome determines state',
            'visualAccepted': False, 'completeGameArt': False}
(folder / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
contact = Image.new('RGB', (3 * 220, 300), '#f8f2df')
draw = ImageDraw.Draw(contact)
for index, entry in enumerate(entries):
    icon = Image.open(root / entry['file']).convert('RGBA')
    for size, top in ((144, 0), (112, 152)):
        thumb = icon.convert('RGBa').resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
        contact.paste(thumb, (index * 220 + (220 - size) // 2, top), thumb)
    draw.text((index * 220 + 30, 280), entry['id'] + ' 144/112px', fill='#205349')
contact.save(qa / 'result-crests-display-contact.png')
print(json.dumps({'exported': [e['file'] for e in entries], 'nativeDimensionsPreserved': True, 'newModelGeneration': False}))
