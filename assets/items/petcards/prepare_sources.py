"""Prepare 1–6 explicit static pet-card source references, never a full decode."""
from pathlib import Path
import json, subprocess, sys
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
key, *tokens = sys.argv[1:]
ids = list(map(int, tokens))
assert 1 <= len(ids) <= 6
catalog = json.loads((ROOT/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
items = {e['item_id']: e for e in catalog['items']}
assert all(items[i]['category'] == 'petcard' for i in ids)
missing = [i for i in ids if not (ROOT/f'references/qqtang-item-data/icons/item-{i}.png').exists()]
if missing:
    subprocess.run([sys.executable, str(ROOT/'scripts/extract-item-art-reference.py'), *map(str, missing)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT/'scripts/make-item-structure-board.py'),
                str((OUT/f'references/structure-{key}.png').relative_to(ROOT)), *map(str, ids)], cwd=ROOT, check=True)
(OUT/f'exports/batch-{key}.requirements.json').write_text(json.dumps(
    {'sourceCatalog':'references/qqtang-item-data/catalog.json', 'items':[items[i] for i in ids],
     'scope':'static card icons only; source values retained, new appearances selected explicitly'},
    ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'batch':key,'ids':ids,'scope':'source-reference prep only'}))
