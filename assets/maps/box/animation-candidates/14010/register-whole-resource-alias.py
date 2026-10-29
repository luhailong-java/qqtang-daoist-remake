"""Bind3 explicitly verified complete-DIMG aliases to existing own candidate PNGs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[5]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
index_path=ROOT/'assets/maps/production-index.json';index=json.loads(index_path.read_text(encoding='utf-8'))
by_id={e['elementId']:e for e in index['elements']}
jobs=[(14010,7010,'box','bomb'),(17018,8018,'common','bun'),(17019,8019,'common','bun')]
receipts=[]
for target_id,source_id,family,source_family in jobs:
    OUT=ROOT/f'assets/maps/{family}/animation-candidates/{target_id}'
    assert not (OUT/'sequence.json').exists(),'Never overwrite an existing target sequence.'
    definition=by_id[target_id];original=by_id[source_id]
    evidence_batch=json.loads((OUT/'metadata-evidence/batch.json').read_text(encoding='utf-8'))
    assert evidence_batch['resourceCount']==1 and evidence_batch['pixelDecodePerformed'] is False
    metadata_path=ROOT/evidence_batch['records'][0]['record'];metadata=json.loads(metadata_path.read_text(encoding='utf-8'))
    assert metadata['candidateElementIds']==[target_id]
    source_dir=ROOT/f'assets/maps/{source_family}/animation-candidates/{source_id}'
    source_seq_path=source_dir/'sequence.json';source_seq=json.loads(source_seq_path.read_text(encoding='utf-8'))
    source_context_path=source_dir/'source-context.json';source_context=json.loads(source_context_path.read_text(encoding='utf-8'))
    digest=metadata['source']['rawResourceSHA256']
    assert digest==definition['dimgSha256']==original['dimgSha256']==source_context['sourceRawSHA256']==source_seq['sourceRawSHA256']
    assert metadata['resourcePath'].replace('\\','/').lower()==definition['candidatePath'].replace('\\','/').lower()
    assert metadata['dimg']['frameCount']==definition['dimgFrameCount']==source_seq['sourceDeclaredFrameCount']
    assert metadata['dimg']['directions']==definition['dimgDirections']==source_seq['sourceDeclaredDirections']
    source_by_index={f['sourceFrameIndex']:f for f in source_seq['frames']}
    source_pixels={f['frameIndex']:f for f in source_context['sourceFrames']}
    frames=[]
    for native in metadata['dimg']['frames']:
        i=native['index'];base=source_by_index[i];pixel_source=source_pixels[i]
        assert [native['width'],native['height']]==base['sourceFrameSize']==pixel_source['sourceFrameSize']
        assert native['frameOffset']==base['sourceFrameOffset']==pixel_source['sourceFrameOffset']
        assert native['encodedPixelSha256']==pixel_source['encodedPixelSHA256']
        assert not native['empty']
        item={'sourceElementId':target_id,'sourceFrameIndex':i,'sourceFrameSize':[native['width'],native['height']],
            'sourceFrameOffset':native['frameOffset'],'sourceMapElemOffset':definition['mapElemOffsetRaw'],
            'sourceFootprintCells':definition['footprintCells'],'sourceGridAttr':definition['gridAttr'],
            'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'nativeFrameStateMeaning':None,
            'structuralEmpty':native['empty'],'sourceFullyTransparentPixels':pixel_source['fullyTransparentPixels'],
            'sourceEncodedPixelSHA256':native['encodedPixelSha256'],
            'sourceCanonicalVisibleRGBAHash':pixel_source['canonicalVisibleRGBAHash'],
            'sourcePixelEvidenceInheritedByExactCompleteDIMGEquality':True,'sourcePixelDecodePerformedForTargetThisPass':False,
            'sourceFrameReference':pixel_source['file'],'sourceFrameReferenceBelongsToElement':source_id,
            'reusedFromCandidateElement':source_id,'exports':{},'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False}
        for density in ['1','4']:
            old=base['exports'][density];file=ROOT/old['file'];assert sha(file)==old['sha256']
            assert [old['width'],old['height']]==[native['width']*int(density),native['height']*int(density)]
            binding={'file':old['file'],'sha256':old['sha256'],'width':old['width'],'height':old['height'],'mode':old['mode'],
                'alphaExtrema':old['alphaExtrema'],'decodedRGBAHashForOwnExport':old['decodedRGBAHashForOwnExport'],
                'decodedRGBAHashInheritedFromExistingCandidateEvidence':True,'exportDensity':int(density),
                'sourceElementId':target_id,'sourceFrameIndex':i,'sourceFrameSize':[native['width'],native['height']],
                'sourceFrameOffset':native['frameOffset'],'sourceMapElemOffset':definition['mapElemOffsetRaw'],
                'sourceFootprintCells':definition['footprintCells'],'sourceGridAttr':definition['gridAttr'],'combinedRenderOrigin':None,
                'reusedFromCandidateElement':source_id,'reusedFromCandidateFrameIndex':i,
                'sourceExportRecord':old['file']+'.source.json','pngReusedWithoutPixelModification':True,
                'offsetsKeptIndependentFromSharedPNG':True,'newModelGeneration':False,'resampledThisPass':False,
                'operation':'direct existing own PNG binding after complete raw DIMG SHA and per-frame payload/dimension/offset equality verification',
                'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'runtimeIntegrated':False}
            item['exports'][density]=binding
        frames.append(item)
    save(OUT/'definition-evidence.json',{'elementId':target_id,'sourceFile':index_path.relative_to(ROOT).as_posix(),
        'sourceFileSHA256':sha(index_path),'definitionSnapshotUnmodified':definition,
        'reusedArtSourceDefinitionId':source_id,'sourceDefinitionComparison':{
            'sourceMapElemOffset':original['mapElemOffsetRaw'],'targetMapElemOffset':definition['mapElemOffsetRaw'],
            'sourceFootprintCells':original['footprintCells'],'targetFootprintCells':definition['footprintCells'],
            'sourceGridAttr':original['gridAttr'],'targetGridAttr':definition['gridAttr'],
            'targetLifeTime':definition['lifeTime'],'targetCanMove':definition['canMove']},
        'nativeLookupMappingConfirmed':False,'logicModified':False})
    result={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':target_id,'family':family,
        'sourceResourcePath':metadata['resourcePath'],'sourceRawSHA256':digest,
        'sourceDeclaredFrameCount':metadata['dimg']['frameCount'],'sourceDeclaredDirections':metadata['dimg']['directions'],
        'sourceFrameIndices':[f['sourceFrameIndex']for f in frames],
        'sourceDefinitionEvidence':(OUT/'definition-evidence.json').relative_to(ROOT).as_posix(),
        'verifiedTargetMetadata':{'file':metadata_path.relative_to(ROOT).as_posix(),'sha256':sha(metadata_path),'pixelDecodePerformed':False},
        'reusedFromCandidateElement':source_id,'reusedFromCandidateSequence':{'file':source_seq_path.relative_to(ROOT).as_posix(),'sha256':sha(source_seq_path)},
        'sourceCandidatePixelEvidence':{'file':source_context_path.relative_to(ROOT).as_posix(),'sha256':sha(source_context_path)},
        'reuseBasis':'entire uncompressed DIMG byte SHA equality, plus each index/dimension/raw frameOffset/encoded payload SHA; not cross-definition frame alias guessing',
        'ownRepresentativeFramesGenerated':0,'newGenerationCount':0,'ownRepresentativeFramesReused':len(frames),'frameBindingsProduced':len(frames),
        'actualNativeAtlasSize':source_seq['actualNativeAtlasSize'],'selectedNativeAtlas':source_seq['selectedNativeAtlas'],
        'selectedNativeAtlasReusedWithoutPixelModification':True,'allResourceFramePositionsPresent':True,
        'sourceFootprintCells':definition['footprintCells'],'sourceMapElemOffset':definition['mapElemOffsetRaw'],'sourceGridAttr':definition['gridAttr'],
        'sourceLifeTime':definition['lifeTime'],'sourceCanMove':definition['canMove'],
        'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,
        'frames':frames,'uniqueOwnRGBAFrames':source_seq['uniqueOwnRGBAFrames'],'RGBAHashCountsInheritedFromSourceCandidateEvidence':True,
        'pixelDecodePerformedThisPass':False,'pixelPayloadValidationForTargetThisPass':'unknown','targetVisibleAlphaIndependentlyDecodedThisPass':False,
        'preview':source_seq['preview'],'previewBelongsToReusedCandidateElement':source_id,
        'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'runtimeIntegrated':False,
        'mainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,
        'pending':source_seq['pending']+['target-specific placement/lookup/runtime and all source candidate art issues remain unaccepted; differing mapElemOffset kept independent','LifeTime is retained raw definition data; no animation timing derived from it']}
    save(OUT/'sequence.json',result)
    (OUT/'README.md').write_text(f'# {target_id} 完整源资源相同的候选复用\n\n《灵葫大作战》生产候选。实际重新读取本目标package条目并只zlib解包/metadata_only校验，完整原DIMG SHA `{digest}` 与{source_id}实证一致，逐帧index、尺寸、frameOffset和encoded payload SHA也逐项核对。无本目标新增RGBA解码/生图/裁切/缩放，新增生图0，直接引用{source_id}已有own PNG；不把跨定义相同字节说成帧内别名。\n\n本目标自己的definition见definition-evidence.json；footprint、GridAttr、lifeTime、canMove均取自身。源frameOffset与本目标mapElemOffset `{definition["mapElemOffsetRaw"]}` 分开保留，未复制{source_id}的地图偏移、未推组合原点或时序。所有原始来源/模型历史保持不变。\n\nsequence.json保留本目标{len(frames)}个帧位索引与1倍/4倍PNG绑定，reusedFromCandidateElement={source_id}，PNG像素完全不改；复用图的比例、轮廓、局部亮点等既有待修全部继承。accepted/geometry/stateCorrespondence/runtime均false，目标运行和放置未验。未改任何main art/global/index/runtime/src/Git，未本地测试或浏览器。\n',encoding='utf-8')
    receipts.append({'target':target_id,'sourceCandidate':source_id,'frames':len(frames),'targetMapElemOffset':definition['mapElemOffsetRaw'],'newGenerationCount':0})
print(json.dumps(receipts))
