"""Fixed20 raster representatives from the actual24-position contract."""
from pathlib import Path
import json

out=Path(__file__).resolve().parent
root=out.parents[2]
source=json.loads((out/'references/world/114/source-contract.json').read_text(encoding='utf-8'))
selections={'a':[0,1,2,3,4,6],'b':[7,8,9,10,12,13],'c':[14,15,16,18,19,20],'d':[21,22]}
if set(sum(selections.values(),[]))!={g[0]for g in source['encodedRasterGroups']}:
    raise ValueError('Representative selection differs from actual source')
for key,indices in selections.items():
    refs=[str(root/f'assets/items/head-adornments/references/world/114/source-phases-{key}.png').replace('\\','/'),
          str(root/'references/image/01-mail-event.png').replace('\\','/'),str(root/'references/image/team-ui-v2.png').replace('\\','/'),
          str(root/'assets/items/head-adornments/icons/114-rose-silk-garland.png').replace('\\','/')]
    spec={'source':f'assets/items/head-adornments/world/world-114-{key}-v1.png','version':f'114-{key}-v1',
          'referencePaths':refs,'frames':[{'itemId':114,'sourceFrameIndex':index,'sourceReference':source['frames'][index]['file'],
              'nativeFrameSize':source['frames'][index]['nativeFrameSize'],'frameOffsetRaw':source['frames'][index]['frameOffsetRaw']}for index in indices]}
    path=out/f'exports/world-114-{key}.json'
    if path.exists():
        raise ValueError('Keep current manual crop specs; do not overwrite')
    path.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared4 batches,20 distinct rasters;24 original positions stay independent')
