"""Six exact source containers; one group2 probe plus four requested phase positions.
No client execution; parse metadata then decode only selected small frames/layers.
"""
import pathlib,json,zlib,hashlib,struct,importlib.util,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3];out=base/'native-role9-evidence'
headers=json.loads((out/'native-walk-headers.json').read_text(encoding='utf-8'))
sp=importlib.util.spec_from_file_location('own_dimg',root/'scripts/inspect-reference-dimg.py');reader=importlib.util.module_from_spec(sp);sp.loader.exec_module(reader)
mode=sys.argv[1]if len(sys.argv)>1 else'probe';assert mode in['probe','probe0','phases','six']
indices=[12]if mode=='probe'else[0]if mode=='probe0'else[0,3]if mode=='six'else[1,2,4,5]
# All six container names were selected and header-read beforehand; no seventh resource.
order=['face']if mode=='probe0'else['body','foot','leg','cloth','face','hair']
selected={r['layer']:r for r in headers['resources']};containers={};decoded_pixels=0;decoded_frames=0;records=[]
with (root/'.artifacts/reference-inputs/object.pkg').open('rb')as pkg:
 for layer in order:
  r=selected[layer];e=r['index'];assert e['rawByteLength']<500000 and e['compressedByteLength']<100000
  pkg.seek(e['packageOffset']);compressed=pkg.read(e['compressedByteLength']);assert hashlib.sha256(compressed).hexdigest()==r['compressedSha256']
  d=zlib.decompressobj();data=d.decompress(compressed,e['rawByteLength']+1);assert d.eof and not d.unused_data and not d.unconsumed_tail and len(data)==e['rawByteLength']
  assert data[:8]==b'QQF\x1aDIMG';version,fi,fc,dc,u24,u28,cw,ch=struct.unpack_from('<8I',data,8);assert version==65536 and fi==24 and fc==24 and dc==4 and[cw,ch]==[100,100]
  # Metadata-only parsing avoids inspect_dimg's automatic first-visible pixel decode.
  cursor=40;frames=[]
  for index in range(fc):
   start=cursor;marker,x,y,pixel_mode=struct.unpack_from('<IiiI',data,cursor);cursor+=16;assert marker==0
   f={'frameIndex':index,'directionGroupIndex':index//6,'phaseIndex':index%6,'frameOffset':[x,y],'pixelMode':pixel_mode,'sourceByteOffset':start,'empty':True}
   if pixel_mode:
    w,h,unknown=struct.unpack_from('<3I',data,cursor);cursor+=12;assert 0<=w<100 and 0<=h<100
    if w and h:
     assert pixel_mode in[3,0x11000000,8,16];length=w*h*(4 if pixel_mode==8 else 3);assert cursor+length<=len(data)
     f.update({'empty':False,'nativeSize':[w,h],'unknownImageHeaderWord':unknown,'pixelDataOffset':cursor,'pixelByteLength':length,'encodedPixelSha256':hashlib.sha256(data[cursor:cursor+length]).hexdigest()});cursor+=length
   frames.append(f)
  assert cursor==len(data)
  containers[layer]={'data':data,'sha256':hashlib.sha256(data).hexdigest(),'frames':frames,'resource':r['exactPath'],'index':e,'strictCompleteContainerAccepted':True}
sheet=Image.new('RGB',(1500,550)if mode=='probe'else(500,550)if mode=='probe0'else(1500,1100)if mode=='six'else(1000,1100),(246,240,222));draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=18)
reused_records=[]
if mode=='six':
 previous=json.loads((out/'group0-four-phase-board.json').read_text(encoding='utf-8'));assert previous['selectedIndices']==[1,2,4,5]
 for pose in previous['records']:
  im=Image.open(pose['diagnosticComposite']).convert('RGB');assert im.size==(100,100);idx=pose['frameIndex'];x=(idx%3)*500;y=(idx//3)*550
  sheet.paste(im.resize((500,500),Image.Resampling.NEAREST),(x,y+50));draw.text((x+10,y+10),f'E group0 frame{idx} / phase{idx}',font=font,fill=(50,60,55));reused_records.append(pose)
for pose_index,index in enumerate(indices):
 planes={};pose_layers=[]
 for layer in order:
  c=containers[layer];f=c['frames'][index];plane=Image.new('RGBA',(100,100),(0,0,0,0));record={'layer':layer,'sourceResource':c['resource'],'sourceDimgSha256':c['sha256'],'sourcePackageIndex':c['index'],**f}
  if not f['empty']:
   w,h=f['nativeSize'];x,y=f['frameOffset'];assert x>=0 and y>=0 and x+w<=100 and y+h<=100
   pixels=reader.decode_frame_pixels(c['data'][f['pixelDataOffset']:f['pixelDataOffset']+f['pixelByteLength']],f['pixelMode'],w,h);decoded_frames+=1;decoded_pixels+=w*h;assert decoded_pixels<100000
   im=Image.frombytes('RGBA',(w,h),pixels);dest=out/f'{layer}-native-walk-f{index:02d}.png';im.save(dest);plane.alpha_composite(im,(x,y))
   record.update({'png':str(dest),'pngSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rgbaSha256':hashlib.sha256(pixels).hexdigest()})
   dest.with_suffix('.png.source.json').write_text(json.dumps({'sourceRoleId':9,**record,'referenceOnly':True,'sourceAppearanceAdopted':False,'operation':'Native selected small frame decode, no resize/repaint/mirror; offset not applied in this tight PNG.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  planes[layer]=plane;pose_layers.append(record)
 composite=Image.new('RGBA',(100,100),(246,240,222,255))
 for layer in order:composite.alpha_composite(planes[layer])
 if mode=='probe':
  # Native leg layer already sampled. Show face,cloth and diagnostic full layer order.
  for i,(name,im)in enumerate([('face',planes['face']),('cloth',planes['cloth']),('six-layer diagnostic',composite)]):
   opaque=Image.new('RGBA',(100,100),(246,240,222,255));opaque.alpha_composite(im);sheet.paste(opaque.convert('RGB').resize((500,500),Image.Resampling.NEAREST),(i*500,50));draw.text((i*500+10,10),f'{name} group2 frame12',font=font,fill=(50,60,55))
 elif mode=='probe0':
  sheet.paste(composite.convert('RGB').resize((500,500),Image.Resampling.NEAREST),(0,50));draw.text((10,10),'face group0 frame0, raw offset',font=font,fill=(50,60,55))
 elif mode=='six':
  x=(index%3)*500;y=(index//3)*550;sheet.paste(composite.convert('RGB').resize((500,500),Image.Resampling.NEAREST),(x,y+50));draw.text((x+10,y+10),f'E group0 frame{index} / phase{index}',font=font,fill=(50,60,55))
 else:
  x=(pose_index%2)*500;y=(pose_index//2)*550;sheet.paste(composite.convert('RGB').resize((500,500),Image.Resampling.NEAREST),(x,y+50));draw.text((x+10,y+10),f'group{index//6} frame{index} / phase{index%6}',font=font,fill=(50,60,55))
 native=out/f'{"face-only"if mode=="probe0"else"six-layer"}-diagnostic-f{index:02d}.png';composite.convert('RGB').save(native)
 records.append({'frameIndex':index,'directionGroupIndex':index//6,'phaseIndex':index%6,'nativeCanvas':[100,100],'diagnosticComposite':str(native),'layers':pose_layers,'timingMs':None,'cardinalDirectionNotYetVerified':True})
stem='group2-direction-probe'if mode=='probe'else'group0-face-direction-probe'if mode=='probe0'else'group0-six-phase-board'if mode=='six'else'group0-four-phase-board'
dest=out/(stem+'-5x.png');sheet.save(dest)
record={'sourceRoleId':9,'ownIdentity':'daoist-child','mode':mode,'sourceObjectCount':len(order),'knownObjectBudgetTotal':6,'selectedIndices':list(range(6))if mode=='six'else indices,'sourceDirectionCount':4,'sourceFramesPerDirection':6,'cardinalOrderAssumed':False,'decodedIndicesThisCall':indices,'decodedNonemptyLayerFrames':decoded_frames,'decodedPixels':decoded_pixels,'reusedAlreadyDecodedPositions':len(reused_records),'compositeOrder':order,'compositeScope':'Inspection overlay using raw common100px canvas and original per-layer offsets. Layer order is an explicit diagnostic choice, not independently verified native rendering order; raw layers retained. head1 not read/used.','board':str(dest),'boardSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'records':sorted(records+reused_records,key=lambda p:p['frameIndex']),'referenceOnly':True,'sourceAppearanceAdopted':False,'runtimeEnabled':False,'fullFamilyQa':False,'clientRun':False,'actualVisualViewed':False}
if mode=='six':
 comparisons=[]
 for layer in order:
  f0=containers[layer]['frames'][0];f3=containers[layer]['frames'][3];fields=['empty','nativeSize','frameOffset','pixelMode','encodedPixelSha256'];same={key:f0.get(key)==f3.get(key)for key in fields}
  comparisons.append({'layer':layer,'frame0':f0,'frame3':f3,'equalFields':same,'sameVisibleLayerEncodedBytesSizeOffset':all(same.values())})
 record['frame0Frame3Comparisons']=comparisons;record['allVisibleLayers0And3Identical']=all(c['sameVisibleLayerEncodedBytesSizeOffset']for c in comparisons);record['aliasApproved']=False;record['aliasCaution']='Do not alias whole poses merely because leg layer alone repeats. Source timing/order remains unknown even if all layers were equal.'
(out/(stem+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k]for k in['mode','sourceObjectCount','selectedIndices','decodedNonemptyLayerFrames','decodedPixels','board']}))
