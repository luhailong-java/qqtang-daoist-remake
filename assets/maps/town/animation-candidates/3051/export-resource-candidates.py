"""Export one explicit resource's source-frame-position candidates, whole poses only."""
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parents[5]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--element',type=int,required=True);p.add_argument('--family',required=True);p.add_argument('--version',required=True);p.add_argument('--batch')
a=p.parse_args();OUT=ROOT/f'assets/maps/{a.family}/animation-candidates/{a.element}'
if a.batch:
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',a.batch)
    OUT=OUT/a.batch
context=json.loads((OUT/'source-context.json').read_text(encoding='utf-8'));check=json.loads((OUT/f'native-check-{a.version}.json').read_text(encoding='utf-8'))
mother=OUT/f'sequence-{a.version}.png';atlas=Image.open(mother).convert('RGBA');assert list(atlas.size)==check['actualNativeAtlasSize']
cuts={};source_by_id={f['frameIndex']:f for f in context['sourceFrames']}
for row in check['frames']:
    index=row['sourceFrameIndex'];b=row['localAlpha8BBox'];cell=row['cellRect']
    rect=[max(0,cell[0]+b[0]-4),max(0,b[1]-4),min(atlas.width,cell[0]+b[2]+4),min(atlas.height,b[3]+4)]
    cuts[index]=(rect,atlas.crop(rect))
logical_scale=min(min(source_by_id[i]['sourceFrameSize'][0]/im.width,source_by_id[i]['sourceFrameSize'][1]/im.height)for i,(_,im)in cuts.items())
records=[];generated={};preview_width=360*len(context['sourceFrames']);preview=Image.new('RGB',(preview_width,1000),(231,234,230));draw=ImageDraw.Draw(preview)
for ordinal,source in enumerate(context['sourceFrames']):
    index=source['frameIndex'];alias=source.get('exactVisibleAliasOfFrameIndex');empty=source['structuralEmpty']or source.get('fullyTransparentPixels',False)
    record={'sourceFrameIndex':index,'sourceFrameSize':source['sourceFrameSize'],'sourceFrameOffset':source['sourceFrameOffset'],
        'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceFootprintCells':context['sourceFootprintCells'],'sourceGridAttr':context['sourceGridAttr'],
        'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'nativeFrameStateMeaning':None,
        'sourceFrameReference':source.get('file'),'sourceCanonicalVisibleRGBAHash':source.get('canonicalVisibleRGBAHash'),
        'structuralEmpty':source['structuralEmpty'],'sourceFullyTransparentPixels':source.get('fullyTransparentPixels'),
        'pixelAliasOfFrameIndex':alias,'exports':{},'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False}
    for density in[1,4]:
        folder=OUT/('frames-logical-x1'if density==1 else'frames-compatible-x4');folder.mkdir(exist_ok=True)
        if empty:
            record['exports'][str(density)]={'file':None,'sourceFrameIndex':index,'reason':'source structural/alpha empty; no invented visible art','sourceFrameOffset':source['sourceFrameOffset'],'sourceMapElemOffset':context['sourceMapElemOffset']}
            continue
        if alias is not None:
            base=generated[(alias,density)]
            binding={'sourceFrameIndex':index,'file':base['file'],'pixelAliasOfFrameIndex':alias,
                'pngReusedWithoutPixelModification':True,'sourceFrameSize':source['sourceFrameSize'],
                'sourceFrameOffset':source['sourceFrameOffset'],'sourceMapElemOffset':context['sourceMapElemOffset'],'combinedRenderOrigin':None,
                'offsetsKeptIndependentFromSharedPNG':True,'accepted':False,'runtimeIntegrated':False}
            save(folder/f'frame-{index:03d}.binding.json',binding);record['exports'][str(density)]=binding;generated[(index,density)]=base
            if density==4:
                display=Image.open(ROOT/base['file']).convert('RGBA')
                if display.width>320 or display.height>420:
                    d=min(320/display.width,420/display.height);display=display.convert('RGBa').resize((round(display.width*d),round(display.height*d)),Image.Resampling.LANCZOS).convert('RGBA')
                x=ordinal*360;draw.text((x+12,16),f'ID{a.element} frame{index} / PNG alias {alias}',fill=(30,50,40))
                preview.paste(display,(x+(360-display.width)//2,55),display)
                draw.rectangle((x+10,500,x+350,970),fill=(30,44,42));preview.paste(display,(x+(360-display.width)//2,525),display)
            continue
        rect,cut=cuts[index];w,h=source['sourceFrameSize'];target=(w*density,h*density);scale=logical_scale*density
        size=(max(1,round(cut.width*scale)),max(1,round(cut.height*scale)))
        resized=cut.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
        result=Image.new('RGBA',target);placement=((target[0]-size[0])//2,target[1]-size[1]);result.alpha_composite(resized,placement)
        file=folder/f'frame-{index:03d}.png';result.save(file);alpha=result.getchannel('A');bbox=alpha.point(lambda v:255 if v>8 else 0).getbbox()
        edge_count=sum(alpha.getpixel((x,0))>8 or alpha.getpixel((x,result.height-1))>8 for x in range(result.width))+sum(alpha.getpixel((0,y))>8 or alpha.getpixel((result.width-1,y))>8 for y in range(1,result.height-1))
        item={'file':file.relative_to(ROOT).as_posix(),'sha256':sha(file),'decodedRGBAHashForOwnExport':hashlib.sha256(result.tobytes()).hexdigest(),
            'width':result.width,'height':result.height,'mode':'RGBA','alphaExtrema':list(alpha.getextrema()),'alpha8BBox':list(bbox)if bbox else None,'alpha8EdgeCount':edge_count,
            'sourceElementId':a.element,'sourceFrameIndex':index,'sourceFrameSize':source['sourceFrameSize'],'sourceFrameOffset':source['sourceFrameOffset'],
            'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceFootprintCells':context['sourceFootprintCells'],'sourceGridAttr':context['sourceGridAttr'],'combinedRenderOrigin':None,
            'derivedFrom':{'file':mother.relative_to(ROOT).as_posix(),'sha256':sha(mother),'generationRecord':str(mother.relative_to(ROOT))+'.generation.json'},
            'operation':{'type':'whole-frame alpha8 crop+4native-pixel guard, shared uniform PMA resize, bottom-center registration',
                'sourceRectLTRB':rect,'uniformScale':scale,'resizedSize':list(size),'placementPx':list(placement),
                'resizeAlpha':'RGBa premultiplied -> Lanczos -> RGBA','resampled':True,'newModelGeneration':False,'nonUniformStretch':False,'componentsMovedOrSynthesized':False},
            'exportDensity':density,'actualNativeAtlasSize':list(atlas.size),'nativeGenerationClaimForExport':False,
            'layoutRegistrationAnchorCandidate':[target[0]/2,target[1]],'layoutAnchorIsNativeClientRoot':False,
            'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'runtimeIntegrated':False}
        save(Path(str(file)+'.source.json'),item);record['exports'][str(density)]=item;generated[(index,density)]=item
        if density==4:
            x=ordinal*360;draw.text((x+12,16),f'ID{a.element} frame{index} / candidate',fill=(30,50,40))
            display=result
            if result.width>320 or result.height>420:
                d=min(320/result.width,420/result.height);display=result.convert('RGBa').resize((round(result.width*d),round(result.height*d)),Image.Resampling.LANCZOS).convert('RGBA')
            preview.paste(display,(x+(360-display.width)//2,55),display)
            draw.rectangle((x+10,500,x+350,970),fill=(30,44,42));preview.paste(display,(x+(360-display.width)//2,525),display)
    records.append(record)
preview.save(OUT/'frame-preview.png')
summary={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':a.element,'family':a.family,
    'sourceResourcePath':context['sourceResourcePath'],'sourceRawSHA256':context['sourceRawSHA256'],'sourceDeclaredFrameCount':context['sourceDeclaredFrames'],
    'sourceDeclaredDirections':context['sourceDeclaredDirections'],'sourceFrameIndices':[f['frameIndex']for f in context['sourceFrames']],
    'ownRepresentativeFramesGenerated':len(cuts),'frameBindingsProduced':len(records),'actualNativeAtlasSize':list(atlas.size),'selectedNativeAtlas':mother.relative_to(ROOT).as_posix(),
    'sourceFootprintCells':context['sourceFootprintCells'],'sourceMapElemOffset':context['sourceMapElemOffset'],'sourceGridAttr':context['sourceGridAttr'],'combinedRenderOrigin':None,
    'nativeFrameTimingMs':None,'loopPolicy':None,'nativeFrameStateMeaning':None,'allResourceFramePositionsPresent':context['allResourceFramesDecoded'],
    'sourcePixelAliasMappingPreserved':True,'PNGReuseAndPerFrameOffsetsSeparated':True,'perResourceLogicalUniformScale':logical_scale,
    'uniqueOwnRGBAFrames':{str(d):len({r['decodedRGBAHashForOwnExport']for (i,dn),r in generated.items()if dn==d})for d in[1,4]},
    'nativeVisibleAspectRatioErrors':{str(r['sourceFrameIndex']):r['visibleAspectRatioRelativeError']for r in check['frames']},
    'frames':records,'accepted':False,'geometryAccepted':False,'stateCorrespondenceAccepted':False,'nativePlaybackAccepted':False,'runtimeIntegrated':False,
    'mainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,
    'preview':(OUT/'frame-preview.png').relative_to(ROOT).as_posix(),'previewIsDiagnosticComposite':True,
    'pending':['source state appearance fidelity and AI detail consistency unaccepted','exact source silhouette/geometry and target-size alpha still need review','native timing, loop/direction meaning and render origin unknown']}
save(OUT/'sequence.json',summary)
lines=[f'# {a.element}全帧位原创候选','',f'2026-10-28。实际核图{len(context["sourceFrames"])}个源帧位，生成{len(cuts)}个不同可见内容的自有候选，保留{len(records)}个原始帧索引/offset记录。主art/index/runtime未改；本文件不是正式验收。','',
       f'当前母图`sequence-{a.version}.png`真实原生{atlas.width}×{atlas.height}，记录在同名`.generation.json`；内置目标Sunburst/max，实际型号/质量未披露为null。源结构板、当前own master及image两主风格均实际附图；修图另附前一母图。','',
       '源原生小帧与逐帧解码/可见像素归组证据见`source-context.json`。相同可见像素仅复用PNG，每帧index与DIMG frameOffset仍独立；mapElemOffset另存，组合渲染原点为null，未推两者相加。','',
       '导出`frames-logical-x1/`对应每个源帧自身宽高，`frames-compatible-x4/`为各自4倍兼容画布。全部派生于当前母图；整帧裁切、统一等比PMA缩放、整帧底部居中注册，没有非均匀拉伸、程序移部件或把静态变换声称新画。原生母图与派生尺寸分别记录。','',
       '当前尺寸/独立帧/alpha边界结果见`sequence.json`；预览`frame-preview.png`为浅深底诊断合成，不是游戏截图。四周无触边不等于源轮廓或状态对应通过；模型重画的小幅细节变化、源亮斑/形状对应、真实时序/循环/方向和组合渲染原点仍待核实。','',
       '仅此资源必要小批源像素与当前图导出，未全45解码/QA，未本地测试、浏览器或Git。全部accepted/geometry/stateCorrespondence/runtime仍false，冻结的三个源码文件未动。','']
(OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'id':a.element,'sourceFrameCount':context['sourceDeclaredFrames'],'bindings':len(records),'ownRepresentativeFrames':len(cuts),'nativeAtlas':list(atlas.size),
    'uniqueOwnRGBA':summary['uniqueOwnRGBAFrames'],'alpha8EdgeCounts4x':[r['exports']['4'].get('alpha8EdgeCount')for r in records],
    'sizes4x':[[r['exports']['4'].get('width'),r['exports']['4'].get('height')]for r in records],'accepted':False},ensure_ascii=True))
