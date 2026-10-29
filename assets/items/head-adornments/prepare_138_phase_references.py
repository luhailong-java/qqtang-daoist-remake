"""Decode only1–6 explicitly selected138 source phases, never the full24-frame set."""
from pathlib import Path
from PIL import Image
import hashlib, importlib.util, json, sys, zipfile

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
indices=[int(a)for a in sys.argv[1:]]
assert 1<=len(indices)<=6 and len(set(indices))==len(indices)
metadata_path=OUT/'references/world/138/metadata/metadata-inspection.json'
inspection=json.loads(metadata_path.read_text(encoding='utf-8'))
source=inspection['records'][0]
frames=source['metadata']['frames']
assert all(i in [0,1,2,6,7,8,12,13,14] for i in indices)
reader_spec=importlib.util.spec_from_file_location('head138_phase_reader',ROOT/'scripts/inspect-reference-dimg.py')
reader=importlib.util.module_from_spec(reader_spec);reader_spec.loader.exec_module(reader)
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as archive:
    data=archive.read(source['sourceMember'])
assert sha(data)==source['sha256']
folder=OUT/'references/world/138'
written=[]
for index in indices:
    frame=frames[index]
    encoded=data[frame['pixelDataOffset']:frame['pixelDataOffset']+frame['pixelByteLength']]
    assert sha(encoded)==frame['encodedPixelSha256']
    pixels=reader.decode_frame_pixels(encoded,frame['pixelMode'],frame['width'],frame['height'])
    image=Image.frombytes('RGBA',(frame['width'],frame['height']),pixels)
    target=folder/f'frame-{index:03d}.png';image.save(target)
    row={'itemId':138,'sourceFrameIndex':index,'file':target.relative_to(ROOT).as_posix(),
         'sha256':sha(target.read_bytes()),'nativeFrameSize':[frame['width'],frame['height']],
         'frameOffsetRaw':frame['frameOffset'],'sourceAlphaBBoxAt16':list(image.getchannel('A').point(lambda a:255 if a>=16 else 0).getbbox()),
         'sourceFrameRecord':frame,'sourceMember':source['sourceMember'],'sourceSha256':source['sha256'],
         'selection':'explicit representative of encoded-payload/size/mode equality group',
         'frameDurationMs':None,'directionSemantic':None,'referenceOnly':True,'notRuntimeArt':True}
    Path(str(target)+'.source.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    written.append({'index':index,'size':row['nativeFrameSize'],'offset':row['frameOffsetRaw']})
print(json.dumps({'decodedExplicitFrames':written,'otherFramesDecoded':False}))
