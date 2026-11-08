"""Inherit known edge evidence for an identical PNG binding; no image read."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
path=OUT/'sequence.json';sequence=json.loads(path.read_text(encoding='utf-8'))
source=next(f for f in sequence['frames']if f['sourceFrameIndex']==0)
target=next(f for f in sequence['frames']if f['sourceFrameIndex']==2)
for density,folder in [('1','frames-logical-x1'),('4','frames-compatible-x4')]:
    old=source['exports'][density];binding=target['exports'][density]
    assert binding['file']==old['file'] and binding['sha256']==old['sha256']
    binding.update({'alpha8BBox':old['alpha8BBox'],'alpha8EdgeCount':old['alpha8EdgeCount'],'alpha8EvidenceInheritedFromIdenticalPNG':True})
    (OUT/folder/'frame-002.binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path.write_text(json.dumps(sequence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Only alias2 JSON inherits identical PNG0 alpha8 evidence; no pixels decoded or files regenerated.')
