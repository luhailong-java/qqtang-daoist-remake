"""Append four most frequent, consistently Boss, original appearance mappings."""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'creatures'
names={30088:('镇林木魁','broad tree-stump guardian with wooden ruyi mallet'),30089:('砂鼎铜兽','round bronze tripod cauldron beast with bell clapper'),30090:('玄潮蚌王','wide scallop-shell pearl sovereign with jade folding fan'),30091:('墨羽判使','short crow Daoist magistrate with large ink brush')}
survey=json.loads((OUT.parent/'adventure-source-survey/static-survey.json').read_text(encoding='utf-8'))
selected=sorted([p for p in survey['rules']['entityIds']if p['bossFlags']==[True]],key=lambda p:(-len(p['mapIds']),p['entityId']))[:4]
assert [p['entityId']for p in selected]==list(names)
catalog=json.loads((ROOT/'references/qqtang-map-data/catalog.json').read_text(encoding='utf-8'));maps={p['id']:p for p in catalog['entries']}
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:rules=json.loads(z.read('QQTang-Local/configs/adventure-rules.json').decode('utf-8-sig'))
path=OUT/'identity-mapping.json';data=json.loads(path.read_text(encoding='utf-8'));existing={p['entityId']for p in data['mappedIdentities']}
for ident,(name,identity)in names.items():
 if ident in existing:continue
 groups=[]
 for m in rules['maps']:
  for g in m.get('npc_drop_groups',[]):
   if g.get('boss_id')!=ident:continue
   assert all(p['is_boss']is True for p in g['combat_profiles'])
   groups.append({'mapId':m['map_id'],'sourceCatalogMapName':maps[m['map_id']]['name'],'sourceMapFile':maps[m['map_id']]['mapFileName'],'sourceGroupUnmodified':g})
 data['mappedIdentities'].append({'entityId':ident,'entityClass':'boss','originalChineseName':None,'originalAppearanceMapping':'unverified','originalActionIndexMapping':'unverified','projectOriginalChineseIdentityName':name,'projectOriginalIdentityEnglish':identity,'identityMappingType':'project-original-appearance-for-source-confirmed-gameplay-ID','scope':'static-master-only; no phases/actions or runtime implementation claimed','sourceClassification':'Boss in all inspected map combat profiles; conflicting30087excluded','occurrenceMapCount':len(groups),'sourceMapGroups':groups,'preserveAllSourceGameplayValues':True,'artAddsNoRules':True,'heldObjectPolicy':'visual attack-anticipation identity only; does not establish skill/range/projectile or phase rules','accepted':False})
data['selection']='first batch four most frequent consistent ordinary IDs; second batch four most frequent consistent Boss IDs; conflict30087excluded'
data['bossBatchMappedAtUTC']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'id':p['entityId'],'name':p['projectOriginalChineseIdentityName'],'maps':[g['mapId']for g in p['sourceMapGroups']],'profiles':list({json.dumps(g['sourceGroupUnmodified']['combat_profiles'],sort_keys=True)for g in p['sourceMapGroups']})}for p in data['mappedIdentities']if p.get('entityClass')=='boss'],ensure_ascii=True))
