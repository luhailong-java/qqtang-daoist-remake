"""Only list resource names for four explicitly chosen INI layer IDs; no decode."""
from pathlib import Path
import struct, json
ROOT=Path(__file__).resolve().parents[3]
data=(ROOT/'.artifacts/reference-inputs/object.idx').read_bytes()
count=struct.unpack_from('<4I',data)[1]
cursor=16; found=[]
for ordinal in range(count):
    length=struct.unpack_from('<H',data,cursor)[0];cursor+=2
    name=data[cursor:cursor+length].decode('gb18030');cursor+=length
    values=struct.unpack_from('<4I',data,cursor);cursor+=16
    if any(word in name for word in ['16701','17301','21500','18807']):
        found.append({'path':name,'packageOffset':values[1],'rawByteLength':values[2],'compressedByteLength':values[3]})
assert cursor==len(data)
print(json.dumps({'indexEntries':count,'matches':found[:32],'matchCount':len(found),'decodedImages':0},ensure_ascii=True))
