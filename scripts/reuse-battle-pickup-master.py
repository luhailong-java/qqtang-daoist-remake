"""Share one own painting only when two full source DIMG resources match bytes."""
from pathlib import Path
import copy,hashlib,json,sys
root=Path(__file__).resolve().parents[1]
target_id,source_id=map(int,sys.argv[1:])
folder=root/'assets/items/battlefield';path=folder/'art.json'
manifest=json.loads(path.read_text(encoding='utf-8'))
painting=next(p for p in manifest['pieces']if p['sceneId']==source_id)
source=json.loads((root/painting['sourceRecord']).read_text(encoding='utf-8'))
target_record=f'references/qqtang-packed-art/object--item--item{target_id}_stand-first-visible.png.source.json'
target=json.loads((root/target_record).read_text(encoding='utf-8'))
if source['resourceSha256']!=target['resourceSha256']or source['nativeFrameSize']!=target['nativeFrameSize']:raise ValueError('Source resources differ; no inferred visual reuse')
if hashlib.sha256((root/painting['file']).read_bytes()).hexdigest()!=painting['sha256']:raise ValueError('Master hash changed')
record=copy.deepcopy(painting);record.update(sceneId=target_id,sourceRecord=target_record,
    sourceFirstFrame=next(f for f in target['dimg']['frames']if not f.get('empty')),
    sourceAnimationFrameCount=target['dimg']['frameCount'])
if target_id==62:record.update(displayName='碧息补给',semanticCandidate='oxygen-value increment; separate scene ID retained')
else:record.update(displayName=f'同源拾取物{target_id}',semanticCandidate='not independently verified')
record['operation']={'type':'explicit-byte-identical-full-source-resource-visible-reuse','sourceSceneId':source_id,
    'sourceDimgSha256':source['resourceSha256'],'sourceMasterRecord':painting['file']+'.provenance.json',
    'newModelGeneration':False,'resampled':False,'pixelFileDuplicated':False,'targetSceneRulesRetained':True}
record['sourceResourceEqualityVerified']=True
provenance=folder/'reuse'/f'{target_id}-from-{source_id}.json';provenance.parent.mkdir(exist_ok=True)
record['provenanceRecord']=provenance.relative_to(root).as_posix()
provenance.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest['pieces']=[p for p in manifest['pieces']if p['sceneId']!=target_id];manifest['pieces'].append(record)
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'targetSceneId':target_id,'sourceSceneId':source_id,'sameWholeSourceResource':True,'fileDuplicated':False,'accepted':False}))
