"""Build773 map-element frame/state contracts from retained JSON only.

No PNG/DIMG/package read, no image import, no tests, no global manifest writes.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import hashlib,json

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
inputs=[]
def read(rel):
    raw=(ROOT/rel).read_bytes()
    value=json.loads(raw.decode('utf-8-sig'))
    inputs.append({'file':rel,'byteLength':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'type':'existing JSON metadata only'})
    return value
def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
baseline=read('assets/maps/production-index.json')
family_source=read('references/qqtang-map-data/visual-reference/families/index.json')
supplement=read('references/qqtang-map-data/visual-reference/binary-supplement/art-reference-index.json')
binary=read('references/qqtang-map-data/binary-properties-inspection.json')
town=read('references/qqtang-map-data/visual-reference/manifest.json')
base={x['elementId']:x for x in baseline['elements']}
extra={x['elementId']:x for x in supplement['elements']}
assert len(base)==721 and len(extra)==52 and not(set(base)&set(extra))
elements={**base,**extra}
assert len(elements)==773 and set(elements)=={x['id']for x in binary['records']}
other={x['elementId']:x for x in family_source['elements']}
fields=['dimgSha256','dimgFrameCount','dimgDirections','selectedFrame','selectedFrameSize','selectedFrameOffsetRaw']
source_conflicts=[{'elementId':ident,'field':key,'production':row.get(key),'referenceIndex':other[ident].get(key)}for ident,row in base.items()for key in fields if row.get(key)!=other[ident].get(key)]
assert not source_conflicts,'Metadata source disagreement must be reviewed, not silently resolved.'
full={}
for row in town.get('resources',[]):
    if row.get('dimg'):
        full[row['mapElementId']]={'dimg':row['dimg'],'file':'references/qqtang-map-data/visual-reference/manifest.json','selector':'resources.mapElementId='+str(row['mapElementId'])}
for ident,row in extra.items():
    if row.get('dimg'):
        full[ident]={'dimg':row['dimg'],'file':'references/qqtang-map-data/visual-reference/binary-supplement/art-reference-index.json','selector':'elements.elementId='+str(ident)}
new_metadata={}
for batch_path in sorted((OUT/'metadata-batches').glob('batch-*/batch.json')):
    batch=read(batch_path.relative_to(ROOT).as_posix())
    assert batch['pixelDecodePerformed']is False
    for entry in batch['records']:
        record=read(entry['record'])
        assert inputs[-1]['sha256']==entry['recordSHA256']
        assert record['pixelDecodePerformed']is False and record['dimg']['pixelDecodePerformed']is False
        assert all('decodedRgbaSha256'not in f for f in record['dimg']['frames'])
        for ident in record['candidateElementIds']:
            if ident not in elements:continue
            expected=elements[ident].get('dimgSha256')or elements[ident].get('dimg',{}).get('sha256')
            assert record['source']['rawResourceSHA256']==expected
            full[ident]={'dimg':record['dimg'],'file':entry['record'],'selector':'dimg','inspectionMode':'metadata_only; no pixel decode'}
            new_metadata[ident]=record
pieces=defaultdict(list)
for path in sorted((ROOT/'assets/maps').glob('*/art.json')):
    rel=path.relative_to(ROOT).as_posix();doc=read(rel)
    for piece in doc.get('pieces',[]):
        pieces[piece['elementId']].append({'artManifest':rel,'record':piece})
unknown_current=sorted(set(pieces)-set(elements))
duplicate_current=[ident for ident,p in pieces.items()if len(p)>1]
raw_groups=defaultdict(list)
for ident,row in elements.items():
    raw_hash=row.get('dimgSha256')or row.get('dimg',{}).get('sha256')
    if raw_hash:raw_groups[raw_hash].append(ident)
rows=[]
for ident,row in sorted(elements.items()):
    origin='baseline721'if ident in base else'binary-supplement52'
    info=row.get('dimg',{})
    count=row.get('dimgFrameCount',info.get('frameCount'))
    directions=row.get('dimgDirections',info.get('directions'))
    raw_hash=row.get('dimgSha256',info.get('sha256'))
    detail=full.get(ident)
    frames=detail['dimg'].get('frames')if detail else None
    selected=row.get('selectedFrame')
    selection_evidence='explicit selectedFrame in production/reference index'
    if selected is None and frames is not None:
        visible=[p['index']for p in frames if p.get('empty')is False and p.get('width',0)>0 and p.get('height',0)>0]
        if len(visible)==1:
            selected=visible[0];selection_evidence='only nonempty frame in retained full metadata; selectedFrame field absent'
    divided=count//directions if isinstance(count,int)and isinstance(directions,int)and directions>0 and count%directions==0 else None
    nonselected=[i for i in range(count)if i!=selected]if isinstance(count,int)and selected is not None else None
    # For a single declared frame, first-visible selected frame0 proves no empty
    # slot. For multi-frame resources, omitted frame tables remain unknown.
    empty_indices=[p['index']for p in frames if p.get('empty')is True]if frames is not None else([]if count==1 and selected==0 else None)
    frame_table=None
    repeated=None
    if frames is not None:
        frame_table=[{k:p[k]for k in ['index','frameOffset','pixelMode','width','height','empty','encodedPixelSha256','decodedRgbaSha256']if k in p}for p in frames]
        by_pixels=defaultdict(list)
        for p in frames:
            if p.get('empty')is False and p.get('encodedPixelSha256'):
                by_pixels[(p.get('pixelMode'),p.get('width'),p.get('height'),p['encodedPixelSha256'])].append(p['index'])
        repeated=[{'frameIndices':indices,'comparison':'encoded pixel bytes + mode + width/height only; frame offset may differ'}for indices in by_pixels.values()if len(indices)>1]
    elif count==1:
        repeated=[]
    current=[]
    for candidate in pieces.get(ident,[]):
        piece=candidate['record'];reference=piece.get('sourceReference',{})
        explicit_reference_match=bool(reference.get('sha256')and reference.get('sha256')==row.get('referencePng',{}).get('sha256'))
        current.append({'file':piece.get('file'),'pngPathExists':bool(piece.get('file')and(ROOT/piece['file']).is_file()),
            'artManifest':candidate['artManifest'],'sha256AsRecorded':piece.get('sha256'),'sha256RecheckedThisPass':False,
            'widthAsRecorded':piece.get('width'),'heightAsRecorded':piece.get('height'),'geometryAcceptedAsRecorded':piece.get('geometryAccepted'),
            'operationTypeAsRecorded':piece.get('operation',{}).get('type'),'singleRasterOnly':True,
            'sourceReferenceSHAEqualsSelectedReference':explicit_reference_match,
            'explicitActionOrFrameSequenceInCurrentRecord':False,'explicitSourceFrameIndicesInCurrentRecord':None,
            'candidateReferenceFramePositions':[selected]if selected is not None else None,
            'framePositionAssociation':'selected source reference of this element; explicit reference SHA match'if explicit_reference_match else'element-ID/static production pipeline association; no explicit source-frame field in art record',
            'additionalSourceFramePositionCoverage':[],'allSourceFramesAccepted':False})
    binary_extra=ident in extra
    rows.append({'elementId':ident,'family':row.get('family'),'definitionOrigin':origin,
        'sourceCandidatePath':row.get('candidatePath'),'nativeLookupMappingStatus':row.get('familyMappingStatus'),
        'sourceMetadata':{'file':'assets/maps/production-index.json'if ident in base else'references/qqtang-map-data/visual-reference/binary-supplement/art-reference-index.json','selector':'elements.elementId='+str(ident)},
        'sourceDimgSHA256':raw_hash,'sourceCompressedStreamSHA256':row.get('compressedStreamSha256'),
        'dimgVersion':row.get('dimgVersion',info.get('version')),'declaredFrameCount':count,'declaredDirections':directions,
        'declaredFramesPerDirection':divided,'directionIndexSemantics':None,'directionOrder':None,'frameDurationMs':None,
        'loopPolicy':None,'frameStateSemantics':None,'animationVersusDamageState':'unconfirmed; frame-count alone does not distinguish animation, break/damage states, empties or repeats',
        'selectedReferenceFrameIndex':selected,'selectedReferenceFrameIndexEvidence':selection_evidence,
        'selectedReferenceFrameSize':row.get('selectedFrameSize'),'selectedReferenceFrameOffset':row.get('selectedFrameOffsetRaw',row.get('selectedFrameOffset')),
        'selectedReferencePng':row.get('referencePng'),'selectedReferencePngReopenedThisPass':False,
        'retainedFullFrameTable':detail is not None,'fullFrameMetadataSource':{k:v for k,v in detail.items()if k!='dimg'}if detail else None,
        'frameMetadata':frame_table,'emptyFrameIndices':empty_indices,'emptyFrameCount':len(empty_indices)if empty_indices is not None else None,
        'emptyFrameDefinition':'structural DIMG empty marker/zero dimensions as recorded; not a new alpha-pixel inspection',
        'selectedFrameAlphaVisibleBoundingBoxAsRecorded':row.get('visibleBoundingBox'),
        'selectedFrameAlphaBoundingBoxRecordPresent':'visibleBoundingBox'in row,
        'fullyTransparentPixelFrameCount':(int(row['visibleBoundingBox']is None)if count==1 and'visibleBoundingBox'in row else None),
        'withinResourceRepeatedEncodedPixelGroups':repeated,'withinResourceRGBAEquivalenceBeyondSelectedFrame':None if count!=1 else'not applicable: only one declared frame',
        'frameTableUnavailableReason':None if detail else'Legacy production/reference indexes retain header counts and selected first-visible frame only; no complete frame list. Not recovered from Git or raw package in this pass.',
        'rawDimgAliasElementIds':sorted(raw_groups.get(raw_hash,[])),'rawDimgAliasIsNotWithinResourceFrameDeduplication':True,
        'sourceFootprintCells':row.get('footprintCells'),'sourceMapElemOffset':row.get('mapElemOffsetRaw'),'sourceGridAttr':row.get('gridAttr'),
        'unserializedFields':{'canHide':None,'canDoSpecial':None,'unknown':True}if binary_extra else None,
        'currentStaticCandidates':current,'candidateSelectedFrameCovered':bool(current and selected is not None),
        'nonselectedDeclaredFramePositionsWithoutCoverageEvidence':nonselected,
        'additionalDistinctArtworkCountRequired':None,'allStatesOrMotionComplete':False,
        'nextEvidence':['recover retained/source frame tables for unknown empty/repeated slots before counting new art','inspect selected frame positions in explicit batches only after permitted','prove client frame/state selection, timing, loops and direction meaning; do not infer from stand filename or LifeTime']if count and count>1 else['static geometry/anchor/material and source lookup still require acceptance; one declared frame does not prove other source action files are absent']})
families=[]
for family in sorted({p['family']for p in rows}):
    subset=[p for p in rows if p['family']==family]
    families.append({'family':family,'definitions':len(subset),'declaredFramePositions':sum(p['declaredFrameCount']or 0 for p in subset),
        'multiFrameDefinitions':sum((p['declaredFrameCount']or 0)>1 for p in subset),'staticCandidates':sum(bool(p['currentStaticCandidates'])for p in subset),
        'nonselectedFramePositionsWithoutCoverage':sum(len(p['nonselectedDeclaredFramePositionsWithoutCoverageEvidence']or[])for p in subset),
        'fullFrameTableKnown':sum(p['retainedFullFrameTable']for p in subset),'emptyOrRepeatUnknownDefinitions':sum(p['emptyFrameCount']is None or p['withinResourceRepeatedEncodedPixelGroups']is None for p in subset)})
multi=[p for p in rows if(p['declaredFrameCount']or 0)>1]
summary={'definitionCount':len(rows),'baselineDefinitions':len(base),'supplementDefinitions':len(extra),
    'declaredFramePositionsAcrossDefinitions':sum(p['declaredFrameCount']or 0 for p in rows),
    'declaredDirectionCountHistogram':dict(Counter(str(p['declaredDirections'])for p in rows)),
    'declaredFrameCountHistogram':dict(Counter(str(p['declaredFrameCount'])for p in rows)),
    'multiFrameDefinitions':len(multi),'singleFrameDefinitions':len(rows)-len(multi),
    'currentStaticCandidateDefinitions':sum(bool(p['currentStaticCandidates'])for p in rows),
    'currentStaticCandidatePNGPathsExisting':sum(any(c['pngPathExists']for c in p['currentStaticCandidates'])for p in rows),
    'currentExplicitActionOrFrameSequences':0,'candidateSelectedReferenceFramePositions':sum(bool(p['currentStaticCandidates'])and p['selectedReferenceFrameIndex']is not None for p in rows),
    'nonselectedDeclaredFramePositionsWithoutCoverageEvidence':sum(len(p['nonselectedDeclaredFramePositionsWithoutCoverageEvidence']or[])for p in rows),
    'distinctAdditionalDrawingsRequired':None,'fullFrameTableDefinitions':sum(p['retainedFullFrameTable']for p in rows),
    'emptyFrameCountKnownDefinitions':sum(p['emptyFrameCount']is not None for p in rows),
    'emptyFrameCountUnknownDefinitions':sum(p['emptyFrameCount']is None for p in rows),
    'emptyFrameCountMeasurement':'structural header/table empty; not whole-image alpha transparency',
    'fullyTransparentPixelFrameCountKnownDefinitions':sum(p['fullyTransparentPixelFrameCount']is not None for p in rows),
    'fullyTransparentPixelFrameCountUnknownDefinitions':sum(p['fullyTransparentPixelFrameCount']is None for p in rows),
    'withinResourceRepeatsUnknownDefinitions':sum(p['withinResourceRepeatedEncodedPixelGroups']is None for p in rows),
    'newDimgMetadataOnlyResources':len(new_metadata),
    'multiFrameDeclaredPositionsInspectedWithoutRGBA':sum(r['dimg']['frameCount']for r in new_metadata.values()),
    'withinResourceIdenticalEncodedRasterAndOffsetExtraSlots':sum(r['dimg']['frameCount']-r['structuralEmptyFrameCount']-r['sameRasterAndOffsetGroupCount']for r in new_metadata.values()),
    'additionalByteDistinctRasterGroupsBeyondSelectedFrame0':sum(r['encodedRasterGroupCount']-1 for r in new_metadata.values()),
    'byteDistinctGroupsAreNotConfirmedVisibleDifferences':True,
    'uniqueSourceDimgSHA256Count':len(raw_groups),'crossDefinitionRawDimgAliasGroups':sum(len(v)>1 for v in raw_groups.values()),
    'sourceIndexFieldConflicts':source_conflicts,'unknownCurrentArtIds':unknown_current,'duplicateCurrentArtIds':duplicate_current,
    'allStatesOrMotionComplete':False,'newImageOrDimgDecodes':0,'decodeCountDefinition':'pixel-plane decoding only;45 separate metadata-only resource inspections are recorded above','testsOrBuildsRun':False,'globalManifestChanged':False}
created=datetime.now(timezone.utc).isoformat()
metadata={'schemaVersion':1,'createdAtUTC':created,'scope':'Retained JSON including45 explicitly bounded metadata-only DIMG inspections;773 frame/state contracts, not animation delivery',
    'sourceAuthenticity':'community-patched-client; Tencent original official authenticity unverified',
    'sourceArchiveSHA256AsPreviouslyRecorded':baseline['source']['archiveSha256'],'archiveOrPackageRehashedThisPass':False,
    'inputs':inputs,'summary':summary,'families':families,
    'coverageDefinition':'One current PNG per definition is a static candidate associated with the selected source reference frame. It is not acceptance and not evidence of other declared frames. No current art record contains an explicit source-frame/action sequence.',
    'frameCountCaution':'954 is counted per definition including identical resource aliases;181 uncovered positions may include repeats/empty/state frames and is not a new-drawing quota.'}
save('summary.json',metadata)
save('elements.json',{'schemaVersion':1,'createdAtUTC':created,'inputSnapshot':'summary.json#inputs','summary':summary,'elements':rows})
save('multi-frame-gap-list.json',{'createdAtUTC':created,'definitions':len(multi),'uncoveredDeclaredFramePositions':summary['nonselectedDeclaredFramePositionsWithoutCoverageEvidence'],'distinctNewDrawingsRequired':None,'semanticsKnown':False,'elements':multi})
save('raw-dimg-alias-groups.json',{'source':'recorded full raw DIMG SHA256 only; no new resource hashing','notWithinResourceFrameDeduplication':True,'groups':[{'dimgSHA256':k,'elementIds':v}for k,v in sorted(raw_groups.items())if len(v)>1]})
lines=['# 地图元素状态与动画资源合同','','2026-10-28。本汇总只读JSON及PNG路径是否存在；另用每次1–6明确资源的metadata_only入口补取45个多帧完整结构表，有界zlib解包、没有RGBA/alpha解码。没有全量图像QA、构建或测试。','',
f'共有**{summary["definitionCount"]}定义、{summary["declaredFramePositionsAcrossDefinitions"]}个按定义计的声明帧位**；{summary["singleFrameDefinitions"]}个单帧、{summary["multiFrameDefinitions"]}个多帧，全部头声明方向数为1。当前{summary["currentStaticCandidateDefinitions"]}个定义各有单张PNG候选，关联选中参考帧0；没有逐源帧索引或动作序列。**181个非零声明帧位尚无覆盖证据，完整地图状态/动画美术未完成。**','',
'181不是181张新图预算：已取完整结构表证明7个确切重复槽位，但不同payload仍可能是alpha全空或可见等价；多帧也可能表现破坏状态。仅凭`stand`文件名、LifeTime、canMove、帧数或方向数都不分配动画语义、时序和方向名称。可见像素和原生调用另行取证。','',
'旧721索引原先只保留头与第一选中帧。现在17个早期中国城记录、52个补充记录和45个新metadata_only多帧记录共114定义有完整结构帧表。45个多帧的226声明帧均无结构空标记，形成219个不同encoded raster+offset组；7个槽位有确切内部重复，因此多于参考帧0的字节组候选为174。字节不同仍可能可见等价，不能把174直接宣布为174张必画新图。跨定义DIMG原始SHA相同不混入文件内部帧归组。','',
'新增52个定义使用现存二进制补充记录，canHide/canDoSpecial未序列化保持null；未从旧Git恢复任何内容。资产哈希只是现存JSON记录值，本轮没有重算图片/包哈希；输入JSON快照哈希均在summary.json。','',
'| 族 | 定义 | 声明帧位 | 多帧定义 | 单PNG候选 | 非零帧位未覆盖 |','|---|---:|---:|---:|---:|---:|']
for f in families:lines.append(f'| {f["family"]} | {f["definitions"]} | {f["declaredFramePositions"]} | {f["multiFrameDefinitions"]} | {f["staticCandidates"]} | {f["nonselectedFramePositionsWithoutCoverage"]} |')
lines+=['','空帧边界：上述空帧计数指DIMG结构空标记/零尺寸，不等于全alpha透明像素图。全透明像素帧数只在已有visibleBoundingBox记录且资源单帧时确定；缺少该证据的记录仍为null，本轮没有开图补证。','']
lines+=['','## 多帧缺项','', '| 元素ID | 族 | 头声明帧数 | 选中参考帧 | 尚无覆盖证据的帧索引 |','|---|---|---:|---:|---|']
for p in multi:lines.append(f'| {p["elementId"]} | {p["family"]} | {p["declaredFrameCount"]} | {p["selectedReferenceFrameIndex"]} | '+', '.join(map(str,p['nonselectedDeclaredFramePositionsWithoutCoverageEvidence']))+' |')
lines+=['','完整773行合同见`elements.json`，多帧优先缺项见`multi-frame-gap-list.json`；方向顺序、播放时长、循环/状态切换全部null。当前静态关联仅表示制作管线针对选中参考帧的候选，不是源帧美术或轮廓通过。每件原帧大小、占地、GridAttr与偏移均作为只读元数据保留。','',
'后续应按明确选定ID/帧位小批补足完整帧表、空/重复及视觉状态证据，再根据原生调用确定真正需要的新画状态与动作；未经证明不能把多帧统一循环、把破坏态当走路，也不能用一张master或静态变换宣布全状态完成。当前重型窗口hold仍有效。','']
(OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
doc='# 地图全状态与动画缺项合同（2026-10-28）\n\n'
doc+='773个源定义均有单PNG静态候选，完整状态/动画仍未完成。现有源JSON声明954个按定义计的帧位，其中45个定义多帧；选中参考帧均为0，非零181个帧位无当前覆盖证据。181可能包括空帧、重复帧或破坏态，不能直接算181张新画或一律循环。\n\n'
doc+='完整分族统计、45个多帧定义列表及证据边界见[合同说明](../references/qqtang-map-data/motion-contract/README.md)，逐773定义见[elements.json](../references/qqtang-map-data/motion-contract/elements.json)，输入JSON快照/哈希见[summary.json](../references/qqtang-map-data/motion-contract/summary.json)。\n\n'
doc+='汇总读取production-index、families索引、17个原manifest、52个补充记录、二进制属性JSON及19族art.json；另以显式1–6资源小批补取45多帧结构表，226帧无结构空标记，219个encoded raster+offset组，有7个确切重复槽。额外字节组代表174个，仍需视觉核验而非新画数量承诺。没有RGBA/alpha解码、全包重哈希、运行清单写入、构建、测试或Git操作；新增52未序列化字段保持未知。\n\n'
doc+='方向名、时序、循环与帧语义未证明均留null。单PNG存在和粗比例改善均不等于全帧、地图轮廓或实机通过。后续先按选定小批补证状态表与原生调用，再确定逐ID实际制作合同。\n'
(ROOT/'docs/MAP_ELEMENT_MOTION_CONTRACT_20261028.md').write_text(doc,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True))
