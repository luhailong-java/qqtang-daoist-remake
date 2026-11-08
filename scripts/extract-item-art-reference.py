"""Read a pinned community item catalog and a bounded set of standalone icons.

Never executes the downloaded client. Decodes only image bytes through this
project's independent DIMG reader. All retained PNGs are reference-only.
"""
from pathlib import Path
import hashlib,json,zipfile,importlib.util,sys
from collections import Counter
from PIL import Image
root=Path(__file__).resolve().parents[1]
module_spec=importlib.util.spec_from_file_location('independent_dimg_reader',root/'scripts/inspect-reference-dimg.py')
decoder=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(decoder)
archive=root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip';member='QQTang-Local/runtime/patches/item-resource-index.json'
folder=root/'references/qqtang-item-data';folder.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive)as package:
    catalog_bytes=package.read(member)
    if hashlib.sha256(catalog_bytes).hexdigest()!='aaef2410d597a9342ad690d166c164354ac8e96657d9bda9ca3f0235452fe098':raise ValueError('Item catalog bytes differ from inspected source')
    original=json.loads(catalog_bytes.decode('utf-8-sig'))
    catalog={'schemaVersion':1,'sourceType':'community-patched-client-resource-restoration-index',
        'officialOriginalAuthenticity':'unverified','sourceArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
        'sourceMember':member,'sourceMemberSha256':hashlib.sha256(catalog_bytes).hexdigest(),
        'itemConfigVersion':original['item_config_version'],'commodityConfigVersion':original['commodity_config_version'],
        'categoryCounts':dict(Counter(item['category']for item in original['items'])),
        'items':[{key:item.get(key)for key in['item_id','category','resource_id','name','description','installed_files']}for item in original['items']]}
    catalog_path=folder/'catalog.json';catalog_text=json.dumps(catalog,ensure_ascii=False,indent=2)+'\n'
    if not catalog_path.exists()or catalog_path.read_text(encoding='utf-8')!=catalog_text:catalog_path.write_text(catalog_text,encoding='utf-8')
    inventory_icon='--inventory-icon'in sys.argv[1:]
    declared_reference='--declared-frames-reference'in sys.argv[1:]
    selected_arguments=[value for value in sys.argv[1:]if value.startswith('--frame=')]
    if len(selected_arguments)>1:raise ValueError('Select at most one explicit source frame per call')
    selected_index=int(selected_arguments[0].split('=',1)[1])if selected_arguments else None
    state_arguments=[value for value in sys.argv[1:]if value.startswith('--state=')]
    if len(state_arguments)>1:raise ValueError('Select at most one installed object state')
    state=state_arguments[0].split('=',1)[1]if state_arguments else None
    if state not in [None,'stand','walk','trigger']or(inventory_icon and state):raise ValueError('Unsupported or conflicting resource selection')
    ids=[int(value)for value in sys.argv[1:]if value not in ['--inventory-icon','--declared-frames-reference']and not value.startswith(('--frame=','--state='))]
    if not 1<=len(ids)<=6:raise ValueError('Decode one to six explicitly selected icons')
    records=[]
    for ident in ids:
        item=next(item for item in original['items']if item['item_id']==ident)
        relative=next(path for path in item['installed_files']if path.lower().endswith('.img')and(not inventory_icon or path.lower().startswith('res/uires/icon/'))and(not state or path.lower().endswith('_'+state+'.img')))
        path='QQTang-Local/runtime/client-patched/'+relative
        data=package.read(path);decoded,frame=decoder.inspect_dimg(data,reference_only_version65537_suffix=declared_reference)
        if selected_index is not None:
            if not 0<=selected_index<len(decoded['frames']):raise ValueError('Selected frame out of range')
            selected=decoded['frames'][selected_index]
            if selected.get('empty'):raise ValueError('Selected source frame is empty')
            begin=selected['pixelDataOffset'];end=begin+selected['pixelByteLength']
            frame={'index':selected_index,'width':selected['width'],'height':selected['height'],
                'pixels':decoder.decode_frame_pixels(data[begin:end],selected['pixelMode'],selected['width'],selected['height'])}
        suffix=('-inventory-icon'if inventory_icon else'-'+state if state else'')+(f'-frame-{selected_index:03d}'if selected_index is not None else'')
        png=folder/'icons'/f'item-{ident}{suffix}.png';png.parent.mkdir(exist_ok=True)
        decoder.encode_frame(frame,png)
        record={'itemId':ident,'category':item['category'],'name':item['name'],'file':png.relative_to(root).as_posix(),
            'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'sourceMember':path,'sourceSha256':hashlib.sha256(data).hexdigest(),
            'nativeFrameSize':[frame['width'],frame['height']],'sourceFrameIndex':frame['index'],
            'sourceFrameCount':decoded['frameCount'],'referenceOnly':True,'notRuntimeArt':True,'officialOriginalAuthenticity':'unverified'}
        record['selectedFrameOffset']=decoded['frames'][frame['index']]['frameOffset']
        record['dimg']=decoded
        if decoded.get('referenceOnlyOpaqueVersionedSuffix'):
            record['completeContainerFormatVerified']=False
            record['referenceScope']='Explicit declared-frame-only inspection of version65537 with hashed opaque suffix; not a complete-format or native-runtime verification'
            record['communityFormatEvidence']={'url':'https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/itemcatalog/dimg.go#L231',
                'gitBlobSha':'c8e5e7a22c12ec18e63068b18f224497b5157f01','caution':'Community parser permits version65537 suffixes; independent native usage and suffix meaning remain unverified'}
        record['resourceKind']='explicit inventory icon'if inventory_icon else'explicit installed '+state if state else'first installed IMG; may be object stand rather than inventory icon'
        png.with_suffix('.png.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');records.append(record)
print(json.dumps({'catalogItems':len(catalog['items']),'decodedItems':[record['itemId']for record in records],'referenceOnly':True}))
