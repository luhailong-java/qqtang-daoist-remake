"""Decode one to six additional property-record image candidates, never game art."""
from pathlib import Path
import hashlib,json,sys,importlib.util,datetime
root=Path(__file__).resolve().parents[1];ids=list(map(int,sys.argv[1:]))
if not 1<=len(ids)<=6:raise ValueError('Explicitly select one to six supplemental map image candidates')
binary=json.loads((root/'references/qqtang-map-data/binary-properties-inspection.json').read_text(encoding='utf-8'))
if binary['fieldDifferenceCount']or binary['sharedPythonDefinitionCount']!=721:raise ValueError('Known-row comparison did not pass')
records={r['id']:r for r in binary['records']if r['id']in binary['additionalIds']}
s=importlib.util.spec_from_file_location('independent_dimg',root/'scripts/inspect-reference-dimg.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
package=(root/'.artifacts/reference-inputs/object.pkg').read_bytes();ib=(root/'.artifacts/reference-inputs/object.idx').read_bytes()
if hashlib.sha256(package).hexdigest()!='3f5a8dfe0f629bd8bbd02ea81226f69be968e1e4c5d737ac78439a7221c1188a' or hashlib.sha256(ib).hexdigest()!='7f26487ceef121ab4352fab8d26051ddb88c8db8fc591c4ac4f267ac5c6e355e':raise ValueError('Package/index pin mismatch')
indexed={e['path'].replace('\\','/').lower():e for e in d.parse_index(ib,len(package))['entries']}
baseline=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'));old_by_sha={e['referencePng']['sha256']:e for e in baseline['elements']if e.get('referencePng')}
folder=root/'references/qqtang-map-data/visual-reference/binary-supplement';folder.mkdir(parents=True,exist_ok=True);index_path=folder/'art-reference-index.json'
out=json.loads(index_path.read_text(encoding='utf-8'))if index_path.exists()else{'schemaVersion':1,'expectedAdditionalDefinitionCount':len(records),'elements':[],
    'sourcePropertyProof':'references/qqtang-map-data/binary-properties-inspection.json','officialOriginalAuthenticity':'unverified','runtimeImported':False}
results=[]
for ident in ids:
    record=records[ident];family,prefix=('exploration',16000)if 16201<=ident<=16227 else('tank',19000)if 19030<=ident<=19054 else(None,None)
    if family is None:raise ValueError('Unrecognized supplemental numeric range')
    candidate=f'object/mapElem/{family}/elem{ident-prefix}_stand.img';entry=indexed.get(candidate.lower())
    if entry is None:raise ValueError(f'No exact indexed candidate path: {candidate}')
    data,compressed_sha=d.unpack_resource(package,entry);info,frame=d.inspect_dimg(data)
    png=folder/'frames'/f'candidate-{ident}.png';png.parent.mkdir(exist_ok=True);d.encode_frame(frame,png);png_sha=hashlib.sha256(png.read_bytes()).hexdigest()
    same=old_by_sha.get(png_sha);group=same['visualGroupId']if same and same['selectedFrameSize']==[frame['width'],frame['height']]else'binary-supplement:'+png_sha
    item={'elementId':ident,'family':family,'familyMappingStatus':'numeric-prefix,exact indexed filename and source-map cooccurrence candidate; native image lookup unverified',
        'candidatePath':entry['path'],'footprintCells':[record['widthCells'],record['heightCells']],'mapElemOffsetRaw':record['offsetRaw'],
        'lifeTime':record['lifeTimeRaw'],'canMove':record['wordAtRecord20'],'level':record['wordAtRecord16'],'gridAttr':record['gridAttrRaw'],
        'canDoSpecial':None,'canHide':None,'unserializedFieldsUnknown':True,'binaryPropertyRecord':record,
        'binaryPropertySourceSha256':binary['sourceSha256'],'selectedFrameSize':[frame['width'],frame['height']],
        'selectedFrameOffset':info['frames'][frame['index']]['frameOffset'],'visualGroupId':group,
        'referencePng':{'file':png.relative_to(root).as_posix(),'sha256':png_sha},'exactExistingReferenceId':same['elementId']if same else None,
        'dimg':info,'compressedStreamSha256':compressed_sha,'referenceOnly':True,'notRuntimeArt':True,'accepted':False}
    png.with_suffix('.png.source.json').write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    out['elements']=[e for e in out['elements']if e['elementId']!=ident];out['elements'].append(item)
    results.append({'id':ident,'candidate':candidate,'size':item['selectedFrameSize'],'exactExistingReferenceId':item['exactExistingReferenceId']})
out['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();out['decodedCandidateCount']=len(out['elements'])
index_path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'supplementReferences':len(out['elements']),'notRuntimeArt':True,'results':results}))
