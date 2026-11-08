"""Save one explicit opaque square-frame atlas batch; no global art mutation."""
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import argparse,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[5];IMAGE=Path('D:/work/image')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--element',type=int,required=True);p.add_argument('--family',required=True);p.add_argument('--batch',required=True)
p.add_argument('--version',required=True);p.add_argument('--host',type=Path,required=True);p.add_argument('--columns',type=int,required=True)
p.add_argument('--previous');p.add_argument('--continuity');p.add_argument('--structure')
a=p.parse_args();assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',a.batch)
OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}/{a.batch}'
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'))
sources=context['sourceFrames'];assert 1<=len(sources)<=6
assert all(not s['structuralEmpty'] and s['alphaExtrema']==[255,255] and s['sourceFrameSize'][0]==s['sourceFrameSize'][1] for s in sources)
own=ROOT/context['currentOwnMaster']['file'];structure=ROOT/a.structure if a.structure else ROOT/context['referenceBoard']
styles=[IMAGE/'designs/mail-ui-v1/01-mail-event.png',IMAGE/'designs/team-ui-v2/team-ui-v2.png']
previous=OUT/f'sequence-{a.previous}.png' if a.previous else None
refs=[previous,structure,own] if previous else [own,structure]
roles=['exact previous own atlas AI edit','actual selected source frame structures','current own identity/material master'] if previous else ['current own identity/material master','actual selected source frame structures']
if a.continuity:
    refs.append(ROOT/a.continuity);roles.append('same resource prior batch visual continuity; not source frame evidence')
refs+=styles;roles+=['primary Daoist Q style','primary Daoist Q style']
target=OUT/f'sequence-{a.version}.png';assert not target.exists();shutil.copyfile(a.host,target)
atlas=Image.open(target).convert('RGBA');assert atlas.getchannel('A').getextrema()==(255,255),'No alpha normalization is allowed by this exporter.'
rows=(len(sources)+a.columns-1)//a.columns
assert atlas.width%a.columns==0 and atlas.height%rows==0
side=atlas.width//a.columns;assert side==atlas.height//rows,'Native atlas must provide actual square cells; no stretching or crop-to-fit geometry.'
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(a.host.stat().st_mtime,timezone.utc).isoformat(),
    'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),
    'width':atlas.width,'height':atlas.height,'storedMode':Image.open(target).mode,'alphaExtrema':[255,255],
    'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False,'promptFile':(OUT/f'prompt-{a.version}.txt').relative_to(ROOT).as_posix(),'referenced_image_paths':[str(x)for x in refs]},
    'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in host exposes no model/quality selectors or verifiable returned model/quality metadata.',
    'hostOutputFile':str(a.host),'officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md',
    'references':[{'file':str(x),'sha256':sha(x),'role':role,'actuallyAttached':True}for x,role in zip(refs,roles)],
    'operation':'AI edit entire opaque atlas' if previous else 'new source-frame-corresponding opaque square atlas',
    'sourceFrameIndices':[s['frameIndex']for s in sources],'sourceContext':(OUT/'source-context.json').relative_to(ROOT).as_posix(),
    'resampled':False,'accepted':False,'runtimeIntegrated':False}
if previous:record['editedFrom']={'file':previous.relative_to(ROOT).as_posix(),'sha256':sha(previous),'generationRecord':str(previous.relative_to(ROOT))+'.generation.json'}
save(Path(str(target)+'.generation.json'),record)
frames=[];preview=Image.new('RGB',(360*len(sources),500),(230,234,229));draw=ImageDraw.Draw(preview)
for ordinal,source in enumerate(sources):
    col=ordinal%a.columns;row=ordinal//a.columns;rect=[col*side,row*side,(col+1)*side,(row+1)*side]
    tile=atlas.crop(rect);assert tile.getchannel('A').getextrema()==(255,255)
    item={'sourceFrameIndex':source['frameIndex'],'sourceFrameSize':source['sourceFrameSize'],'sourceFrameOffset':source['sourceFrameOffset'],
        'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceFootprintCells':context['sourceFootprintCells'],'sourceGridAttr':context['sourceGridAttr'],
        'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'nativeFrameStateMeaning':None,'sourceCanonicalVisibleRGBAHash':source['canonicalVisibleRGBAHash'],
        'sourceFrameReference':source['file'],'nativeCellRectLTRB':rect,'nativeCellSize':[side,side],'nativeCellAlphaExtrema':[255,255],
        'exports':{},'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False}
    for density in [1,4]:
        folder=OUT/('frames-logical-x1' if density==1 else 'frames-compatible-x4');folder.mkdir(exist_ok=True)
        size=tuple(v*density for v in source['sourceFrameSize']);result=tile.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
        assert result.getchannel('A').getextrema()==(255,255)
        file=folder/f'frame-{source["frameIndex"]:03d}.png';result.save(file)
        export={'file':file.relative_to(ROOT).as_posix(),'sha256':sha(file),'decodedRGBAHashForOwnExport':hashlib.sha256(result.tobytes()).hexdigest(),
            'width':size[0],'height':size[1],'mode':'RGBA','alphaExtrema':[255,255],'exportDensity':density,
            'sourceElementId':a.element,'sourceFrameIndex':source['frameIndex'],'sourceFrameSize':source['sourceFrameSize'],
            'sourceFrameOffset':source['sourceFrameOffset'],'sourceMapElemOffset':context['sourceMapElemOffset'],'combinedRenderOrigin':None,
            'derivedFrom':{'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generationRecord':str(target.relative_to(ROOT))+'.generation.json'},
            'operation':{'type':'exact complete native square cell crop + uniform PMA resize','sourceRectLTRB':rect,'uniformScale':size[0]/side,
                'resampled':True,'newModelGeneration':False,'alphaNormalizationPerformed':False,'interiorSquareSearchPerformed':False,
                'nonUniformStretch':False,'componentsMovedOrSynthesized':False,'resizeAlpha':'RGBa premultiplied -> Lanczos -> RGBA'},
            'nativeGenerationClaimForExport':False,'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'seamlessVerified':False,'runtimeIntegrated':False}
        save(Path(str(file)+'.source.json'),export);item['exports'][str(density)]=export
        if density==4:preview.paste(result,(ordinal*360+100,80),result)
    draw.text((ordinal*360+15,20),f'ID{a.element} source frame{source["frameIndex"]}',fill=(30,50,40));frames.append(item)
preview.save(OUT/'frame-preview.png')
summary={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':a.element,'family':a.family,'batch':a.batch,
    'sourceResourcePath':context['sourceResourcePath'],'sourceRawSHA256':context['sourceRawSHA256'],
    'sourceDeclaredFrameCount':context['sourceDeclaredFrames'],'sourceDeclaredDirections':context['sourceDeclaredDirections'],
    'sourceFrameIndices':[s['frameIndex']for s in sources],'ownRepresentativeFramesGenerated':len(frames),'frameBindingsProduced':len(frames),
    'actualNativeAtlasSize':list(atlas.size),'selectedNativeAtlas':target.relative_to(ROOT).as_posix(),'atlasGrid':[a.columns,rows],
    'nativeSquareCellSize':[side,side],'opaqueSourceAndOwnExports':True,'alphaNormalizationPerformed':False,'interiorSquareSearchPerformed':False,
    'sourceFootprintCells':context['sourceFootprintCells'],'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceGridAttr':context['sourceGridAttr'],
    'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,
    'allResourceFramePositionsPresent':context['allResourceFramesDecoded'],'frames':frames,
    'uniqueOwnRGBAFrames':{str(d):len({f['exports'][str(d)]['decodedRGBAHashForOwnExport']for f in frames})for d in[1,4]},
    'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'seamlessVerified':False,'runtimeIntegrated':False,
    'mainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,
    'pending':['exact source stripe/seam positions and cross-phase material stability unaccepted','edge continuity against neighboring tiles unverified','native timing/state meaning/loop/combined render origin unknown']}
save(OUT/'sequence.json',summary)
(OUT/'README.md').write_text(f'# {a.element} {a.batch} 满格方形帧候选\n\n源帧位 '+','.join(str(s['frameIndex'])for s in sources)+f'，共{context["sourceDeclaredFrames"]}原始帧中的{len(frames)}帧。本批母图真实原生{atlas.width}×{atlas.height}、{a.columns}列×{rows}行，每格原生{side}²；40²与160²是整格裁切后等比PMA派生。源与输出alpha均255，无alpha规范化、透明立物fit、内接方形搜索、非均匀拉伸或程序移部件。\n\n逐图记录见母图同名generation.json，配置目标Sunburst/max，实际型号/质量未披露为null。实际附own master、所选源帧结构、两主风格；续批可另附同资源先前母图仅作材质连续性。source frameOffset与mapElemOffset分别保留，不推相加；组合原点/时序/loop均null。\n\n格栅/轨道条带与边轨接缝的精确位置、跨帧材质一致性、邻接拼缝未验收。accepted/stateCorrespondence/seamless/runtime均false，不等于完整可运行机关。未改主art/index/runtime，未本地测试/浏览器/Git。\n',encoding='utf-8')
print(json.dumps({'elementId':a.element,'batch':a.batch,'native':list(atlas.size),'nativeCell':[side,side],'indices':summary['sourceFrameIndices'],'uniqueOwnRGBAFrames':summary['uniqueOwnRGBAFrames'],'alpha':[255,255],'accepted':False}))
