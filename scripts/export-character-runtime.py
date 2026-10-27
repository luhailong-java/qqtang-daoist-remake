"""Premultiplied-alpha runtime resize of retained original masters; no new art."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[1]
art_path=root/'assets/art.json'
art=json.loads(art_path.read_text(encoding='utf-8'))
ids=['daoist-child','moon-shadow','mountain-guardian','lotus-healer']
out=root/'assets/characters/runtime';out.mkdir(exist_ok=True)
records=[]
for index,ident in enumerate(ids):
    source=root/'assets/characters'/f'{ident}.png'
    im=Image.open(source).convert('RGBA')
    resized=im.convert('RGBa').resize((1024,1024),Image.Resampling.LANCZOS).convert('RGBA')
    target=out/f'{ident}.png';resized.save(target)
    bbox=resized.getchannel('A').getbbox()
    entry={'file':'./'+target.relative_to(root).as_posix(),'width':1024,'height':1024,
        'rect':[bbox[0],bbox[1],bbox[2]-bbox[0],bbox[3]-bbox[1]]}
    art['characters']['assets'][index]=entry
    record={'file':entry['file'],'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'source':source.relative_to(root).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'sourceProvenance':source.relative_to(root).as_posix()+'.source.json',
        'sourceSize':list(im.size),'exportSize':[1024,1024],'scale':.25,
        'operation':'premultiplied-alpha-LANCZOS-full-canvas-resize','newModelGeneration':False,
        'nativeGenerationResolution':None,'nativeGenerationResolutionConfirmed':False,
        'alphaExtrema':list(resized.getchannel('A').getextrema()),'visibleBounds':list(bbox),
        'runtimeDecodedBytes':1024*1024*4}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    records.append(record)
art_path.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'manifest.json').write_text(json.dumps({'schemaVersion':1,'characters':records,
    'decodedBytesBefore':4096*4096*4*4,'decodedBytesAfter':1024*1024*4*4},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exports':len(records),'decodedMiBBefore':256,'decodedMiBAfter':16}))
