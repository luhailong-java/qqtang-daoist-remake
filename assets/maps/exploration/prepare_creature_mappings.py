"""Four original appearance identities; source gameplay groups copied unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'creatures';OUT.mkdir(exist_ok=True)
names={30082:('苔玉石灵','round square-headed mossy jade stone imp'),30084:('流砂葫芦妖','double-bulb sandy jade gourd imp'),30080:('折叶符灵','folded ivory paper and jade leaf imp'),30086:('螺壳藤精','spiral-shell jade vine snail imp')}
catalog=json.loads((ROOT/'references/qqtang-map-data/catalog.json').read_text(encoding='utf-8'));maps={p['id']:p for p in catalog['entries']}
member='QQTang-Local/configs/adventure-rules.json'
with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:raw=z.read(member)
rules=json.loads(raw.decode('utf-8-sig'));rows=[]
for ident,(name,identity)in names.items():
 groups=[]
 for m in rules['maps']:
  for g in m.get('npc_drop_groups',[]):
   if g.get('boss_id')!=ident:continue
   assert all(p['is_boss']is False for p in g['combat_profiles'])
   groups.append({'mapId':m['map_id'],'sourceCatalogMapName':maps[m['map_id']]['name'],'sourceMapFile':maps[m['map_id']]['mapFileName'],'sourceGroupUnmodified':g})
 rows.append({'entityId':ident,'originalChineseName':None,'originalAppearanceMapping':'unverified','originalActionIndexMapping':'unverified','projectOriginalChineseIdentityName':name,'projectOriginalIdentityEnglish':identity,'identityMappingType':'project-original-appearance-for-source-confirmed-gameplay-ID','scope':'static-master-only; no actions or runtime implementation claimed','sourceClassification':'ordinary entity in all inspected map combat profiles','occurrenceMapCount':len(groups),'sourceMapGroups':groups,'preserveAllSourceGameplayValues':True,'artAddsNoRules':True,'accepted':False})
out={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'authorization':'root coordinator relayed human authorization for own creature appearance identities; original gameplay IDs and values retained','source':{'member':member,'sha256':hashlib.sha256(raw).hexdigest(),'type':'community-curated-config','officialOriginalAuthenticity':'unverified'},'selection':'four IDs with greatest distinct-map occurrence count among97 surveyed IDs and consistently is_boss=false','mappedIdentities':rows,'fullSetStaticComplete':False,'fullSetActionsComplete':False,'accepted':False}
(OUT/'identity-mapping.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'id':p['entityId'],'name':p['projectOriginalChineseIdentityName'],'maps':p['occurrenceMapCount'],'uniqueProfiles':list({json.dumps(g['sourceGroupUnmodified']['combat_profiles'],sort_keys=True)for g in p['sourceMapGroups']})}for p in rows],ensure_ascii=True))
