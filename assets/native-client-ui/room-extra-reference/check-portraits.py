"""Check own portrait registration, original card alpha and final native edges."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct

from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path,value,check):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if check:
        if path.read_bytes()!=raw:raise ValueError('Portrait evidence differs')
    else:path.write_bytes(raw)


def build(check=False):
    spec=importlib.util.spec_from_file_location('room_portrait_art',ROOT/'scripts/native-ui-roomextra-art.py')
    art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
    rows=[];raw_hashes=set();native_hashes=set()
    board=Image.new('RGB',(1000,1240))
    draw=ImageDraw.Draw(board)
    for bg_index,bg in enumerate(('#142720','#f3ead2')):
        draw.rectangle((0,bg_index*620,999,bg_index*620+619),fill=bg)
    aliases=list(art._ROLES)+art._EXTRA
    for alias in aliases:
        extra=alias in art._EXTRA
        key=f'roomextra-{"extra" if extra else "role"}-{alias}'
        path=ROOT/art.PAINT_INPUTS[key]
        image=Image.open(path).convert('RGBA')
        geometry=art.icon_geometry(image)
        crop=image.crop(geometry['sourceBox'])
        factor=min(45/crop.width,45/crop.height)
        extent=(max(1,round(crop.width*factor)),max(1,round(crop.height*factor)))
        registered=Image.new('L',(55,55))
        body=crop.convert('RGBa').resize(extent,Image.Resampling.LANCZOS).convert('RGBA').getchannel('A')
        registered.paste(body,(4+(47-extent[0])//2,4+47-1-extent[1]))
        source=art._BY_PATH[f'object/ui/room/char/icon_{alias}.img']
        frames=[]
        for frame in source['metadata']['frames']:
            i=frame['index'];x,y=frame['frameOffset'];w,h=frame['width'],frame['height']
            kept=Image.new('L',(55,55));kept.paste(registered.crop((x,y,x+w,y+h)),(x,y))
            if kept.tobytes()!=registered.tobytes():raise ValueError('A native state window cuts the own portrait subject')
            original_path=ROOT/source['frames'][i]['file']
            original=Image.open(original_path).convert('RGBA')
            if original.getchannel('A').crop((4,4,w-4,h-4)).getextrema()!=(255,255):
                raise ValueError('Original portrait interior alpha is not a plain opaque card; do not inherit face silhouettes')
            native_path=HERE/'candidate/decoded'/f'icon_{alias}-{i:02}.png'
            native=Image.open(native_path).convert('RGBA')
            if native.getchannel('A').tobytes()!=original.getchannel('A').tobytes():
                raise ValueError('Original portrait card functional alpha changed')
            saturated_green=0
            for r,g,b,a in struct.iter_unpack('4B',native.tobytes()):
                if a>=8 and g>=150 and g-r>80 and g-b>80:saturated_green+=1
            frames.append({**record(native_path),'index':i,'frameOffset':frame['frameOffset'],
                           'cardAlphaIdenticalToSource':True,'ownSubjectPixelsClippedByNativeWindow':0,
                           'selectedSaturatedGreenPixelCount':saturated_green})
        if extra:
            generation_path=path.with_suffix('.png.generation.json')
            generation=json.loads(generation_path.read_bytes())
            if generation['sha256']!=record(path)['sha256'] or generation['sourceNativePath']!=source['nativePath']:
                raise ValueError('Actual new portrait provenance differs from its stable native slot')
            if generation['submitted']!=next(r['submitted'] for r in json.loads((HERE/'extra-icon-generation-requests.json').read_bytes())['requests'] if r['slotKey']==alias):
                raise ValueError('Recorded actual image prompt differs')
            raw_hashes.add(record(path)['sha256'])
            native_hashes.add(record(HERE/'candidate/decoded'/f'icon_{alias}-00.png')['sha256'])
            slot=art._EXTRA.index(alias)
            native=Image.open(HERE/'candidate/decoded'/f'icon_{alias}-00.png').convert('RGBA')
            for bg_index,bg in enumerate(('#142720','#f3ead2')):
                x,y=(slot%5)*200+12,bg_index*620+(slot//5)*150+10
                surface=Image.new('RGBA',native.size,bg);surface.alpha_composite(native)
                surface=surface.convert('RGB').resize((native.width*2,native.height*2),Image.Resampling.NEAREST)
                board.paste(surface,(x,y));draw.text((x,y+116),f'icon_{alias}',fill='#f3ead2' if bg_index==0 else '#142720')
        rows.append({'alias':alias,'sourceRoleId':art._ROLES[alias]['sourceRoleId'] if alias in art._ROLES else None,
                     'input':record(path),'packing':geometry,'logicalSubjectAlphaSha256':hashlib.sha256(registered.tobytes()).hexdigest(),
                     'sameLogicalSubjectForAllNativeStates':True,'frames':frames,
                     'newBuiltinOriginal':extra,'worldModelBindingVerified':False})
    if len(raw_hashes)!=17 or len(native_hashes)!=17:raise ValueError('Extra UI slots require seventeen distinct actual originals and native portraits')
    diagnostic=HERE/'candidate/extra-icon-edge-diagnostic.png'
    if check:
        old=Image.open(diagnostic)
        if old.size!=board.size or old.convert('RGB').tobytes()!=board.tobytes():raise ValueError('Portrait compositing diagnostic changed')
    else:board.save(diagnostic)
    result={'schemaVersion':1,'checker':record(Path(__file__).resolve()),'renderer':record(ROOT/'scripts/native-ui-roomextra-art.py'),
            'scope':'Twenty proven project role identities plus seventeen independent original PVE/unbound UI image slots',
            'portraitIdentities':37,'newActualBuiltinOriginals':17,'uniqueNewMasterHashes':len(raw_hashes),
            'uniqueNewNativePortraitHashes':len(native_hashes),'nativeStateWindowsClipOwnSubject':False,
            'sourceCardInteriorAlphaCheckedOpaque':True,'portraitCardAlphaIdenticalToSource':True,
            'selectedGreenCriterion':'A>=8, G>=150, G-R>80 and G-B>80; designed jade colors are not automatically artifacts',
            'diagnostic':record(diagnostic),'diagnosticMethod':'Actual native decoded UI cards alpha-composited onto deep jade and ivory then nearest-neighbor2x',
            'items':rows,'visualAccepted':False,'nativeRuntimeVerified':False,'worldCreatureActionsComplete':False}
    save(HERE/'portrait-evidence.json',result,check)
    print(json.dumps({'portraitIdentities':37,'newDistinctOriginals':17,'nativeSubjectClips':0,
                      'newNativeSelectedGreenPixels':sum(f['selectedSaturatedGreenPixelCount'] for r in rows if r['newBuiltinOriginal'] for f in r['frames']),
                      'readOnlyReplay':check}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');build(parser.parse_args().check)
