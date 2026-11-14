"""Export/replay all94 social/marriage sources using the project native codec."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module);return module


ART=load('socialmarriage_art','scripts/native-ui-socialmarriage-art.py')
HELP=load('socialmarriage_helpers','assets/native-client-ui/common-reference/export-common.py')
CODEC=HELP.CODEC
FONT=Path('C:/Windows/Fonts/msyh.ttc')


def sha(data):return hashlib.sha256(data).hexdigest()
def record(path):return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def check_nonpixels(before,after,metadata):
    if len(before)!=len(after):raise ValueError('Native social container length changed')
    left,right=bytearray(before),bytearray(after)
    for frame in metadata['frames']:
        if frame['empty']:continue
        start,length=frame['pixelDataOffset'],frame['pixelByteLength']
        left[start:start+length]=bytes(length);right[start:start+length]=bytes(length)
    if left!=right:raise ValueError('Native social nonpixel header/offset/footer changed')


def contact(items,check):
    previews=[]
    for page in range(4):
        rows=items[page*24:(page+1)*24]
        heights=[260 if max(f['height']for f in item['frames'])>110 else 140 for item in rows]
        board=Image.new('RGB',(1200,sum(heights)),'#eae3d1');draw=ImageDraw.Draw(board);top=0
        for item,height in zip(rows,heights,strict=True):
            draw.text((5,top+3),item['nativePath']+' / pending review',fill='#214b3c',font=ImageFont.load_default(size=13))
            for frame in item['frames']:
                with Image.open(ROOT/frame['file'])as im:
                    scale=min(2,267/im.width,(height-48)/im.height)
                    image=HELP.scaled(im,tuple(max(1,round(v*scale))for v in im.size))
                x=6+frame['index']*296
                draw.text((x,top+20),f"raw{frame['index']} off{tuple(frame['frameOffset'])}",fill='#214b3c')
                board.paste(image,(x+12,top+37),image)
            top+=height
        path=HERE/f'candidate-all-states-{page+1}.png';HELP.png(path,board,check);previews.append(record(path))
    return previews


def palette(items,check):
    samples,overflows,limits=[],[],[]
    for item in items:
        geometry=ART.layouts()[item['nativePath'].casefold()]
        if not geometry['textFields']:continue
        frame=item['frames'][0];ox,oy=frame['frameOffset']
        with Image.open(ROOT/frame['file'])as picture:
            picture=picture.convert('RGBA')
            for field in geometry['textFields']:
                x,y,w,h=field['rectInBackgroundLogicalSpace'];px,py=x+w//2-ox,y+h//2-oy
                if x-ox<0 or y-oy<0 or x+w-ox>picture.width or y+h-oy>picture.height:
                    overflows.append({'nativePath':item['nativePath'],'scope':field['scope'],'sourceLogicalRect':[x,y,w,h],
                                      'sourceNativeOffset':[ox,oy],'runtimeCropVerified':False})
                if not 0<=px<picture.width or not 0<=py<picture.height:continue
                sample_method='Declared field center'
                if picture.getpixel((px,py))[3]<8:
                    # A source paragraph can extend below its speech bubble.
                    # Record that overflow, and sample an actual visible part
                    # of the unchanged source viewport rather than empty RGBA.
                    candidates=[(xx,yy)for yy in range(max(0,y-oy),min(picture.height,y+h-oy))
                        for xx in range(max(0,x-ox),min(picture.width,x+w-ox))if picture.getpixel((xx,yy))[3]>=8]
                    if not candidates:continue
                    px,py=min(candidates,key=lambda point:abs(point[0]-(x+w//2-ox))+abs(point[1]-(y-oy+12)))
                    sample_method='First-line point within visible source Alpha; full declared overflow remains unverified'
                fg=field['sourceForeground']['value'];background=picture.getpixel((px,py))
                ratios=[]
                for underlay in(0,255):
                    opacity=background[3]/255
                    bg=[round(c*opacity+underlay*(1-opacity))for c in background[:3]]
                    composite=[round((c*fg[3]+b*(255-fg[3]))/255)for c,b in zip(fg[:3],bg,strict=True)]
                    a,b=ART.luminance(composite),ART.luminance(bg)
                    ratios.append((max(a,b)+.05)/(min(a,b)+.05))
                row={'nativePath':item['nativePath'],'scope':field['scope'],'point':[px,py],
                     'sourceForegroundRgba':fg,'nativeBackgroundRgba':list(background),'minimumBlackWhiteUnderlayContrast':min(ratios),'sampleMethod':sample_method,
                     'sourceForegroundEvidence':field['sourceForeground'],'activeControlFlowConfirmed':False}
                samples.append(row)
                if min(ratios)<4.5:limits.append(row)
    result={'schemaVersion':1,'layoutEvidence':record(HERE/'layout-evidence.json'),'samples':samples,
       'sourceRectsExtendingBeyondNativeRaster':overflows,'belowSelectedThreshold':limits,'selectedThreshold':4.5,
       'interpretation':'Native decoded background samples for statically recognized fields only. Source-overflow rectangles remain unchanged. Dynamic/native text, arbitrary colors and active pages remain unverified.',
       'nativeRuntimeVerified':False,'visualAccepted':False}
    path=HERE/'palette-evidence.json';HELP.write_json(path,result,check);return record(path),limits


def illustration_evidence(items,check):
    records=[]
    for key,path in ART.PAINT_INPUTS.items():
        if '/illustrations/'not in path:continue
        file=ROOT/path;metadata=file.with_suffix('.png.generation.json')
        generated=json.loads(metadata.read_bytes())
        if record(file)['sha256']!=generated['sha256']:raise ValueError('Original generated master changed')
        if generated['actualReturnedModel']is not None or generated['actualReturnedQuality']is not None:
            raise ValueError('Unexpected undisclosed built-in model/quality claim')
        with Image.open(file)as image:
            rgba=image.convert('RGBA');bbox=rgba.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
        records.append({'key':key,**record(file),'generation':record(metadata),'actualModel':None,'actualQuality':None,
            'originalMode':generated['mode'],'originalSize':generated['size'],'visibleAlphaAtLeast8Bounds':list(bbox)if bbox else None})
    path=HERE/'illustration-evidence.json'
    value={'schemaVersion':1,'originalModelGenerations':4,'masters':records,
        'generatedPortraitSourceAlphaReused':False,
        'derivedNativeResources':[r['nativePath']for r in items if any(token in r['nativePath'].casefold()for token in('/marriage/bg/','/marriage/priest/','dlg_marriageconfirm'))],
        'operation':'Own returned original RGB scenes fit to native dimensions. Own returned RGBA portraits are visible-bounds fit; no original QQTang portrait or scene RGB/Alpha reused.',
        'nativeRuntimeVerified':False,'visualAccepted':False}
    HELP.write_json(path,value,check);return record(path)


def opacity_evidence(items,source,check):
    native='object/ui/marriage/dlg_priestChat.img'
    item=next(r for r in items if r['nativePath']==native)
    original=next(r for r in source['resources']if r['nativePath']==native.casefold())
    with Image.open(ROOT/original['frames'][0]['file'])as before,Image.open(ROOT/item['frames'][0]['file'])as after:
        a,b=before.getchannel('A').tobytes(),after.getchannel('A').tobytes()
        changed=sum(x!=y for x,y in zip(a,b,strict=True))
        old=before.convert('RGBA').getpixel((98,27));new=after.convert('RGBA').getpixel((98,27))
    value={'schemaVersion':1,'nativePath':native,'sourceFrameIndex':0,'sourceRasterSize':[198,97],
        'sourceDeclaredCanvas':[213,103],'sourceFrameOffset':[7,5],
        'sourceWordsRect':[15,20,180,140],'sourceWordsForegroundRgba':[51,113,149,255],
        'sourceFirstLineRgba':list(old),'ownFirstLineRgba':list(new),'changedAlphaPixels':changed,
        'policy':'Own opaque paper rounded bubble and lower-right tail; original decorative translucency is intentionally replaced. No original character/glyph Alpha is reused.',
        'reason':'204-alpha white alone cannot provide 4.5 contrast for the fixed blue source text over black. Opaque own white supports it. The over-height source text rectangle remains unchanged and needs runtime crop review.',
        'nonpixelHeaderAndGeometryUnchanged':True,'nativeRuntimeVerified':False,'visualAccepted':False}
    path=HERE/'opacity-policy.json';HELP.write_json(path,value,check);return record(path)


def semantic_evidence(items,source,check):
    tga=next(r for r in items if r['format']=='TGA')
    raw=(ROOT/tga['file']).read_bytes();meta,_=CODEC.inspect_native(raw,metadata_only=True)
    value={'schemaVersion':1,'scope':'Native graphic resources only; no original code, text constants or runtime callbacks changed',
       'groups':[{'group':group,'nativeResources':sum(r['nativePath'].casefold().startswith('object/ui/'+group+'/')for r in items),
                  'sourcePositions':sum(len(r['frames'])for r in items if r['nativePath'].casefold().startswith('object/ui/'+group+'/'))}for group in('guidebar','marriage')],
       'sourceReferences':record(HERE/'manifest.json'),'layoutEvidence':record(HERE/'layout-evidence.json'),
       'formats':{'QQF/DIMG':93,'TGA':1},'independentCodeSourceOriginalBytesIncluded':False,
       'tgaCheckmark':{'nativePath':tga['nativePath'],'sourceSize':[10,8],'sourceContainerBytes':364,
          'sourcePixelByteRange':[18,338],'descriptor':meta['frames'][0]['tgaDescriptor'],
          'originalStorageOrigin':'bottom-left','nonpixelPrefixHex':raw[:18].hex(),'nonpixelSuffixHex':raw[-26:].hex(),
          'ownGlyphRaster':True,'originalGlyphAlphaReused':False,'nativeOrientationRoundtripVerified':True},
       'sourceAlphaExact':[r['nativePath']for r in items if r['frames'][0]['functionalAlphaExactlyPreserved']],
       'sourceAlphaPolicy':'Only listed empty masks, progress fills, blank value/menu geometry retain their structural Alpha. All other scene, portrait, caption, icon, checkbox and UI skin pixels are newly composed.',
       'uiOpacityReconstruction':record(HERE/'opacity-policy.json'),
       'sourcePathsWithoutExactLiteralBinding':[r['nativePath']for r in source['resources']if not r['sourceBindings']],
       'pathEvidenceBoundary':'Literal occurrence, prototype inheritance and source image geometry are evidence of source intent, not executed loading. Computed filenames and active branches remain pending.',
       'sourceLayoutAssociations':['Kin member/manager callback-named alternate backgrounds share socialityDlg coordinates',
           'Player info mask is at(-10,-16), so parent fields are translated(+10,+16)',
           'Marriage confirmation backgrounds occur in uiMain alongside the shared marriageConfirmDlg; its brown text remains unchanged'],
       'sourceButtonPositions':'Every raw source position remains. Own normal/gray/bright/pressed materials or pale/jade tab families are assigned per stored family, with no timing values added.',
       'generatedOriginalMasters':4,'derivedIllustrationResources':10,'allGameArtComplete':False,
       'nativeRuntimeVerified':False,'visualAccepted':False,'originalTimingVerified':False}
    path=HERE/'semantic-contract.json';HELP.write_json(path,value,check);return record(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    check=parser.parse_args().check;source_path=HERE/'manifest.json';source=json.loads(source_path.read_bytes())
    original={r['nativePath'].casefold():r for r in source['resources']}
    if set(original)!={p.casefold()for p in ART.PATHS}or len(ART.PATHS)!=94:raise ValueError('Social/marriage source scope changed')
    pkg_path=ROOT/source['source']['package']['file']
    if record(pkg_path)!=source['source']['package']:raise ValueError('Pinned native package changed')
    package=pkg_path.read_bytes()
    paint_paths={k:v for k,v in HELP.ROOT_PAINTS.items()if k in('panel','normal','hover','pressed')};paint_paths.update(ART.PAINT_INPUTS)
    paints={key:Image.open(ROOT/path).convert('RGBA')for key,path in paint_paths.items()}
    items=[];alpha_count=0;format_counts={}
    for native,(kind,label)in ART.PATHS.items():
        ref=original[native.casefold()];raw,compressed=CODEC.reader.unpack_resource(package,ref['packageEntry'])
        if sha(raw)!=ref['sourceSha256']or compressed!=ref['compressedSha256']:raise ValueError('Native source hash changed')
        metadata,_=CODEC.inspect_native(raw,metadata_only=True)
        for frame,source_frame in zip(metadata['frames'],ref['frames'],strict=True):
            with Image.open(ROOT/source_frame['file'])as expected:
                actual=CODEC.decode_native_frame(raw,frame)
                if actual.size!=expected.size or actual.tobytes()!=expected.convert('RGBA').tobytes():raise ValueError('Decoded source orientation/pixels differ')
        pictures={f['index']:ART.render(kind,label,f['index'],(f['width'],f['height']),paints,FONT,HELP.nine_slice,HELP.scaled)
                  for f in metadata['frames']if not f['empty']}
        output,_,decoded=CODEC.replace_frames(raw,pictures);check_nonpixels(raw,output,metadata)
        if output==raw:raise ValueError('Selected resource still has original pixels')
        target=HERE/'patch'/native
        if check:
            if target.read_bytes()!=output:raise ValueError('Native social/marriage export replay differs: '+native)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(output)
        frames=[]
        for frame,image in decoded:
            png=HERE/'decoded'/f"{native.removeprefix('object/ui/').removesuffix('.img').replace('/','__')}-{frame['index']:02}.png"
            HELP.png(png,image,check);stem=native.casefold().removeprefix('object/ui/').removesuffix('.img');alpha_input=None
            if stem in ART.STRUCTURAL_ALPHA_INPUTS:
                alpha_input=record(ROOT/ART.STRUCTURAL_ALPHA_INPUTS[stem])
                if image.getchannel('A').tobytes()!=ART.structural_alpha(stem).tobytes():raise ValueError('Functional source Alpha changed')
                alpha_count+=1
            frames.append({**record(png),'index':frame['index'],'width':image.width,'height':image.height,
                'frameOffset':frame['frameOffset'],'pixelMode':frame['pixelMode'],'decodedRgbaSha256':sha(image.tobytes()),
                'alphaExtrema':list(image.getchannel('A').getextrema()),'functionalAlphaInput':alpha_input,
                'functionalAlphaExactlyPreserved':True if alpha_input else None})
        format_counts[ref['format']]=format_counts.get(ref['format'],0)+1
        items.append({**record(target),'nativePath':native,'format':ref['format'],'sourceSha256':ref['sourceSha256'],
            'sourcePacked':True,'sourceLoose':False,'rendererKind':kind,'caption':label,'frames':frames,
            'allNonpixelBytesIdenticalToSource':True,'originalCharacterOrCaptionAlphaReused':False,
            'sourceBindings':ref['sourceBindings'],'nativeRuntimeVerified':False,'visualAccepted':False})
    if sum(len(i['frames'])for i in items)!=175 or alpha_count!=9:raise ValueError('Social source positions/functional Alpha count differs')
    opacity_record=opacity_evidence(items,source,check)
    palette_record,limits=palette(items,check);illustrations=illustration_evidence(items,check);semantics=semantic_evidence(items,source,check)
    provenance=[]
    for path in ART.PAINT_INPUTS.values():
        for suffix in('.provenance.json','.generation.json'):
            file=ROOT/(path+suffix)
            if file.is_file():provenance.append(record(file))
    result={'schemaVersion':1,'scope':'94 own social/family/profile/covenant native resources;175 source positions',
        'sourceReferences':record(source_path),'layoutEvidence':record(HERE/'layout-evidence.json'),'paletteEvidence':palette_record,
        'illustrationEvidence':illustrations,'opacityPolicy':opacity_record,'semanticContract':semantics,'items':items,'renderer':record(ROOT/'scripts/native-ui-socialmarriage-art.py'),
        'exporter':record(Path(__file__)),'nativeCodec':record(ROOT/'scripts/native-ui-format.py'),
        'exportHelpers':record(ROOT/'assets/native-client-ui/common-reference/export-common.py'),
        'paintInputs':[record(ROOT/path)for path in paint_paths.values()],'paintProvenance':provenance,
        'referenceInputs':[record(ROOT/path)for path in ART.REFERENCE_INPUTS],
        'font':{'family':'Microsoft YaHei','sha256':sha(FONT.read_bytes())},
        'structuralAlphaInputs':[{'purpose':key,**record(ROOT/path)}for key,path in ART.STRUCTURAL_ALPHA_INPUTS.items()],
        'nativeResources':94,'sourcePositions':175,'sourceFormats':format_counts,'functionalAlphaPositions':alpha_count,
        'originalModelGenerations':4,'paletteSamplesBelowSelectedThreshold':len(limits),
        'previews':contact(items,check),'visualMappingAssumptions':ART.VISUAL_MAPPING_ASSUMPTIONS,
        'nativeRuntimeVerified':False,'visualAccepted':False,'installedToClient':False}
    HELP.write_json(HERE/'candidate-manifest.json',result,check)
    print(json.dumps({'nativeResources':94,'sourcePositions':175,'formats':format_counts,'functionalAlphaPositions':alpha_count,
        'paletteBelowThreshold':len(limits),'nativeReplayChecked':check}))


if __name__=='__main__':main()
