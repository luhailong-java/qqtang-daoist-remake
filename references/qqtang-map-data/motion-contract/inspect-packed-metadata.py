"""Inspect1–6 explicit package resources without decoding any pixel plane.

Example: python inspect-packed-metadata.py --batch batch-01 --resource
object/mapElem/town/elem50_stand.img --resource object/mapElem/town/elem51_stand.img
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import argparse,hashlib,importlib.util,json,re,zlib

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
norm=lambda value:value.replace('\\','/').lower()
def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def groups(frames,with_offsets=False):
    grouped=defaultdict(list)
    for frame in frames:
        if frame['empty']:
            continue
        key=(frame['pixelMode'],frame['width'],frame['height'],frame['encodedPixelSha256'])
        if with_offsets:
            key+=tuple(frame['frameOffset'])
        grouped[key].append(frame)
    return [{'frameIndices':[f['index']for f in value],
             'representativeFrameIndex':value[0]['index'],'pixelMode':value[0]['pixelMode'],
             'size':[value[0]['width'],value[0]['height']],
             'encodedPixelSha256':value[0]['encodedPixelSha256'],
             'frameOffsets':[f['frameOffset']for f in value],
             'allOffsetsEqual':all(f['frameOffset']==value[0]['frameOffset']for f in value),
             'visibleAlpha':'unknown','visuallyDistinctFromOtherGroups':None}
            for value in grouped.values()]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',required=True)
    parser.add_argument('--resource',action='append',required=True)
    parser.add_argument('--expected-sha256',action='append',default=[])
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--reference-only-version65537-suffix',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',args.batch):
        parser.error('Use a lowercase alphanumeric/hyphen batch name, maximum64characters.')
    if not 1<=len(args.resource)<=6 or len({norm(p)for p in args.resource})!=len(args.resource):
        parser.error('Explicitly select1–6 different package resource paths.')
    if args.expected_sha256 and len(args.expected_sha256)!=len(args.resource):
        parser.error('If provided, repeat --expected-sha256 once per resource in matching order.')
    if any(not re.fullmatch('[0-9a-fA-F]{64}',h)for h in args.expected_sha256):
        parser.error('Expected SHA256 must be64hex characters.')
    destination=(args.output_dir if args.output_dir is not None else OUT/'metadata-batches'/args.batch)
    destination=(ROOT/destination).resolve()if not destination.is_absolute()else destination.resolve()
    if not destination.is_relative_to(ROOT):
        parser.error('Output directory must stay inside this project.')
    baseline_path=ROOT/'assets/maps/production-index.json'
    baseline_bytes=baseline_path.read_bytes();baseline=json.loads(baseline_bytes.decode('utf-8-sig'))
    supplement=json.loads((ROOT/'references/qqtang-map-data/visual-reference/binary-supplement/art-reference-index.json').read_text(encoding='utf-8'))
    candidates=defaultdict(list)
    for element in baseline['elements']+supplement['elements']:
        if element.get('candidatePath'):
            candidates[norm(element['candidatePath'])].append(element)
    source=baseline['source'];input_dir=ROOT/'.artifacts/reference-inputs'
    index_path=input_dir/'object.idx';package_path=input_dir/'object.pkg'
    index_bytes=index_path.read_bytes();index_hash=sha(index_bytes)
    expected_inputs=source['inputFiles']
    if index_hash!=expected_inputs['object.idx']['sha256'] or len(index_bytes)!=expected_inputs['object.idx']['byteLength']:
        raise ValueError('Index bytes differ from previously pinned source metadata.')
    if package_path.stat().st_size!=expected_inputs['object.pkg']['byteLength']:
        raise ValueError('Cached package byte length differs from previously pinned source metadata.')
    module_path=ROOT/'scripts/inspect-reference-dimg.py'
    spec=importlib.util.spec_from_file_location('metadata_only_dimg_reader',module_path)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    def forbidden_pixel_decode(*unused,**unused_keywords):
        raise RuntimeError('This metadata-only CLI must never call decode_frame_pixels.')
    reader.decode_frame_pixels=forbidden_pixel_decode
    by_path={norm(e['path']):e for e in reader.parse_index(index_bytes,package_path.stat().st_size)['entries']}
    destination.mkdir(parents=True,exist_ok=True)
    records=[]
    with package_path.open('rb')as package:
        for number,path in enumerate(args.resource):
            entry=by_path.get(norm(path))
            if entry is None:
                raise ValueError('Exact indexed resource path not found: '+path)
            package.seek(entry['packageOffset']);compressed=package.read(entry['compressedByteLength'])
            if len(compressed)!=entry['compressedByteLength']:
                raise ValueError('Compressed chunk truncated: '+entry['path'])
            inflater=zlib.decompressobj();raw=inflater.decompress(compressed,entry['rawByteLength']+1)
            if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail or len(raw)!=entry['rawByteLength']:
                raise ValueError('Zlib framing/expanded length does not match index: '+entry['path'])
            digest=sha(raw);candidate_rows=candidates.get(norm(path),[])
            expected_hashes={e.get('dimgSha256')or e.get('dimg',{}).get('sha256')for e in candidate_rows}
            expected_hashes.discard(None)
            if args.expected_sha256:
                expected_hashes.add(args.expected_sha256[number].lower())
            if expected_hashes and expected_hashes!={digest}:
                raise ValueError('Raw resource SHA does not match fixed expected evidence: '+entry['path'])
            compressed_hash=sha(compressed)
            expected_compressed={e.get('compressedStreamSha256')for e in candidate_rows}
            expected_compressed.discard(None)
            if expected_compressed and expected_compressed!={compressed_hash}:
                raise ValueError('Compressed chunk SHA differs from retained source evidence: '+entry['path'])
            metadata,visible=reader.inspect_dimg(raw,metadata_only=True,reference_only_version65537_suffix=args.reference_only_version65537_suffix)
            if visible is not None or metadata['pixelDecodePerformed']is not False or any('decodedRgbaSha256'in f for f in metadata['frames']):
                raise RuntimeError('Metadata-only contract violated; no result may be published.')
            raster_groups=groups(metadata['frames']);pose_groups=groups(metadata['frames'],True)
            empty_indices=[f['index']for f in metadata['frames']if f['empty']]
            frame0_group=next((g['frameIndices']for g in raster_groups if 0 in g['frameIndices']),[])
            record={'schemaVersion':1,'createdAtUTC':datetime.now(timezone.utc).isoformat(),
                'resourcePath':entry['path'],'candidateElementIds':[e['elementId']for e in candidate_rows],
                'candidateLookupStatus':'exact candidate path from retained element metadata only; native client lookup not proved',
                'source':{'archiveURL':source['archiveUrl'],'archiveSHA256PriorPinned':source['archiveSha256'],
                          'archiveRehashedThisPass':False,'packageFile':package_path.relative_to(ROOT).as_posix(),
                          'packageSHA256PriorPinned':expected_inputs['object.pkg']['sha256'],'packageRehashedThisPass':False,
                          'indexFile':index_path.relative_to(ROOT).as_posix(),'indexSHA256':index_hash,
                          'indexEntry':entry,'compressedChunkSHA256':compressed_hash,'rawResourceSHA256':digest,
                          'expectedRawSHA256':sorted(expected_hashes),'expectedSHA256Matches':bool(expected_hashes),
                          'readerFile':module_path.relative_to(ROOT).as_posix(),'readerSHA256':sha(module_path.read_bytes()),
                          'sourceAuthenticity':'community-patched client; Tencent original official authenticity unverified'},
                'submittedMode':{'metadata_only':True,'reference_only_version65537_suffix':args.reference_only_version65537_suffix},
                'dimg':metadata,'structuralEmptyFrameIndices':empty_indices,'structuralEmptyFrameCount':len(empty_indices),
                'encodedRasterGroups':raster_groups,'sameRasterAndOffsetGroups':pose_groups,
                'encodedRasterGroupCount':len(raster_groups),'sameRasterAndOffsetGroupCount':len(pose_groups),
                'repeatedEncodedRasterGroups':[g for g in raster_groups if len(g['frameIndices'])>1],
                'byteIdenticalToFrame0Indices':frame0_group,'nonemptyIndicesWithDifferentPayloadFromFrame0':[f['index']for f in metadata['frames']if not f['empty']and f['index']not in frame0_group],
                'pixelDecodePerformed':False,'pixelPayloadValidation':'unknown','visibleAlpha':'unknown','runtimeUsable':False,
                'semantics':{'directionOrder':None,'frameDurationMs':None,'loopPolicy':None,'animationVersusDamageState':None},
                'limitations':['Encoded payload groups establish exact byte identity or difference, not canonical visible RGBA equivalence.','Structural empty flags do not prove alpha-empty encoded images.','Same pixel bytes at different frameOffsets remain different placement states.','No timing/direction/state meaning is inferred; no PNG or art frames are produced.']}
            filename='entry-'+str(entry['ordinal'])+'-'+Path(norm(entry['path'])).stem+'.metadata.json'
            record_path=destination/filename;save(record_path,record)
            records.append({'resourcePath':entry['path'],'candidateElementIds':record['candidateElementIds'],
                            'record':record_path.relative_to(ROOT).as_posix(),'recordSHA256':sha(record_path.read_bytes()),
                            'rawResourceSHA256':digest,'declaredFrameCount':metadata['frameCount'],'declaredDirections':metadata['directions'],
                            'structuralEmptyFrameCount':len(empty_indices),'encodedRasterGroupCount':len(raster_groups),
                            'sameRasterAndOffsetGroupCount':len(pose_groups),'pixelDecodePerformed':False})
    report={'batch':args.batch,'createdAtUTC':datetime.now(timezone.utc).isoformat(),'resourcesSelectedExplicitly':args.resource,
            'resourceCount':len(records),'pixelDecodePerformed':False,'pixelPayloadValidation':'unknown','visibleAlpha':'unknown',
            'runtimeUsable':False,'testsOrBuildsRun':False,'pngFilesProduced':0,'records':records}
    save(destination/'batch.json',report)
    print(json.dumps(report,ensure_ascii=True))
if __name__=='__main__':
    main()
