"""Prepare24 metadata positions using only the nine explicit representative pixel references."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inspection=read(OUT/'references/world/138/metadata/metadata-inspection.json')
source=inspection['records'][0]
catalog=read(ROOT/'references/qqtang-item-data/catalog.json')
item=next(e for e in catalog['items']if e['item_id']==138)
representatives={i:g[0]for g in source['encodedRasterGroups']for i in g}
frames=[]
for frame in source['metadata']['frames']:
    index=frame['index'];representative=representatives[index]
    reference=read(OUT/f'references/world/138/frame-{representative:03d}.png.source.json')
    assert reference['sourceFrameRecord']['encodedPixelSha256']==frame['encodedPixelSha256']
    assert reference['nativeFrameSize']==[frame['width'],frame['height']]
    frames.append({'itemId':138,'sourceFrameIndex':index,'sourcePhaseIndex':index,
                   'directionIndex':None,'directionSemantic':None,'sourceFrameRecord':frame,
                   'file':reference['file'],'sha256':reference['sha256'],
                   'nativeFrameSize':[frame['width'],frame['height']],'frameOffsetRaw':frame['frameOffset'],
                   'sourceAlphaBBoxAt16':reference['sourceAlphaBBoxAt16'],
                   'rasterReferenceRepresentativeIndex':representative,
                   'rasterAliasEvidence':'same encoded payload SHA, width, height and pixel mode; rawOffset not inherited',
                   'frameDurationMs':None,'referenceOnly':True,'notRuntimeArt':True})
contract={'itemId':138,'sourceName':item['name'],'sourceDescription':item['description'],
          'sourceMembers':{r['state']:r['sourceMember']for r in inspection['records']},
          'sourceSha256':source['sha256'],'standWalkByteIdentical':True,'sourceDimg':source['metadata'],
          'completeContainerLayoutParsed':True,'metadataOnlyStructureAccepted':True,
          'all24PixelFramesDecoded':False,'explicitPixelRepresentativeIndices':sorted(set(representatives.values())),
          'pixelReferenceCount':9,'officialAuthenticity':'unverified community client',
          'frameOrder':list(range(24)),'directions':4,'directionSemantic':None,
          'directionBlockOrderKnown':False,'frameDurationMs':None,'loop':None,
          'encodedRasterGroups':source['encodedRasterGroups'],
          'encodedPoseGroupsIncludingRawOffset':source['encodedPoseGroupsIncludingRawOffset'],
          'frames':frames,'referenceOnly':True,'notRuntimeArt':True,'runtimeUsable':False}
save(OUT/'references/world/138/source-contract.json',contract)
for key,indices in [('a',[0,1,2,6,7,8]),('b',[12,13,14])]:
    references=[str(OUT/f'references/world/138/source-phases-{key}.png'),
                'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png',
                str(OUT/'references/world/138/own-appearance-master-reference.png')]
    if key=='b':references.append(str(OUT/'world/world-138-a-v1.png'))
    spec={'source':f'assets/items/head-adornments/world/world-138-{key}-v1.png','version':f'138-{key}-v1',
          'referencePaths':references,'frames':[]}
    for pos,index in enumerate(indices):
        f=frames[index]
        rect=[pos%3*512,pos//3*512,(pos%3+1)*512,(pos//3+1)*512]if key=='a'else[pos*512,0,(pos+1)*512,1024]
        spec['frames'].append({'itemId':138,'sourceFrameIndex':index,'sourceReference':f['file'],
                               'nativeFrameSize':f['nativeFrameSize'],'frameOffsetRaw':f['frameOffsetRaw'],'manualRect':rect})
    save(OUT/f'exports/world-138-{key}.json',spec)
print(json.dumps({'itemId':138,'positions':24,'distinctRasterReferences':9,'poseGroups':len(source['encodedPoseGroupsIncludingRawOffset']),'directions':4,'directionOrderKnown':False}))
