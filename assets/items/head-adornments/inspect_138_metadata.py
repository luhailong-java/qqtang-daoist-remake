"""Bounded two-member metadata-only inspection of head item138, no RGBA decode."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import hashlib, importlib.util, json, zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
EXPECTED = '14b9e22c087a32011e845b0c85c3f540566e4a1aa0f1b32ed351b6823a8d46d3'
reader_spec = importlib.util.spec_from_file_location('head138_metadata_reader', ROOT/'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(reader_spec)
reader_spec.loader.exec_module(reader)
def forbidden(*args, **kwargs):
    raise RuntimeError('Metadata-only preparation must never decode RGBA.')
reader.decode_frame_pixels = forbidden
records = []
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as archive:
    for state in ['stand', 'walk']:
        member = f'QQTang-Local/runtime/client-patched/object/thadorn/thadorn36_{state}.img'
        data = archive.read(member)
        assert hashlib.sha256(data).hexdigest() == EXPECTED
        metadata, visible = reader.inspect_dimg(data, metadata_only=True)
        assert visible is None and metadata['pixelDecodePerformed'] is False
        assert not any('decodedRgbaSha256' in f for f in metadata['frames'])
        groups = defaultdict(list)
        poses = defaultdict(list)
        for frame in metadata['frames']:
            key = (frame.get('empty'), frame.get('width'), frame.get('height'), frame.get('pixelMode'), frame.get('encodedPixelSha256'))
            groups[key].append(frame['index'])
            poses[key+(tuple(frame['frameOffset']),)].append(frame['index'])
        records.append({'state':state, 'sourceMember':member, 'sha256':EXPECTED,
                        'byteLength':len(data), 'metadata':metadata,
                        'encodedRasterGroups':list(groups.values()),
                        'encodedPoseGroupsIncludingRawOffset':list(poses.values()),
                        'pixelDecodePerformed':False, 'runtimeUsable':False})
result = {'schemaVersion':1, 'itemId':138, 'createdAtUTC':datetime.now(timezone.utc).isoformat(),
          'mode':'metadata_only', 'sourceKind':'two explicit ZIP loose-client members, object.pkg CLI index does not list these paths',
          'records':records, 'standWalkByteIdentical':records[0]['sha256']==records[1]['sha256'],
          'pixelAlphaValidation':'unknown; encoded payload equality is structural evidence only',
          'directionCardinalOrder':None, 'frameDurationMs':None, 'loop':None,
          'accepted':False, 'runtimeUsable':False}
destination = OUT/'references/world/138/metadata'
destination.mkdir(parents=True,exist_ok=True)
(destination/'metadata-inspection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'itemId':138, 'frames':records[0]['metadata']['frameCount'],
                  'directions':records[0]['metadata']['directions'],
                  'rasterGroups':records[0]['encodedRasterGroups'],
                  'poseGroups':records[0]['encodedPoseGroupsIncludingRawOffset'],
                  'rgbaDecoded':0, 'runtimeUsable':False}))
