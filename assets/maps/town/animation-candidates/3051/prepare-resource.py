"""Prepare one explicit map-state resource, decoding at most6 source frames."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import argparse,hashlib,importlib.util,json,zlib,re
ROOT=Path(__file__).resolve().parents[5]
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--element',type=int,required=True);parser.add_argument('--frames',type=int,nargs='+');parser.add_argument('--batch')
args=parser.parse_args()
contract=json.loads((ROOT/'references/qqtang-map-data/motion-contract/elements.json').read_text(encoding='utf-8'))
element=next(e for e in contract['elements']if e['elementId']==args.element)
metadata_path=ROOT/element['fullFrameMetadataSource']['file'];source=json.loads(metadata_path.read_text(encoding='utf-8'))
assert source['source']['rawResourceSHA256']==element['sourceDimgSHA256']
selected=args.frames if args.frames is not None else list(range(source['dimg']['frameCount']))
assert 1<=len(selected)<=6 and len(set(selected))==len(selected)and all(0<=i<source['dimg']['frameCount']for i in selected)
OUT=ROOT/f'assets/maps/{element["family"]}/animation-candidates/{args.element}'
if args.batch:
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',args.batch)
    OUT=OUT/args.batch
OUT.mkdir(parents=True,exist_ok=True)
assert not (OUT/'source-context.json').exists(),'Keep prior source batches; choose a new batch directory rather than overwrite.'
entry=source['source']['indexEntry']
with (ROOT/source['source']['packageFile']).open('rb')as package:
    package.seek(entry['packageOffset']);compressed=package.read(entry['compressedByteLength'])
assert sha(compressed)==source['source']['compressedChunkSHA256']
inflater=zlib.decompressobj();raw=inflater.decompress(compressed,entry['rawByteLength']+1)
assert inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail and len(raw)==entry['rawByteLength']
assert sha(raw)==element['sourceDimgSHA256']
spec=importlib.util.spec_from_file_location('bounded_resource_source_reader',ROOT/'scripts/inspect-reference-dimg.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
checked,unused=reader.inspect_dimg(raw,metadata_only=True);assert unused is None
art_path=ROOT/f'assets/maps/{element["family"]}/art.json';art_bytes=art_path.read_bytes();art=json.loads(art_bytes.decode('utf-8'))
own=next(p for p in art['pieces']if p['elementId']==args.element)
assert sha((ROOT/own['file']).read_bytes())==own['sha256']
folder=OUT/'source-frames';folder.mkdir(exist_ok=True)
rows=[];images={};canonical_groups={}
for index in selected:
    frame=checked['frames'][index]
    item={'frameIndex':index,'sourceFrameSize':[frame['width'],frame['height']],'sourceFrameOffset':frame['frameOffset'],
        'sourceMapElemOffset':element['sourceMapElemOffset'],'combinedRenderOrigin':None,'structuralEmpty':frame['empty']}
    if frame['empty']:
        item.update({'file':None,'pixelDecodePerformed':False,'fullyTransparentPixels':None});rows.append(item);continue
    payload=raw[frame['pixelDataOffset']:frame['pixelDataOffset']+frame['pixelByteLength']]
    assert sha(payload)==frame['encodedPixelSha256']
    pixels=reader.decode_frame_pixels(payload,frame['pixelMode'],frame['width'],frame['height'])
    image=Image.frombytes('RGBA',(frame['width'],frame['height']),pixels)
    path=folder/f'frame-{index:03d}.png';image.save(path)
    canonical=bytearray(pixels)
    for offset in range(0,len(canonical),4):
        if canonical[offset+3]==0:canonical[offset:offset+3]=b'\x00\x00\x00'
    visible_hash=sha(str(image.size).encode('ascii')+canonical)
    alias=canonical_groups.setdefault(visible_hash,index)
    images[index]=image
    item.update({'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'pixelDecodePerformed':True,
                 'encodedPixelSHA256':frame['encodedPixelSha256'],'decodedRgbaSHA256':sha(pixels),'canonicalVisibleRGBAHash':visible_hash,
                 'canonicalVisibleDefinition':'RGBA with RGB zeroed only where alpha==0, dimensions included; original PNG unchanged',
                 'exactVisibleAliasOfFrameIndex':alias if alias!=index else None,
                 'alphaExtrema':list(image.getchannel('A').getextrema()),'alphaBBox':list(image.getchannel('A').getbbox())if image.getchannel('A').getbbox()else None,
                 'fullyTransparentPixels':image.getchannel('A').getextrema()[1]==0,'operation':'decode actual declared native frame, no offset applied, no crop or resize'})
    rows.append(item)
board=Image.new('RGBA',(1536,1024));cell_w=1536//len(selected)
max_w=max((im.width for im in images.values()),default=1);max_h=max((im.height for im in images.values()),default=1)
scale=min(cell_w*.72/max_w,760/max_h)
for col,index in enumerate(selected):
    if index not in images:continue
    image=images[index];enlarged=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.NEAREST)
    x=col*cell_w+(cell_w-enlarged.width)//2;y=880-enlarged.height;board.alpha_composite(enlarged,(x,y))
    next(r for r in rows if r['frameIndex']==index).update({'referenceBoardRect':[x,y,x+enlarged.width,y+enlarged.height],
         'referenceBoardInspectionScale':scale,'referenceBoardResampling':'nearest-neighbor, reference only'})
board_path=OUT/('source-structure-'+('-'.join(map(str,selected)))+'.png');board.save(board_path)
result={'createdAtUTC':datetime.now(timezone.utc).isoformat(),'elementId':args.element,'family':element['family'],
    'sourceResourcePath':source['resourcePath'],'sourceRawSHA256':element['sourceDimgSHA256'],
    'sourceMetadata':metadata_path.relative_to(ROOT).as_posix(),'sourceDeclaredFrames':checked['frameCount'],'sourceDeclaredDirections':checked['directions'],
    'selectedSourceIndices':selected,'sourceFramesDecodedThisBatch':len(images),'allResourceFramesDecoded':len(selected)==checked['frameCount'],
    'sourceFootprintCells':element['sourceFootprintCells'],'sourceMapElemOffset':element['sourceMapElemOffset'],'sourceGridAttr':element['sourceGridAttr'],
    'combinedRenderOrigin':None,'nativeStateSemantics':None,'nativeFrameTimingMs':None,'nativeLoopPolicy':None,
    'currentOwnMaster':own,'currentMainArtManifest':art_path.relative_to(ROOT).as_posix(),'currentMainArtManifestSHA256AtStart':sha(art_bytes),
    'referenceBoard':board_path.relative_to(ROOT).as_posix(),'referenceBoardSHA256':sha(board_path.read_bytes()),
    'referenceBoardNotRuntimeArt':True,'sourceFrames':rows,'nonemptyDistinctVisibleGroupsInThisBatch':len(canonical_groups),
    'mainArtModified':False,'sourceLookupStatus':'candidate exact resource path from retained source mapping; native lookup unverified'}
save(OUT/'source-context.json',result)
print(json.dumps({'elementId':args.element,'family':element['family'],'sourceFrames':rows,'ownMaster':own['file'],
                  'board':board_path.relative_to(ROOT).as_posix(),'distinctVisibleGroups':len(canonical_groups),'mapElemOffset':element['sourceMapElemOffset']},ensure_ascii=True))
