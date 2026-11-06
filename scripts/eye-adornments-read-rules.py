"""Reread full current rule files before each model call; show changes in full."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];batch=sys.argv[1]
previous=ROOT/'docs/eye-adornments-last-rule-read.json'
old=json.loads(previous.read_text(encoding='utf-8'))if previous.exists()else{}
paths=[Path('D:/work/image/AGENTS.md'),Path('D:/work/image/config/image-generation.json'),Path('D:/work/image/docs/IMAGE_MODEL_POLICY.md')]
records=[]
for p in paths:
    raw=p.read_bytes();text=raw.decode('utf-8-sig');digest=hashlib.sha256(raw).hexdigest()
    changed=old.get(str(p))!=digest
    records.append({'file':str(p),'sha256':digest,'completeTextReadThisCall':True,'unchangedFromPreviousFullRead':not changed})
    print('FILE '+str(p)+' / FULL READ / '+('CHANGED OR FIRST READ'if changed else'CONTENT IDENTICAL'))
    if changed or p.name=='image-generation.json':print(text)
    else:
        for line in text.splitlines():
            if any(x in line for x in['内置','未披露','道家 Q','逐图','付费','参考图','主参考','不放大','不把裁切','共享 Git']):print(line)
    old[str(p)]=digest
record={'batch':batch,'fullFilesReread':records,'configSnapshot':json.loads(paths[1].read_text(encoding='utf-8-sig'))}
(ROOT/f'docs/eye-adornments-{batch}-rules-read.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
previous.write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
