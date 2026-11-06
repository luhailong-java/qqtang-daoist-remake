"""Save up to six newly painted static inventory icons, never wearer animation."""
from pathlib import Path
from PIL import Image
import json,sys,subprocess,shutil,hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
key,host=sys.argv[1:3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec_path=OUT/f'exports/batch-{key}.json'
spec=read(spec_path)
assert 1<=len(spec['items'])<=6
source=ROOT/spec['source'];existing=host=='--existing'
if not existing:shutil.copyfile(host,source)
refs=spec['referencePaths']
node='C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if not existing:
    subprocess.run([node,str(ROOT/'scripts/register-generated-image.mjs'),spec['source'],
                    str((OUT/f'prompts/batch-{key}.prompt.txt').relative_to(ROOT)),host,*refs],cwd=ROOT,check=True)
gen=source.with_suffix('.png.generation.json');j=read(gen)
j['references'][0]['purpose']='true inventory icon functional reference only, not object stand/walk or runtime pixels'
j['references'][3]['purpose']='own original inventory art paint finish reference'
for ref in j['references'][4:]:ref['purpose']='own project identity or appearance reference; no historical source identity mapping'
j['submittedParameters']['transparent_background']=spec.get('transparent',True);save(gen,j)
if spec.get('editTarget') and not existing:
    subprocess.run([node,str(ROOT/'scripts/mark-generation-edit.mjs'),spec['source'],spec['editTarget']],cwd=ROOT,check=True)
w,h=Image.open(source).size
for n,e in enumerate(spec['items']):
    e['rect']=[0,0,w,h] if e.get('fullCanvas') else e.get('manualRect',[round(n%3*w/3),round(n//3*h/2),round((n%3+1)*w/3),round((n//3+1)*h/2)])
    e['sourceReference']=f'references/qqtang-item-data/icons/item-{e["itemId"]}-inventory-icon.png'
save(spec_path,spec)
subprocess.run([sys.executable,str(ROOT/'scripts/export-item-art.py'),str(spec_path.relative_to(ROOT))],cwd=ROOT,check=True)
manifest=OUT/'art.json';art=read(manifest);states={e['itemId']:e for e in read(OUT/'source-state-inventory.json')['items']}
ids={e['itemId']for e in spec['items']}
for e in art['items']:
    if e['itemId'] not in ids:continue
    declared=next(p for p in spec['items']if p['itemId']==e['itemId'])
    src=ROOT/e['sourceReference'];record=read(Path(str(src)+'.source.json'))
    e.update({'assetRole':'independent static inventory icon for overhead adornment',
              'scope':'inventory icon only; no wearable world master or complete animation produced',
              'sourceReferenceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),
              'sourceReferenceRecord':e['sourceReference']+'.source.json','sourceResourceKind':record['resourceKind'],
              'sourceNativeInventoryFrameSize':record['nativeFrameSize'],'sourceInventoryFrameOffsetRaw':record['selectedFrameOffset'],
              'worldStateSourceSummary':states[e['itemId']]['worldStates'],
              'worldStaticMasterProduced':False,'completeAnimationProduced':False,'accepted':False,
              'checksPending':['function-and-identity-review','alpha-and-small-size-review','world-master-production','all-original-direction-and-action-frames','client-anchor-and-runtime-adoption']})
    for field in ['projectDisplayName','appearanceChoice','projectIdentity','identityReference','sourceVisualLimitation','sourceEffectHint']:
        if field in declared:e[field]=declared[field]
    if e.get('identityReference'):e['identityReferenceSha256']=hashlib.sha256((ROOT/e['identityReference']).read_bytes()).hexdigest()
    save(ROOT/(e['file']+'.provenance.json'),e)
art['items'].sort(key=lambda e:e['itemId']);save(manifest,art)
print(json.dumps({'category':'thadorn','currentInventoryCandidates':len(art['items']),'worldMasters':0,'completeAnimations':0,'accepted':0}))
