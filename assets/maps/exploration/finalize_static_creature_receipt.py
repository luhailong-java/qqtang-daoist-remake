"""Small-JSON delivery receipt; never scans or decodes the master inventory."""
from pathlib import Path
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'creatures'
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
art=json.loads((OUT/'art.json').read_text(encoding='utf-8'))
mapping=json.loads((OUT/'identity-mapping.json').read_text(encoding='utf-8'))
survey=json.loads((OUT.parent/'adventure-source-survey/static-survey.json').read_text(encoding='utf-8'))
expected={p['entityId']for p in survey['rules']['entityIds']}
actual={p['entityId']for p in art['masters']}
assert expected==actual and len(art['masters'])==97 and len(mapping['mappedIdentities'])==97
assert all(p['accepted']is False and p['actionsProduced']==[] for p in art['masters'])
assert all((ROOT/p['file']).is_file() and (ROOT/p['generationRecord']).is_file() for p in art['masters'])
classes={k:sum(p.get('entityClass','ordinary')==k for p in art['masters'])for k in ['ordinary','boss','mixed-context']}
assert classes=={'ordinary':70,'boss':26,'mixed-context':1}
art.update({'sourceIdStaticDraftCoverageComplete':True,'staticCandidateCount':97,'fullSetStaticComplete':False,'fullSetActionsComplete':False,'acceptanceNote':'All97 source IDs have static drafts; static acceptance, direction/action sets and runtime verification remain incomplete.'})
save(OUT/'art.json',art)
receipt={'recordedAtUTC':datetime.now(timezone.utc).isoformat(),'inspectionType':'small JSON identity/path existence only; no image decode/scan/hash audit',
         'sourceEntityCount':97,'staticCandidateCount':97,'classes':classes,'missingSourceIds':sorted(expected-actual),'unexpectedIds':sorted(actual-expected),
         'allCurrentPathsExist':True,'allGenerationRecordPathsExist':True,'allAccepted':False,'actionsProduced':0,'runtimeVerification':False,'heavyWorkHoldRespected':True,
         'currentRepairs':[
             {'entityId':30094,'attempts':2,'selected':'v1','result':'v2 and v3 retained isolated upper-right dot, unselected; stop same point after two unsuccessful attempts','status':'pending'},
             {'entityId':30109,'attempts':1,'selected':'v2','result':'displayed ear padding slightly improved, still narrower than requested8%; full alpha bounds not accepted','status':'partial-pending'},
             {'entityId':30040,'attempts':1,'selected':'v2','result':'displayed isolated dot outside right arm removed; full alpha/in-game QA pending','status':'target-improved-not-accepted'},
             {'entityId':30076,'attempts':1,'selected':'v1','result':'v2 still showed floating marks above quill fan; unselected','status':'pending'},
             {'entityId':30077,'attempts':1,'selected':'v2','result':'displayed dot below front claw removed; lateral padding remains narrow and unaccepted','status':'partial-pending'},
             {'entityId':30104,'attempts':1,'selected':'v2','result':'displayed isolated marks around antlers/below feet removed; colored fringe/full alpha still pending','status':'target-improved-not-accepted'}],
         'limitations':['Static coverage is not completed entity art','No direction/frame/action timing established from these masters','No full inventory image decoding, build, runtime test or Git changes performed']}
save(OUT/'static-delivery-receipt.json',receipt)
pending=json.loads((OUT/'visual-pending.json').read_text(encoding='utf-8'))
pending['repairReceipt']='static-delivery-receipt.json'
for p in pending['items']:
    r=next((r for r in receipt['currentRepairs']if r['entityId']==p['entityId']),None)
    if r:p.update({'repairStatus':r['status'],'selectedVersion':r['selected'],'attempts':r['attempts'],'repairObservation':r['result']})
save(OUT/'visual-pending.json',pending)
print(json.dumps({'staticCandidates':97,'classes':classes,'pathChecksOnly':True,'fullArtAccepted':False,'actionsProduced':0}))
