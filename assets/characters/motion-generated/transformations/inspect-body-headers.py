"""16 exact DIMG headers only for eight declared avatars. No frame pixel decode."""
import pathlib,json,struct,zlib,hashlib,importlib.util,sys
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent
root=base.parents[3]
assert root.name=='qqtang-ui'
index_path=root/'.artifacts/reference-inputs/object.idx';package_path=root/'.artifacts/reference-inputs/object.pkg'
spec=importlib.util.spec_from_file_location('own_independent_dimg_reader',root/'scripts/inspect-reference-dimg.py')
own=importlib.util.module_from_spec(spec);spec.loader.exec_module(own)
index_bytes=index_path.read_bytes();index=own.parse_index(index_bytes,package_path.stat().st_size)
by_path={e['path'].replace('\\','/').lower():e for e in index['entries']}
masters=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
player=json.loads((base.parent/'roster-player-static-evidence.json').read_text(encoding='utf-8'))
cfg={c['id']:c for c in player['playerPy']['assignments']['playerCfg']}
records=[];compressed_read=0
with package_path.open('rb')as package:
 for avatar in masters['entries']:
  ident=avatar['sourceAvatarRoleId'];entry={'avatarRoleId':ident,'ownIdentity':avatar['ownIdentity']['id'],'nativePlayerIni':avatar['nativePlayerIni'],'playerPyActions':cfg.get(ident),'actions':[]}
  for action,section in avatar['nativePlayerIni']['sections'].items():
   if action not in ['stand','walk']:raise ValueError('Unexpected declaration; inspect independently')
   body=section['body'];name=f'object/body/body{body}_{action}.img';source=by_path.get(name.lower())
   if source is None:entry['actions'].append({'action':action,'body':body,'path':name,'missingIndexEntry':True});continue
   size=source['compressedByteLength'];assert size<=100000
   compressed_read+=size;assert compressed_read<=500000
   package.seek(source['packageOffset']);compressed=package.read(size);assert len(compressed)==size
   decoder=zlib.decompressobj();header=decoder.decompress(compressed,40)
   assert len(header)==40 and header[:8]==b'QQF\x1aDIMG'
   version,frame_info_size,frames,directions,u24,u28,cw,ch=struct.unpack_from('<8I',header,8)
   assert version in [65536,65537] and frame_info_size==24 and 1<=frames<=1024 and 1<=directions<=32 and frames%directions==0
   entry['actions'].append({'action':action,'body':body,'path':name,'index':source,'compressedSha256':hashlib.sha256(compressed).hexdigest(),'headerHex':header.hex(),'headerSha256':hashlib.sha256(header).hexdigest(),'version':version,'frameInfoSize':frame_info_size,'frameCount':frames,'directions':directions,'declaredFramesPerDirection':frames//directions,'unknown24and28':[u24,u28],'declaredCanvas':[cw,ch],'scope':'40 expanded bytes only; zlib remainder/pixel frames/complete container not decoded or verified','semanticDirectionOrder':None,'playbackTimingMs':None})
  records.append(entry)
out={'schemaVersion':1,'scope':'Exact16 stand/walk DIMG40-byte headers of eight NativeTransformation avatars; read-only static small bounds, no game/build/frame decode.','sourceArchiveSha256':own.ARCHIVE_SHA256,'sourceArchiveHashScope':'Previously fixed package; full archive/package not rehashed during machine freeze','indexPath':str(index_path),'indexBytes':len(index_bytes),'indexSha256':hashlib.sha256(index_bytes).hexdigest(),'packagePath':str(package_path),'packageBytes':package_path.stat().st_size,'compressedBytesRead':compressed_read,'expandedBytesRead':sum(len(e['actions'])*40 for e in records),'fullImageDecodes':0,'resources':records,'formatSemantics':'Community format + independent raw header signature/field checks; cardinal direction index order and client usage not independently verified.'}
(base/'native-body-direction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'compressedBytesRead':compressed_read,'expandedBytesRead':out['expandedBytesRead'],'avatars':[{'id':e['avatarRoleId'],'cfg':e['playerPyActions'],'actions':[{k:a.get(k)for k in ['action','body','frameCount','directions','declaredFramesPerDirection']}for a in e['actions']]}for e in records]},ensure_ascii=False))
