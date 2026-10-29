"""Refresh explicitly identical-source aliases after parent paint/crop replacement."""
from pathlib import Path
import json,copy,shutil,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
index={e['elementId']:e for e in read(ROOT/'assets/maps/production-index.json')['elements']};manifest=read(OUT/'art.json');painted={p['elementId']:p for p in manifest['pieces']};refreshed=[]
for ident,before in list(painted.items()):
    parent=before.get('sourcePictureAliasOfElementId')
    if parent is None:continue
    e=index[ident];src=painted[parent]
    if index[parent]['referencePng']['sha256']!=e['referencePng']['sha256']or index[parent]['selectedFrameSize']!=e['selectedFrameSize']:raise ValueError('Alias reference mismatch')
    path=ROOT/before['file'];shutil.copyfile(ROOT/src['file'],path);p=copy.deepcopy(src)
    p.update({'elementId':ident,'file':before['file'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sourceReference':e['referencePng'],'footprintCells':e['footprintCells'],'sourceFootprintCells':e['footprintCells'],'sourceGridAttr':e['gridAttr'],'sourceMapElemOffsetRaw':e['mapElemOffsetRaw'],'sourceFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourcePictureAliasOfElementId':parent,'accepted':False,'geometryAccepted':False})
    p['operation']={'type':'same-source-picture-original-paint-reuse','newModelGeneration':False,'resampled':False,'sourcePaintedFile':src['file'],'sourcePaintedSha256':src['sha256']};painted[ident]=p;write(path.with_suffix('.png.provenance.json'),p);refreshed.append(ident)
manifest['pieces']=[painted[key]for key in sorted(painted)];write(OUT/'art.json',manifest);print(json.dumps({'refreshedAliases':refreshed}))
