"""Aggregate recorded candidate batches only; no image decoding or runtime writes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
records=[];frames=[]
for batch in['batch-01','batch-02']:
    path=OUT/batch/'sequence.json';record=json.loads(path.read_text(encoding='utf-8'));frames+=record['frames']
    records.append({'batch':batch,'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'selectedNativeAtlas':record['selectedNativeAtlas'],'actualNativeAtlasSize':record['actualNativeAtlasSize'],'sourceFrameIndices':record['sourceFrameIndices']})
assert sorted(f['sourceFrameIndex']for f in frames)==list(range(11))
result={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':8017,'family':'bun',
    'sourceDeclaredFrameCount':11,'sourceDeclaredDirections':1,'sourceFrameIndices':list(range(11)),
    'sourceResourcePath':'object\\mapElem\\bun\\elem17_stand.img','sourceRawSHA256':'be9dc2c44925bd64864ecf6468eb43519ec31c4acbbfee0ef496d42f6e28d018',
    'sourceFrameSize':[40,40],'sourceMapElemOffset':[0,0],'sourceFootprintCells':[1,1],'sourceGridAttr':[3855],
    'sourceFrameOffsetsPreservedIndividually':True,'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,
    'allSourceFramePositionsHaveCandidates':True,'ownRepresentativeFramesGenerated':11,'frameBindingsProduced':11,
    'uniqueOwnRGBAFrames':{str(d):len({f['exports'][str(d)]['decodedRGBAHashForOwnExport']for f in frames})for d in[1,4]},
    'sourcePixelDecodeBatchSizes':[6,5],'thisAggregationDecodedPixels':False,'nativeAtlasBatches':records,'frames':frames,
    'sourceAndOwnAlphaExtrema':[255,255],'alphaNormalizationPerformed':False,'interiorSquareSearchPerformed':False,
    'nativeAtlasWholeCellsOnly':True,'uniformPMAResizeOnly':True,'componentsMovedOrSynthesizedByCode':False,
    'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'seamlessVerified':False,'runtimeIntegrated':False,
    'mainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,
    'pending':['batch-01 source0 band position remains visibly lower than source; some rail cross-seam positions differ','cross-phase surface crack/detail and lighting stability unaccepted','exact center-band and side-rail coordinates require focused repair; no automatic strip shifting used','seams to neighboring map tiles unverified','native source lookup/timing/state meaning/loop/combined origin remain unknown']}
(OUT/'sequence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('# 8017 十一帧位原创候选\n\n源0–10共11帧已分6+5两个必要小批实际核图，canonical visible RGBA十一种各不相同，无可复用源像素。每源帧40×40、frameOffset[0,0]，mapElemOffset[0,0]和GridAttr3855原样独立保留，组合原点/时序/loop/帧状态语义均null。\n\n首批整套选batch-01/sequence-v3.png，后批选batch-02/sequence-v1.png；均真实原生1536×1024、每格512²。后批第六格是无source index的灰色排版占位，明确未导出。全部40²和160²是原生完整方格等比PMA派生，alpha255，无alpha规范化或透明立物fit；每张及模型/时间/来源记录在各批。目标Sunburst/max，实际型号/质量null。\n\n11/11仅指不同源帧位均有自有绘制候选，所有accepted/geometry/stateCorrespondence/seamless/runtime仍false。源0的首段格栅仍偏低，部分侧轨接缝和条带坐标偏差、跨帧纹理稳定及邻接拼缝待修。首批v1/v2重复了相近边轨接缝，v3重画改善部分侧轨差异，但没有宣称全部准确；未程序移条带或拼坏帧。\n\n入口sequence.json含所有逐帧索引和双密度路径，source-aggregate.json为只聚合JSON的源像素去重证据。主bun/art.json、全局index/runtime、冻结三源码及Git均未改，未本地测试/浏览器或全族扫描。\n',encoding='utf-8')
print(json.dumps({'frameBindings':11,'uniqueOwnRGBAFrames':result['uniqueOwnRGBAFrames'],'accepted':False}))
