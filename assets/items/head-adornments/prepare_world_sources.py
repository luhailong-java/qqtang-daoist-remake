"""Decode the explicit small 2/4-frame world contracts; never load a client."""
from pathlib import Path
from PIL import Image
import json,zipfile,importlib.util,hashlib,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ident=int(sys.argv[1]);assert ident in [42,54]
catalog=json.loads((ROOT/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
entry=next(e for e in catalog['items']if e['item_id']==ident)
assert entry['category']=='thadorn'
mod=importlib.util.spec_from_file_location('bounded_world_dimg',ROOT/'scripts/inspect-reference-dimg.py')
decoder=importlib.util.module_from_spec(mod);mod.loader.exec_module(decoder)
sha=lambda data:hashlib.sha256(data).hexdigest()
folder=OUT/f'references/world/{ident}';folder.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as package:
    paths={s:'QQTang-Local/runtime/client-patched/'+next(p for p in entry['installed_files']if p.endswith('_'+s+'.img'))for s in ['stand','walk']}
    data=package.read(paths['stand']);walk=package.read(paths['walk'])
assert data==walk
decoded,_=decoder.inspect_dimg(data)
assert decoded['version']==65536 and decoded['directions']==1 and decoded['frameCount']==(2 if ident==42 else 4)
frames=[]
for f in decoded['frames']:
    assert not f.get('empty')
    pixels=decoder.decode_frame_pixels(data[f['pixelDataOffset']:f['pixelDataOffset']+f['pixelByteLength']],f['pixelMode'],f['width'],f['height'])
    image=Image.frombytes('RGBA',(f['width'],f['height']),pixels)
    target=folder/f'frame-{f["index"]:03d}.png';image.save(target)
    row={'itemId':ident,'sourceFrameIndex':f['index'],'directionIndex':0,'directionSemantic':None,
         'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target.read_bytes()),
         'nativeFrameSize':[f['width'],f['height']],'frameOffsetRaw':f['frameOffset'],
         'sourceAlphaBBoxAt16':list(image.getchannel('A').point(lambda a:255 if a>=16 else 0).getbbox()),
         'sourceFrameRecord':f,'frameDurationMs':None,'sourceTimingStatus':'not supplied by inspected DIMG',
         'sourceMembers':paths,'sourceSha256':sha(data),'referenceOnly':True,'notRuntimeArt':True}
    Path(str(target)+'.source.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    frames.append(row)
doc={'itemId':ident,'sourceName':entry['name'],'sourceDescription':entry['description'],
     'sourceMembers':paths,'sourceSha256':sha(data),'standWalkByteIdentical':True,'sourceDimg':decoded,
     'completeContainerLayoutParsed':True,'officialAuthenticity':'unverified community client',
     'frameOrder':[f['sourceFrameIndex']for f in frames],'directions':1,'directionSemantic':None,
     'frameDurationMs':None,'loop':None,'frames':frames,'referenceOnly':True,'notRuntimeArt':True}
(folder/'source-contract.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'itemId':ident,'frames':[{'index':f['sourceFrameIndex'],'size':f['nativeFrameSize'],'offset':f['frameOffsetRaw']}for f in frames],'directions':1,'timing':None,'referenceOnly':True}))
