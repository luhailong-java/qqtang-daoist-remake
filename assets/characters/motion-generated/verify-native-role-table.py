"""Statically read only PE headers and a bounded role DWORD range inside fixed ZIP.
No extraction, imports, DLL loads, execution, disassembly or compilation of client.
"""
import hashlib,json,pathlib,re,struct,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8')
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
SOURCE=json.loads((HERE/'rolecatalog-fixed-source-evidence.json').read_text(encoding='utf-8'))
EXPECTED={int(k):[int(x.strip()) for x in values.split(',')] for k,values in re.findall(r'^\s*(\d+):\s*\{([0-9, ]+)\}',SOURCE['combat']['content'],re.M)}
assert len(EXPECTED)==20 and all(len(v)==6 for v in EXPECTED.values())
ENTRY='QQTang-Local/runtime/client-patched/Client.exe'
VA=0x7f2680
ROWS=24
ROW_BYTES=24
with zipfile.ZipFile(ARCHIVE) as z:
    info=z.getinfo(ENTRY)
    with z.open(info) as stream:
        header=stream.read(16384)
        assert header[:2]==b'MZ'
        peoff=struct.unpack_from('<I',header,0x3c)[0]
        assert peoff+24<=len(header) and header[peoff:peoff+4]==b'PE\0\0'
        machine,count,stamp,_,_,optsize,_=struct.unpack_from('<HHIIIHH',header,peoff+4)
        opt=peoff+24
        magic=struct.unpack_from('<H',header,opt)[0]
        assert magic==0x10b,'Expected PE32'
        imagebase=struct.unpack_from('<I',header,opt+28)[0]
        rva=VA-imagebase
        sections=[]
        for n in range(count):
            at=opt+optsize+n*40
            assert at+40<=len(header)
            name=header[at:at+8].rstrip(b'\0').decode('ascii')
            virtualsize,virtualaddr,rawsize,rawptr=struct.unpack_from('<IIII',header,at+8)
            sections.append({'name':name,'virtualSize':virtualsize,'rva':virtualaddr,'rawSize':rawsize,'rawOffset':rawptr})
        section=next(s for s in sections if s['rva']<=rva<s['rva']+s['rawSize'])
        offset=section['rawOffset']+rva-section['rva']
        assert offset>=0 and offset+ROWS*ROW_BYTES<=info.file_size
        assert rva+ROWS*ROW_BYTES<=section['rva']+section['rawSize']
        stream.seek(offset)
        data=stream.read(ROWS*ROW_BYTES)
        assert len(data)==ROWS*ROW_BYTES
        rows=[]
        for role in range(ROWS):
            raw=list(struct.unpack_from('<6I',data,role*ROW_BYTES))
            decoded=[n^0x1234 for n in raw]
            rows.append({'sourceRoleId':role,'va':hex(VA+role*ROW_BYTES),'rawDwords':raw,'xorKey':'0x1234','decodedSixValues':decoded,'expectedFromCombatGo':EXPECTED.get(role),'matchesCombatGo':decoded==EXPECTED[role] if role in EXPECTED else None})
        mismatches=[r for r in rows if r['matchesCombatGo'] is False]
        result={'schemaVersion':1,'archive':str(ARCHIVE),'expectedArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7','archiveHashEvidence':'Fixed ZIP previously verified; no whole288MB rehash during heavy-resource freeze','archiveEntry':ENTRY,'entryBytes':info.file_size,'entryCRC32':f'{info.CRC:08x}', 'readMode':'zipfile read-only PE32 header and one bounded data slice; ZipExtFile.seek can stream-decompress preceding bytes internally; no input execution or extraction','logicalReadsBytes':len(header)+len(data),'executedInput':False,'disassemblyPerformed':False,'machine':hex(machine),'imageBase':hex(imagebase),'peOffset':peoff,'dataVA':hex(VA),'dataRVA':hex(rva),'fileOffset':offset,'dataBytes':len(data),'dataSha256':hashlib.sha256(data).hexdigest(),'containingSection':section,'source':{'commit':SOURCE['commit'],'url':SOURCE['combat']['display_url'],'gitBlobSha':SOURCE['combat']['sha']},'semanticsEvidence':'Names/order of six attributes are from combat.go declarations/comments; raw PE comparison independently confirms numeric bytes, not original function usage, gameplay timing or official authenticity','comparedPlayableRows':len(EXPECTED),'matchedPlayableRows':len(EXPECTED)-len(mismatches),'rows':rows,'mismatches':mismatches}
        (HERE/'native-role-table-static-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('entryBytes','imageBase','fileOffset','dataBytes','dataSha256','logicalReadsBytes','comparedPlayableRows','matchedPlayableRows','mismatches')},ensure_ascii=False))
        if mismatches:sys.exit(1)
