"""Explicitly decode only3050's four declared frames for this authorized batch."""
from pathlib import Path
from PIL import Image
import importlib.util,json,hashlib,zlib
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
metadata_path=ROOT/'references/qqtang-map-data/motion-contract/metadata-batches/batch-01/entry-2312-elem50_stand.metadata.json'
source=json.loads(metadata_path.read_text(encoding='utf-8'));assert source['candidateElementIds']==[3050] and source['dimg']['frameCount']==4
entry=source['source']['indexEntry']
with (ROOT/source['source']['packageFile']).open('rb')as package:
    package.seek(entry['packageOffset']);compressed=package.read(entry['compressedByteLength'])
assert sha(compressed)==source['source']['compressedChunkSHA256']
inflater=zlib.decompressobj();raw=inflater.decompress(compressed,entry['rawByteLength']+1)
assert inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail and len(raw)==entry['rawByteLength']
assert sha(raw)==source['source']['rawResourceSHA256']
spec=importlib.util.spec_from_file_location('explicit_four_frame_reader',ROOT/'scripts/inspect-reference-dimg.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
checked,visible=reader.inspect_dimg(raw,metadata_only=True)
assert visible is None and checked['frameCount']==4 and checked['trailingByteLength']==0
board=Image.new('RGBA',(1536,1024));rows=[]
folder=OUT/'source-frames';folder.mkdir(parents=True,exist_ok=True)
for frame in checked['frames']:
    assert frame['empty']is False
    payload=raw[frame['pixelDataOffset']:frame['pixelDataOffset']+frame['pixelByteLength']]
    assert sha(payload)==frame['encodedPixelSha256']
    pixels=reader.decode_frame_pixels(payload,frame['pixelMode'],frame['width'],frame['height'])
    im=Image.frombytes('RGBA',(frame['width'],frame['height']),pixels)
    path=folder/f'frame-{frame["index"]:03d}.png';im.save(path)
    enlarged=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST)
    cell_x=(frame['index']%2)*768;cell_y=(frame['index']//2)*512
    x=cell_x+(768-enlarged.width)//2;y=cell_y+460-enlarged.height
    board.alpha_composite(enlarged,(x,y))
    rows.append({'frameIndex':frame['index'],'sourceFrameSize':[im.width,im.height],'sourceFrameOffset':frame['frameOffset'],
        'sourceMapElemOffset':[1,60],'combinedRenderOrigin':None,
        'encodedPixelSHA256':frame['encodedPixelSha256'],'decodedRgbaSHA256':sha(pixels),
        'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'alphaExtrema':list(im.getchannel('A').getextrema()),
        'sourcePNGOperation':'decode exact declared frame payload without offset application, crop or resize',
        'boardInspectionScale':4,'boardResampling':'nearest-neighbor','boardRect':[x,y,x+enlarged.width,y+enlarged.height]})
board.save(OUT/'four-source-structure.png')
report={'elementId':3050,'sourceMetadata':metadata_path.relative_to(ROOT).as_posix(),'sourceRawSHA256':sha(raw),
    'sourceCandidatePath':source['resourcePath'],'sourceLookupStatus':'candidate, native lookup unverified',
    'pixelFramesDecodedThisAuthorizedPass':4,'all45RGBAFalse':True,'nativeTimingMs':None,'frameStateSemantics':None,
    'board':'assets/maps/town/animation-candidates/3050/four-source-structure.png','boardReferenceOnly':True,
    'boardNotRuntimeArt':True,'boardIsNewModelGeneration':False,'frames':rows}
(OUT/'source-frame-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'elementId':3050,'decodedSourceFrames':4,'frames':rows,'noRuntimeOrLogicChange':True},ensure_ascii=True))
