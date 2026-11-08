"""Four source-confirmed Boss IDs, project-original appearance identities."""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
names={30006:('灵芝盘翁','wide amber-jade lingzhi cap elder with wooden ruyi'),30009:('玉芽藤皇','round layered jade sprout sovereign with curved twig hook'),30012:('玉简匣君','broad ivory-and-jade bamboo-scroll box sovereign with ceremonial whisk'),30014:('云角玉犀','huge-headed pale-jade rhino guardian with rounded stone mallet')}
survey=json.loads((ROOT/'assets/maps/exploration/adventure-source-survey/static-survey.json').read_text(encoding='utf-8'));flags={p['entityId']:p['bossFlags']for p in survey['rules']['entityIds']}
catalog=json.loads((ROOT/'references/qqtang-map-data/catalog.json').read_text(encoding='utf-8'));maps={p['id']:p for p in catalog['entries']}
member='QQTang-Local/configs/adventure-rules.json'
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:raw=z.read(member)
rules=json.loads(raw.decode('utf-8-sig'));rows=[]
for ident,(name,identity)in names.items():
 assert flags[ident]==[True]
 groups=[]
 for m in rules['maps']:
  for g in m.get('npc_drop_groups',[]):
   if g.get('boss_id')!=ident:continue
   assert all(p['is_boss']is True for p in g['combat_profiles'])
   groups.append({'mapId':m['map_id'],'sourceCatalogMapName':maps[m['map_id']]['name'],'sourceMapFile':maps[m['map_id']]['mapFileName'],'sourceGroupUnmodified':g})
 rows.append({'entityId':ident,'entityClass':'boss','originalChineseName':None,'originalAppearanceMapping':'unverified','originalActionIndexMapping':'unverified','projectOriginalChineseIdentityName':name,'projectOriginalIdentityEnglish':identity,'identityMappingType':'project-original-appearance-for-source-confirmed-gameplay-ID','scope':'static-master-only; no phases/actions or runtime implementation claimed','sourceClassification':'Boss in all inspected map combat profiles; no conflict','occurrenceMapCount':len(groups),'sourceMapGroups':groups,'preserveAllSourceGameplayValues':True,'artAddsNoRules':True,'heldObjectPolicy':'visual anticipation/readability only; does not add skill, range, projectile, phase or attribute','accepted':False})
data={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'entityIdNamespace':'adventure-rules.maps.npc_drop_groups.boss_id; distinct from inventory item_id','authorization':'project coordinator relayed human authorization for own creature appearance identities; source gameplay values retained','source':{'member':member,'sha256':hashlib.sha256(raw).hexdigest(),'type':'community-curated-config','officialOriginalAuthenticity':'unverified','archiveRehashedThisPass':False},'mappedIdentities':rows,'fullSetStaticComplete':False,'fullSetActionsComplete':False,'accepted':False}
(OUT/'identity-mapping.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'identities':list(names),'consistentBossFlags':True,'sourceGroupsPreserved':True}))
