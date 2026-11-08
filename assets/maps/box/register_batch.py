"""Save only current remote batch; provenance and uniform source-frame exports."""
from pathlib import Path
from PIL import Image
import sys,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
NODE=Path('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
key,host=sys.argv[1:3];spec=json.loads((OUT/f'batch-{key}.json').read_text(encoding='utf-8'))
source=OUT/f'props-{key}-v1.png';shutil.copyfile(host,source)
refs=[str(OUT/f'references/structure-{key}.png'),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']+spec.get('extraReferences',[])
rel=source.relative_to(ROOT).as_posix();prompt=(OUT/f'batch-{key}.prompt.txt').relative_to(ROOT).as_posix()
subprocess.run([str(NODE),str(ROOT/'scripts/register-generated-image.mjs'),rel,prompt,host,*refs],cwd=ROOT,check=True)
record=source.with_suffix('.png.generation.json');d=json.loads(record.read_text(encoding='utf-8'));d['submittedParameters']['transparent_background']=spec.get('transparent',True);record.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
w,h=Image.open(source).size;cols=spec.get('cols',3);rows=spec.get('rows',2)
items=[]
for n,item in enumerate(spec['items']):
    ident,name,*options=item
    rect=[round(n%cols*w/cols),round(n//cols*h/rows),round((n%cols+1)*w/cols),round((n//cols+1)*h/rows)]
    items.append({'elementId':ident,'name':name,'rect':rect,**(options[0]if options else {})})
export={'family':OUT.name,'source':rel,'items':items};dest=OUT/f'batch-{key}-export.json';dest.write_text(json.dumps(export,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'scripts/export-map-art-batch.py'),str(dest.relative_to(ROOT))],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(OUT/'production_tools.py'),'enrich',str(dest.relative_to(ROOT))],cwd=ROOT,check=True)
