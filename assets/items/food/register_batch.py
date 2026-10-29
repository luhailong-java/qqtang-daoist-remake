"""Save up to six current generated static catalog icons with faithful provenance."""
from pathlib import Path
from PIL import Image
import json,sys,subprocess,shutil,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];key,host=sys.argv[1:3]
spec_path=OUT/f'exports/batch-{key}.json';spec=json.loads(spec_path.read_text(encoding='utf-8'));source=ROOT/spec['source'];shutil.copyfile(host,source);rel=source.relative_to(ROOT).as_posix()
refs=[str(OUT/f'references/structure-{key}.png'),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png',str(ROOT/'assets/items/items-a-v1.png')]+spec.get('extraReferences',[])
node='C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,str(ROOT/'scripts/register-generated-image.mjs'),rel,f'assets/items/{OUT.name}/prompts/batch-{key}.prompt.txt',host,*refs],cwd=ROOT,check=True)
rp=source.with_suffix('.png.generation.json');d=json.loads(rp.read_text(encoding='utf-8'));d['references'][0]['purpose']='source catalog item functional shape/content reference only; not runtime art';d['references'][3]['purpose']='previous original-painted item material and finish reference';d['submittedParameters']['transparent_background']=spec.get('transparent',True)
for extra in d['references'][4:]:extra['purpose']='previous original-painted same category finish/identity reference'
rp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
w,h=Image.open(source).size
for n,item in enumerate(spec['items']):item['rect']=item.get('manualRect',[round(n%3*w/3),round(n//3*h/2),round((n%3+1)*w/3),round((n//3+1)*h/2)])
spec_path.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');subprocess.run([sys.executable,str(ROOT/'scripts/export-item-art.py'),str(spec_path.relative_to(ROOT))],cwd=ROOT,check=True)
manifest_path=OUT/'art.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));ids={item['itemId']for item in spec['items']}
for item in manifest['items']:
    if item['itemId']not in ids:continue
    reference=ROOT/item['sourceReference'];item['sourceReferenceSha256']=hashlib.sha256(reference.read_bytes()).hexdigest();item['sourceReferenceRecord']=item['sourceReference']+'.source.json';item['scope']='independent static catalog icon; not pet entity, skill effects or animation';item['checksPending']=['functional-content-visual-review','alpha-and-background-review','small-size-readability','runtime-adoption'];(ROOT/(item['file']+'.provenance.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest['items'].sort(key=lambda item:item['itemId']);manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'categoryFolder':OUT.name,'batch':key,'iconCandidates':len(manifest['items']),'accepted':0}))
