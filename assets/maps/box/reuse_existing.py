"""Explicit same-reference-picture paint reuse; metadata lookup and file copy only."""
from pathlib import Path
import json,hashlib,copy,shutil
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
inventory={p['elementId']:p for p in read(ROOT/'assets/maps/production-index.json')['elements']}
source={k:v for k,v in inventory.items()if v['family']==OUT.name}
families={inventory[e['referencePng']['representativeElementId']]['family']for e in source.values()}
available={}
for family in sorted(families-{OUT.name}):
    file=ROOT/f'assets/maps/{family}/art.json'
    if not file.is_file():continue
    for p in read(file)['pieces']:
        e=inventory[p['elementId']];key=(e['referencePng']['sha256'],tuple(e['selectedFrameSize']))
        available.setdefault(key,p)
manifest=read(OUT/'art.json')if(OUT/'art.json').exists()else{'schemaVersion':1,'tilePixels':40,'status':'production-candidates','pieces':[]}
have={p['elementId']for p in manifest['pieces']};reused=[]
for ident,e in source.items():
    if ident in have:continue
    original=available.get((e['referencePng']['sha256'],tuple(e['selectedFrameSize'])))
    if not original:continue
    before=ROOT/original['file']
    if sha(before)!=original['sha256']:raise ValueError('Source painted candidate hash mismatch')
    path=OUT/'pieces'/f'{ident}-shared-painted-candidate.png';shutil.copyfile(before,path);piece=copy.deepcopy(original)
    piece.update({'elementId':ident,'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'sourceReference':e['referencePng'],'footprintCells':e['footprintCells'],'sourceFootprintCells':e['footprintCells'],'sourceGridAttr':e['gridAttr'],'sourceMapElemOffsetRaw':e['mapElemOffsetRaw'],'sourceFrameOffsetRaw':e['selectedFrameOffsetRaw'],'crossFamilyPaintedReuseOfElementId':original['elementId'],'geometryAccepted':False,'accepted':False,'status':'same-source-picture-cross-family-paint-reuse-candidate-awaiting-validation'})
    piece['operation']={'type':'same-reference-sha-and-frame-explicit-cross-family-paint-reuse','sourcePaintedFile':original['file'],'sourcePaintedSha256':original['sha256'],'sourcePaintedProvenance':original['file']+'.provenance.json'if(ROOT/(original['file']+'.provenance.json')).exists()else original['file']+'.source.json','referenceImageSha256':e['referencePng']['sha256'],'resampled':False,'newModelGeneration':False}
    write(path.with_suffix('.png.provenance.json'),piece);manifest['pieces'].append(piece);reused.append({'elementId':ident,'fromElementId':original['elementId']})
manifest['pieces'].sort(key=lambda p:p['elementId']);write(OUT/'art.json',manifest)
print(json.dumps({'family':OUT.name,'newReused':reused,'total':len(manifest['pieces']),'pending':[ident for ident in source if ident not in{p['elementId']for p in manifest['pieces']}]}))
