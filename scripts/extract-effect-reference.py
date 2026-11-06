"""Read at most six literal effect records; never execute downloaded code.

The zero-padded magic filename association remains a numeric-name candidate,
not proof of the original renderer's lookup. Decoded PNGs are reference-only.
"""
from pathlib import Path
import ast,hashlib,json,zipfile,re,importlib.util,sys
root=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('independent_dimg',root/'scripts/inspect-reference-dimg.py')
d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
names=sys.argv[1:]
if not 1<=len(names)<=6 or any(not re.fullmatch(r'[A-Za-z0-9_]+',n)for n in names):raise ValueError('Select one to six literal effect basenames')
folder=root/'references/qqtang-effect-data';folder.mkdir(parents=True,exist_ok=True)
package=(root/'.artifacts/reference-inputs/object.pkg').read_bytes()
index_bytes=(root/'.artifacts/reference-inputs/object.idx').read_bytes()
if hashlib.sha256(package).hexdigest()!='3f5a8dfe0f629bd8bbd02ea81226f69be968e1e4c5d737ac78439a7221c1188a':raise ValueError('Package digest mismatch')
if hashlib.sha256(index_bytes).hexdigest()!='7f26487ceef121ab4352fab8d26051ddb88c8db8fc591c4ac4f267ac5c6e355e':raise ValueError('Index digest mismatch')
index=d.parse_index(index_bytes,len(package));by_path={e['path'].lower():e for e in index['entries']};decoded_paths=set();results=[]
with zipfile.ZipFile(root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:
    for name in names:
        member=f'QQTang-Local/runtime/client-patched/effect/{name}.eff';raw=z.read(member)
        if len(raw)>128*1024:raise ValueError('Effect text exceeds bounded literal size')
        literal=ast.literal_eval(raw.decode('gb18030'));resources=[]
        for part in literal[1]:
            descriptor=part[0];resource=descriptor[1][0]
            if resource not in resources:resources.append(resource)
        record={'effect':name,'sourceMember':member,'sourceSha256':hashlib.sha256(raw).hexdigest(),
            'sourceArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
            'operation':'ast.literal_eval of bounded tuple/list data only; no execution',
            'officialOriginalAuthenticity':'unverified','literal':literal,'resourceNames':resources,'visualReferenceCandidates':[]}
        for resource in resources:
            match=re.fullmatch(r'magic(\d+)',resource)
            if not match:continue
            candidate=f'object\\magic\\magic{int(match[1]):04d}.img'
            if candidate not in by_path:continue
            entry=by_path[candidate]
            if candidate not in decoded_paths:
                if len(decoded_paths)>=6:raise ValueError('Maximum six image decodes per invocation')
                data,compressed_sha=d.unpack_resource(package,entry);info,frame=d.inspect_dimg(data)
                image_path=folder/f'{Path(candidate.replace(chr(92),"/")).stem}-first-visible.png'
                d.encode_frame(frame,image_path)
                source={'file':image_path.relative_to(root).as_posix(),'sha256':hashlib.sha256(image_path.read_bytes()).hexdigest(),
                    'packagePath':candidate,'packageSha256':hashlib.sha256(package).hexdigest(),'resourceSha256':hashlib.sha256(data).hexdigest(),
                    'compressedStreamSha256':compressed_sha,'firstVisibleFrameIndex':frame['index'],'nativeFrameSize':[frame['width'],frame['height']],
                    'dimg':info,'referenceOnly':True,'notRuntimeArt':True,
                    'effectNameLookup':'numeric resource-name association only; original client resolution unverified'}
                image_path.with_suffix('.png.source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                decoded_paths.add(candidate)
            record['visualReferenceCandidates'].append({'effectResourceName':resource,'packagePath':candidate,'lookupVerified':False})
        (folder/f'{name}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        results.append({'effect':name,'resourceNames':resources,'candidateImages':len(record['visualReferenceCandidates'])})
print(json.dumps(results))
