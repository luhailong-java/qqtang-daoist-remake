"""Exactly3 tiny native leg probes at frame0/6/12, no assumed cardinal ordering."""
import pathlib,json,zlib,hashlib,importlib.util,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3];out=base/'native-role9-evidence'
header=json.loads((out/'native-walk-headers.json').read_text(encoding='utf-8'));source=next(r for r in header['resources']if r['layer']=='leg');e=source['index']
assert e['rawByteLength']<150000 and e['compressedByteLength']<30000
with (root/'.artifacts/reference-inputs/object.pkg').open('rb')as p:p.seek(e['packageOffset']);compressed=p.read(e['compressedByteLength'])
assert hashlib.sha256(compressed).hexdigest()==source['compressedSha256']
d=zlib.decompressobj();raw=d.decompress(compressed,e['rawByteLength']+1);assert d.eof and not d.unused_data and not d.unconsumed_tail and len(raw)==e['rawByteLength']
sp=importlib.util.spec_from_file_location('own_dimg',root/'scripts/inspect-reference-dimg.py');reader=importlib.util.module_from_spec(sp);sp.loader.exec_module(reader)
meta,first=reader.inspect_dimg(raw);assert meta['directions']==4 and meta['frameCount']==24 and meta['declaredCanvas']==[100,100]
board=Image.new('RGB',(1500,550),(246,240,222));draw=ImageDraw.Draw(board);font=ImageFont.load_default(size=18)
records=[];total=0
for i,index in enumerate([0,6,12]):
 f=meta['frames'][index];assert not f['empty'] and f['width']<100 and f['height']<100
 pixels=first['pixels']if index==first['index']else reader.decode_frame_pixels(raw[f['pixelDataOffset']:f['pixelDataOffset']+f['pixelByteLength']],f['pixelMode'],f['width'],f['height'])
 total+=f['width']*f['height'];assert total<10000
 im=Image.frombytes('RGBA',(f['width'],f['height']),pixels);dest=out/f'leg10901-walk-f{index:02d}.png';im.save(dest)
 view=Image.new('RGBA',(100,100),(246,240,222,255));x,y=f['frameOffset'];assert x>=0 and y>=0 and x+im.width<=100 and y+im.height<=100;view.alpha_composite(im,(x,y));board.paste(view.convert('RGB').resize((500,500),Image.Resampling.NEAREST),(i*500,50))
 draw.text((i*500+12,10),f'group {index//6} / frame {index} / raw offset {x},{y}',font=font,fill=(50,60,55))
 rec={'frameIndex':index,'directionGroupIndex':index//6,'phaseIndex':0,'semanticCardinal':None,'nativeSize':[f['width'],f['height']],'frameOffset':f['frameOffset'],'pixelMode':f['pixelMode'],'encodedPixelSha256':f['encodedPixelSha256'],'rgbaSha256':hashlib.sha256(pixels).hexdigest(),'png':str(dest),'pngSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'referenceOnly':True,'notOwnCharacterArt':True}
 dest.with_suffix('.png.source.json').write_text(json.dumps({'sourceRoleId':9,'sourceResource':source['exactPath'],'sourceDimgSha256':meta['sha256'],'sourcePackageIndex':e,**rec,'operation':'Native selected-frame decode only; no resizing/mirroring/repainting in this PNG.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');records.append(rec)
sheet=out/'leg-direction-probes-5x.png';board.save(sheet)
record={'sourceRoleId':9,'ownIdentity':'daoist-child','sourceResource':source['exactPath'],'sourceDimgSha256':meta['sha256'],'sourceCompressedSha256':source['compressedSha256'],'containerStrictAccepted':meta['strictCompleteContainerAccepted'],'sourceDimg':meta,'decodedIndices':[0,6,12],'decodedFrameCount':3,'totalDecodedPixels':total,'records':records,'board':str(sheet),'boardSha256':hashlib.sha256(sheet.read_bytes()).hexdigest(),'operation':'Reference-only selected source legs at original100px canvas with original offsets, 5x NEAREST inspection sheet. Labels use group/index only; cardinal order not assumed.','directionVisuallyVerified':False,'timingMs':None,'sourceAppearanceAdopted':False,'runtimeEnabled':False}
(out/'leg-direction-probes.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k]for k in['sourceResource','decodedIndices','totalDecodedPixels','board','directionVisuallyVerified']}))
