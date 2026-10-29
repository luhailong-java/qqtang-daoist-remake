"""Adopt one explicitly selected existing image portrait; preserve historical records."""
from pathlib import Path
import json,sys,hashlib,shutil,datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];IMAGE=ROOT.parent/'image';slug=sys.argv[1];package=sys.argv[2]if len(sys.argv)>2 else'pets-xianling-20260924'
folder=IMAGE/'designs'/package;source=folder/f'ui/{slug}/portrait_512.png';derived=source.with_suffix('.png.derived.json');generation=folder/f'source/{slug}-E.png.generation.json';review=folder/f'records/{slug}-visual-review.json'
for p in[source,derived,generation,review]:
    if not p.is_file():raise FileNotFoundError(p)
identity=next(e for e in json.loads((folder/'asset-config.json').read_text(encoding='utf-8'))['pets']if e['slug']==slug);target=OUT/f'references/canon/{slug}.png';target.parent.mkdir(exist_ok=True);shutil.copyfile(source,target)
records=[]
for p,suffix in[(derived,'.image-derived.json'),(generation,'.image-generation.json'),(review,'.image-visual-review.json')]:
    dest=target.with_suffix('.png'+suffix);shutil.copyfile(p,dest);records.append({'file':dest.relative_to(ROOT).as_posix(),'imageRepoRelative':p.relative_to(IMAGE).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'context':'historical image package record kept byte-identical; not current generation'})
meta={'slug':slug,'name':identity['name'],'identitySummary':identity['identitySummary'],'file':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'imageRepoRelative':source.relative_to(IMAGE).as_posix(),'imageRepository':'sibling image art repository; remote identity maintained by root association record','operation':'byte-identical reference copy; no resampling or model generation','referenceOnly':True,'purpose':'new-project appearance choice; no historical QQTang-ID mapping and no MMO attributes adopted','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historicalRecords':records}
target.with_suffix('.png.adoption.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');index=OUT/'adoption-index.json';d=json.loads(index.read_text(encoding='utf-8'))if index.exists()else{'schemaVersion':1,'relationship':'new-project-appearance-selection-not-historical-mapping','references':[]};d['references']=[e for e in d['references']if e['slug']!=slug]+[meta];index.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'adopted':slug,'file':meta['file'],'imageRepoRelative':meta['imageRepoRelative']}))
