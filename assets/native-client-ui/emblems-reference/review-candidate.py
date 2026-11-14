"""Review own native UI pixels and prove source frame structure is retained."""
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    spec=importlib.util.spec_from_file_location('codec',ROOT/'scripts/native-ui-format.py')
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    own=json.loads((HERE/'own-mapping.json').read_bytes());targets={e['nativePath']:e for e in own['items']}
    native=json.loads((ROOT/'assets/native-client-ui/login-v1/manifest.json').read_bytes())
    allitems=[e for e in native['items'] if e['nativePath'] in targets]
    if len(allitems)!=141:raise ValueError('All 141 UI slots must be exported')
    frames=[];audit=[]
    package=(ROOT/'.artifacts/reference-inputs/object.pkg').read_bytes()
    index=codec.reader.parse_index((ROOT/'.artifacts/reference-inputs/object.idx').read_bytes(),len(package))
    source={e['path'].replace('\\','/').lower():e for e in index['entries']}
    for item in allitems:
        path=item['nativePath']
        if path.lower() in source:raw=codec.reader.unpack_resource(package,source[path.lower()])[0]
        else:
            with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as z:
                raw=z.read('QQTang-Local/runtime/client-patched/'+path)
        patch=(ROOT/item['file']).read_bytes();before,_=codec.inspect_native(raw,True);after,_=codec.inspect_native(patch,True)
        old=bytearray(raw);new=bytearray(patch)
        for a,b in zip(before['frames'],after['frames'],strict=True):
            for key in ('index','offset','frameOffset','pixelMode','width','height','empty','pixelDataOffset','pixelByteLength'):
                if a.get(key)!=b.get(key):raise ValueError('Native geometry changed')
            if a['empty']:continue
            start=a['pixelDataOffset'];end=start+a['pixelByteLength'];old[start:end]=new[start:end]=b'\0'*(end-start)
        if old!=new:raise ValueError('Native non-pixel framing changed')
        decoded=[]
        for f in after['frames']:
            if f['empty']:continue
            image=codec.decode_native_frame(patch,f)
            if image.getchannel('A').getextrema()[1]==0:raise ValueError('Own native slot became empty')
            frames.append((path,f['index'],image,f['frameOffset']))
            decoded.append({'index':f['index'],'rgbaSha256':hashlib.sha256(image.tobytes()).hexdigest(),
                            'size':list(image.size),'offset':f['frameOffset'],'alphaExtrema':list(image.getchannel('A').getextrema())})
        audit.append({'nativePath':path,'nativePatch':record(ROOT/item['file']),'frames':decoded,'nonPixelBytesEqual':True})
    previews=[]
    for page,start in enumerate(range(0,len(frames),72)):
        contact=Image.new('RGBA',(1080,8*130),'#eee7d2');draw=ImageDraw.Draw(contact)
        for n,(path,index,image,offset) in enumerate(frames[start:start+72]):
            x,y=(n%9)*120,(n//9)*130
            draw.text((x+2,y+2),path.removeprefix('object/ui/').replace('level/',''),fill='#264a3d')
            draw.text((x+2,y+14),f'#{index} {image.width}x{image.height} @{offset}',fill='#264a3d')
            factor=min(3,100//image.width,80//image.height)
            enlarged=image.resize((image.width*factor,image.height*factor),Image.Resampling.NEAREST)
            contact.alpha_composite(enlarged,(x+(120-enlarged.width)//2,y+31))
            contact.alpha_composite(image,(x+3,y+103))
        out=HERE/f'candidate-contact-{page+1:02}.png';contact.save(out,optimize=True);previews.append(record(out))
    report={'schemaVersion':1,'scope':'Own UI slots; static pixel/structure verification only','resources':len(audit),
       'sourcePositions':len(frames),'sourceMapping':record(HERE/'own-mapping.json'),'reviewer':record(Path(__file__)),
       'items':audit,'previews':previews,'visualAccepted':False,'nativeRuntimeVerified':False,'sourceTimingVerified':False,
       'cursorHotspotVerified':False,'allGameArtComplete':False}
    (HERE/'candidate-qa.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'resources':len(audit),'positions':len(frames),'pages':len(previews),'nonPixelBytesEqual':True}))


if __name__=='__main__':main()
