"""Read two exact static-data references already visible in bounded code.

No search, execution, disassembly, client extraction, or full-file hash.
"""
import hashlib
import json
from pathlib import Path
import struct
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ENTRY='QQTang-Local/runtime/client-patched/Client.exe'
SLICES=[
    (0x7a369c,0x60,'window-005eec60.txt:0x5eec6c writes this immediate to object[0]'),
    (0x7f6a50,0x10,'window-005f532d.txt:0x5f535c passes this exact static argument to0x5f52ea'),
]
records=[]
with zipfile.ZipFile(ARCHIVE) as archive:
    entry=archive.getinfo(ENTRY)
    assert entry.file_size==13860864 and entry.CRC==0x04f986c5
    with archive.open(entry) as stream:
        header=stream.read(16384)
        pe=struct.unpack_from('<I',header,0x3c)[0]
        assert header[:2]==b'MZ' and header[pe:pe+4]==b'PE\0\0'
        machine,count,_,_,_,optsize,_=struct.unpack_from('<HHIIIHH',header,pe+4)
        opt=pe+24
        assert machine==0x14c and struct.unpack_from('<H',header,opt)[0]==0x10b
        base=struct.unpack_from('<I',header,opt+28)[0]
        sections=[]
        for n in range(count):
            at=opt+optsize+n*40
            virtualsize,rva,rawsize,rawptr=struct.unpack_from('<IIII',header,at+8)
            sections.append(dict(name=header[at:at+8].rstrip(b'\0').decode('ascii'),rva=rva,rawSize=rawsize,rawOffset=rawptr))
        for va,size,source in SLICES:
            rva=va-base
            section=next(s for s in sections if s['rva']<=rva and rva+size<=s['rva']+s['rawSize'])
            offset=section['rawOffset']+rva-section['rva']
            stream.seek(offset)
            data=stream.read(size)
            assert len(data)==size
            records.append(dict(va=hex(va),rva=hex(rva),fileOffset=offset,byteLength=size,sha256=hashlib.sha256(data).hexdigest(),bytesHex=data.hex(),
                                dwords=[dict(byteOffset=hex(i),value=hex(struct.unpack_from('<I',data,i)[0])) for i in range(0,size,4)],source=source))
result=dict(schemaVersion=1,archive=str(ARCHIVE),archiveEntry=ENTRY,entryBytes=entry.file_size,entryCRC32=f'{entry.CRC:08x}',
            expectedArchiveSha256='fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
            logicalHeaderReadBytes=len(header),logicalDataReadBytes=sum(r['byteLength'] for r in records),inputExecuted=False,clientExtracted=False,
            readMode='ZIP bounded PE header and two exact static references; no scan; seek may internally stream-decompress preceding bytes',slices=records)
(HERE/'native-data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
