"""Export/replay seventeen original lobby controls without client installation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name,relative):
    spec = importlib.util.spec_from_file_location(name,ROOT/relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ART = module('lobbyextra_art','scripts/native-ui-lobbyextra-art.py')
HELP = module('lobbyextra_export_helpers','assets/native-client-ui/common-reference/export-common.py')
FONT = Path('C:/Windows/Fonts/msyh.ttc')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def nonpixels(before,after,metadata):
    if len(before) != len(after):
        raise ValueError('Native lobby container length changed')
    left,right = bytearray(before),bytearray(after)
    for frame in metadata['frames']:
        if frame['empty']:
            continue
        start,length = frame['pixelDataOffset'],frame['pixelByteLength']
        left[start:start+length] = bytes(length)
        right[start:start+length] = bytes(length)
    if left != right:
        raise ValueError('Native nonpixel bytes, positions or offsets changed')


def preview(items,check):
    heights = [max(140*((len(item['frames'])+4)//5),240 if max(f['height'] for f in item['frames'])>70 else 0)
               for item in items]
    board = Image.new('RGB',(1200,sum(heights)),'#eae3d1')
    draw,font,top = ImageDraw.Draw(board),ImageFont.load_default(size=14),0
    for item,height in zip(items,heights,strict=True):
        draw.text((6,top+3),item['nativePath']+' / pending user review',font=font,fill='#214b3c')
        for n,frame in enumerate(item['frames']):
            picture = Image.open(ROOT/frame['file']).convert('RGBA')
            scale = min(3,208/picture.width,(height-44)/picture.height,100/picture.height if len(item['frames'])>5 else 10)
            picture = HELP.scaled(picture,tuple(max(1,round(v*scale)) for v in picture.size))
            x,y = 6+(n%5)*238,top+(n//5)*140
            draw.text((x,y+21),f"raw{frame['index']} off{tuple(frame['frameOffset'])}",font=font,fill='#214b3c')
            board.paste(picture,(x+8,y+42),picture)
        top += height
    path = HERE/'candidate-all-states.png'
    HELP.png(path,board,check)
    return record(path)


def glyph_contract(resource,source,check):
    if source['metadata']['declaredCanvas'] != [11,14] or len(source['metadata']['frames']) != 10:
        raise ValueError('Native number canvas or position count differs')
    glyphs = []
    for frame,(size,offset),export in zip(source['metadata']['frames'],ART.DIGIT_LAYOUT,resource['frames'],strict=True):
        if (frame['width'],frame['height']) != size or tuple(frame['frameOffset']) != offset:
            raise ValueError('Native cropped digit layout changed')
        with Image.open(ROOT/export['file']) as picture:
            bbox = picture.getchannel('A').getbbox()
        if not bbox or not (0<=bbox[0]<bbox[2]<=size[0] and 0<=bbox[1]<bbox[3]<=size[1]):
            raise ValueError('Empty or clipped own digit')
        logical = [bbox[0]+offset[0],bbox[1]+offset[1],bbox[2]+offset[0],bbox[3]+offset[1]]
        glyphs.append({'sourceFrameIndex':frame['index'],'character':str(frame['index']),
                       'sourceSize':list(size),'sourceOffset':list(offset),'ownNativeInkBounds':list(bbox),
                       'ownDeclaredCanvasInkBounds':logical,'preview':{k:export[k] for k in ('file','sha256')},
                       'sourceAlphaReused':False})
    path = HERE/'glyph-layout.json'
    HELP.write_json(path,{'schemaVersion':1,'nativePath':resource['nativePath'],'sourceDeclaredCanvas':[11,14],
       'sourceFrameOrder':'0123456789','fontFamily':'Microsoft YaHei','fontSize':13,'strokeWidth':1,
       'fontSha256':sha(FONT.read_bytes()),'uiEvidence':record(HERE/'ui-evidence.json'),'glyphs':glyphs,
       'operation':'New own glyph raster, each full ink extent centered in the unchanged original native cropped frame; no per-glyph scale.',
       'runtimeSpacingVerified':False,'visualAccepted':False},check)
    return record(path)


def check_chat_contrast(items,check):
    evidence_path = HERE/'ui-evidence.json'
    evidence = json.loads(evidence_path.read_bytes())
    rgba = evidence['explicitChatForeground']['literalAssignments']['drawcolor']
    def luminance(rgb):
        channels=[v/255 for v in rgb]
        linear=[v/12.92 if v<=0.04045 else ((v+.055)/1.055)**2.4 for v in channels]
        return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722),strict=True))
    rows=[]
    for item in items:
        if item['rendererKind'] not in ('lobbyextra-chatmax','lobbyextra-chatmin','lobbyextra-chatnormal'):
            continue
        frame=item['frames'][0]
        with Image.open(ROOT/frame['file'])as picture:
            background=picture.convert('RGBA').getpixel((100,60))
        opacity=background[3]/255
        # The lightest underlay is the worst case for this light foreground.
        composited=[round(v*opacity+255*(1-opacity))for v in background[:3]]
        ratio=(luminance(rgba[:3])+.05)/(luminance(composited)+.05)
        if ratio<4.5:
            raise ValueError('Native cyan default foreground loses contrast on chat field')
        rows.append({'nativePath':item['nativePath'],'point':[100,60],'nativeBackgroundRgba':list(background),
                     'lightestUnderlayCompositeRgb':composited,'explicitSourceDefaultForeground':rgba,'contrastRatio':ratio})
    path=HERE/'chat-contrast.json'
    HELP.write_json(path,{'schemaVersion':1,'sourceEvidence':record(evidence_path),'samples':rows,
       'scope':'Default explicit cyan only; per-message runtime color updates and actual composition remain unverified',
       'nativeRuntimeVerified':False,'visualAccepted':False},check)
    return record(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    check=parser.parse_args().check
    source_path=HERE/'manifest.json'
    source=json.loads(source_path.read_bytes())
    by_path={r['nativePath'].casefold():r for r in source['resources']}
    if set(by_path)!={p.casefold()for p in ART.PATHS}:
        raise ValueError('Native lobby source scope differs')
    package_path=ROOT/source['source']['package']['file']
    if record(package_path)!=source['source']['package']:
        raise ValueError('Pinned native package differs')
    package=package_path.read_bytes()
    paint_inputs={key:value for key,value in HELP.ROOT_PAINTS.items() if key in ('panel','normal','hover','pressed')}
    paint_inputs.update(ART.PAINT_INPUTS)
    paints={key:Image.open(ROOT/path).convert('RGBA')for key,path in paint_inputs.items()}
    items=[]
    alpha_count=0
    for path,(kind,label)in ART.PATHS.items():
        original=by_path[path.casefold()]
        raw,compressed=HELP.CODEC.reader.unpack_resource(package,original['packageEntry'])
        if sha(raw)!=original['sourceSha256'] or compressed!=original['compressedSha256']:
            raise ValueError('Source native lobby image differs')
        pictures={f['index']:ART.render(kind,label,f['index'],(f['width'],f['height']),paints,FONT,HELP.nine_slice,HELP.scaled)
                  for f in original['metadata']['frames']if not f['empty']}
        output,metadata,decoded=HELP.CODEC.replace_frames(raw,pictures)
        nonpixels(raw,output,metadata)
        target=HERE/'patch'/path
        if check:
            if target.read_bytes()!=output:
                raise ValueError('Native lobby output replay differs')
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(output)
        frames=[]
        for frame,image in decoded:
            png=HERE/'decoded'/f"{Path(path).stem}-{frame['index']:02}.png"
            HELP.png(png,image,check)
            structural=None
            if kind!='lobbyextra-digit':
                input_path=ROOT/ART.STRUCTURAL_ALPHA_INPUTS[f"{kind}-{frame['index']}"]
                with Image.open(input_path)as alpha_source:
                    if alpha_source.getchannel('A').tobytes()!=image.getchannel('A').tobytes():
                        raise ValueError('Functional source lobby Alpha changed after native encoding')
                structural=record(input_path)
                alpha_count+=1
            frames.append({**record(png),'index':frame['index'],'width':image.width,'height':image.height,
                           'frameOffset':frame['frameOffset'],'pixelMode':frame['pixelMode'],
                           'structuralAlphaInput':structural,'decodedRgbaSha256':sha(image.tobytes()),
                           'decodedAlphaSha256':sha(image.getchannel('A').tobytes()),
                           'alphaOperation':'Own new glyph raster'if kind=='lobbyextra-digit'else'Exact source structural Alpha'})
        items.append({**record(target),'nativePath':path,'sourceSha256':original['sourceSha256'],
                      'sourcePacked':True,'sourceLoose':False,'rendererKind':kind,'caption':label,'frames':frames,
                      'allNonPixelBytesIdenticalToSource':True,'visualAccepted':False,'nativeRuntimeVerified':False})
    if alpha_count!=31 or len(items)!=17 or sum(len(i['frames'])for i in items)!=41:
        raise ValueError('Native lobby counts differ')
    number=next(i for i in items if i['rendererKind']=='lobbyextra-digit')
    glyphs=glyph_contract(number,by_path[number['nativePath'].casefold()],check)
    contrast=check_chat_contrast(items,check)
    result={'schemaVersion':1,'scope':'All17 remaining selRoom original-art resources;41 source positions',
      'sourceReferences':record(source_path),'uiEvidence':record(HERE/'ui-evidence.json'),'glyphContract':glyphs,
      'chatContrast':contrast,'items':items,'renderer':record(ROOT/'scripts/native-ui-lobbyextra-art.py'),
      'exporter':record(Path(__file__)),'codec':record(ROOT/'scripts/native-ui-format.py'),
      'exportHelpers':record(ROOT/'assets/native-client-ui/common-reference/export-common.py'),
      'paintInputs':[record(ROOT/p)for p in paint_inputs.values()],
      'font':{'family':'Microsoft YaHei','sha256':sha(FONT.read_bytes())},
      'structuralAlphaInputs':[{'purpose':name,**record(ROOT/path)}for name,path in ART.STRUCTURAL_ALPHA_INPUTS.items()],
      'structuralAlphaPlaneCount':alpha_count,'newOwnGlyphPositions':10,
      'previews':[preview(items,check)],'visualMappingAssumptions':ART.VISUAL_MAPPING_ASSUMPTIONS,
      'newModelGeneration':False,'nativeRuntimeVerified':False,'visualAccepted':False,'installedToClient':False}
    HELP.write_json(HERE/'candidate-manifest.json',result,check)
    print(json.dumps({'nativeResources':len(items),'sourcePositions':41,'exactSourceAlphaPlanes':alpha_count,
                      'newOwnDigitPositions':10,'allHeadersAndOffsetsRetained':True,'nativeReplayChecked':check}))


if __name__=='__main__':
    main()
