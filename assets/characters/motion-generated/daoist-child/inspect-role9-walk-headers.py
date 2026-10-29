"""Source-role9 walk: one tiny INI and at most6 exact DIMG40-byte headers, no pixels."""
import pathlib,json,struct,zlib,hashlib,importlib.util,configparser,zipfile,sys
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3]
mapping=json.loads((base.parent/'roster-skin-mapping-20261028.json').read_text(encoding='utf-8'))
slot=next(s for s in mapping['slots']if s['sourceRoleId']==9)
assert slot['appearance']['identityId']=='daoist-child'
source=slot['sourcePlayerIni']['source']
archive=root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
with zipfile.ZipFile(archive)as z:
 info=z.getinfo(source['archiveEntry']);assert info.file_size==source['bytes'] and info.file_size<4096
 raw=z.read(info);assert hashlib.sha256(raw).hexdigest()==source['sha256']
 text=raw.decode(source['encoding']);ini=configparser.ConfigParser(interpolation=None);ini.read_string(text)
 assert dict(ini['walk'])==slot['sourcePlayerIni']['sections']['walk']
spec=importlib.util.spec_from_file_location('own_dimg_reader',root/'scripts/inspect-reference-dimg.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
pkg=root/'.artifacts/reference-inputs/object.pkg';idx=root/'.artifacts/reference-inputs/object.idx';index_raw=idx.read_bytes();entries=reader.parse_index(index_raw,pkg.stat().st_size)['entries']
lookup={e['path'].replace('\\','/').lower():e for e in entries}
selected=[('leg','10901'),('cloth','10901'),('face','10901'),('hair','10901'),('body','1'),('foot','1')]
reports=[];compressed_total=0
with pkg.open('rb')as package:
 for layer,id in selected:
  name=f'object/{layer}/{layer}{id}_walk.img';entry=lookup.get(name.lower())
  if not entry:reports.append({'layer':layer,'id':id,'exactPath':name,'status':'missing-index-entry'});continue
  assert entry['compressedByteLength']<1000000
  package.seek(entry['packageOffset']);compressed=package.read(entry['compressedByteLength']);compressed_total+=len(compressed);assert compressed_total<2000000
  header=zlib.decompressobj().decompress(compressed,40);assert len(header)==40 and header[:8]==b'QQF\x1aDIMG'
  version,fi,fc,dc,u24,u28,cw,ch=struct.unpack_from('<8I',header,8)
  assert version in[65536,65537]and fi==24 and 1<=fc<=1024 and 1<=dc<=32 and fc%dc==0
  reports.append({'layer':layer,'id':id,'exactPath':name,'index':entry,'compressedSha256':hashlib.sha256(compressed).hexdigest(),'headerSha256':hashlib.sha256(header).hexdigest(),'headerHex':header.hex(),'version':version,'frameCount':fc,'directions':dc,'framesPerDirection':fc//dc,'declaredCanvas':[cw,ch],'cardinalOrder':None,'playbackTimingMs':None,'scope':'40 expanded bytes only; no pixel decode or full-container acceptance'})
out=base/'native-role9-evidence';out.mkdir(exist_ok=True)
record={'schemaVersion':1,'sourceRoleId':9,'ownIdentity':'daoist-child','sourceRoleMapping':'assets/characters/motion-generated/roster-skin-mapping-20261028.json','sourceArchive':str(archive),'expectedArchiveSha256':mapping['source']['archiveSha256'],'archiveHashScope':'Previously fixed archive, not rehashed during machine freeze','playerIni':{**source,'text':text,'actualReadSha256':hashlib.sha256(raw).hexdigest()},'walkLayers':dict(ini['walk']),'selectionScope':'Six exact objects: leg/cloth/face/hair10901 plus body1/foot1 walk. head1 not needed for first leg-phase evidence; no broad object scan/pixels.','indexSha256':hashlib.sha256(index_raw).hexdigest(),'packageBytes':pkg.stat().st_size,'compressedBytesRead':compressed_total,'expandedHeaderBytes':40*sum('frameCount'in e for e in reports),'pixelFramesDecoded':0,'resources':reports,'originalAppearanceAdopted':False,'externalCodeExecuted':False,'clientRun':False}
(out/'native-walk-headers.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'playerIni':source,'walk':dict(ini['walk']),'compressedBytesRead':compressed_total,'expandedHeaderBytes':record['expandedHeaderBytes'],'resources':[{k:r.get(k)for k in['layer','exactPath','status','version','frameCount','directions','framesPerDirection','declaredCanvas']}for r in reports]},ensure_ascii=False))
