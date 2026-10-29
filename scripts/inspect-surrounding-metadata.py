"""Bounded, inert DIMG metadata read for explicit source ear IDs. Never executes client or decodes pixels."""
from pathlib import Path
import argparse,json,hashlib,zipfile,importlib.util

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('ids',nargs='+',type=int)
parser.add_argument('--state',choices=['stand','walk'],required=True)
parser.add_argument('--reference-version65537-suffix',action='store_true')
args=parser.parse_args()
if not 1<=len(args.ids)<=6 or len(set(args.ids))!=len(args.ids):raise ValueError('Select one to six distinct IDs')
catalog=json.loads((root/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
by_id={i['item_id']:i for i in catalog['items']if i['category']=='ear'}
if any(i not in by_id for i in args.ids):raise ValueError('Unknown source ear ID')
spec=importlib.util.spec_from_file_location('inert_dimg_metadata',root/'scripts/inspect-reference-dimg.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def refuse_pixels(*_a,**_kw):raise RuntimeError('Pixel decoding is forbidden in metadata-only inspection')
reader.decode_frame_pixels=refuse_pixels
archive=root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
if archive.stat().st_size!=288298460:raise ValueError('Previously hashed pinned archive size changed')
records=[]
with zipfile.ZipFile(archive)as package:
    for ident in args.ids:
        item=by_id[ident]
        matches=[p for p in item['installed_files']if p.startswith('object/ear/')and p.endswith('_'+args.state+'.img')]
        if len(matches)!=1:raise ValueError('Source state is not uniquely installed')
        member='QQTang-Local/runtime/client-patched/'+matches[0]
        data=package.read(member)
        decoded,visible=reader.inspect_dimg(data,metadata_only=True,reference_only_version65537_suffix=args.reference_version65537_suffix)
        if visible is not None or decoded['pixelDecodePerformed']:raise ValueError('Unexpected pixel decode')
        record={'sourceItemId':ident,'sourceCategory':'ear','sourceResourceId':item['resource_id'],'sourceName':item['name'],
          'state':args.state,'sourceMember':member,'sourceRawSha256':hashlib.sha256(data).hexdigest(),
          'sourceArchiveIdentity':'Previously pinned SHAfd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7; size rechecked, not rehashed in this bounded read.',
          'inspection':'metadata-only, no RGBA decode, source image retained only as pinned archive data',
          'nativeTimingMs':None,'directionSemantics':None,'headOrBodyAttachment':None,'runtimeUsable':False,'metadata':decoded}
        folder=root/f'assets/items/surroundings/references/world/{ident}';folder.mkdir(parents=True,exist_ok=True)
        (folder/(args.state+'.metadata.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        other='walk'if args.state=='stand'else'stand'
        other_path=folder/(other+'.metadata.json')
        if other_path.is_file():
            prior=json.loads(other_path.read_text(encoding='utf-8'))
            alias={'sourceItemId':ident,'standAndWalkRawSha256Equal':prior['sourceRawSha256']==record['sourceRawSha256'],
                'records':['stand.metadata.json','walk.metadata.json'],
                'evidence':'Independent SHA256 of complete raw installed DIMG bytes in each explicit state read; no pixel decoding.',
                'nativeStateMeaningVerified':False,'runtimeUsable':False}
            (folder/'state-alias.json').write_text(json.dumps(alias,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        records.append({'itemId':ident,'state':args.state,'frameCount':decoded['frameCount'],'directions':decoded['directions']})
print(json.dumps({'pixelDecodePerformed':False,'records':records}))
