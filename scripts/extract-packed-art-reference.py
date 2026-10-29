"""Decode one to six explicitly named package resources for reference only."""
from pathlib import Path
import hashlib,json,importlib.util,sys
root=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('independent_dimg',root/'scripts/inspect-reference-dimg.py')
d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
requested=sys.argv[1:]
if not 1<=len(requested)<=6:raise ValueError('Select one to six explicit package paths')
package=(root/'.artifacts/reference-inputs/object.pkg').read_bytes();ib=(root/'.artifacts/reference-inputs/object.idx').read_bytes()
ps=hashlib.sha256(package).hexdigest();ix=hashlib.sha256(ib).hexdigest()
if ps!='3f5a8dfe0f629bd8bbd02ea81226f69be968e1e4c5d737ac78439a7221c1188a' or ix!='7f26487ceef121ab4352fab8d26051ddb88c8db8fc591c4ac4f267ac5c6e355e':raise ValueError('Pinned package or index mismatch')
entries={e['path'].replace('\\','/'):e for e in d.parse_index(ib,len(package))['entries']}
folder=root/'references/qqtang-packed-art';folder.mkdir(parents=True,exist_ok=True);rows=[]
for requested_argument in requested:
    requested_path,separator,frame_argument=requested_argument.partition('@')
    entry=entries[requested_path];data,compressed_sha=d.unpack_resource(package,entry);info,frame=d.inspect_dimg(data)
    suffix='-first-visible.png'
    if separator:
        selected=info['frames'][int(frame_argument)]
        if selected.get('empty'):raise ValueError('Explicit frame is empty')
        start=selected['pixelDataOffset'];end=start+selected['pixelByteLength']
        frame={'index':selected['index'],'width':selected['width'],'height':selected['height'],
            'pixels':d.decode_frame_pixels(data[start:end],selected['pixelMode'],selected['width'],selected['height'])}
        suffix=f'-frame-{frame["index"]:03d}.png'
    name=requested_path.replace('/','--').removesuffix('.img')+suffix;out=folder/name
    d.encode_frame(frame,out)
    record={'file':out.relative_to(root).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'sourceArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
        'packagePath':requested_path,'packageSha256':ps,'indexSha256':ix,'entry':entry,
        'resourceSha256':hashlib.sha256(data).hexdigest(),'compressedSha256':compressed_sha,'dimg':info,
        'selectedFrameIndex':frame['index'],'nativeFrameSize':[frame['width'],frame['height']],
        'operation':'independent explicitly selected frame decode without resampling or client composition',
        'referenceOnly':True,'notRuntimeArt':True,'officialOriginalAuthenticity':'unverified'}
    out.with_suffix('.png.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows.append({'file':record['file'],'frameCount':info['frameCount'],'directions':info['directions'],'nativeFrameSize':[frame['width'],frame['height']]})
print(json.dumps(rows))
