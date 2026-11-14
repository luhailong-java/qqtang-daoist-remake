"""Export/replay47 loose native controls without install or original execution."""
import argparse
import hashlib
from importlib import util
import json
import math
from pathlib import Path
import zipfile

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ART = module('loose_controls_export_art', 'scripts/native-ui-loose-controls-art.py')
HELP = module('loose_controls_export_helpers', 'assets/native-client-ui/common-reference/export-common.py')
CODEC, FONT = HELP.CODEC, Path('C:/Windows/Fonts/msyh.ttc')


def sha(value): return hashlib.sha256(value).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def alpha_summary(alpha):
    box = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
    return {'sha256': sha(alpha.tobytes()), 'extrema': list(alpha.getextrema()),
            'alpha8BBoxXYXY': list(box) if box else None}


def nonpixels(before, after, metadata):
    a, b = bytearray(before), bytearray(after)
    for frame in metadata['frames']:
        if frame['empty']: continue
        start, length = frame['pixelDataOffset'], frame['pixelByteLength']
        a[start:start + length], b[start:start + length] = bytes(length), bytes(length)
    if a != b: raise ValueError('Loose control nonpixel/header/frame bytes changed')


def reason(family):
    return {
        'numeric': 'Own font/special-sign raster replaces old glyph alpha inside the complete original stored frame, retaining per-glyph crop and offset',
        'gem': 'Own jade/gold faceted gem with distinct gloss samples replaces old decorative gem pixels and silhouette; original14/15 positions retained with unknown timing',
        'chat-button': 'Own smile/horn/message glyph and jade control surface replace old colored icon silhouette; original state slots and crop remain exact',
        'room-chat': 'Own jade-roof room and speech symbol replace old red building icon inside the full original frame',
        'gender': 'Own standard male/female line symbol replaces old color/glyph alpha inside the full original native frame',
        'mode': 'Own whistle or chequered flag preserves the actual observed source symbol role; whole original frame only',
        'file-icon': 'Own file/folder/computer/drive line symbol replaces source icon alpha within unchanged native canvas and offset',
        'server': 'Own small jade/ochre server indicator replaces the original decorative silhouette; observed normal/red distinction retained',
        'network': 'Own font raster replaces source network status letters and arrows; exact native frame geometry retained',
        'hourglass': 'Own jade and gold hourglass replaces old blue decorative icon within complete original crop and offset',
    }[family]


def observed(family, label, index):
    if family == 'numeric':
        if label == '/': value = '/'
        elif index < 10: value = str(index)
        elif label == 'digits-colon': value = ':'
        elif label == 'digits-slash': value = '/'
        else: value = 'bottom horizontal baseline' if index == 10 else 'decimal point'
        return {'sourceObservedSymbol': value, 'runtimeIndexUseVerified': False}
    if family == 'chat-slice':
        return {'sourceObservedSlice': ('top cap', 'body strip', 'bottom speech-tail strip')[index],
                'assumedAnimation': False}
    if family in ('arrow3','face-tab','lock3'):
        return {'sourceObservedSurface': ('base','bright','depressed')[index], 'runtimeStateVerified': False}
    if family == 'gem': return {'sourceObservedGlossSlot': index, 'runtimeDurationMs': None}
    return {'sourceStoredSlot': index, 'runtimeStateVerified': False}


def previews(resources, check):
    result, font = [], ImageFont.load_default(size=14)
    for page in range(math.ceil(len(resources) / 8)):
        subset = resources[page * 8:(page + 1) * 8]
        heights = []
        for item in subset:
            cell = max(88, min(340, max(f['height'] for f in item['frames']) * 3 + 24))
            heights.append(28 + 2 * math.ceil(item['declaredFrameCount'] / 5) * cell)
        board = Image.new('RGB',(1500,sum(heights)),'#eae3d0'); draw,y = ImageDraw.Draw(board),0
        for item,height in zip(subset,heights):
            rows=math.ceil(item['declaredFrameCount']/5); half=(height-28)//2;cell=half//rows
            draw.text((8,y+4),item['nativePath']+' / native candidate / pending review',font=font,fill='#214b3c')
            draw.rectangle((0,y+28+half,1499,y+height-1),fill='#193f35')
            for frame in item['frames']:
                with Image.open(ROOT/frame['file']) as p:
                    factor=min(4,280/p.width,(cell-22)/p.height)
                    picture=HELP.scaled(p,tuple(max(1,round(v*factor)) for v in p.size))
                index=frame['index'];x,top=8+index%5*300,y+28+index//5*cell
                for top_y,ink in ((top,'#214b3c'),(top+half,'#fff3d5')):
                    draw.text((x,top_y),f'raw{index} off{tuple(frame["frameOffset"])}',font=font,fill=ink)
                    board.paste(picture,(x,top_y+20),picture)
            for index in item['sourceEmptyFrameIndices']:
                x,top=8+index%5*300,y+28+index//5*cell
                for top_y,ink in ((top,'#214b3c'),(top+half,'#fff3d5')):
                    draw.text((x,top_y),f'raw{index} EMPTY retained',font=font,fill=ink)
            y+=height
        path=HERE/f'candidate-all-states-{page+1:02}.png'
        HELP.png(path,board,check)
        result.append({**record(path),'runtimeScreenshot':False,
                       'operation':'All actual native-mode-decoded candidate positions on light/dark diagnostic grounds; empty source slots labeled only'})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    check=parser.parse_args().check
    source_path=HERE/'manifest.json'; source=json.loads(source_path.read_bytes())
    by_path={r['nativePath']:r for r in source['resources']}
    if set(by_path)!=set(ART.PATHS) or len(by_path)!=47: raise ValueError('Full47 loose control scope differs')
    dynamic=json.loads((HERE/'dynamic-layout-evidence.json').read_bytes())
    archive_path=ROOT/source['sourceArchive']['file']
    if record(archive_path)!=source['sourceArchive']: raise ValueError('Pinned source archive changed')
    paint_inputs={k:v for k,v in HELP.ROOT_PAINTS.items() if k in ('panel','normal','hover','pressed')}
    paint_inputs.update(ART.PAINT_INPUTS)
    paints={k:Image.open(ROOT/v).convert('RGBA') for k,v in paint_inputs.items()}
    resources=[]
    with zipfile.ZipFile(archive_path) as archive:
        for native,(kind,label) in ART.PATHS.items():
            src,spec=by_path[native],ART.SPECS[kind]
            raw=archive.read(src['archiveMember'])
            if sha(raw)!=src['sourceSha256']: raise ValueError('Loose source hash changed')
            pictures={f['index']:ART.render(kind,label,f['index'],(f['width'],f['height']),paints,FONT,HELP.nine_slice,HELP.scaled)
                      for f in src['metadata']['frames'] if not f['empty']}
            output,metadata,decoded=CODEC.replace_frames(raw,pictures)
            nonpixels(raw,output,metadata)
            if output==raw: raise ValueError('A loose source path has no replacement pixels')
            patch=HERE/'patch'/native
            if check:
                if patch.read_bytes()!=output: raise ValueError('Native loose control patch replay differs')
            else:
                patch.parent.mkdir(parents=True,exist_ok=True);patch.write_bytes(output)
            frames=[]
            for frame,picture in decoded:
                index=frame['index']; before_record=src['frames'][index]
                with Image.open(ROOT/before_record['file']) as original: before=original.getchannel('A')
                after=picture.getchannel('A');diff=ImageChops.difference(before,after);box=diff.getbbox()
                if spec['alpha']=='source' and box is not None: raise ValueError('Structural loose alpha differs')
                if after.getextrema()[1]<8: raise ValueError('Own loose control frame became invisible')
                path=HERE/'decoded'/f"{native.removeprefix('res/uiRes/').removesuffix('.img').replace('/', '__')}-{index:02}.png"
                HELP.png(path,picture,check)
                start=frame['pixelDataOffset']
                if CODEC.encode_pixels(picture,frame['pixelMode'])!=output[start:start+frame['pixelByteLength']]:
                    raise ValueError('Loose pixel native encode/replay differs')
                frames.append({**record(path),'index':index,'sourceFrameIndex':index,'width':frame['width'],'height':frame['height'],
                    'pixelMode':frame['pixelMode'],'frameOffset':frame['frameOffset'],'decodedRgbaSha256':sha(picture.tobytes()),
                    'alphaPolicy':spec['alpha'],'sourceAlphaExactlyPreserved':box is None,
                    'sourceAlpha':alpha_summary(before),'candidateAlpha':alpha_summary(after),
                    'changedAlphaBBoxXYXY':list(box) if box else None,'changedAlphaPixelCount':sum(v!=0 for v in diff.tobytes()),
                    'alphaRedrawRoiXYXY':[0,0,frame['width'],frame['height']] if spec['alpha']=='redraw' else None,
                    'alphaRedrawReason':reason(spec['family']) if spec['alpha']=='redraw' else None,
                    'stateObservation':observed(spec['family'],label,index),'sourceFrameDurationMs':None})
            empty=[f['index'] for f in metadata['frames'] if f['empty']]
            resources.append({**record(patch),'nativePath':native,'rendererKind':kind,'family':spec['family'],'caption':label,
                'sourceSha256':src['sourceSha256'],'sourceArchiveMember':src['archiveMember'],'sourcePacked':False,'sourceLoose':True,
                'declaredFrameCount':len(metadata['frames']),'sourceEmptyFrameIndices':empty,'frames':frames,
                'allNonPixelBytesIdenticalToSource':True,'sourceAlphaPolicy':spec['alpha'],
                'nativeRuntimeVerified':False,'visualAccepted':False})
    positions=sum(len(r['frames']) for r in resources);declared=sum(r['declaredFrameCount'] for r in resources)
    structural=sum(f['alphaPolicy']=='source' for r in resources for f in r['frames']);cosmetic=positions-structural
    if (len(resources),declared,positions,structural,cosmetic)!=(47,132,131,31,100):
        raise ValueError('Full loose native/empty/alpha counts changed')
    result={'schemaVersion':1,'scope':'All47 loose controls,132 declared slots,131 nonempty;168 face bodies,2 GIF portraits and inventory icons excluded',
        'sourceReferences':record(source_path),'items':resources,'referenceContracts':[record(ROOT/p) for p in ART.REFERENCE_INPUTS],
        'nativeResourceCount':len(resources),'declaredSourceFramePositions':declared,'sourceFramePositions':positions,'sourceEmptyPositions':1,
        'exactStructuralAlphaPolicyPositions':structural,'cosmeticAlphaRedrawPositions':cosmetic,
        'actualExactAlphaPositions':sum(f['sourceAlphaExactlyPreserved'] for r in resources for f in r['frames']),
        'allSourceAlphaUnchanged':False,'allNonpixelBytesPreserved':True,
        'renderer':record(ROOT/'scripts/native-ui-loose-controls-art.py'),'exporter':record(Path(__file__)),
        'captureScript':record(HERE/'capture-source.py'),'nativeCodec':record(ROOT/'scripts/native-ui-format.py'),
        'paintInputs':[{'purpose':k,**record(ROOT/v)} for k,v in paint_inputs.items()],
        'structuralAlphaInputs':[{'purpose':k,**record(ROOT/v)} for k,v in ART.STRUCTURAL_ALPHA_INPUTS.items()],
        'font':{'family':'Microsoft YaHei','sourcePath':str(FONT),'sha256':sha(FONT.read_bytes())},
        'previews':previews(resources,check),'visualMappingAssumptions':ART.VISUAL_MAPPING_ASSUMPTIONS,
        'newModelGeneration':False,'originalColorOrGlyphPixelsReused':False,'sourceTimingVerified':False,
        'nativeRuntimeVerified':False,'visualAccepted':False,'installedToClient':False,'allLooseUiOrRuntimeTextComplete':False}
    HELP.write_json(HERE/'candidate-manifest.json',result,check)
    print(json.dumps({'resources':len(resources),'declaredPositions':declared,'positions':positions,'emptyPositions':1,
                      'exactStructuralAlpha':structural,'cosmeticAlphaRedraws':cosmetic,'nativeReplay':check,'installed':False}))


if __name__=='__main__': main()
