"""Share identical rasters only; keep each source sequence position and rawOffset independent."""
from pathlib import Path
from copy import deepcopy
import json,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ident=int(sys.argv[1]);read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contract=read(OUT/f'references/world/{ident}/source-contract.json');doc=read(OUT/'world-art.json')
item=next(e for e in doc['items']if e['itemId']==ident)
reps={g[0]:next(f for f in item['frames']if f['sourceFrameIndex']==g[0])for g in contract['encodedRasterGroups']}
frames=[]
for source in contract['frames']:
    index=source['sourceFrameIndex'];rep=source['rasterReferenceRepresentativeIndex'];frame=deepcopy(reps[rep])
    frame.update({'sourceFrameIndex':index,'sourcePhaseIndex':index,'directionIndex':None,'imagePhaseRepresentativeIndex':rep,
                  'frameOffsetRaw':source['frameOffsetRaw'],'frameOffsetPxAtDensity4':[q*4 for q in source['frameOffsetRaw']],
                  'sourceNativeFrameRecord':source['sourceFrameRecord'],
                  'provenanceRecord':frame['file']+'.provenance.json'if index==rep else f'assets/items/head-adornments/world/{ident}/position-{index:03d}.alias.json',
                  'rasterImageShared':index!=rep,'rasterAliasOfSourceFrameIndex':rep if index!=rep else None,
                  'rasterAliasEvidence':'same encoded SHA/native width/height/pixel mode; rawOffset is this position\'s own',
                  'frameWithinDirection':None,'directionCardinalOrder':None})
    if index!=rep:frame['operation']={'type':'exact-raster-file-reference-reuse','newModelGeneration':False,
        'representativeSourceFrameIndex':rep,'representativeFile':frame['file'],
        'geometry':'same native width/height only; rawOffset remains source position\'s own','originalPaintOperation':frame['operation']}
    save(ROOT/frame['provenanceRecord'],frame);frames.append(frame)
item.update({'frames':frames,'sourceDeclaredFrameCoverageComplete':True,'candidateFrameCoverage':len(frames),
             'candidateSequencePositionCount':len(frames),'candidateUniqueRasterCount':len(reps),
             'sourceEncodedRasterGroups':contract['encodedRasterGroups'],
             'sourceEncodedPoseGroupsIncludingRawOffset':contract['encodedPoseGroupsIncludingRawOffset'],
             'sourceEncodedPoseGroupCount':len(contract['encodedPoseGroupsIncludingRawOffset']),
             'sourceDirectionBlockOrderKnown':False,'directions':contract['directions'],'directionSemantic':None,
             'frameDurationsMs':None,'loop':None,'candidateCoverageMeaning':'source linear positions, unique raster files and raster+offset groups are distinct counts',
             'completeAnimationAccepted':False,'animationTimingKnown':False,'accepted':False,'runtimeAdopted':False})
save(OUT/'world-art.json',doc)
print(json.dumps({'itemId':ident,'sourcePositions':len(frames),'paintedRasterFiles':len(reps),'poseGroups':item['sourceEncodedPoseGroupCount'],'accepted':0}))
