"""Inspect1–3 explicit head items' stand/walk metadata; forbid all RGBA decoding."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import hashlib,importlib.util,json,sys,zipfile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ids=[int(x)for x in sys.argv[1:]]
assert 1<=len(ids)<=3 and len(set(ids))==len(ids)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
headers=read(OUT/'source-state-inventory.json')
reader_spec=importlib.util.spec_from_file_location('bounded_head_metadata',ROOT/'scripts/inspect-reference-dimg.py')
reader=importlib.util.module_from_spec(reader_spec);reader_spec.loader.exec_module(reader)
def forbidden(*args,**kwargs):raise RuntimeError('metadata_only must not decode pixels')
reader.decode_frame_pixels=forbidden
reports=[]
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as archive:
    for ident in ids:
        item=next(x for x in headers['items']if x['itemId']==ident)
        records=[]
        assert len(item['worldStates'])==2
        for source in item['worldStates']:
            data=archive.read(source['sourceMember'])
            assert hashlib.sha256(data).hexdigest()==source['sourceSha256']
            assert len(data)==source['byteLength']
            metadata,image=reader.inspect_dimg(data,metadata_only=True)
            assert image is None and metadata['pixelDecodePerformed']is False
            assert not any('decodedRgbaSha256'in f for f in metadata['frames'])
            raster=defaultdict(list);poses=defaultdict(list)
            for f in metadata['frames']:
                key=(f['empty'],f.get('width'),f.get('height'),f.get('pixelMode'),f.get('encodedPixelSha256'))
                raster[key].append(f['index']);poses[key+(tuple(f['frameOffset']),)].append(f['index'])
            records.append({'state':source['state'],'sourceMember':source['sourceMember'],
                            'sha256':source['sourceSha256'],'byteLength':len(data),'metadata':metadata,
                            'encodedRasterGroups':list(raster.values()),'encodedPoseGroupsIncludingRawOffset':list(poses.values()),
                            'pixelDecodePerformed':False,'runtimeUsable':False})
        doc={'schemaVersion':1,'itemId':ident,'sourceName':item['sourceName'],'sourceDescription':item['sourceDescription'],
             'createdAtUTC':datetime.now(timezone.utc).isoformat(),'mode':'metadata_only',
             'sourceKind':'two explicit ZIP loose-client members, SHA matched prior bounded source headers',
             'records':records,'standWalkByteIdentical':records[0]['sha256']==records[1]['sha256'],
             'pixelAlphaValidation':'unknown; encoded payload equality is structural evidence only',
             'directionCardinalOrder':None,'frameDurationMs':None,'loop':None,'accepted':False,'runtimeUsable':False}
        destination=OUT/f'references/world/{ident}/metadata';destination.mkdir(parents=True,exist_ok=True)
        (destination/'metadata-inspection.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        reports.append({'itemId':ident,'sourceName':item['sourceName'],'frameCount':records[0]['metadata']['frameCount'],
                        'directions':records[0]['metadata']['directions'],'rasterGroupCount':len(records[0]['encodedRasterGroups']),
                        'poseGroupCount':len(records[0]['encodedPoseGroupsIncludingRawOffset']),
                        'representatives':[g[0]for g in records[0]['encodedRasterGroups']],'rgbaDecoded':0})
print(json.dumps(reports,ensure_ascii=False))
