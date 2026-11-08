"""Register one world-frame mother with its actual submitted references."""
from pathlib import Path
import json,shutil,subprocess,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
key,host=sys.argv[1:3]
register_only='--register-only' in sys.argv[3:]
spec_path=OUT/f'exports/world-{key}.json';spec=json.loads(spec_path.read_text(encoding='utf-8'))
if spec.get('doNotExport'):raise ValueError('Rejected take is retired and must not replace current candidates')
source=ROOT/spec['source'];source.parent.mkdir(parents=True,exist_ok=True)
node='C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if host!='--existing':
    shutil.copyfile(host,source)
    prompt_file=OUT/f'prompts/world-{key}.prompt.txt'
    prompt_text=prompt_file.read_text(encoding='utf-8')
    subprocess.run([node,str(ROOT/'scripts/register-generated-image.mjs'),spec['source'],
                    prompt_text.strip(),host,*spec['referencePaths']],cwd=ROOT,check=True)
    if spec.get('editTarget'):
        subprocess.run([node,str(ROOT/'scripts/mark-generation-edit.mjs'),spec['source'],spec['editTarget']],cwd=ROOT,check=True)
record=Path(str(source)+'.generation.json');d=json.loads(record.read_text(encoding='utf-8'))
d['references'][0]['purpose']='actual decoded source world-frame action board; exact per-frame structure and phase, not runtime source pixels'
for e in d['references'][3:]:
    if spec.get('editTarget') and Path(e['path']).resolve()==(ROOT/spec['editTarget']).resolve():
        e['purpose']='actual AI edit target; correct world silhouette while preserving useful own design'
    else:e['purpose']='own same-item appearance/material reference only; not native world canvas or timing'
d['submittedParameters']['transparent_background']=True
if host!='--existing':
    import hashlib
    d['promptFile']=prompt_file.relative_to(ROOT).as_posix()
    d['promptFileSha256']=hashlib.sha256(prompt_file.read_bytes()).hexdigest()
    d['submittedPromptSha256']=hashlib.sha256(prompt_text.strip().encode('utf-8')).hexdigest()
    d['promptSubmission']='Complete prompt file text, trimmed at beginning/end only; new registrations only'
record.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if not register_only:
    subprocess.run([sys.executable,str(OUT/'export_world_batch.py'),str(spec_path.relative_to(ROOT))],cwd=ROOT,check=True)
