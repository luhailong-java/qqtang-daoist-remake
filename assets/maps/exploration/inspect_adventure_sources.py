"""Bounded static ZIP directory and small JSON/index inspection only.

Never runs the community client or decodes image resources. Does not rehash the
large archive during the reserved heavy-job window; records prior pinned hash.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,hashlib,importlib.util,collections
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'adventure-source-survey';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('independent_dimg_reader',ROOT/'scripts/inspect-reference-dimg.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
sha=lambda b:hashlib.sha256(b).hexdigest()
archive=ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip';prefix='QQTang-Local/runtime/client-patched/'
with zipfile.ZipFile(archive)as z:
 names=z.namelist();member='QQTang-Local/configs/adventure-rules.json';b=z.read(member);rules=json.loads(b.decode('utf-8-sig'))
 top={k:{'type':type(v).__name__,'count':len(v)if isinstance(v,(list,dict))else None}for k,v in rules.items()}
 ids=collections.defaultdict(lambda:{'mapIds':set(),'bossFlags':set(),'dropPools':set(),'nameValues':set()})
 def visit(node,map_id=None):
  if isinstance(node,dict):
   map_id=node.get('map_id',map_id)
   if 'boss_id'in node:
    r=ids[node['boss_id']]
    if map_id is not None:r['mapIds'].add(map_id)
    if node.get('drop_pool'):r['dropPools'].add(node['drop_pool'])
    for p in node.get('combat_profiles',[]):r['bossFlags'].add(p.get('is_boss'))
    for key in ['name','boss_name','npc_name','entity_name']:
     if node.get(key):r['nameValues'].add(str(node[key]))
   for v in node.values():visit(v,map_id)
  elif isinstance(node,list):
   for v in node:visit(v,map_id)
 visit(rules)
 idrows=[dict(entityId=k,**{f:sorted(x)for f,x in v.items()})for k,v in sorted(ids.items())]
 idxmember=prefix+'data/object.idx';idxbytes=z.read(idxmember);pkglength=z.getinfo(prefix+'data/object.pkg').file_size;idx=decoder.parse_index(idxbytes,pkglength)
 matching=[e for e in idx['entries']if any(s in e['path'].lower()for s in ['npc','monster','boss','mob','enemy','adventure','devil','pve'])]
 dirnames=[n for n in names if any(s in n.lower()for s in ['monster','boss','npc','mob','enemy','adventure','battlefield'])]
 config_names=[{'member':n,'bytes':z.getinfo(n).file_size}for n in names if n.startswith(prefix+'config/')]
 result={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'archive':str(archive),'archiveSHA256PriorPinned':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7','archiveRehashedThisPass':False,'executedExternalCode':False,'decodedImages':0,'officialOriginalAuthenticity':'unverified-community-patched-client','rules':{'member':member,'bytes':len(b),'sha256':sha(b),'topLevel':top,'entityIds':idrows},'objectIndex':{'member':idxmember,'bytes':len(idxbytes),'sha256':sha(idxbytes),'entryCount':len(idx['entries']),'matchingPaths':matching},'directoryMatches':dirnames,'configDirectory':config_names,'limitations':['Community curated gameplay IDs are not original official identity proof.','Object index keyword match is a candidate, not verified ID→sprite or action mapping.','No PNG or DIMG frame decoded in this pass.']}
 (OUT/'static-survey.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'rulesTopLevel':top,'entityCount':len(idrows),'entityIds':idrows,'objectIndexCount':len(idx['entries']),'matchingPathCount':len(matching),'sampleMatchingPaths':[e['path']for e in matching[:45]],'configNames':config_names[:50],'directoryMatches':dirnames[:30],'report':str(OUT/'static-survey.json')},ensure_ascii=True))
