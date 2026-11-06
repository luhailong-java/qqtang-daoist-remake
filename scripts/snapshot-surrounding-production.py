"""Manifest-only production queue for source ear cosmetics; no frame decoding or runtime adoption."""
from pathlib import Path
import json,hashlib,datetime

root=Path(__file__).resolve().parents[1]
catalog_path=root/'references/qqtang-item-data/catalog.json';catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
items=[i for i in catalog['items']if i['category']=='ear']
if len(items)!=catalog['categoryCounts']['ear']:raise ValueError('Source category count mismatch')
current=json.loads((root/'assets/items/surroundings/art.json').read_text(encoding='utf-8'))
by_id={i['itemId']:i for i in current['items']};entries=[]
for index,item in enumerate(items):
    own=by_id.get(item['item_id'])
    metadata_folder=root/f"assets/items/surroundings/references/world/{item['item_id']}"
    metadata_records={}
    for state in ['stand','walk']:
        path=metadata_folder/(state+'.metadata.json')
        if path.is_file():
            record=json.loads(path.read_text(encoding='utf-8'))
            metadata_records[state]={'file':path.relative_to(root).as_posix(),'sourceRawSha256':record['sourceRawSha256'],
                'declaredFrameCount':record['metadata']['frameCount'],'declaredDirections':record['metadata']['directions'],
                'pixelDecodePerformed':record['metadata']['pixelDecodePerformed']}
    entries.append({**item,'productionBatch':chr(ord('a')+index//6),
      'ownDisplayName':own.get('projectDisplayName')if own else None,
      'inventoryCandidate':own['file']if own else None,
      'inventoryCandidatePresent':bool(own and(root/own['file']).is_file()),'inventoryAccepted':False,
      'worldCandidateManifest':None,'worldFrameContractKnown':False,'worldDeclaredMetadata':metadata_records,
      'standWalkRawSha256Equal':(metadata_records['stand']['sourceRawSha256']==metadata_records['walk']['sourceRawSha256'])if len(metadata_records)==2 else None,
      'runtimeAdopted':False})
record={'schemaVersion':1,'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'sourceCatalog':'references/qqtang-item-data/catalog.json','sourceCatalogSha256':hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
 'sourceCategory':'ear','sourceItemCount':len(entries),
 'meaning':'Source category contains surrounding shields, auras, vehicles and body-surrounding appearances; not interpreted as earrings.',
 'inventoryCandidates':sum(x['inventoryCandidatePresent']for x in entries),'inventoryAccepted':0,'worldAccepted':0,
 'worldMetadataItemCount':sum(bool(x['worldDeclaredMetadata'])for x in entries),
 'worldMetadataStateCount':sum(len(x['worldDeclaredMetadata'])for x in entries),
 'standWalkRawIdenticalItemCount':sum(x['standWalkRawSha256Equal']is True for x in entries),
 'nativeHistoricalVersionVerified':False,'entries':entries}
(root/'assets/items/surroundings/source-contract.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k]for k in['sourceItemCount','inventoryCandidates','inventoryAccepted','worldAccepted']}))
