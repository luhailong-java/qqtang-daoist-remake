"""Record actual adopted PNG usage separately from prepared appearance references."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
index=read(OUT/'adoption-index.json')
items=read(OUT/'art.json')['items']
used=[]
for ref in index['references']:
    actual=[e for e in items if e.get('identityReference')==ref['file']]
    ref['useState']='used-as-generation-appearance-reference' if actual else 'prepared-reference-only-not-used'
    ref['usedByItemIds']=[e['itemId'] for e in actual]
    ref['newProjectFiles']=[e['file'] for e in actual]
    save(ROOT/(ref['file']+'.adoption.json'),ref)
    if actual:used.append({'slug':ref['slug'],'imageRepoRelative':ref['imageRepoRelative'],'itemIds':ref['usedByItemIds']})
save(OUT/'adoption-index.json',index)
print(json.dumps({'actualUsedReferences':used}))
