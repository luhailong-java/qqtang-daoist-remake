"""Read exactly six selected DIMG headers; never decode a pixel plane."""
from pathlib import Path
from datetime import datetime,timezone
import struct,json,hashlib,zlib,zipfile,configparser,io
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'creatures'/'motion-contract'
OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive=ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
index_path=ROOT/'.artifacts/reference-inputs/object.idx'
package_path=ROOT/'.artifacts/reference-inputs/object.pkg'
index=index_path.read_bytes();cursor=16;entries={}
for ordinal in range(struct.unpack_from('<4I',index)[1]):
    length=struct.unpack_from('<H',index,cursor)[0];cursor+=2
    name=index[cursor:cursor+length].decode('gb18030');cursor+=length
    reserved,offset,rawsize,compsize=struct.unpack_from('<4I',index,cursor);cursor+=16
    entries[name]={'ordinal':ordinal,'offset':offset,'rawByteLength':rawsize,'compressedByteLength':compsize,'reservedWord':reserved}
assert cursor==len(index)
selected=[f'object\\cloth\\cloth{layer}_{action}.img' for layer in [16701,17301] for action in ['stand','walk','die']]
assert len(selected)==6
resources=[]
with package_path.open('rb')as package:
    for path in selected:
        entry=entries[path];package.seek(entry['offset']);compressed=package.read(entry['compressedByteLength'])
        assert len(compressed)==entry['compressedByteLength']
        inflater=zlib.decompressobj();raw=inflater.decompress(compressed,entry['rawByteLength']+1)
        assert inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail and len(raw)==entry['rawByteLength']
        assert len(raw)>=40 and raw[:8]==b'QQF\x1aDIMG'
        words=list(struct.unpack_from('<8I',raw,8));version,info_size,count,directions,u24,u28,width,height=words
        assert 1<=directions<=32 and 1<=count<=1024 and count%directions==0
        item={'resourcePath':path,'indexEntry':entry,'indexSHA256':sha(index),
              'compressedChunkSHA256':sha(compressed),'rawResourceSHA256':sha(raw),'header40SHA256':sha(raw[:40]),
              'headerHex':raw[:40].hex(),'version':version,'declaredFrameInfoSize':info_size,'declaredFrameCount':count,
              'declaredDirections':directions,'declaredFramesPerDirection':count//directions,
              'declaredCanvas':[width,height],'unknownHeaderWordsAt24And28':[u24,u28],
              'directionOrder':None,'frameDurationMs':None,'loopPolicy':None,'footAnchor':None,
              'entityIdBinding':None,'nativePlayerBindingType':'INI layer link only; not bound to any97 adventure boss_id',
              'pixelPlanesDecoded':0,'frameBodiesInspected':False,'wholeContainerAccepted':False,
              'scope':'header declarations and bounded zlib stream only; does not establish actual direction order, frames, motion or client playback'}
        resources.append(item)
        save(OUT/(Path(path.replace('\\','/')).name+'.header.json'),item)
inis=[]
with zipfile.ZipFile(archive)as z:
    for player in [67,73]:
        member=f'QQTang-Local/runtime/client-patched/object/player/player{player}.ini'
        raw=z.read(member);text=raw.decode('gb18030');cfg=configparser.ConfigParser();cfg.read_file(io.StringIO(text))
        inis.append({'nativePlayerNumber':player,'member':member,'bytes':len(raw),'sha256':sha(raw),'textUnmodified':text,
                     'sections':{s:dict(cfg[s])for s in cfg.sections()},'adventureEntityBinding':None,
                     'note':'player73 cry=173701 is kept exactly; no arithmetic correction or inferred replacement'})
source={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'archive':archive.relative_to(ROOT).as_posix(),
        'archiveSHA256PriorPinned':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7',
        'archiveRehashedThisPass':False,'packageFile':package_path.relative_to(ROOT).as_posix(),
        'packageZIPMember':'QQTang-Local/runtime/client-patched/data/object.pkg','packageRehashedThisPass':False,
        'indexFile':index_path.relative_to(ROOT).as_posix(),'indexZIPMember':'QQTang-Local/runtime/client-patched/data/object.idx',
        'indexBytes':len(index),'indexSHA256':sha(index),'selectedResourceCount':6,'pixelPlanesDecoded':0,
        'sourceAuthenticity':'community-patched-client; Tencent original official authenticity unverified',
        'iniSamples':inis,'resourceSamples':resources,'mappedAdventureEntities':0,
        'formatEvidence':{'localFile':'.artifacts/reference-inputs/community-dimg-format.go','readOnly':True,'executed':False,
                          'scope':'40-byte header layout only; no use of default100ms GM preview as native timing'},
        'limitations':['INI status names and DIMG counts do not prove NPC mapping.','No direction names/order or timing inferred.','No DIMG frame/pixel decode or full-package validation performed.']}
save(OUT/'six-header-evidence.json',source)
print(json.dumps({'selectedHeaders':len(resources),'pixelPlanesDecoded':0,'mappedAdventureEntities':0,'rows':[{'path':x['resourcePath'],'frames':x['declaredFrameCount'],'directions':x['declaredDirections'],'perDirection':x['declaredFramesPerDirection']}for x in resources]},ensure_ascii=True))
