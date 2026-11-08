"""Read only explicit source-cited native windows and derived exact references.

No client execution, import, extraction, tests, compilation, scanning, or PNG
decode. A tiny COFF data wrapper lets the already-installed llvm-objdump decode
only each requested window. The wrapper is deleted after decoding.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ENTRY = 'QQTang-Local/runtime/client-patched/Client.exe'
OBJDUMP = Path('C:/Program Files/Microsoft Visual Studio/18/Enterprise/VC/Tools/Llvm/x64/bin/llvm-objdump.exe')
COMMIT = '4b3a245fd985cabd4abd68ade6c282cc163d9edb'
WINDOWS = [
    (0x5d80e1, 0x2bb, 'internal/game/mapdata/competitive_battlefield.go#L227-L232'),
    (0x5d839c, 0x200, 'internal/game/mapdata/competitive_battlefield.go#L260-L264'),
    (0x60c518, 0x100, 'internal/game/battleengine/pickup.go#L164-L167'),
    (0x5cb4b7, 0xa7, 'local:window-005d80e1.txt VA0x5d831e direct-call target; no guessed xref'),
    (0x5eee48, 0x29, 'local:window-005d80e1.txt VA0x5d82e6 and0x5d832d direct-call target; no guessed xref'),
    (0x5f532d, 0x200, 'local:window-005cb4b7.txt VA0x5cb4ff direct-call target; no guessed xref'),
    (0x5f52ea, 0x43, 'local:window-005f532d.txt VA0x5f5361 direct-call target; no guessed xref'),
    (0x5eec60, 0x98, 'local:window-005f532d.txt VA0x5f538a constructor direct-call target; no guessed xref'),
    (0x5ef073, 0x4b, 'local:native-data.json VA0x7a369c+0x20 contains0x5ef073; exact slot called at0x5d82f4/0x5d833b'),
    (0x5ef003, 0x70, 'local:native-data.json VA0x7a369c slots+0xc/+0x10 contain0x5ef003/0x5ef04f; two bounded slots, meanings unknown before decode'),
    (0x5eee22, 0x26, 'local:native-data.json VA0x7a369c slot+0x4 contains0x5eee22; slot called at0x5cb510'),
    (0x5eedb1, 0x71, 'local:native-data.json VA0x7a369c slot+0x14 contains0x5eedb1; exact bounded slot, meaning unknown before decode'),
    (0x5ef283, 0x4c, 'local:native-data.json VA0x7a369c slot+0x3c contains0x5ef283; called by0x5eee41 initialization'),
    (0x5ef340, 0x8a, 'local:native-data.json VA0x7a369c slot+0x24 contains0x5ef340; exact bounded slot, meaning unknown before decode'),
    (0x5ef0be, 0xec, 'local:native-data.json VA0x7a369c slot+0x44 contains0x5ef0be; exact bounded slot, meaning unknown before decode'),
    (0x5eee71, 0x192, 'internal/game/battleengine/native_scene_lifecycle.go#L5-L7; bounded retirement-to-known-slot0x5ef003 window, no guessed xref'),
    (0x40c900, 0x60, 'local:window-005eee71.txt VA0x5eefe2/0x5eef4d direct-call target for two computed arguments'),
    (0x4053a8, 0x40, 'local:window-005ef003.txt VA0x5ef043 direct-call target on object+0x20; meaning unknown before decode'),
    (0x5c3b44, 0x80, 'local:window-005eee22.txt VA0x5eee2f direct-call target whose result becomes object+0x14'),
    (0x582b70, 0x30, 'local:window-0040c900.txt VA0x40c900 direct-jump target'),
    (0x583ac0, 0x180, 'local:window-004053a8.txt VA0x4053a8 direct-jump target'),
    (0x582ba0, 0x120, 'local:window-00582b70.txt continuation at its decoded instruction boundary0x582ba0; no address search'),
    (0x403cb5, 5, 'local:window-00583ac0.txt VA0x583af7 exact layer-draw call target'),
    (0x583340, 0x180, 'local:window-00403cb5.txt exact direct-jump target for layer drawing'),
    (0x5834be, 0x440, 'local:window-00583340.txt continuation at decoded instruction boundary0x5834be; terminal branch already targets0x5838f4'),
    (0x407ae5, 5, 'local:window-00583340.txt VA0x583492 exact call target returning selected frame-like pointer; type not inferred before decode'),
    (0x480970, 0xc0, 'local:window-00407ae5.txt direct-jump target of selected frame-like accessor'),
    (0x406b9f, 5, 'local:window-005834be.txt VA0x5834c4/0x5834eb exact point construction call'),
    (0x412521, 5, 'local:window-005834be.txt VA0x5834f2 exact point operation call; semantics not guessed'),
    (0x40372e, 5, 'local:window-005834be.txt VA0x5834fe exact point result copy call'),
    (0x585460, 0x100, 'local:three known direct-jump targets0x585460/0x5854a0/0x5854e0 from window-0040372e/00406b9f/00412521.txt; bounded helper window'),
]

def digest(data):
    return hashlib.sha256(data).hexdigest()

previous = HERE/'native-windows.json'
records = json.loads(previous.read_text(encoding='utf-8'))['windows'] if previous.exists() else []
code_bytes_read_this_run = 0
with zipfile.ZipFile(ARCHIVE) as archive:
    entry = archive.getinfo(ENTRY)
    assert entry.file_size == 13860864 and entry.CRC == 0x04f986c5
    with archive.open(entry) as stream:
        header = stream.read(16384)
        assert header[:2] == b'MZ'
        pe = struct.unpack_from('<I', header, 0x3c)[0]
        assert header[pe:pe+4] == b'PE\0\0'
        machine, count, _, _, _, opt_size, _ = struct.unpack_from('<HHIIIHH', header, pe+4)
        opt = pe+24
        assert machine == 0x14c and struct.unpack_from('<H', header, opt)[0] == 0x10b
        image_base = struct.unpack_from('<I', header, opt+28)[0]
        sections = []
        for index in range(count):
            at = opt+opt_size+40*index
            name = header[at:at+8].rstrip(b'\0').decode('ascii')
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from('<IIII', header, at+8)
            sections.append(dict(name=name, rva=rva, virtualSize=virtual_size, rawSize=raw_size, rawOffset=raw_offset))
        for va, size, source in WINDOWS:
            if any(record['va'] == hex(va) and record['byteLength'] == size for record in records):
                continue
            rva = va-image_base
            section = next(s for s in sections if s['rva'] <= rva and rva+size <= s['rva']+s['rawSize'])
            offset = section['rawOffset']+rva-section['rva']
            stream.seek(offset)
            data = stream.read(size)
            assert len(data) == size
            code_bytes_read_this_run += size
            # Non-executable relocatable COFF containing exactly the bounded bytes.
            coff = struct.pack('<HHIIIHH', 0x14c, 1, 0, 0, 0, 0, 0)
            coff += struct.pack('<8sIIIIIIHHI', b'.text\0\0\0', 0, va, size, 60, 0, 0, 0, 0, 0x60000020)
            wrapper = HERE / (f'window-{va:08x}.obj')
            try:
                wrapper.write_bytes(coff+data)
                result = subprocess.run([str(OBJDUMP), '-d', '--triple=i386-pc-windows', '--x86-asm-syntax=intel', str(wrapper)], capture_output=True, text=True, check=True)
            finally:
                wrapper.unlink(missing_ok=True)
            disassembly = f'window-{va:08x}.txt'
            (HERE/disassembly).write_text(result.stdout, encoding='utf-8')
            records.append(dict(va=hex(va), rva=hex(rva), fileOffset=offset, byteLength=size,
                                sha256=digest(data), bytesHex=data.hex(), containingSection=section,
                                sourceAddressCitation=source if source.startswith('local:') else f'https://github.com/kuuhaku1314/qqtang/blob/{COMMIT}/{source}',
                                disassembly=disassembly, functionEndKnown=False))

evidence = dict(schemaVersion=1, archive=str(ARCHIVE), expectedArchiveSha256='fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
    archiveHashEvidence='Previously verified fixed ZIP; no whole288MB rehash in resource freeze', archiveEntry=ENTRY,
    entryBytes=entry.file_size, entryCRC32=f'{entry.CRC:08x}', machine=hex(machine), imageBase=hex(image_base),
    logicalHeaderReadBytes=len(header), logicalCodeReadBytes=sum(record['byteLength'] for record in records),
    latestRunNewCodeReadBytes=code_bytes_read_this_run,
    readMode='ZipExtFile bounded PE header and explicit source-cited code windows; forward seek may decompress preceding bytes internally',
    inputExecuted=False, clientExtracted=False, testsRun=False, compilationPerformed=False, pngDecoded=False,
    disassembler=str(OBJDUMP), wrapper='Tiny temporary COFF data wrapper, no linker/compiler; deleted after disassembly', windows=records,
    limitations=['Community-patched client; Tencent authenticity and target historical version remain unverified.',
                 'Address labels originate in fixed community source. Instruction bytes confirm only what is visibly decoded here.',
                 'No full-binary scan, guessed xrefs, guessed function ends, client execution, or render comparison.'])
(HERE/'native-windows.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(windowCount=len(records), latestRunNewCodeReadBytes=code_bytes_read_this_run, logicalCodeReadBytes=evidence['logicalCodeReadBytes']), ensure_ascii=False))
