"""Link only actually used image identities, leaving pet-card records untouched."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
items=read(OUT/'art.json')['items']
prior=read(ROOT/'assets/items/petcards/adoption-index.json')['references']
refs=[]
for ref in prior:
    use=[e for e in items if e.get('identityReference')==ref['file']]
    if not use:continue
    row={**ref,'useState':'used-as-generation-appearance-reference',
         'usedByItemIds':[e['itemId']for e in use],'newProjectFiles':[e['file']for e in use],
         'scope':'overhead-adornment static inventory icon only; wearable masters and animations not produced'}
    refs.append(row)
doc={'schemaVersion':1,'relationship':'new-project-appearance-selection-not-historical-mapping','references':refs}
(OUT/'adoption-index.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actualUsedReferences':[{'slug':e['slug'],'itemIds':e['usedByItemIds']}for e in refs]}))
