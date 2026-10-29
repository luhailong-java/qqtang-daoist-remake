"""Preserve24 sequence positions while sharing nine explicitly painted raster candidates."""
from pathlib import Path
from copy import deepcopy
import json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contract=read(OUT/'references/world/138/source-contract.json')
doc=read(OUT/'world-art.json')
item=next(e for e in doc['items']if e['itemId']==138)
representatives={g[0]:next(f for f in item['frames']if f['sourceFrameIndex']==g[0])for g in contract['encodedRasterGroups']}
frames=[]
for source in contract['frames']:
    index=source['sourceFrameIndex'];rep=source['rasterReferenceRepresentativeIndex']
    frame=deepcopy(representatives[rep])
    frame.update({'sourceFrameIndex':index,'sourcePhaseIndex':index,'directionIndex':None,
                  'imagePhaseRepresentativeIndex':rep,'frameOffsetRaw':source['frameOffsetRaw'],
                  'frameOffsetPxAtDensity4':[v*4 for v in source['frameOffsetRaw']],
                  'sourceNativeFrameRecord':source['sourceFrameRecord'],
                  'provenanceRecord':frame['file']+'.provenance.json' if index==rep else f'assets/items/head-adornments/world/138/position-{index:03d}.alias.json',
                  'rasterImageShared':index!=rep,'rasterAliasOfSourceFrameIndex':rep if index!=rep else None,
                  'rasterAliasEvidence':'strict encodedPixelSha256 + native width/height + pixelMode equal; each position keeps its own source offset',
                  'frameWithinDirection':None,'directionCardinalOrder':None})
    if index!=rep:
        frame['operation']={'type':'exact-raster-file-reference-reuse','newModelGeneration':False,
                            'representativeSourceFrameIndex':rep,'representativeFile':frame['file'],
                            'geometry':'same native width/height only; rawOffset belongs to this source position',
                            'originalPaintOperation':frame['operation']}
    save(ROOT/frame['provenanceRecord'],frame);frames.append(frame)
item.update({'frames':frames,'sourceDeclaredFrameCoverageComplete':True,'candidateFrameCoverage':24,
             'candidateSequencePositionCount':24,'candidateUniqueRasterCount':9,
             'sourceEncodedRasterGroups':contract['encodedRasterGroups'],
             'sourceEncodedPoseGroupsIncludingRawOffset':contract['encodedPoseGroupsIncludingRawOffset'],
             'sourceEncodedPoseGroupCount':18,'sourceDirectionBlockOrderKnown':False,
             'directions':4,'directionSemantic':None,'frameDurationsMs':None,'loop':None,
             'candidateCoverageMeaning':'24 original linear positions represented by9 raster files, not9 original animation frames;18 distinct source raster+offset poses',
             'completeAnimationAccepted':False,'animationTimingKnown':False,'accepted':False,'runtimeAdopted':False})
save(OUT/'world-art.json',doc)
print(json.dumps({'itemId':138,'sourcePositions':24,'paintedRasterFiles':9,'sourceRasterPlusOffsetGroups':18,'accepted':0,'runtimeAdopted':False}))
