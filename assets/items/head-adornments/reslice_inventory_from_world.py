"""Two inventory reslices from native painted world mothers, no new generation."""
from pathlib import Path
import json,subprocess,sys,hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior={e['itemId']:e for e in read(OUT/'art.json')['items']}
world={e['itemId']:e for e in read(OUT/'world-art.json')['items']}
copy_fields=['projectDisplayName','sourceReferenceSha256','sourceReferenceRecord','sourceResourceKind',
             'sourceNativeInventoryFrameSize','sourceInventoryFrameOffsetRaw','worldStateSourceSummary',
             'worldStaticMasterProduced','worldFrameCandidatesProduced','worldRepresentationIndex','completeAnimationProduced','worldStatus']
for ident,name in [(42,'three-hearts-world-mother-v2'),(54,'jade-trophy-world-mother-v2')]:
    frame=world[ident]['frames'][0]
    spec={'assetDirectory':'assets/items/head-adornments','source':frame['derivedFrom']['file'],
          'items':[{'itemId':ident,'name':name,'rect':frame['operation']['sourceCellRectLTRB'],
                    'sourceReference':prior[ident]['sourceReference'],'relatedFrameCandidate':frame['file']}]}
    spec_path=OUT/f'exports/inventory-world-{ident}-reslice.json';save(spec_path,spec)
    subprocess.run([sys.executable,str(ROOT/'scripts/export-item-art.py'),str(spec_path.relative_to(ROOT))],cwd=ROOT,check=True)
    doc=read(OUT/'art.json')
    item=next(e for e in doc['items']if e['itemId']==ident)
    for field in copy_fields:
        if field in prior[ident]:item[field]=prior[ident][field]
    item.update({'assetRole':'independent static inventory icon for overhead adornment',
                 'scope':'inventory reslice of original-painted world mother; not the small world export enlarged',
                 'appearanceChoice':'reuse same-item world mother crop after world geometry correction; no new model generation',
                 'accepted':False,'checksPending':['alpha-and-small-size-review','runtime-adoption'],
                 'resliceReason':'remove old stray inventory fragments and keep same-item appearance coherent with world art'})
    save(ROOT/(item['file']+'.provenance.json'),item);save(OUT/'art.json',doc)
    print(json.dumps({'itemId':ident,'file':item['file'],'nativePaintMother':item['derivedFrom']['file'],'newModelGeneration':False}))
