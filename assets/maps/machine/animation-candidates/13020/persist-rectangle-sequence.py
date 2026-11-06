"""Record/export one <=6-frame opaque rectangular atlas with exact native proportions."""
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[5];IMAGE=Path('D:/work/image')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--element',type=int,required=True);p.add_argument('--family',required=True)
p.add_argument('--version',required=True);p.add_argument('--host',type=Path,required=True);p.add_argument('--structure',required=True);p.add_argument('--previous')
a=p.parse_args();OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}'
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'));sources=context['sourceFrames'];assert 1<=len(sources)<=6
assert all(not s['structuralEmpty'] and s['alphaExtrema']==[255,255] for s in sources)
own=ROOT/context['currentOwnMaster']['file'];structure=ROOT/a.structure;styles=[IMAGE/'designs/mail-ui-v1/01-mail-event.png',IMAGE/'designs/team-ui-v2/team-ui-v2.png']
previous=OUT/f'sequence-{a.previous}.png'if a.previous else None
refs=[previous,structure,own,*styles]if previous else [own,structure,*styles]
roles=['exact own atlas AI edit','actual selected full-rectangle source geometry','current own identity/material master','primary Daoist Q style','primary Daoist Q style']if previous else ['current own identity/material master','actual selected full-rectangle source geometry','primary Daoist Q style','primary Daoist Q style']
target=OUT/f'sequence-{a.version}.png';assert not target.exists();shutil.copyfile(a.host,target)
stored=Image.open(target);stored_mode=stored.mode;atlas=stored.convert('RGBA');assert atlas.getchannel('A').getextrema()==(255,255)
assert atlas.width%len(sources)==0;cell_width=atlas.width//len(sources)
assert all(cell_width*s['sourceFrameSize'][1]==atlas.height*s['sourceFrameSize'][0]for s in sources),'Native full rectangles do not match source aspect; never stretch or interior-crop shorelines.'
record={'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generatedAt':datetime.fromtimestamp(a.host.stat().st_mtime,timezone.utc).isoformat(),
    'generatedAtEvidence':'host output last-write timestamp','recordedAtUTC':datetime.now(timezone.utc).isoformat(),
    'width':atlas.width,'height':atlas.height,'storedMode':stored_mode,'alphaExtrema':[255,255],
    'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False,'promptFile':(OUT/f'prompt-{a.version}.txt').relative_to(ROOT).as_posix(),'referenced_image_paths':[str(x)for x in refs]},
    'actualModel':None,'actualQuality':None,'unverifiedReason':'Host does not expose model/quality selection or verified returned metadata.',
    'hostOutputFile':str(a.host),'officialCheckRecord':'docs/IMAGE_CONFIG_VERIFICATION_20261028.md',
    'references':[{'file':str(x),'sha256':sha(x),'role':role,'actuallyAttached':True}for x,role in zip(refs,roles)],
    'operation':'AI edit complete opaque rectangular atlas'if previous else'new source-corresponding opaque rectangular phase atlas',
    'sourceFrameIndices':[s['frameIndex']for s in sources],'sourceContext':(OUT/'source-context.json').relative_to(ROOT).as_posix(),
    'resampled':False,'accepted':False,'runtimeIntegrated':False}
if previous:record['editedFrom']={'file':previous.relative_to(ROOT).as_posix(),'sha256':sha(previous),'generationRecord':str(previous.relative_to(ROOT))+'.generation.json'}
save(Path(str(target)+'.generation.json'),record)
frames=[];preview=Image.new('RGB',(260*len(sources),1150),(230,234,229));draw=ImageDraw.Draw(preview)
for ordinal,source in enumerate(sources):
    rect=[ordinal*cell_width,0,(ordinal+1)*cell_width,atlas.height];cut=atlas.crop(rect)
    item={'sourceFrameIndex':source['frameIndex'],'sourceFrameSize':source['sourceFrameSize'],'sourceFrameOffset':source['sourceFrameOffset'],
        'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceFootprintCells':context['sourceFootprintCells'],'sourceGridAttr':context['sourceGridAttr'],
        'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'nativeFrameStateMeaning':None,
        'structuralEmpty':False,'sourceFullyTransparentPixels':False,'sourceFrameReference':source['file'],
        'sourceCanonicalVisibleRGBAHash':source['canonicalVisibleRGBAHash'],'nativeCompleteCellRect':rect,
        'nativeCellSize':[cell_width,atlas.height],'nativeFullRectangleAspectError':0,'nativeAlphaExtrema':[255,255],
        'exports':{},'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False}
    for density in[1,4]:
        folder=OUT/('frames-logical-x1'if density==1 else'frames-compatible-x4');folder.mkdir(exist_ok=True)
        size=tuple(n*density for n in source['sourceFrameSize']);scale=size[0]/cell_width
        assert abs(atlas.height*scale-size[1])<1e-9
        result=cut.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA');assert result.getchannel('A').getextrema()==(255,255)
        file=folder/f'frame-{source["frameIndex"]:03d}.png';result.save(file)
        export={'file':file.relative_to(ROOT).as_posix(),'sha256':sha(file),'decodedRGBAHashForOwnExport':hashlib.sha256(result.tobytes()).hexdigest(),
            'width':size[0],'height':size[1],'mode':'RGBA','alphaExtrema':[255,255],'exportDensity':density,
            'sourceElementId':a.element,'sourceFrameIndex':source['frameIndex'],'sourceFrameSize':source['sourceFrameSize'],
            'sourceFrameOffset':source['sourceFrameOffset'],'sourceMapElemOffset':context['sourceMapElemOffset'],
            'sourceFootprintCells':context['sourceFootprintCells'],'sourceGridAttr':context['sourceGridAttr'],'combinedRenderOrigin':None,
            'derivedFrom':{'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'generationRecord':str(target.relative_to(ROOT))+'.generation.json'},
            'operation':{'type':'exact complete native rectangular column crop + strictly uniform PMA resize',
                'sourceRectLTRB':rect,'uniformScale':scale,'resampled':True,'newModelGeneration':False,
                'alphaNormalizationPerformed':False,'alphaFitPerformed':False,'interiorSquareSearchPerformed':False,
                'nonUniformStretch':False,'componentsMovedOrSynthesized':False,'resizeAlpha':'RGBa premultiplied -> Lanczos -> RGBA'},
            'actualNativeCellSize':[cell_width,atlas.height],'nativeGenerationClaimForExport':False,
            'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'seamlessVerified':False,'runtimeIntegrated':False}
        save(Path(str(file)+'.source.json'),export);item['exports'][str(density)]=export
        if density==4:
            display=result.convert('RGBa').resize((240,1040),Image.Resampling.LANCZOS).convert('RGBA')
            preview.paste(display,(ordinal*260+10,60),display)
    draw.text((ordinal*260+10,20),f'ID{a.element} frame{source["frameIndex"]}',fill=(30,50,40));frames.append(item)
preview.save(OUT/'frame-preview.png')
summary={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':a.element,'family':a.family,
    'sourceResourcePath':context['sourceResourcePath'],'sourceRawSHA256':context['sourceRawSHA256'],
    'sourceDeclaredFrameCount':context['sourceDeclaredFrames'],'sourceDeclaredDirections':context['sourceDeclaredDirections'],
    'sourceFrameIndices':[s['frameIndex']for s in sources],'ownRepresentativeFramesGenerated':len(frames),'frameBindingsProduced':len(frames),
    'actualNativeAtlasSize':list(atlas.size),'selectedNativeAtlas':target.relative_to(ROOT).as_posix(),
    'nativeCompleteColumnSize':[cell_width,atlas.height],'nativeSourceDensityRatio':cell_width/sources[0]['sourceFrameSize'][0],
    'sourceAndOwnAlphaExtrema':[255,255],'nativeFullRectangleAspectError':0,
    'sourceFootprintCells':context['sourceFootprintCells'],'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceGridAttr':context['sourceGridAttr'],
    'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,
    'allResourceFramePositionsPresent':context['allResourceFramesDecoded'],'frames':frames,
    'uniqueOwnRGBAFrames':{str(d):len({f['exports'][str(d)]['decodedRGBAHashForOwnExport']for f in frames})for d in[1,4]},
    'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'seamlessVerified':False,'runtimeIntegrated':False,
    'mainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,'preview':(OUT/'frame-preview.png').relative_to(ROOT).as_posix(),
    'previewIsDiagnosticComposite':True,'pending':['internal bank/slat geometry versus source and fixed-detail stability not accepted','per-source water/glow phases unaccepted','neighbor/map boundaries unverified','source lookup/timing/state meaning/loop/combined render origin unknown']}
save(OUT/'sequence.json',summary)
(OUT/'README.md').write_text(f'# {a.element} 满幅矩形水渠六帧候选\n\n《灵葫大作战》生产候选。源六帧各120×520，footprint{context["sourceFootprintCells"]}、源frameOffset逐帧见sequence.json、mapElemOffset独立{context["sourceMapElemOffset"]}及GridAttr{context["sourceGridAttr"]}分别保留。真实原生母图{atlas.width}×{atlas.height}、六完整列各{cell_width}×{atlas.height}，原生比严格等于120:520，等比密度{cell_width/120}；不是原生480×2080。原生RGB→RGBA的alpha天然255，无alpha规范化、透明fit、内接矩形搜索、岸线裁边或非均匀拉伸。\n\n导出120×520与480×2080均为完整原生列裁取后严格等比PMA派生，4倍表示输出密度，不冒称模型原生细节。逐图generation.json实际submitted transparent_background=false，目标Sunburst/max，工具未披露实际型号/质量为null；实际附own master、源满幅六列结构及两主风格。\n\n六个源可见像素各不同，六个own候选各不同。内渠/岸线/跨条板固定形状与源的对应、水光相位、边界拼缝和模型细节跨帧稳定未验收；外矩形比例与全不透明通过记录不代表内部几何或状态通过。accepted/geometry/stateCorrespondence/seamless/runtime仍false，时序/loop/组合原点null。\n\n未改主art/index/runtime/src/Git或冻结三源码；只当前六源必要核图/当张切片，无本地测试/浏览器/全族QA。\n',encoding='utf-8')
print(json.dumps({'id':a.element,'sourceFrames':len(frames),'native':list(atlas.size),'nativeCell':[cell_width,atlas.height],
    'nativeAspectExact':True,'nativeOpacity':[255,255],'sizes4x':[[f['exports']['4']['width'],f['exports']['4']['height']]for f in frames],
    'uniqueOwnRGBA':summary['uniqueOwnRGBAFrames'],'accepted':False}))
