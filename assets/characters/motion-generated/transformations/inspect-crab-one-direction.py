"""Only avatar54's tiny1-direction stand+two walk frames, reference-only."""
import pathlib,json,zlib,hashlib,importlib.util,sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3]
spec=importlib.util.spec_from_file_location('own_dimg',root/'scripts/inspect-reference-dimg.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
evidence=json.loads((base/'native-body-direction-evidence.json').read_text(encoding='utf-8'))
role=next(r for r in evidence['resources']if r['avatarRoleId']==54)
out=base/'source-reference';out.mkdir(exist_ok=True)
records=[];decoded_pixels=0
with (root/'.artifacts/reference-inputs/object.pkg').open('rb')as package:
 for action in role['actions']:
  e=action['index'];assert e['rawByteLength']<30000 and e['compressedByteLength']<10000
  package.seek(e['packageOffset']);compressed=package.read(e['compressedByteLength']);assert hashlib.sha256(compressed).hexdigest()==action['compressedSha256']
  d=zlib.decompressobj();data=d.decompress(compressed,e['rawByteLength']+1);assert d.eof and not d.unused_data and not d.unconsumed_tail and len(data)==e['rawByteLength']
  report,first=m.inspect_dimg(data);assert report['directions']==1 and report['frameCount']==(1 if action['action']=='stand' else 2)
  for frame in report['frames']:
   assert not frame['empty'] and frame['width']<=128 and frame['height']<=128
   decoded_pixels+=frame['width']*frame['height'];assert decoded_pixels<=20000
   p=frame['pixelDataOffset'];pixels=m.decode_frame_pixels(data[p:p+frame['pixelByteLength']],frame['pixelMode'],frame['width'],frame['height'])
   im=Image.frombytes('RGBA',(frame['width'],frame['height']),pixels);dest=out/f"avatar54-{action['action']}-frame{frame['index']}.png";im.save(dest)
   enlarged=Image.new('RGBA',im.size,(246,240,222,255));enlarged.alpha_composite(im);enlarged=enlarged.convert('RGB').resize((im.width*5,im.height*5),Image.Resampling.NEAREST);preview=dest.with_name(dest.stem+'-5x-reference.jpg');enlarged.save(preview,quality=95)
   record={'avatar':54,'action':action['action'],'sourcePackagePath':action['path'],'sourceDimgSha256':hashlib.sha256(data).hexdigest(),'directions':1,'frameCount':report['frameCount'],'frameIndex':frame['index'],'nativeSize':[frame['width'],frame['height']],'frameOffset':frame['frameOffset'],'png':str(dest),'preview':str(preview),'referenceOnly':True,'notRuntimeArt':True,'directionIndex':0,'cardinalLabelVerified':None,'operation':'independent decode of selected tiny source frame;5x NEAREST on ivory is inspection only, not native HD or own art','playbackTimingMs':None}
   dest.with_suffix('.png.source.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');records.append(record)
(out/'avatar54-source-states.json').write_text(json.dumps({'scope':'avatar54 single-direction only; three small necessary source poses','totalPixelCount':decoded_pixels,'fullFamilyQa':False,'records':records},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'totalPixelCount':decoded_pixels,'records':records}))
