"""Decode1–6 explicit encoded-raster representatives from an existing metadata-only contract."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,sys,zipfile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ident=int(sys.argv[1]);indices=[int(a)for a in sys.argv[2:]]
assert 1<=len(indices)<=6 and len(set(indices))==len(indices)
folder=OUT/f'references/world/{ident}'
inspection=json.loads((folder/'metadata/metadata-inspection.json').read_text(encoding='utf-8'))
source=inspection['records'][0];frames=source['metadata']['frames']
assert all(i in [g[0]for g in source['encodedRasterGroups']]for i in indices)
reader_spec=importlib.util.spec_from_file_location('bounded_head_phase_reader',ROOT/'scripts/inspect-reference-dimg.py')
reader=importlib.util.module_from_spec(reader_spec);reader_spec.loader.exec_module(reader)
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as archive:data=archive.read(source['sourceMember'])
assert sha(data)==source['sha256']
written=[]
for index in indices:
    f=frames[index];encoded=data[f['pixelDataOffset']:f['pixelDataOffset']+f['pixelByteLength']]
    assert sha(encoded)==f['encodedPixelSha256']
    pixels=reader.decode_frame_pixels(encoded,f['pixelMode'],f['width'],f['height'])
    image=Image.frombytes('RGBA',(f['width'],f['height']),pixels)
    target=folder/f'frame-{index:03d}.png';image.save(target)
    row={'itemId':ident,'sourceFrameIndex':index,'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target.read_bytes()),
         'nativeFrameSize':[f['width'],f['height']],'frameOffsetRaw':f['frameOffset'],
         'sourceAlphaBBoxAt16':list(image.getchannel('A').point(lambda a:255 if a>=16 else 0).getbbox()),
         'sourceFrameRecord':f,'sourceMember':source['sourceMember'],'sourceSha256':source['sha256'],
         'selection':'explicit representative of encoded-payload/size/mode equality group',
         'frameDurationMs':None,'directionSemantic':None,'referenceOnly':True,'notRuntimeArt':True}
    Path(str(target)+'.source.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    written.append({'index':index,'size':row['nativeFrameSize'],'offset':row['frameOffsetRaw']})
print(json.dumps({'itemId':ident,'decodedExplicitFrames':written,'otherFramesDecoded':False}))
