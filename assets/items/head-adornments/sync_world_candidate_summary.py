"""Update owned small metadata summaries after actual world frame exports."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
world=read(OUT/'world-art.json')
counts={}
for item in world['items']:
    frames=item['frames']
    xmin=min(f['frameOffsetRaw'][0]for f in frames)
    ymin=min(f['frameOffsetRaw'][1]for f in frames)
    xmax=max(f['frameOffsetRaw'][0]+f['logicalFrameSize'][0]for f in frames)
    ymax=max(f['frameOffsetRaw'][1]+f['logicalFrameSize'][1]for f in frames)
    item['rawOffsetPlusSizeEnvelope']=[xmin,ymin,xmax,ymax]
    item['rawEnvelopeSize']=[xmax-xmin,ymax-ymin]
    item['envelopeInterpretation']='arithmetic offset+size only; native origin/sign not verified'
    item['sourceStatePlaybackTimingShared']=None
    counts[item['itemId']]=len(frames)
    for frame in frames:
        frame['positionWithinRawEnvelope']=[frame['frameOffsetRaw'][0]-xmin,frame['frameOffsetRaw'][1]-ymin]
        save(ROOT/frame.get('provenanceRecord',frame['file']+'.provenance.json'),frame)
save(OUT/'world-art.json',world)
for filename,key in [('source-state-inventory.json','items'),('art.json','items')]:
    doc=read(OUT/filename)
    for item in doc[key]:
        if item['itemId']not in counts:continue
        item['worldStaticMasterProduced']=True
        item['worldFrameCandidatesProduced']=counts[item['itemId']]
        item['worldRepresentationIndex']='assets/items/head-adornments/world-art.json'
        item['completeAnimationProduced']=False
        item['worldStatus']='declared frame candidates present; timing, geometry and runtime not accepted'
        if filename=='art.json':save(ROOT/(item['file']+'.provenance.json'),item)
    if filename=='source-state-inventory.json':
        doc['headerSummary'].update({'worldStaticMastersProduced':len(counts),'worldFrameCandidatesProduced':sum(counts.values()),'completeAnimationsProduced':0})
    save(OUT/filename,doc)
p=OUT/'README.md'
s=p.read_text(encoding='utf-8')
s=s.replace('当前35项世界master及完整动画均未制作。按协调安排优先单独制作42的2帧1方向及54的4帧1方向，用真实world动作帧/各自尺寸/rawOffset，不能借256背包画布充当世界尺寸，不增造方向。源帧时序未知，挂点坐标系/符号和客户端应用方式待证，未经批准不接运行。',
'''当前42的2帧1方向、54的4帧1方向已产生新世界帧候选，共6帧；world-art.json单独记录，原始尺寸×4、rawOffset和源顺序保留。42包含正面/侧边，54含四高光及偏移起伏。首稿杯比例约11%偏宽，B实际编辑后改善至约1.65%—2.04%；爱心约1.30%—1.36%，仍未验收。挂点合同见docs/HEAD_ATTACHMENT_CONTRACT.md。其余33项没有世界表示；所有时序/原点/符号、当前角色头节点和实机仍未知，完整动画与运行批准仍无。''')
p.write_text(s,encoding='utf-8')
print(json.dumps({'worldFrameCandidates':sum(counts.values()),'items':counts,'accepted':0,'runtimeAdopted':False}))
