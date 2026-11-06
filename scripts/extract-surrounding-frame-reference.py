"""Decode at most six explicit current cosmetic frames after metadata-only structural inspection."""
from pathlib import Path
import argparse,json,hashlib,zipfile,importlib.util
from PIL import Image

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('item_id',type=int);parser.add_argument('--state',choices=['stand','walk'],required=True);parser.add_argument('--frames',nargs='+',type=int,required=True)
args=parser.parse_args()
if not 1<=len(args.frames)<=6 or len(set(args.frames))!=len(args.frames):raise ValueError('Select one to six unique frame indices')
source_path=root/f'assets/items/surroundings/references/world/{args.item_id}/{args.state}.metadata.json'
record=json.loads(source_path.read_text(encoding='utf-8'))
with zipfile.ZipFile(root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:data=z.read(record['sourceMember'])
if hashlib.sha256(data).hexdigest()!=record['sourceRawSha256']:raise ValueError('Current source no longer matches bounded metadata evidence')
spec=importlib.util.spec_from_file_location('bounded_dimg',root/'scripts/inspect-reference-dimg.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
decode=reader.decode_frame_pixels
def refuse(*_a,**_kw):raise RuntimeError('Unexpected eager decode')
reader.decode_frame_pixels=refuse
metadata,_=reader.inspect_dimg(data,metadata_only=True)
out=source_path.parent/'selected-frames';out.mkdir(exist_ok=True);results=[]
for index in args.frames:
    if not 0<=index<len(metadata['frames']):raise ValueError('Frame out of bounds')
    f=metadata['frames'][index]
    if f.get('empty'):raise ValueError('Explicit frame is structurally empty')
    begin=f['pixelDataOffset'];pixels=decode(data[begin:begin+f['pixelByteLength']],f['pixelMode'],f['width'],f['height'])
    path=out/f'{args.state}-{index:03d}.png';reader.encode_frame({'index':index,'width':f['width'],'height':f['height'],'pixels':pixels},path)
    im=Image.open(path).convert('RGBA');preview=im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST)
    preview_path=out/f'{args.state}-{index:03d}-8x.png';preview.save(preview_path)
    evidence={'referenceOnly':True,'notRuntimeArt':True,'itemId':args.item_id,'state':args.state,'frameIndex':index,
       'sourceRecord':source_path.relative_to(root).as_posix(),'sourceRawSha256':record['sourceRawSha256'],
       'sourceFrame':f,'file':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'nativeSize':list(im.size),'previewFile':preview_path.relative_to(root).as_posix(),
       'previewOperation':'8x nearest inspection enlargement, not new native detail','decodedFrameCountThisCall':len(args.frames)}
    path.with_suffix('.png.source.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results.append(evidence['file'])
print(json.dumps({'itemId':args.item_id,'decodedExplicitFrames':args.frames,'references':results}))
