"""Reuse5 actually decoded equivalent source rasters, retaining each target offset."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (OUT/'sequence.json').exists(),'Do not overwrite a target sequence.'
target_context_path=OUT/'source-context.json';target_context=json.loads(target_context_path.read_text(encoding='utf-8'))
source_dir=ROOT/'assets/maps/treasure/animation-candidates/10006';source_context_path=source_dir/'source-context.json'
source_context=json.loads(source_context_path.read_text(encoding='utf-8'));source_seq_path=source_dir/'sequence.json'
source_seq=json.loads(source_seq_path.read_text(encoding='utf-8'))
index_path=ROOT/'assets/maps/production-index.json';index=json.loads(index_path.read_text(encoding='utf-8'))
definition=next(e for e in index['elements']if e['elementId']==14031)
assert target_context['elementId']==14031 and target_context['allResourceFramesDecoded']
assert target_context['sourceRawSHA256']==definition['dimgSha256']
assert source_context['sourceRawSHA256']!=target_context['sourceRawSHA256'],'This case is not complete-DIMG equality.'
by_index={f['frameIndex']:f for f in source_context['sourceFrames']};own_by_index={f['sourceFrameIndex']:f for f in source_seq['frames']}
assert len(target_context['sourceFrames'])==len(by_index)==source_seq['sourceDeclaredFrameCount']==5
frames=[];comparisons=[]
for target in target_context['sourceFrames']:
    i=target['frameIndex'];source=by_index[i];base=own_by_index[i]
    for field in['sourceFrameSize','encodedPixelSHA256','decodedRgbaSHA256','canonicalVisibleRGBAHash','sha256']:
        assert target[field]==source[field],(i,field)
    assert target['sourceFrameOffset']!=source['sourceFrameOffset']
    item={'sourceElementId':14031,'sourceFrameIndex':i,'sourceFrameSize':target['sourceFrameSize'],
        'sourceFrameOffset':target['sourceFrameOffset'],'sourceMapElemOffset':definition['mapElemOffsetRaw'],
        'sourceFootprintCells':definition['footprintCells'],'sourceGridAttr':definition['gridAttr'],
        'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'nativeFrameStateMeaning':None,
        'structuralEmpty':False,'sourceFullyTransparentPixels':False,
        'sourceFrameReference':target['file'],'sourceCanonicalVisibleRGBAHash':target['canonicalVisibleRGBAHash'],
        'sourcePixelDecodePerformedInPriorPreparation':True,'pixelAliasOfFrameIndex':None,
        'reusedFromCandidateElement':10006,'reusedFromCandidateFrameIndex':i,
        'sourceRasterEquivalentAcrossDefinitions':True,'wholeRawDimgSHAEqual':False,
        'sourceFrameOffsetComparedToReusedCandidate':{'target':target['sourceFrameOffset'],'reusedCandidateSource':source['sourceFrameOffset']},
        'exports':{},'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False}
    for density in['1','4']:
        old=base['exports'][density];file=ROOT/old['file'];assert sha(file)==old['sha256']
        assert [old['width'],old['height']]==[n*int(density)for n in target['sourceFrameSize']]
        item['exports'][density]={'file':old['file'],'sha256':old['sha256'],'width':old['width'],'height':old['height'],'mode':old['mode'],
            'alphaExtrema':old['alphaExtrema'],'decodedRGBAHashForOwnExport':old['decodedRGBAHashForOwnExport'],
            'decodedRGBAHashInheritedFromExistingOwnExportEvidence':True,'exportDensity':int(density),
            'sourceElementId':14031,'sourceFrameIndex':i,'sourceFrameSize':target['sourceFrameSize'],
            'sourceFrameOffset':target['sourceFrameOffset'],'sourceMapElemOffset':definition['mapElemOffsetRaw'],
            'sourceFootprintCells':definition['footprintCells'],'sourceGridAttr':definition['gridAttr'],'combinedRenderOrigin':None,
            'reusedFromCandidateElement':10006,'reusedFromCandidateFrameIndex':i,'sourceExportRecord':old['file']+'.source.json',
            'pngReusedWithoutPixelModification':True,'offsetsKeptIndependentFromSharedPNG':True,
            'newModelGeneration':False,'resampledThisPass':False,'wholeRawDimgSHAEqual':False,
            'operation':'existing own PNG reuse after actual target/source decoded raster equality; keep target frameOffset and mapElemOffset independent',
            'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'runtimeIntegrated':False}
    frames.append(item)
    comparisons.append({'sourceFrameIndex':i,'sourceFrameSize':target['sourceFrameSize'],
        'encodedPixelSHA256':target['encodedPixelSHA256'],'decodedRgbaSHA256':target['decodedRgbaSHA256'],
        'canonicalVisibleRGBAHash':target['canonicalVisibleRGBAHash'],'sourcePngSHA256':target['sha256'],
        'targetFrameOffset':target['sourceFrameOffset'],'referenceFrameOffset':source['sourceFrameOffset'],
        'pixelBytesEqual':True,'offsetEqual':False})
save(OUT/'definition-evidence.json',{'elementId':14031,'sourceFile':index_path.relative_to(ROOT).as_posix(),'sourceFileSHA256':sha(index_path),
    'definitionSnapshotUnmodified':definition,'logicModified':False,'sourceLookupStillCandidate':True})
save(OUT/'pixel-equivalence-evidence.json',{'elementId':14031,'reusedCandidateElementId':10006,
    'targetRawDimgSHA256':target_context['sourceRawSHA256'],'referenceRawDimgSHA256':source_context['sourceRawSHA256'],
    'wholeRawDimgSHAEqual':False,'targetSourceContext':{'file':target_context_path.relative_to(ROOT).as_posix(),'sha256':sha(target_context_path)},
    'referenceSourceContext':{'file':source_context_path.relative_to(ROOT).as_posix(),'sha256':sha(source_context_path)},
    'proof':'Five actual DIMG frames decoded in explicit<=6 batch; dimensions, encoded payload, decoded RGBA, canonical visible RGBA and PNG SHA all equal at corresponding indices; offsets intentionally differ.',
    'frames':comparisons,'thisRegistrationDecodedPixels':False,'PNGByteHashesRechecked':True})
result={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':14031,'family':'box',
    'sourceResourcePath':target_context['sourceResourcePath'],'sourceRawSHA256':target_context['sourceRawSHA256'],
    'sourceDeclaredFrameCount':5,'sourceDeclaredDirections':target_context['sourceDeclaredDirections'],'sourceFrameIndices':list(range(5)),
    'reusedFromCandidateElement':10006,'reusedFromCandidateSequence':{'file':source_seq_path.relative_to(ROOT).as_posix(),'sha256':sha(source_seq_path)},
    'sourcePixelEquivalenceEvidence':(OUT/'pixel-equivalence-evidence.json').relative_to(ROOT).as_posix(),'wholeRawDimgSHAEqual':False,
    'ownRepresentativeFramesGenerated':0,'newGenerationCount':0,'ownRepresentativeFramesReused':5,'frameBindingsProduced':5,
    'actualNativeAtlasSize':source_seq['actualNativeAtlasSize'],'selectedNativeAtlas':source_seq['selectedNativeAtlas'],
    'selectedNativeAtlasReusedWithoutPixelModification':True,'allResourceFramePositionsPresent':True,
    'sourceFootprintCells':definition['footprintCells'],'sourceMapElemOffset':definition['mapElemOffsetRaw'],'sourceGridAttr':definition['gridAttr'],
    'sourceLifeTime':definition['lifeTime'],'sourceCanMove':definition['canMove'],
    'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,
    'uniqueOwnRGBAFrames':source_seq['uniqueOwnRGBAFrames'],'RGBAHashCountsInheritedFromSourceCandidateEvidence':True,
    'frames':frames,'pixelDecodePerformedThisRegistration':False,
    'preview':source_seq['preview'],'previewBelongsToReusedCandidateElement':10006,
    'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'runtimeIntegrated':False,
    'mainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,
    'pending':source_seq['pending']+['target frame offsets and mapElemOffset are distinct; native combined origin/lookup/placement still unknown','only raster equality established; not a complete-DIMG byte alias']}
save(OUT/'sequence.json',result)
(OUT/'README.md').write_text('# 14031 五帧像素相同、坐标独立的候选复用\n\n《灵葫大作战》生产候选。本目标实际逐帧核图后，0–4与10006的尺寸、encoded payload SHA、decoded RGBA SHA、canonical visible RGBA及原帧PNG SHA全部一致。两个完整DIMG SHA不同，不能称完整资源字节别名。证据见pixel-equivalence-evidence.json。\n\n目标frameOffset为[0,19]/[0,20]/[0,19]/[0,17]/[0,20]，10006为[0,2]/[0,3]/[0,2]/[0,0]/[0,3]；自己的mapElemOffset[0,20]和definition/footprint/Grid/lifeTime/canMove保留。不按+17差值推客户端组合原点，也不把两类offset相加。\n\n5个源帧位复用10006已有own候选PNG，像素不改，新增生图0、不裁切/不缩放。每帧独立index、源尺寸和offset都在sequence.json，双尺寸160×236/232/236/244/232与对应x1保留。原母图真实原生1983×793，历史模型/质量/来源不改写。借用预览仍标10006来源，不冒充本目标运行截图。\n\n火焰/火星高差、局部状态和雕云/石块跨帧细节等10006原待修全部继承，accepted/geometry/stateCorrespondence/runtime均false，时序/loop/组合原点null。未改main art/index/runtime/src/Git或冻结三源码，未本地测试/浏览器/全族扫描。\n',encoding='utf-8')
print(json.dumps({'target':14031,'reusedFrom':10006,'frames':5,'newGenerationCount':0,'wholeDimgEqual':False,
    'targetMapElemOffset':definition['mapElemOffsetRaw'],'targetFrameOffsets':[f['sourceFrameOffset']for f in frames],'accepted':False}))
