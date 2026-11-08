"""Slice the current complete four-prop atlas; uniform PMA whole-frame only."""
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mother=OUT/'sequence-v3.png';generation=Path(str(mother)+'.generation.json')
native_check=json.loads((OUT/'native-check-v3.json').read_text(encoding='utf-8'))
source=json.loads((OUT/'source-frame-provenance.json').read_text(encoding='utf-8'))
current=json.loads((ROOT/'assets/maps/town/art.json').read_text(encoding='utf-8'))
own=next(p for p in current['pieces']if p['elementId']==3050)
assert own['file']=='assets/maps/town/pieces/3050-dragon-lantern.png'
assert sha(ROOT/own['file'])==own['sha256']
atlas=Image.open(mother).convert('RGBA');assert list(atlas.size)==native_check['nativeSize']
cuts=[]
for row in native_check['frames']:
    left,top,right,bottom=row['localAlpha8BBox'];cx,cy,_,_=row['cellRect']
    # The4-pixel crop guard is whole-pose padding, never a component transform.
    rect=[max(0,cx+left-4),max(0,cy+top-4),min(atlas.width,cx+right+4),min(atlas.height,cy+bottom+4)]
    cuts.append((row['frameIndex'],rect,atlas.crop(rect)))
common_size=(max(im.width for _,_,im in cuts),max(im.height for _,_,im in cuts))
frames=[];rgba_hashes={1:[],4:[]};preview=Image.new('RGB',(1280,970),(231,234,230));draw=ImageDraw.Draw(preview)
for index,rect,cut in cuts:
    registered=Image.new('RGBA',common_size)
    registration=((common_size[0]-cut.width)//2,common_size[1]-cut.height)
    registered.alpha_composite(cut,registration)
    source_frame=source['frames'][index]
    item={'sourceFrameIndex':index,'sourceFrameSize':source_frame['sourceFrameSize'],'sourceFrameOffset':source_frame['sourceFrameOffset'],
          'sourceMapElemOffset':[1,60],'sourceFootprintCells':own['sourceFootprintCells'],'sourceGridAttr':[0],
          'combinedRenderOrigin':None,'nativeTimingMs':None,'sourceDirectionMeaning':None,'nativeActionSemantic':None,
          'sourceFrameEvidence':source_frame['file'],'sourceFrameEncodedPixelSHA256':source_frame['encodedPixelSHA256'],
          'nativeAtlasCropLTRB':rect,'wholePoseRegistrationOffsetInCommonCanvas':list(registration),'commonWholePoseCanvasSize':list(common_size),
          'exports':{},'accepted':False,'geometryAccepted':False,'visualStateCorrespondenceAccepted':False}
    for density in[1,4]:
        target_size=(43*density,101*density)
        scale=min(target_size[0]/common_size[0],target_size[1]/common_size[1])
        resize_size=(round(common_size[0]*scale),round(common_size[1]*scale))
        resized=registered.convert('RGBa').resize(resize_size,Image.Resampling.LANCZOS).convert('RGBA')
        result=Image.new('RGBA',target_size);placement=((target_size[0]-resize_size[0])//2,target_size[1]-resize_size[1])
        result.alpha_composite(resized,placement)
        folder=OUT/('frames-logical-x1'if density==1 else'frames-compatible-x4');folder.mkdir(exist_ok=True)
        path=folder/f'frame-{index:03d}.png';result.save(path)
        alpha=result.getchannel('A');bounds=alpha.point(lambda a:255 if a>8 else 0).getbbox()
        edge_count=sum(1 for x in range(result.width)if alpha.getpixel((x,0))>8 or alpha.getpixel((x,result.height-1))>8)+sum(1 for y in range(1,result.height-1)if alpha.getpixel((0,y))>8 or alpha.getpixel((result.width-1,y))>8)
        record={'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'width':result.width,'height':result.height,'mode':'RGBA','alphaExtrema':list(alpha.getextrema()),
            'sourceElementId':3050,'sourceFrameIndex':index,'sourceFrameSize':[43,101],'sourceFrameOffset':source_frame['sourceFrameOffset'],'sourceMapElemOffset':[1,60],'sourceGridAttr':[0],
            'combinedRenderOrigin':None,'derivedFrom':{'file':mother.relative_to(ROOT).as_posix(),'sha256':sha(mother),'generationRecord':generation.relative_to(ROOT).as_posix()},
            'operation':{'type':'whole-pose crop, shared-canvas bottom-center registration, common uniform PMA Lanczos resize',
                'sourceRectLTRB':rect,'cropBoundsMethod':'alpha>8 bounding rect plus4native-pixel guard; no content painting',
                'commonWholePoseCanvasSize':list(common_size),'wholePosePlacementInCommonCanvas':list(registration),
                'uniformScale':scale,'resizedCommonCanvasSize':list(resize_size),'placementPx':list(placement),'resampled':True,
                'newModelGeneration':False,'resizeAlpha':'premultiplied RGBa -> Lanczos -> RGBA','nonUniformStretch':False,'componentsMovedOrSynthesized':False},
            'exportDensity':density,'nativeGenerationSize':list(atlas.size),'nativeResolutionClaimForExport':False,
            'registrationAnchorCandidate':[target_size[0]/2,target_size[1]],'registrationAnchorIsNativeClientRoot':False,
            'alpha8BBox':list(bounds),'alpha8EdgeCount':edge_count,'accepted':False,'geometryAccepted':False,'runtimeIntegrated':False}
        save(Path(str(path)+'.source.json'),record)
        item['exports'][str(density)]=record
        rgba_hashes[density].append(hashlib.sha256(result.tobytes()).hexdigest())
        if density==4:
            x=index*320;draw.text((x+15,15),f'frame {index} / source43x101 / candidate',fill=(30,50,40))
            preview.paste(result,(x+74,50),result)
            draw.rectangle((x+10,480,x+310,940),fill=(30,44,42));preview.paste(result,(x+74,510),result)
    frames.append(item)
preview.save(OUT/'four-frame-preview.png')
report={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':3050,
    'scope':'complete4source frame-position original-art candidate set; not native playback/semantic acceptance',
    'sourceResource':'object\\mapElem\\town\\elem50_stand.img','sourceRawSHA256':source['sourceRawSHA256'],
    'sourceDeclaredFrameCount':4,'sourceDeclaredDirections':1,'sourceFrameIndices':[0,1,2,3],'sourceFrameOffsets':[[0,0]]*4,
    'sourceMapElemOffset':[1,60],'sourceFootprintCells':own['sourceFootprintCells'],'sourceGridAttrAsExisting':[0],
    'combinedRenderOrigin':None,'nativeFrameTimingMs':None,'loopPolicy':None,'frameStateSemantics':None,
    'selectedNativeAtlas':mother.relative_to(ROOT).as_posix(),'actualNativeAtlasSize':list(atlas.size),
    'selectionReason':'single-row v3 permits separate whole-prop crops; v2 row-boundary proximity is not selected',
    'previousOwnStaticMaster':{'file':own['file'],'sha256':own['sha256'],'artManifestUnmodified':True},
    'sourceFramesActuallyViewed':4,'newOriginalArtFramesPresent':4,'fullFramePositionCandidateCoverage':True,
    'uniqueDerivedRGBAFrames':{str(d):len(set(h))for d,h in rgba_hashes.items()},
    'allFourDerivedFramesDifferent':all(len(set(h))==4 for h in rgba_hashes.values()),
    'commonWholePoseCanvasSize':list(common_size),'pixelDensityExports':[1,4],'derivedExportsNativeGenerated':False,
    'frames':frames,'accepted':False,'geometryAccepted':False,'visualStateCorrespondenceAccepted':False,'nativeAnimationContractAccepted':False,
    'runtimeIntegrated':False,'townMainArtChanged':False,'globalManifestChanged':False,'testsOrBrowserRun':False,
    'pending':['v3 visible aspect errors approximately7.6–8.3%; source exact silhouette fidelity not accepted',
               'four AI redraws retain small shape/ornament/brightness variation requiring visual state consistency review',
               'alpha edge/registration and source phase appearance still need target-size/dynamic review',
               'native timing, loop/state meaning and render origin remain unknown; do not invent playback'],
    'preview':'assets/maps/town/animation-candidates/3050/four-frame-preview.png',
    'previewOperation':'diagnostic alpha compositing on light/dark neutral backgrounds; not new art or a client screenshot'}
save(OUT/'sequence.json',report)
save(OUT/'selection.json',{'selected':'v3','reasons':report['selectionReason'],'v1':'narrow; tight row edges','v2':'better ratio but unsafe row-boundary proximity','v3':'complete separated whole poses; current candidate remains unaccepted','accepted':False})
print(json.dumps({'sourceFrameCount':4,'ownCandidateFrames':4,'logicalSize':[43,101],'compatibleSize':[172,404],'actualNativeAtlas':list(atlas.size),
                  'commonCanvas':list(common_size),'uniqueFrames':report['uniqueDerivedRGBAFrames'],'alpha8EdgeCounts4x':[f['exports']['4']['alpha8EdgeCount']for f in frames],
                  'fullFramePositionCandidateCoverage':True,'accepted':False,'townMainArtChanged':False},ensure_ascii=True))
