"""Read-only proof of47 native loose controls, glyph slots and retained empties."""
import argparse
import hashlib
from importlib import util
import json
from pathlib import Path
import zipfile

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=util.spec_from_file_location('loose_controls_qa_codec',ROOT/'scripts/native-ui-format.py')
CODEC=util.module_from_spec(spec);spec.loader.exec_module(CODEC)


def sha(data): return hashlib.sha256(data).hexdigest()


def record(path): return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def require(ok, message):
    if not ok: raise ValueError(message)


def geometry(metadata):
    return {key:([{k:v for k,v in f.items() if k!='encodedPixelSha256'} for f in value] if key=='frames' else value)
            for key,value in metadata.items() if key!='sha256'}


def decoded(raw,frame):
    start=frame['pixelDataOffset']
    pixels=CODEC.reader.decode_frame_pixels(raw[start:start+frame['pixelByteLength']],frame['pixelMode'],frame['width'],frame['height'])
    return Image.frombytes('RGBA',(frame['width'],frame['height']),pixels)


def components(alpha):
    width,height=alpha.size
    remaining={(x,y) for y in range(height) for x in range(width) if alpha.getpixel((x,y))>=96}
    groups=[]
    while remaining:
        seed=remaining.pop(); group={seed};todo=[seed]
        while todo:
            x,y=todo.pop()
            for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if (nx,ny) in remaining:
                    remaining.remove((nx,ny));group.add((nx,ny));todo.append((nx,ny))
        groups.append(group)
    return groups


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    check=parser.parse_args().check
    source_path,candidate_path=HERE/'manifest.json',HERE/'candidate-manifest.json'
    source,candidate=json.loads(source_path.read_bytes()),json.loads(candidate_path.read_bytes())
    src={r['nativePath']:r for r in source['resources']};rows={r['nativePath']:r for r in candidate['items']}
    require(src.keys()==rows.keys() and len(rows)==47,'Exact47 loose scope changed')
    archive_path=ROOT/source['sourceArchive']['file']
    require(record(archive_path)==source['sourceArchive'],'Pinned archive differs')
    for ref in candidate['referenceContracts']+candidate['paintInputs']+candidate['structuralAlphaInputs']:
        require(sha((ROOT/ref['file']).read_bytes())==ref['sha256'],'Own/source input differs: '+ref['file'])
    positions=declared=structural=redraw=exact=0
    empty_records=[];multis=[];numeric=[];pictures={}
    with zipfile.ZipFile(archive_path) as archive:
        for native,item in rows.items():
            before=archive.read(src[native]['archiveMember']);after=(ROOT/item['file']).read_bytes()
            require(sha(before)==src[native]['sourceSha256'],'Loose source hash differs')
            require(sha(after)==item['sha256'] and before!=after,'Candidate missing/unchanged')
            bm,_=CODEC.reader.inspect_dimg(before,metadata_only=True);am,_=CODEC.reader.inspect_dimg(after,metadata_only=True)
            require(bm==src[native]['metadata'],'Captured source metadata differs')
            require(geometry(bm)==geometry(am),'Native loose geometry/header changed')
            bmask,amask=bytearray(before),bytearray(after)
            images={};stored={f['index']:f for f in item['frames']}
            declared+=len(am['frames'])
            for frame in am['frames']:
                index=frame['index']
                if frame['empty']:
                    require(index not in stored and frame['width']==frame['height']==frame['pixelMode']==0,'Original empty slot filled')
                    empty_records.append({'nativePath':native,'index':index,'metadataExactlyPreserved':True})
                    continue
                row=stored[index];a,b=decoded(after,frame),decoded(before,frame)
                start,length=frame['pixelDataOffset'],frame['pixelByteLength']
                bmask[start:start+length],amask[start:start+length]=bytes(length),bytes(length)
                require(CODEC.encode_pixels(a,frame['pixelMode'])==after[start:start+length],'Native pixel replay differs')
                require(sha(a.tobytes())==row['decodedRgbaSha256'],'Decoded RGBA hash differs')
                with Image.open(ROOT/row['file']) as png:
                    require(png.mode=='RGBA' and png.size==a.size and png.tobytes()==a.tobytes(),'Decoded candidate PNG differs')
                with Image.open(ROOT/src[native]['frames'][index]['file']) as png:
                    require(png.tobytes()==b.tobytes(),'Source PNG differs')
                diff=ImageChops.difference(a.getchannel('A'),b.getchannel('A'));box=diff.getbbox()
                require((list(box) if box else None)==row['changedAlphaBBoxXYXY'],'Alpha difference bbox differs')
                require(sum(v!=0 for v in diff.tobytes())==row['changedAlphaPixelCount'],'Alpha difference count differs')
                if row['alphaPolicy']=='source':
                    require(box is None,'Exact functional alpha changed');structural+=1
                else:
                    require(row['alphaRedrawRoiXYXY']==[0,0,a.width,a.height] and row['alphaRedrawReason'],'Cosmetic alpha exception lacks original-frame bounds/reason')
                    redraw+=1
                exact+=box is None;positions+=1;images[index]=a
            require(bmask==amask,'Native bytes outside pixel planes changed')
            if len(images)>1:
                distinct=len({(p.size,sha(p.tobytes())) for p in images.values()})
                require(distinct==len(images),'Multi-position family collapsed into duplicate bitmaps: '+native)
                multis.append({'nativePath':native,'nonemptyPositions':len(images),'distinctDecodedBitmaps':distinct})
            if item['family']=='numeric':
                if len(images)>=10:
                    require(len({(images[i].size,sha(images[i].tobytes())) for i in range(10)})==10,'Digits0-9 collapsed')
                    box=images[1].getchannel('A').point(lambda v:255 if v>=32 else 0).getbbox()
                    require(box and box[3]-box[1]>=images[1].height-3,'Narrow digit1 became a tiny dot')
                numeric.append({'nativePath':native,'sourceObservedSymbols':[f['stateObservation']['sourceObservedSymbol'] for f in item['frames']]})
            pictures[native]=images
    require((len(rows),declared,positions,structural,redraw)==(47,132,131,31,100),'Full loose count/alpha policy changed')
    require(empty_records==[{'nativePath':'res/uiRes/selRoom/mapFilter/mapfilter_selected_dashl.img','index':1,'metadataExactlyPreserved':True}],'Exact source empty slot differs')
    colon=pictures['res/uiRes/number/num.img'][10]
    require(len(components(colon.getchannel('A')))==2,'Colon does not retain two separate visible marks')
    bottom=pictures['res/uiRes/number/youxibi_shuzi.img'][10]
    point=pictures['res/uiRes/number/youxibi_shuzi.img'][11]
    require(bottom.size==(7,1) and point.size==(2,2),'Bottom baseline/decimal native crop changed')
    require(len(candidate['previews'])==len(source['sourceBoards'])==6,'All-state pagination differs')
    for ref in candidate['previews']+source['sourceBoards']:
        require(record(ROOT/ref['file'])=={k:ref[k] for k in ('file','sha256')},'Source/candidate board changed')
    # Blue51,113,149 live input text needs a pale surface throughout proven rect.
    entry=pictures['res/uiRes/gameChat/liaotianshurukuang_di.img'][0]
    for xy in ((12,4),(255,4),(12,15),(255,15),(100,10)):
        rgb=entry.getpixel(xy)[:3]
        require(min(rgb)>180,'Proven game blue input text region lost pale backing')
    # Persist the final corrected native outputs at diagnostic scale. The
    # regular six all-state sheets remain the complete review denominator.
    review=Image.new('RGB',(1200,810),'#eae3d0');d=ImageDraw.Draw(review);font=ImageFont.load_default(size=14)
    chosen=[('number/num',1),('number/num',10),('number/itemNum',1),
            ('selRoom/room/num_player',1),('face/biaoqingxuandan_di',0),
            ('selRoom/recorder/botton_videostart',0)]
    for i,(relative,index) in enumerate(chosen):
        image=pictures['res/uiRes/'+relative+'.img'][index]
        x,y=i%3*400,i//3*405
        d.text((x+7,y+5),relative+' raw'+str(index),font=font,fill='#214b3c')
        d.rectangle((x,y+205,x+399,y+404),fill='#193f35')
        factor=min(8,380/image.width,170/image.height)
        rgba=image.convert('RGBa').resize(tuple(max(1,round(v*factor)) for v in image.size),Image.Resampling.LANCZOS).convert('RGBA')
        review.paste(rgba,(x+8,y+28),rgba);review.paste(rgba,(x+8,y+230),rgba)
    review_path=HERE/'final-corrections-review.png'
    if check:
        with Image.open(review_path) as previous:
            require(previous.mode==review.mode and previous.size==review.size and previous.tobytes()==review.tobytes(),'Final correction board replay differs')
    else: review.save(review_path,optimize=True)
    result={'schemaVersion':1,'scope':'47 loose controls,132 declared positions,131 nonempty; all inventory/body faces excluded',
        'source':record(source_path),'candidate':record(candidate_path),'verifier':record(Path(__file__)),
        'nativeResourceCount':47,'declaredSourceFramePositions':132,'nonemptyFramePositions':131,
        'exactStructuralAlphaPositions':structural,'cosmeticAlphaRedrawPolicyPositions':redraw,'actualExactAlphaPositions':exact,
        'emptySlots':empty_records,'allNativeMetadataAndNonpixelBytesEqual':True,'nativeDecodedPngAndReencodeReplayEqual':True,
        'numericFamilies':numeric,'narrowOnesRemainTall':True,'colonHasTwoSeparatedMarks':True,
        'bottomBaselineAndDecimalCropAndOffsetRetained':True,'multiPositionFamilies':multis,
        'blueInputTextRegionHasPaleBackground':True,'sourcePages':6,'candidateLightDarkPages':6,
        'finalCorrectionReviewBoard':record(review_path),
        'staticSourceAndCandidateBoardsActuallyViewedByAgent':True,
        'staticReviewMethod':'view_image of all6 source and6 candidate all-state pages; corrected narrow1/colon and opaque-alpha panel native outputs re-viewed in final-corrections-review.png',
        'nativeProgramExecuted':False,'providedDirectoryWritten':False,'installedToClient':False,
        'sourceTimingVerified':False,'nativeRuntimeVerified':False,'visualAccepted':False,
        'limitations':['25 paths lack exact literal binding; seven byte-identical packed copies do not prove loose-loader aliases',
                       'Static review is not user visual acceptance or native runtime screenshots',
                       'One-pixel-wide source currency1 is inherently thin; original dark-background usage remains a runtime check',
                       'Source durations, animation loop branches and text width remain unverified']}
    raw=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8');path=HERE/'qa-result.json'
    if check: require(path.read_bytes()==raw,'Loose QA proof replay differs')
    else: path.write_bytes(raw)
    print(json.dumps({'resources':47,'declaredPositions':132,'positions':131,'emptyPositions':1,
                      'nativeReplay':True,'independentGlyphChecks':True,'readOnlyCheck':check}))


if __name__=='__main__': main()
