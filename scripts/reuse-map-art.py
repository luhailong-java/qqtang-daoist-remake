"""Explicitly reuse an existing painting only for identical decoded source art."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[1]
arguments=sys.argv[1:];extra=[value[8:]for value in arguments if value.startswith('--extra=')]
if len(extra)>1:raise ValueError('Use at most one supplemental inventory')
family,ident,source_family,source_ident=[value for value in arguments if not value.startswith('--extra=')];ident=int(ident);source_ident=int(source_ident)
index=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))
elements={item['elementId']:item for item in index['elements']}
if extra:
    for item in json.loads((root/extra[0]).read_text(encoding='utf-8'))['elements']:
        if item['elementId']in elements:raise ValueError('Supplement cannot replace a baseline definition')
        elements[item['elementId']]=item
target_element=elements[ident];source_element=elements[source_ident]
if target_element['family']!=family or source_element['family']!=source_family:raise ValueError('Element/family mismatch')
if target_element['visualGroupId']!=source_element['visualGroupId'] or target_element['selectedFrameSize']!=source_element['selectedFrameSize']:
    raise ValueError('Source visible content/frame extent is not identical; cannot infer reuse from names')
source_manifest=json.loads((root/'assets/maps'/source_family/'art.json').read_text(encoding='utf-8'))
painting=next(item for item in source_manifest['pieces']if item['elementId']==source_ident)
if hashlib.sha256((root/painting['file']).read_bytes()).hexdigest()!=painting['sha256']:raise ValueError('Painting file hash mismatch')
origins=painting.get('derivedFrom',{});origins=origins if isinstance(origins,list)else[origins]
generation=next((item['generationRecord']for item in origins if item.get('generationRecord')),None)
if not generation:raise ValueError('Painting lacks generation source chain')
source_record=painting.get('provenanceRecord')or next((painting['file']+suffix for suffix in['.provenance.json','.source.json']if(root/(painting['file']+suffix)).is_file()),None)
folder=root/'assets/maps'/family;folder.mkdir(parents=True,exist_ok=True);record_path=folder/'reuse'/f'{ident}-from-{source_ident}.json';record_path.parent.mkdir(exist_ok=True)
record={'elementId':ident,'file':painting['file'],'sha256':painting['sha256'],'width':painting['width'],'height':painting['height'],
    'worldFrameWidth':painting['worldFrameWidth'],'worldFrameHeight':painting['worldFrameHeight'],'exportDensity':painting['exportDensity'],
    'sourceFootprintCells':target_element['footprintCells'],'sourceMapElemOffset':target_element['mapElemOffsetRaw'],
    'sourceGridAttr':target_element['gridAttr'],'provenanceRecord':record_path.relative_to(root).as_posix(),
    'derivedFrom':{'file':painting['file'],'sha256':painting['sha256'],'generationRecord':generation,'sourceRecord':source_record},
    'operation':{'type':'explicit-existing-paint-visible-alias-reuse','newModelGeneration':False,'resampled':False,
        'sourceElementId':source_ident,'identicalSourceVisualGroup':target_element['visualGroupId'],
        'sourceNativeFrameSize':target_element['selectedFrameSize'],'pixelFileDuplicated':False,'targetRulesRetained':True},
    'geometryAccepted':False,'accepted':False,'seamlessVerified':False,'status':'painted-visible-alias-candidate-awaiting-in-game-validation'}
if target_element.get('binaryPropertyRecord'):
    record['binaryPropertyEvidence']={key:target_element.get(key)for key in['binaryPropertyRecord','binaryPropertySourceSha256','familyMappingStatus','canDoSpecial','canHide','unserializedFieldsUnknown']}
    record['binaryPropertyEvidence']['sourceInspection']='references/qqtang-map-data/binary-properties-inspection.json'
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest_path=folder/'art.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))if manifest_path.exists()else{'schemaVersion':1,'tilePixels':40,'status':'production-candidates','pieces':[]}
manifest['pieces']=[item for item in manifest['pieces']if item['elementId']!=ident];manifest['pieces'].append(record)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'target':ident,'source':source_ident,'sharedFile':painting['file'],'accepted':False}))
