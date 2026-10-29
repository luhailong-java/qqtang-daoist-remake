"""Append original appearance identities from a small project-authored spec."""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,sys
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'creatures'
specpath=ROOT/sys.argv[1];spec=json.loads(specpath.read_text(encoding='utf-8'))
assert 1<=len(spec['identities'])<=4
survey=json.loads((OUT.parent/'adventure-source-survey/static-survey.json').read_text(encoding='utf-8'));source={p['entityId']:p for p in survey['rules']['entityIds']}
catalog=json.loads((ROOT/'references/qqtang-map-data/catalog.json').read_text(encoding='utf-8'));maps={p['id']:p for p in catalog['entries']}
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:rules=json.loads(z.read('QQTang-Local/configs/adventure-rules.json').decode('utf-8-sig'))
path=OUT/'identity-mapping.json';data=json.loads(path.read_text(encoding='utf-8'));existing={p['entityId']for p in data['mappedIdentities']};added=[]
for item in spec['identities']:
 ident=item['entityId'];klass=item['entityClass'];assert klass in ['ordinary','boss'];expected=klass=='boss';assert source[ident]['bossFlags']==[expected]
 if ident in existing:continue
 groups=[]
 for m in rules['maps']:
  for g in m.get('npc_drop_groups',[]):
   if g.get('boss_id')!=ident:continue
   assert all(p['is_boss']is expected for p in g['combat_profiles'])
   groups.append({'mapId':m['map_id'],'sourceCatalogMapName':maps[m['map_id']]['name'],'sourceMapFile':maps[m['map_id']]['mapFileName'],'sourceGroupUnmodified':g})
 data['mappedIdentities'].append({'entityId':ident,'entityClass':klass,'originalChineseName':None,'originalAppearanceMapping':'unverified','originalActionIndexMapping':'unverified','projectOriginalChineseIdentityName':item['name'],'projectOriginalIdentityEnglish':item['identityEnglish'],'identityMappingType':'project-original-appearance-for-source-confirmed-gameplay-ID','scope':'static-master-only; no phases/actions or runtime implementation claimed','sourceClassification':klass+' in all inspected map combat profiles','occurrenceMapCount':len(groups),'sourceMapGroups':groups,'preserveAllSourceGameplayValues':True,'artAddsNoRules':True,'heldObjectPolicy':'visual attack-anticipation identity only; no skill/range/projectile or phase rule added','identityBatchSpec':specpath.relative_to(ROOT).as_posix(),'accepted':False});added.append(ident)
data['selection']='prioritize most frequent source IDs within consistent ordinary/Boss classes; conflicting30087held unconfirmed';data['lastBatchMappedAtUTC']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mappedTotal':len(data['mappedIdentities']),'newIdentities':added,'allSourceGameplayGroupsRetained':True}))
