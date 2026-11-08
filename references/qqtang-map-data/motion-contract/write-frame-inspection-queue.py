"""Produce explicit frame representatives from the45 metadata-only reports."""
from pathlib import Path
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
contract={x['elementId']:x for x in json.loads((OUT/'elements.json').read_text(encoding='utf-8'))['elements']}
records={}
for batch in sorted((OUT/'metadata-batches').glob('batch-*/batch.json')):
    for item in json.loads(batch.read_text(encoding='utf-8'))['records']:
        record=json.loads((ROOT/item['record']).read_text(encoding='utf-8'))
        for ident in record['candidateElementIds']:
            records[ident]=(record,item['record'])
assert len(records)==45
queue=[];repeats=[]
for ident,(record,source)in sorted(records.items()):
    row=contract[ident];selected=row['selectedReferenceFrameIndex']
    for group in record['encodedRasterGroups']:
        if len(group['frameIndices'])>1:
            repeats.append({'elementId':ident,'sourceMetadata':source,**group})
        if selected in group['frameIndices']:
            continue
        queue.append({'elementId':ident,'family':row['family'],'sourceResourcePath':record['resourcePath'],
            'sourceRawSHA256':record['source']['rawResourceSHA256'],'sourceMetadata':source,
            'representativeFrameIndex':group['representativeFrameIndex'],'equivalentEncodedFrameIndices':group['frameIndices'],
            'frameSize':group['size'],'frameOffsets':group['frameOffsets'],'pixelMode':group['pixelMode'],'encodedPixelSHA256':group['encodedPixelSha256'],
            'existingSelectedFrameIndex':selected,'existingOwnStaticCandidates':[p['file']for p in row['currentStaticCandidates']],
            'sourceMapElemOffset':row['sourceMapElemOffset'],'sourceFootprintCells':row['sourceFootprintCells'],
            'dimgFrameOffsetAndMapElemOffsetAreSeparate':True,'combinedRenderOrigin':None,
            'readyForBoundedVisualInspection':True,'readyForFinalPainting':False,'visibleDifferenceConfirmed':False,
            'frameSemantics':None,'nativeTimingMs':None,'directionMeaning':None,
            'nextStep':'Inspect exact source frame with current own master; only then define original repaint, no component shifts from old AI art.'})
assert len(queue)==174
first_record,first_path=records[3050]
first={'elementId':3050,'frameIndices':[f['index']for f in first_record['dimg']['frames']],
       'resourcePath':first_record['resourcePath'],'sourceMetadata':first_path,
       'sourceFrameSizes':[[f['width'],f['height']]for f in first_record['dimg']['frames']],
       'sourceFrameOffsets':[f['frameOffset']for f in first_record['dimg']['frames']],
       'sourceMapElemOffset':contract[3050]['sourceMapElemOffset'],'combinedRenderOrigin':None,
       'existingOwnStaticCandidates':[p['file']for p in contract[3050]['currentStaticCandidates']],
       'scope':'First complete four-frame candidate set including reference frame0; visual content still to inspect, not an animation semantic claim.'}
report={'createdAtUTC':datetime.now(timezone.utc).isoformat(),'sourceMultiFrameDefinitions':45,'declaredFramePositions':226,
    'structuralEmptyPositions':0,'encodedRasterAndOffsetGroups':219,'withinResourceRepeatedExtraSlots':7,
    'additionalByteRepresentativeCandidates':174,'requiredNewDrawingCount':None,'pixelDecodePerformedForThisQueue':False,
    'firstCompleteResource':first,'knownRepeatedGroups':repeats,'additionalFrameInspectionQueue':queue,
    'limitations':['Groups are per resource/definition; no cross-definition DIMG alias collapse.','Encoded bytes differ is not proof of visible pixel difference.','No generation, PNG, runtime frame binding, timing or direction order delivered by this queue.']}
(OUT/'next-frame-inspection-queue.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='# 多帧下一批核图/转绘候选\n\n45个多帧定义的226帧结构表已齐：结构空帧0，219个不同encoded raster+offset组，7个确切重复槽，额外字节代表174个。174尚未确认可见差异，不能直接作为必画数量。\n\n'
text+='先处理3050全部四个原帧位（0–3），实际查看其内容再确定是否适合独立状态美术；当前自有静态图只作身份/材质参考。每帧原尺寸、DIMG frameOffset及独立mapElemOffset都保留，组合渲染原点未知，不将两种偏移相加。若3050实际是全透明或不宜独立转绘的未知标记，再明确换3051。\n\n'
text+='精确源路径、SHA、每帧尺寸/offset、174个代表位与现有自有master位置见[next-frame-inspection-queue.json](next-frame-inspection-queue.json)。后续每次仅1–6个明确源帧核图，不全45解码；不从旧AI图片程序搬移部件来伪造不同状态，不据数字/族名猜动作或时序。\n'
(OUT/'NEXT_DRAW_CANDIDATES.md').write_text(text,encoding='utf-8')
print(json.dumps({'multiFrameDefinitions':45,'encodedRasterGroups':219,'additionalRepresentatives':174,'firstCompleteResource':first,'pixelDecodePerformed':False},ensure_ascii=True))
