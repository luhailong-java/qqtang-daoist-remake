"""Derived 64px/40px QA board, not new model art or a runtime screenshot."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import datetime

root = Path(__file__).resolve().parents[1]
entries = json.loads((root / 'assets/items/eye-adornments/art.json').read_text(encoding='utf-8'))['items']
if len(entries) != 72:
    raise ValueError('Complete72 candidate category required')
board = Image.new('RGB', (12 * 136, 6 * 160), '#f8f2df')
draw = ImageDraw.Draw(board)
inputs = []
for index, entry in enumerate(entries):
    source = root / entry['file']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != entry['sha256']:
        raise ValueError('Input changed')
    image = Image.open(source).convert('RGBA')
    x, y = index % 12 * 136, index // 12 * 160
    draw.rectangle((x, y, x + 135, y + 159), outline='#d8c9a0')
    for size, top in ((64, 4), (40, 76)):
        thumb = image.resize((size, size), Image.Resampling.LANCZOS)
        board.paste(thumb, (x + (136 - size) // 2, y + top), thumb)
    draw.text((x + 12, y + 122), str(entry['itemId']) + ' 64/40px', fill='#205349')
    inputs.append({'itemId': entry['itemId'], 'file': entry['file'], 'sha256': digest})
target = root / 'qa/eye-adornments-small-size.png'
board.save(target)
record = {'file': target.relative_to(root).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'createdAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sizes': [64, 40],
          'operation': 'RGBA LANCZOS resize and ivory composite for inspection', 'inputs': inputs,
          'newModelGeneration': False, 'runtimeScreenshot': False, 'visualAccepted': False}
target.with_suffix('.png.source.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: value for key, value in record.items() if key != 'inputs'}))
