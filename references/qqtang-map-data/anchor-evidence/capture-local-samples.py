"""Capture five existing JSON contracts and bounded resource headers, no pixels.

Reads only the recorded object.pkg streams for explicit IDs. Decompresses the
small DIMG containers to inspect their40/28-byte headers; never decodes PNG/RGBA.
"""
import hashlib
import json
from pathlib import Path
import struct
import zlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IDS=[3001,3002,3019,3050,11007]
def read_json(relative):
    return json.loads((ROOT/relative).read_text(encoding='utf-8'))
def digest(data):
    return hashlib.sha256(data).hexdigest()

production=read_json('assets/maps/production-index.json')
properties=read_json('references/qqtang-map-data/binary-properties-inspection.json')
by_id={e['elementId']:e for e in production['elements']}
by_property={e['id']:e for e in properties['records']}
source_prop=ROOT/properties['sourceFile']
prop_data=source_prop.read_bytes()
assert digest(prop_data)==properties['sourceSha256']
art={}
for family in ['town','match']:
    manifest=read_json(f'assets/maps/{family}/art.json')
    for piece in manifest['pieces']:
        if piece['elementId'] in IDS:art[piece['elementId']]=piece
records=[]
compressed_read=0
with (ROOT/'.artifacts/reference-inputs/object.pkg').open('rb') as package:
    for ident in IDS:
        item=by_id[ident]
        entry=item['packageEntry']
        package.seek(entry['packageOffset'])
        compressed=package.read(entry['compressedByteLength'])
        compressed_read+=len(compressed)
        assert digest(compressed)==item['compressedStreamSha256']
        decoder=zlib.decompressobj()
        data=decoder.decompress(compressed,entry['rawByteLength']+1)
        assert len(data)==entry['rawByteLength'] and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
        assert digest(data)==item['dimgSha256'] and data[:8]==b'QQF\x1aDIMG'
        words=list(struct.unpack_from('<8I',data,8))
        marker,fx,fy,mode=struct.unpack_from('<IiiI',data,40)
        fw,fh,unknown=struct.unpack_from('<III',data,56)
        assert marker==0 and mode!=0
        prop=by_property[ident]
        fixed=prop_data[prop['recordOffset']:prop['recordOffset']+24]
        pid,w,h,ox,oy,life,level,move=struct.unpack('<IHHhhiII',fixed)
        assert pid==ident and [w,h]==item['footprintCells'] and [ox,oy]==item['mapElemOffsetRaw']
        assert [fx,fy]==item['selectedFrameOffsetRaw'] and [fw,fh]==item['selectedFrameSize']
        piece=art[ident]
        records.append(dict(elementId=ident,footprintCells=[w,h],logicalFootprintAt40=[w*40,h*40],
            mapElemOffsetRaw=[ox,oy],binaryPropertyRecordOffset=prop['recordOffset'],binaryPropertyFixedHeaderHex=fixed.hex(),
            candidatePath=item['candidatePath'],packageEntry=entry,dimgSha256=digest(data),dimgFirst68BytesHex=data[:68].hex(),
            dimgHeader=dict(version=words[0],frameInfoSize=words[1],frameCount=words[2],directions=words[3],declaredCanvas=words[6:8]),
            firstFrame=dict(offset=40,frameOffset=[fx,fy],size=[fw,fh],pixelMode=mode,unknownImageHeaderWord=unknown),
            retainedVisibleBoundingBox=item['visibleBoundingBox'],visibleBoundsEvidence='Existing JSON only; no PNG or alpha read in this capture',
            runtimeArt={key:piece.get(key) for key in ['file','worldFrameWidth','worldFrameHeight','mapElemOffsetRaw','geometryAccepted','accepted']},
            candidateAtAnchorZero=dict(currentMinusMapElemOffset=[-ox,-oy],
                hypotheticalPlusDimgFrameOffset=[-ox+fx,-oy+fy],hypotheticalMinusDimgFrameOffset=[-ox-fx,-oy-fy],
                arithmeticOnly=True,nativeCorrectFormulaSelected=False)))
snapshot_inputs=['src/map-art.js','src/original-maps.js','assets/maps/production-index.json','assets/maps/town/art.json','assets/maps/match/art.json','references/qqtang-map-data/binary-properties-inspection.json']
snapshot=[dict(file=path,byteLength=(ROOT/path).stat().st_size,sha256=digest((ROOT/path).read_bytes())) for path in snapshot_inputs]
result=dict(schemaVersion=1,capturedOn='2026-10-28',scope='Five explicit element contracts; bounded DIMG framing and source property bytes, no pixel decoding',
            sourceArchiveSha256=production['source']['archiveSha256'],sourceType=production['source']['sourceType'],officialOriginalAuthenticity='unverified',
            packageIdentityEvidence='Previously verified fixed object.pkg; this capture verifies only five compressed-stream and DIMG hashes, not full35MB package',
            compressedBytesRead=compressed_read,sourcePropertySha256=digest(prop_data),inputSnapshot=snapshot,records=records,
            runtimeWrites=False,testsRun=False,clientExecuted=False,pixelsDecoded=False,newArtGenerated=False,
            limitations=['DIMG frameOffset, prop offsets, visible alpha bounds, and package byte offsets are separate namespaces.',
                         'Native property+8/+0xa layout matches these serialized headers, but property allocation/loading has not been fully traced.',
                         'Candidate arithmetic distinguishes hypotheses; it is not an acceptance test or original-client proof.'])
(HERE/'local-anchor-samples.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(sampleCount=len(records),compressedBytesRead=compressed_read,pixelsDecoded=False),ensure_ascii=False))
