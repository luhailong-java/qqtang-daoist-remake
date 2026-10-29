"""Collect two already-recorded explicit source batches; does not read pixels."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
contexts=[json.loads((OUT/b/'source-context.json').read_text(encoding='utf-8'))for b in['batch-01','batch-02']]
frames=[f for c in contexts for f in c['sourceFrames']]
assert sorted(f['frameIndex']for f in frames)==list(range(11))
groups={}
for f in frames:groups.setdefault(f['canonicalVisibleRGBAHash'],[]).append(f['frameIndex'])
record={'elementId':8017,'sourceRawSHA256':contexts[0]['sourceRawSHA256'],'sourceFrameCount':11,
    'pixelDecodeBatchSizes':[6,5],'all11IndicesInspected':True,'distinctCanonicalVisibleRGBA':len(groups),
    'visiblePixelAliasGroups':[v for v in groups.values()if len(v)>1],
    'canonicalHashDefinition':'40x40 dimensions included; source RGBA with hidden RGB zeroed at alpha==0; existing PNG unchanged',
    'sourceFrameSizes':[f['sourceFrameSize']for f in frames],'sourceFrameOffsets':[f['sourceFrameOffset']for f in frames],
    'sourceMapElemOffset':contexts[0]['sourceMapElemOffset'],'sourceGridAttr':contexts[0]['sourceGridAttr'],
    'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,
    'sourceFrames':frames,'thisAggregationDecodedPixels':False,'runtimeAccepted':False}
(OUT/'source-aggregate.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'indices':len(frames),'distinctVisible':len(groups),'aliasGroups':record['visiblePixelAliasGroups']}))
