"""Build a world source contract after all distinct, bounded source phases are available."""
from pathlib import Path
import json,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ident=int(sys.argv[1]);read=lambda p:json.loads(p.read_text(encoding='utf-8'))
inspection=read(OUT/f'references/world/{ident}/metadata/metadata-inspection.json');source=inspection['records'][0]
item=next(e for e in read(ROOT/'references/qqtang-item-data/catalog.json')['items']if e['item_id']==ident)
representatives={i:g[0]for g in source['encodedRasterGroups']for i in g};frames=[]
for f in source['metadata']['frames']:
    index=f['index'];rep=representatives[index]
    reference=read(OUT/f'references/world/{ident}/frame-{rep:03d}.png.source.json')
    assert reference['sourceFrameRecord']['encodedPixelSha256']==f['encodedPixelSha256']
    assert reference['nativeFrameSize']==[f['width'],f['height']]
    frames.append({'itemId':ident,'sourceFrameIndex':index,'sourcePhaseIndex':index,'directionIndex':None,'directionSemantic':None,
                   'sourceFrameRecord':f,'file':reference['file'],'sha256':reference['sha256'],
                   'nativeFrameSize':[f['width'],f['height']],'frameOffsetRaw':f['frameOffset'],
                   'sourceAlphaBBoxAt16':reference['sourceAlphaBBoxAt16'],'rasterReferenceRepresentativeIndex':rep,
                   'rasterAliasEvidence':'same encoded SHA/native size/pixel mode; rawOffset remains this position\'s own',
                   'frameDurationMs':None,'referenceOnly':True,'notRuntimeArt':True})
doc={'itemId':ident,'sourceName':item['name'],'sourceDescription':item['description'],
     'sourceMembers':{r['state']:r['sourceMember']for r in inspection['records']},'sourceSha256':source['sha256'],
     'standWalkByteIdentical':inspection['standWalkByteIdentical'],'sourceDimg':source['metadata'],
     'completeContainerLayoutParsed':True,'metadataOnlyStructureAccepted':True,'allDeclaredPixelFramesDecoded':False,
     'explicitPixelRepresentativeIndices':sorted(set(representatives.values())),'pixelReferenceCount':len(set(representatives.values())),
     'officialAuthenticity':'unverified community client','frameOrder':list(range(len(frames))),
     'directions':source['metadata']['directions'],'directionSemantic':None,'directionBlockOrderKnown':False,
     'frameDurationMs':None,'loop':None,'encodedRasterGroups':source['encodedRasterGroups'],
     'encodedPoseGroupsIncludingRawOffset':source['encodedPoseGroupsIncludingRawOffset'],
     'frames':frames,'referenceOnly':True,'notRuntimeArt':True,'runtimeUsable':False}
(OUT/f'references/world/{ident}/source-contract.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'itemId':ident,'sourcePositions':len(frames),'pixelReferences':len(set(representatives.values())),'runtimeUsable':False}))
