"""Small manifest-only progress snapshot; no image decoding or QA claims."""
from pathlib import Path
import json,hashlib,datetime
from collections import Counter
root=Path(__file__).resolve().parents[1]
baseline=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))
definitions={e['elementId']:e for e in baseline['elements']};baseline_count=len(definitions)
binary=json.loads((root/'references/qqtang-map-data/binary-properties-inspection.json').read_text(encoding='utf-8'))
if binary['fieldDifferenceCount'] or binary['sharedPythonDefinitionCount']!=baseline_count:raise ValueError('Supplement source comparison changed')
for ident in binary['additionalIds']:
    family='exploration'if 16201<=ident<=16227 else'tank'if 19030<=ident<=19054 else None
    if family is None or ident in definitions:raise ValueError('Unexpected supplemental definition')
    definitions[ident]={'elementId':ident,'family':family,'definitionSource':'binary-property-supplement'}
family_names=[f['family']for f in baseline['families']]
family_names+=sorted({e['family']for e in definitions.values()}-set(family_names))
families=[];covered=set();foreign=[]
for name in family_names:
    definition_count=sum(e['family']==name for e in definitions.values())
    path=root/f'assets/maps/{name}/art.json';pieces=[];digest=None
    if path.exists():
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest();pieces=json.loads(raw)['pieces']
    ids={p['elementId']for p in pieces if (root/p['file']).is_file()}
    known={ident for ident in ids if ident in definitions and definitions[ident]['family']==name}
    foreign.extend({'manifestFamily':name,'elementId':ident}for ident in ids-known);covered|=known
    families.append({'family':name,'definitionCount':definition_count,'candidateFilesPresent':len(known),
        'pendingCount':definition_count-len(known),'acceptedCount':0,'manifest':str(path.relative_to(root)).replace('\\','/'),
        'manifestSha256':digest,'validation':'JSON membership and file existence only; no image decoding, geometry or visual acceptance'})
items=json.loads((root/'assets/items/art.json').read_text(encoding='utf-8'))['items']
catalog=json.loads((root/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
item_candidates={};painted_item_ids={i['itemId']for i in items if(root/i['file']).is_file()}
for category in ['skills','food','forge','petcards','cards-currency','platform','head-adornments','surroundings','namecard-borders','namecard-borders/inventory','namecard-borders/walk']:
    path=root/f'assets/items/{category}/art.json'
    if path.exists():
        entries=json.loads(path.read_text(encoding='utf-8')).get('items',[])
        present=[i for i in entries if(root/i['file']).is_file()];painted_item_ids|={i['itemId']for i in present}
        item_candidates[category]={'candidateFilesPresent':len({i['itemId']for i in present}),'sourceCategories':dict(Counter(i['category']for i in present)),
            'acceptedCount':0,'manifest':path.relative_to(root).as_posix()}
creature_path=root/'assets/maps/exploration/creatures/art.json'
creatures=json.loads(creature_path.read_text(encoding='utf-8')).get('masters',[])if creature_path.exists()else[]
roster=json.loads((root/'assets/characters/motion-generated/roster-skin-mapping-20261028.json').read_text(encoding='utf-8'))
transforms=json.loads((root/'assets/characters/motion-generated/transformations/manifest.json').read_text(encoding='utf-8'))
battlefield=json.loads((root/'assets/items/battlefield/art.json').read_text(encoding='utf-8'))
effect_clips=[]
for group in ['bubbles','flames','states']:
    manifest=json.loads((root/f'assets/effects/{group}/manifest.json').read_text(encoding='utf-8'))
    effect_clips+=manifest.get('resources',manifest.get('clips',[]))
effect_frames=[f for clip in effect_clips for f in clip['frames']]
portraits=json.loads((root/'assets/characters/portraits-candidates/manifest.json').read_text(encoding='utf-8'))
semantic=json.loads((root/'assets/ui/semantic-extra/manifest.json').read_text(encoding='utf-8'))
head_world=json.loads((root/'assets/items/head-adornments/world-art.json').read_text(encoding='utf-8'))
head_frames=[f for item in head_world['items'] for f in item['frames']]
pickup=json.loads((root/'assets/items/battlefield/animation/manifest.json').read_text(encoding='utf-8'))
pickup_frames=[f for clip in pickup['resources'] for f in clip['frames']]
map_sequences=json.loads((root/'assets/maps/animation-candidates-index.json').read_text(encoding='utf-8'))
record={'schemaVersion':1,'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope':'current lightweight production snapshot; not a replacement for verified production-index or runtime manifests',
    'sourceIdentity':'community-patched-client; Tencent target historical version unverified',
    'baselinePythonMapDefinitionCount':baseline_count,'additionalBinaryMapDefinitionCount':len(binary['additionalIds']),
    'binaryPropertyEvidence':'references/qqtang-map-data/binary-properties-inspection.json',
    'binarySupplementRuntimeImported':False,'binarySupplementUnserializedFields':['canDoSpecial','canHide'],
    'mapDefinitionCount':len(definitions),'mapCandidateFilesPresent':len(covered),'mapPendingFirstPass':len(definitions)-len(covered),
    'mapAcceptedCount':0,'families':families,'foreignOrUnknownManifestIds':foreign,
    'sourceItemRecordCount':len(catalog['items']),'sourceItemCategoryCounts':catalog['categoryCounts'],
    'paintedConsumableIconCandidates':len({i['itemId']for i in items if (root/i['file']).is_file()}),
    'otherItemCategoryCandidates':item_candidates,
    'sourceItemIdsWithAnyCandidate':len(painted_item_ids),
    'itemRepresentationCountCaution':'Inventory icon and nameplate bitmap may represent the same item ID; group counts are not additive.',
    'accountRoleStaticIdentityCandidates':sum((root/s['appearance']['master']).is_file()for s in roster['slots']),
    'temporaryTransformationStaticCandidates':sum((root/s['ownIdentity']['master']).is_file()for s in transforms['entries']),
    'derivedRolePortraitCandidates':sum((root/e['file']).is_file()for e in portraits['entries']),
    'additionalDerivedSemanticUIIcons':sum((root/e['file']).is_file()for e in semantic['entries']),
    'headAdornmentWorldItemCandidates':len(head_world['items']),
    'headAdornmentWorldFullyRecordedResources':sum(len(i['frames'])==i['sourceFrameCount']for i in head_world['items']),
    'headAdornmentWorldPartiallyRecordedResources':sum(len(i['frames'])!=i['sourceFrameCount']for i in head_world['items']),
    'headAdornmentWorldDeclaredFramePositionsForStartedResources':sum(i['sourceFrameCount']for i in head_world['items']),
    'headAdornmentWorldSourceFramePositions':len(head_frames),
    'headAdornmentWorldUniqueReferencedPngFiles':len({f['file']for f in head_frames if(root/f['file']).is_file()}),
    'battlefieldAnimationResources':len(pickup['resources']),
    'battlefieldAnimationSourceFramePositions':len(pickup_frames),
    'battlefieldAnimationUniqueReferencedPngFiles':len({f['file']for f in pickup_frames if f.get('file')and(root/f['file']).is_file()}),
    'mapAnimationCandidateSequenceCount':map_sequences['sequenceCount'],
    'mapAnimationSourceFramePositionsRecorded':map_sequences['sourceFramePositionsRecorded'],
    'newRepresentationAcceptedCount':0,
    'battlefieldSceneMasterCandidates':len({p['sceneId']for p in battlefield['pieces']if(root/p['file']).is_file()}),
    'effectResourceCandidates':len(effect_clips),'effectSourceFrameEntries':len(effect_frames),
    'effectEmptySourceFrameEntries':sum(bool(f.get('empty'))for f in effect_frames),
    'effectUniqueReferencedPngFiles':len({f['file']for f in effect_frames if f.get('file')and(root/f['file']).is_file()}),
    'creatureStaticMasterCandidates':len({i['entityId']for i in creatures if (root/i['file']).is_file()}),
    'consumableIconAcceptedCount':0,'allGameArtComplete':False,
    'localHeavyVerification':'paused by authorized resource coordination; docs/LOCAL_RESOURCE_WINDOW_20261028.md',
    'limitations':['No complete-game percentage: 773 map definitions and 2945 source item records are separate inventories.',
        '721 Python definitions match shared binary fields exactly; 52 additional binary rows have no serialized canDoSpecial or canHide values. Native lookup and target-version authenticity remain unverified.',
        'Candidates may contain known proportion, seam, anchor, alpha, state and animation defects.',
        'Source creature identities, all character actions, costumes, UI states, effects and runtime acceptance remain in production.',
        'assets/maps/production-index.json and runtime-manifests.json remain at their last verified snapshot until coordinated verification resumes.']}
out=root/'docs/ART_PRODUCTION_STATUS_20261028.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k]for k in['mapDefinitionCount','mapCandidateFilesPresent','mapPendingFirstPass','mapAcceptedCount','sourceItemRecordCount','paintedConsumableIconCandidates','allGameArtComplete']}))
