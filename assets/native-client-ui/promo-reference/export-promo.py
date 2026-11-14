"""Read pinned loose sources and replay15 own promotion/profile replacements."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FONT=Path('C:/Windows/Fonts/msyh.ttc')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


ART=load('promo_art','scripts/native-ui-promo-art.py')
HELP=load('promo_helpers','assets/native-client-ui/common-reference/export-common.py')
CODEC=HELP.CODEC


def sha(data):return hashlib.sha256(data).hexdigest()
def record(path):return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def save(path,value,check):HELP.write_json(path,value,check)


def board(rows,key,file,check):
    out=Image.new('RGB',(1032,5*530),'#eae3d1');draw=ImageDraw.Draw(out)
    for i,row in enumerate(rows):
        x,y=(i%3)*344,(i//3)*530
        draw.text((x+4,y+4),row['nativePath'],font=ImageFont.load_default(size=11),fill='#244b3e')
        with Image.open(ROOT/row[key])as picture:
            rgba=picture.convert('RGBA');ratio=min(1,(334/rgba.width),(480/rgba.height))
            image=HELP.scaled(rgba,(round(rgba.width*ratio),round(rgba.height*ratio)))
        out.paste(image,(x+(344-image.width)//2,y+30),image)
    path=HERE/file;HELP.png(path,out,check);return record(path)


def gif_details(raw):
    with Image.open(io.BytesIO(raw))as im:
        info={k:v.hex()if isinstance(v,bytes)else v for k,v in im.info.items()if k!='extension'}
        return {'pillowFormat':im.format,'mode':im.mode,'frameCount':im.n_frames,'size':list(im.size),
            'duration':im.info.get('duration'),'loop':im.info.get('loop'),'disposal':im.disposal_method,
            'background':im.info.get('background'),'comment':im.info.get('comment'),'transparency':im.info.get('transparency'),
            'tileRect':list(im.tile[0][1])if im.tile else None,'info':info}


def compare_nonpixels(before,after,meta):
    if len(before)!=len(after):raise ValueError('Non-GIF container length changed')
    left,right=bytearray(before),bytearray(after)
    for f in meta['frames']:
        if f['empty']:continue
        p,n=f['pixelDataOffset'],f['pixelByteLength'];left[p:p+n]=bytes(n);right[p:p+n]=bytes(n)
    if left!=right:raise ValueError('Native nonpixel byte differs')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');check=parser.parse_args().check
    inventory_path=ROOT/'references/qqtang-ui-data/native-ui-inventory.json';inventory=json.loads(inventory_path.read_bytes())
    archive=ROOT/inventory['sourceArchive']['file']
    with archive.open('rb')as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=inventory['sourceArchive']['sha256']:raise ValueError('Pinned archive hash changed')
    lookup={r['canonicalPath']:r for r in inventory['resources']};sources=[];items=[];raws={};format_rows=[]
    with zipfile.ZipFile(archive)as zipped:
        for native,(kind,label)in ART.PATHS.items():
            ref=lookup[native.casefold()]
            if ref['storage']!='loose':raise ValueError('Promotion group must stay loose')
            raw=zipped.read(ref['archiveMember']);raws[native]=raw
            if sha(raw)!=ref['sourceSha256']:raise ValueError('Pinned loose member differs')
            meta,_=CODEC.inspect_native(raw,metadata_only=True)
            if len(meta['frames'])!=1 or meta['frames'][0]['empty']:raise ValueError('Unexpected promotional positions')
            f=meta['frames'][0];im=CODEC.decode_native_frame(raw,f);source_png=HERE/'frames'/f"{native.replace('/','__')}-00.png"
            HELP.png(source_png,im,check)
            bindings=[b for b in inventory['bindings']if b.get('canonicalPath')==native.casefold()]
            sources.append({'nativePath':native,'sourceLoose':True,'archiveMember':ref['archiveMember'],'sourceSha256':sha(raw),
                'sourceBytes':len(raw),'format':ref['format'],'metadata':meta,'frames':[{'index':0,'width':im.width,'height':im.height,
                'frameOffset':f['frameOffset'],'pixelMode':f['pixelMode'],**record(source_png),'decodedRgbaSha256':sha(im.tobytes())}],
                'sourceBindings':bindings,'nativeRuntimeVerified':False})
            details={'nativePath':native,'format':ref['format'],'originalCanvas':meta['declaredCanvas'],'originalFrameOffset':f['frameOffset'],'originalPixelMode':f['pixelMode']}
            if ref['format']=='GIF':details.update({'sourceDetails':gif_details(raw),'retainedSemanticProperties':meta['gifProperties'],
                'policy':'Own palette/LZW/file length can change. GIF89a, full-canvas one-frame opaque image, canvas, duration, loop, disposal, background index and interlace remain.',
                'nonpixelBytesExactlyPreserved':False,'originalPortraitOrAlphaReused':False})
            else:details.update({'pixelByteRange':[f['pixelDataOffset'],f['pixelDataOffset']+f['pixelByteLength']],
                'nonpixelPrefixHex':raw[:f['pixelDataOffset']].hex(),'nonpixelSuffixHex':raw[f['pixelDataOffset']+f['pixelByteLength']:].hex(),'nonpixelBytesExactlyPreserved':True})
            if ref['format']=='TGA':details.update({'sourcePixelDepthBits':24,'sourceStorageOrigin':'bottom-left',
                'sourceDescriptor':f['tgaDescriptor'],'sourceContainerBytes':len(raw),'orientationRoundtripVerified':True})
            format_rows.append(details)
    if len(sources)!=15:raise ValueError('Promotion scope changed')
    source_value={'schemaVersion':1,'scope':'13 top-level promotion cards and2 default profile GIFs;15 source positions',
        'source':{'archive':inventory['sourceArchive'],'inventory':record(inventory_path)},'decodeExporter':record(Path(__file__)),
        'nativeCodec':record(ROOT/'scripts/native-ui-format.py'),'resources':sources,'resourceCount':15,'decodedNonemptyFrameCount':15,
        'sourceClientMutated':False,'nativeRuntimeVerified':False,'visualAccepted':False}
    save(HERE/'manifest.json',source_value,check)
    contract={'schemaVersion':1,'scope':'12 DIMG,1 uncompressed24-bit TGA and2 GIF89a originals, all single-position loose UI images',
        'sourceReferences':record(HERE/'manifest.json'),'resources':format_rows,'structuralAlphaInputs':[],
        'sourceAlphaPolicy':'No original promotional letters, brand pixels, human portraits or silhouette Alpha reused. New own compositions are opaque; no structural masking contract requires old Alpha.',
        'bindingBoundary':'Two profile GIFs occur literally in uiMain/playerInfoDlg.avt and uiSelRoom/ui_getPlayerDetail. Thirteen promotion paths have no full-path literal occurrence in the inventoried13 PYC modules. Computed paths/native loading/click destination remain unknown.',
        'activeCampaignsImplemented':False,'originalClientCodeChanged':False,'nativeRuntimeVerified':False,'visualAccepted':False}
    save(HERE/'format-contract.json',contract,check)
    paints={k:Image.open(ROOT/v).convert('RGBA')for k,v in ART.PAINT_INPUTS.items()}
    for ref in sources:
        native=ref['nativePath'];kind,label=ART.PATHS[native];f=ref['metadata']['frames'][0]
        painting=ART.render(kind,label,0,(f['width'],f['height']),paints,FONT,HELP.nine_slice,HELP.scaled)
        output,source_meta,decoded=CODEC.replace_frames(raws[native],{0:painting})
        if output==raws[native]:raise ValueError('Source pixels unchanged')
        after,_=CODEC.inspect_native(output,metadata_only=True)
        if ref['format']=='GIF':
            if after['gifProperties']!=source_meta['gifProperties']:raise ValueError('GIF semantic change')
            detail=gif_details(output)
            if detail['mode']!='P'or detail['comment']is not None or detail['transparency']is not None or detail['tileRect']!=[0,0,140,226]:raise ValueError('GIF metadata contract differs')
        else:compare_nonpixels(raws[native],output,source_meta)
        target=HERE/'patch'/native
        if check:
            if target.read_bytes()!=output:raise ValueError('Promotion native replay differs')
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(output)
        frame,picture=decoded[0];png=HERE/'decoded'/f"{native.replace('/','__')}-00.png";HELP.png(png,picture,check)
        if list(picture.size)!=after['declaredCanvas']or picture.getchannel('A').getextrema()!=(255,255):raise ValueError('Own full-canvas opaque portrait/card required')
        items.append({**record(target),'nativePath':native,'sourceLoose':True,'sourcePacked':False,'format':ref['format'],
            'sourceSha256':ref['sourceSha256'],'rendererKind':kind,'caption':label,'sourceBindings':ref['sourceBindings'],
            'frames':[{**record(png),'index':0,'width':picture.width,'height':picture.height,'frameOffset':frame['frameOffset'],
                'pixelMode':frame['pixelMode'],'decodedRgbaSha256':sha(picture.tobytes()),'alphaExtrema':[255,255]}],
            'allNonpixelBytesIdenticalToSource':True if ref['format']!='GIF'else None,
            'gifSemanticProperties':after.get('gifProperties'),'originalCharacterOrCaptionAlphaReused':False,'nativeRuntimeVerified':False,'visualAccepted':False})
    provenance=[]
    for path in ART.PAINT_INPUTS.values():
        for suffix in('.source.json','.provenance.json','.generation.json'):
            file=ROOT/(path+suffix)
            if file.is_file():provenance.append(record(file))
    source_rows=[{'nativePath':r['nativePath'],'png':r['frames'][0]['file']}for r in sources]
    own_rows=[{'nativePath':r['nativePath'],'png':r['frames'][0]['file']}for r in items]
    result={'schemaVersion':1,'scope':'15 own promotional and profile illustrations,15 original positions','sourceReferences':record(HERE/'manifest.json'),
        'items':items,'nativeResources':15,'sourcePositions':15,'sourceFormats':{'QQF/DIMG':12,'TGA':1,'GIF':2},'functionalAlphaPositions':0,
        'renderer':record(ROOT/'scripts/native-ui-promo-art.py'),'exporter':record(Path(__file__)),'nativeCodec':record(ROOT/'scripts/native-ui-format.py'),
        'exportHelpers':record(ROOT/'assets/native-client-ui/common-reference/export-common.py'),
        'paintInputs':[record(ROOT/path)for path in ART.PAINT_INPUTS.values()],'paintProvenance':provenance,
        'referenceInputs':[record(ROOT/path)for path in ART.REFERENCE_INPUTS],'font':{'family':'Microsoft YaHei','sha256':sha(FONT.read_bytes())},
        'sourcePreview':board(source_rows,'png','source-contact.png',check),'candidatePreview':board(own_rows,'png','candidate-contact.png',check),
        'newModelGeneration':False,'originalModelGenerations':0,'visualMappingAssumptions':ART.VISUAL_MAPPING_ASSUMPTIONS,
        'nativeRuntimeVerified':False,'visualAccepted':False,'installedToClient':False}
    save(HERE/'candidate-manifest.json',result,check)
    print(json.dumps({'nativeResources':15,'sourcePositions':15,'formats':result['sourceFormats'],'gifPropertiesVerified':2,'nonpixelContainersVerified':13,'replayChecked':check}))


if __name__=='__main__':main()
