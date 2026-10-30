"""Read one explicit footprint resource; optionally decode <=6 selected frames."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,zipfile

root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('item_id',type=int);ap.add_argument('--state',choices=['stand','walk'],default='stand');ap.add_argument('--frames',nargs='*',type=int,default=[]);args=ap.parse_args()
if len(args.frames)>6 or len(set(args.frames))!=len(args.frames):raise ValueError('Select at most six unique current frames')
catalog=json.loads((root/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
item=next(i for i in catalog['items']if i['item_id']==args.item_id and i['category']=='footprint')
paths=[p for p in item['installed_files']if p.startswith('object/footprint/')and p.endswith('_'+args.state+'.img')]
if len(paths)!=1:raise ValueError('Missing or ambiguous declared footprint state')
member='QQTang-Local/runtime/client-patched/'+paths[0]
with zipfile.ZipFile(root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:data=z.read(member)
spec=importlib.util.spec_from_file_location('footprint_dimg',root/'scripts/inspect-reference-dimg.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
decode=reader.decode_frame_pixels
def refuse(*_a,**_kw):raise RuntimeError('Unexpected eager pixel decode')
reader.decode_frame_pixels=refuse
metadata,_=reader.inspect_dimg(data,metadata_only=True)
folder=root/f'assets/items/footprints/references/world/{args.item_id}';folder.mkdir(parents=True,exist_ok=True)
record={'itemId':args.item_id,'sourceName':item['name'],'state':args.state,'sourceMember':member,'sourceRawSha256':hashlib.sha256(data).hexdigest(),'sourceArchiveSha256':catalog['sourceArchiveSha256'],'metadata':metadata,'referenceOnly':True,'pixelDecodePerformed':False,'inspectedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeTimingKnown':False,'runtimeAccepted':False}
(folder/f'{args.state}.metadata.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected=[]
for index in args.frames:
    if not 0<=index<len(metadata['frames']):raise ValueError('Frame index outside source table')
    f=metadata['frames'][index]
    if f.get('empty'):raise ValueError('Selected frame is structurally empty')
    begin=f['pixelDataOffset'];pixels=decode(data[begin:begin+f['pixelByteLength']],f['pixelMode'],f['width'],f['height'])
    target=folder/f'{args.state}-{index:03d}.png';reader.encode_frame({'index':index,'width':f['width'],'height':f['height'],'pixels':pixels},target)
    evidence={'itemId':args.item_id,'state':args.state,'frameIndex':index,'sourceFrame':f,'sourceMember':member,'sourceRawSha256':record['sourceRawSha256'],'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'referenceOnly':True,'notRuntimeArt':True,'decodedExplicitFramesThisCall':args.frames}
    target.with_suffix('.png.source.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');selected.append(evidence['file'])
print(json.dumps({'itemId':args.item_id,'state':args.state,'frameCount':metadata['frameCount'],'frames':[{'index':f['index'],'size':[f.get('width'),f.get('height')],'empty':f.get('empty',False)}for f in metadata['frames']],'decodedExplicitFrames':args.frames,'selected':selected}))
