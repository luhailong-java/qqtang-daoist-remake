"""Record one source-confirmed entity without overriding its per-map Boss flags."""
from pathlib import Path
from datetime import datetime, timezone
import json, zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'creatures'
survey = json.loads((OUT.parent/'adventure-source-survey/static-survey.json').read_text(encoding='utf-8'))
source = next(x for x in survey['rules']['entityIds'] if x['entityId'] == 30087)
assert source['bossFlags'] == [False, True]
catalog = {x['id']:x for x in json.loads((ROOT/'references/qqtang-map-data/catalog.json').read_text(encoding='utf-8'))['entries']}
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as archive:
    rules = json.loads(archive.read('QQTang-Local/configs/adventure-rules.json').decode('utf-8-sig'))
groups = []
for entry in rules['maps']:
    for group in entry.get('npc_drop_groups', []):
        if group.get('boss_id') != 30087:
            continue
        assert all(type(p['is_boss']) is bool for p in group['combat_profiles'])
        map_id = entry['map_id']
        groups.append({'mapId':map_id, 'sourceCatalogMapName':catalog[map_id]['name'], 'sourceMapFile':catalog[map_id]['mapFileName'], 'sourceGroupUnmodified':group})
assert {p['is_boss'] for g in groups for p in g['sourceGroupUnmodified']['combat_profiles']} == {False, True}
path = OUT/'identity-mapping.json'
data = json.loads(path.read_text(encoding='utf-8'))
assert not any(x['entityId'] == 30087 for x in data['mappedIdentities'])
data['mappedIdentities'].append({
    'entityId':30087, 'entityClass':'mixed-context', 'originalChineseName':None,
    'originalAppearanceMapping':'unverified', 'originalActionIndexMapping':'unverified',
    'projectOriginalChineseIdentityName':'云篆卷灵',
    'projectOriginalIdentityEnglish':'warm ivory scroll spirit with broad rolled ends, jade face patch, tiny short body and wooden ruler',
    'identityMappingType':'project-original-appearance-for-source-confirmed-gameplay-ID',
    'scope':'static-master-only; no phases/actions or runtime implementation claimed',
    'sourceClassification':'is_boss differs between source map combat profiles; no single global ordinary/Boss classification assigned',
    'sourceBossFlags':[False, True], 'globalBossClassificationConfirmed':False,
    'occurrenceMapCount':len(groups), 'sourceMapGroups':groups,
    'preserveAllSourceGameplayValues':True, 'artAddsNoRules':True,
    'heldObjectPolicy':'visual identity only; no skill/range/projectile or phase rule added',
    'identityBatchSpec':'assets/maps/exploration/creatures/mixed-01.spec.json', 'accepted':False
})
data['selection']='all97 source entity IDs mapped; 30087 retains mixed-context classification and unmodified per-map profiles'
data['lastBatchMappedAtUTC']=datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mappedTotal':len(data['mappedIdentities']),'entityId':30087,'entityClass':'mixed-context','mapCount':len(groups),'flagsPreserved':[False,True]}))
