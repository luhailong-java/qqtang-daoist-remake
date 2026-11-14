"""Convert existing original inventory PNGs to their exact installed native icon resources."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'assets/native-client-ui/inventory-v1'
ARCHIVE = ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
CATALOG = ROOT/'references/qqtang-item-data/catalog.json'
FOLDERS = (
    'skills', 'food', 'forge', 'petcards', 'cards-currency', 'platform', 'head-adornments',
    'surroundings', 'eye-adornments', 'footprints', 'namecard-borders/inventory',
    'mouth-adornments/cloud-masquerade-a', 'wing-adornments/spirit-wings-a',
    'profile-frames/elemental-medals', 'scenic-backgrounds/four-seasons-a',
    'clothing-adornments/dragon-guard-a', 'entry-effects/world-1658',
)
MANIFESTS = ['assets/items/art.json'] + [f'assets/items/{name}/art.json' for name in FOLDERS]
MANIFESTS += [f'assets/items/{name}/inventory-combined.json' for name in ('hats','back-adornments','bubble-skins')]
spec = importlib.util.spec_from_file_location('native_codec',ROOT/'scripts/native-ui-format.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def save_json(path, data, check):
    if check:
        if json.loads(path.read_bytes()) != data:
            raise ValueError(f'Native inventory metadata differs: {path}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())


def save_bytes(path, content, check):
    if check:
        if path.read_bytes() != content:
            raise ValueError(f'Native inventory bytes differ: {path}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(content)


def save_image(path, picture, check):
    if check:
        with Image.open(path) as actual:
            if (actual.mode,actual.size,actual.tobytes()) != (picture.mode,picture.size,picture.tobytes()):
                raise ValueError(f'Native inventory pixels differ: {path}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        picture.save(path,optimize=True)


def candidate_fit(picture, size):
    visible = picture.getchannel('A').point(lambda value:255 if value >= 8 else 0).getbbox()
    if visible is None:
        raise ValueError('Inventory candidate has no visible content')
    content = picture.crop(visible)
    scale = min(size[0]/content.width,size[1]/content.height)
    fitted = tuple(max(1,round(axis*scale)) for axis in content.size)
    placement = tuple((axis-drawn)//2 for axis,drawn in zip(size,fitted,strict=True))
    output = Image.new('RGBA',size)
    resized = content.convert('RGBa').resize(fitted,Image.Resampling.LANCZOS).convert('RGBA')
    output.alpha_composite(resized,placement)
    return output,{'type':'visible alpha content, uniform centered fit into original native frame',
                   'sourceAlpha8BBox':list(visible),'uniformScale':scale,
                   'scaledSize':list(fitted),'placementPx':list(placement),
                   'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    check = parser.parse_args().check
    with ARCHIVE.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Native source archive changed')
    catalog = {e['item_id']:e for e in json.loads(CATALOG.read_bytes())['items']}
    candidates = {}
    inputs = []
    for filename in MANIFESTS:
        path = ROOT/filename
        inputs.append(ref(path))
        for item in json.loads(path.read_bytes())['items']:
            previous = candidates.get(item['itemId'])
            if previous and (previous['file'],previous['sha256']) != (item['file'],item['sha256']):
                raise ValueError('Two different inventory candidates for one source item')
            candidates[item['itemId']] = item
    resources, sources, pending = [], [], []
    destinations = set()
    with zipfile.ZipFile(ARCHIVE) as archive:
        for item_id,item in sorted(candidates.items()):
            source = catalog[item_id]
            if item['category'] != source['category']:
                raise ValueError(f'Inventory category differs: {item_id}')
            candidate_path = ROOT/item['file']
            if sha(candidate_path.read_bytes()) != item['sha256']:
                raise ValueError(f'Own candidate changed: {item_id}')
            native_paths = [path for path in source['installed_files'] if path.startswith('res/uiRes/icon/') and path.endswith('.img')]
            if len(native_paths) != 1:
                pending.append({'itemId':item_id,'reason':'No unique installed native inventory IMG in the catalog','installedFiles':source['installed_files']})
                continue
            native_path = native_paths[0]
            if native_path.lower() in destinations:
                raise ValueError('Two items resolve to the same native icon destination')
            destinations.add(native_path.lower())
            member = 'QQTang-Local/runtime/client-patched/'+native_path
            raw = archive.read(member)
            metadata,_ = codec.reader.inspect_dimg(raw,metadata_only=True,reference_only_version65537_suffix=True)
            if metadata['frameCount'] != 1 or metadata['frames'][0]['empty']:
                pending.append({'itemId':item_id,'nativePath':native_path,'reason':'Multiple native phases need a separate export',
                                'sourceSha256':sha(raw),'metadata':metadata})
                continue
            normalization = None
            encode_source = raw
            if metadata['trailingByteLength']:
                if metadata['version'] != 65537:
                    raise ValueError('No compatible normalization for this opaque container')
                encode_source = bytearray(raw[:metadata['parsedByteLength']])
                struct.pack_into('<I',encode_source,8,65536)
                encode_source = bytes(encode_source)
                normalization = {'type':'declared one-frame image in supported version65536',
                    'sourceVersion':65537,'targetVersion':65536,
                    'removedOpaqueTailBytes':metadata['trailingByteLength'],
                    'sourceOpaqueTailSha256':metadata['trailingBytesSha256'],
                    'logicalCanvasAndFrameGeometryPreserved':True}
            frame = metadata['frames'][0]
            with Image.open(candidate_path) as picture:
                if picture.mode != 'RGBA' or picture.size != (item['width'],item['height']):
                    raise ValueError(f'Own inventory canvas differs: {item_id}')
                replacement,operation = candidate_fit(picture,(frame['width'],frame['height']))
            output,_,decoded = codec.replace_frames(encode_source,{0:replacement})
            if decoded[0][1].getchannel('A').getextrema()[1] < 8:
                raise ValueError(f'Native icon lost all visible pixels: {item_id}')
            native_file = HERE/'patch'/native_path
            save_bytes(native_file,output,check)
            preview_file = HERE/'decoded'/f'{item_id}.png'
            save_image(preview_file,decoded[0][1],check)
            original_record = {'nativePath':native_path,'itemId':item_id,'resourceId':source['resource_id'],
                               'sourceArchiveMember':member,'sourceSha256':sha(raw),'metadata':metadata}
            sources.append(original_record)
            resources.append({**ref(native_file),'nativePath':native_path,'itemId':item_id,'category':source['category'],
                              'resourceId':source['resource_id'],'projectDisplayName':item.get('projectDisplayName') or item.get('sourceName') or source['name'],
                              'sourceSha256':sha(raw),'sourceLoose':True,'sourcePacked':False,
                              'derivedFrom':ref(candidate_path),'operation':operation,
                              'containerNormalization':normalization,
                              'frames':[{**ref(preview_file),'index':0,'width':frame['width'],'height':frame['height'],
                                         'pixelMode':frame['pixelMode'],'frameOffset':frame['frameOffset']}],
                              'visualAccepted':False,'nativeRuntimeVerified':False})
    contract_path = HERE/'source-contract.json'
    save_json(contract_path,{'schemaVersion':1,'sourceArchiveSha256':ARCHIVE_SHA,'catalog':ref(CATALOG),'items':sources},check)
    save_json(HERE/'manifest.json',{'schemaVersion':1,'scope':'native inventory icons from existing own painted candidates',
              'sourceContract':ref(contract_path),'inputManifests':inputs,'items':resources,'pendingItems':pending,
              'candidateItemCount':len(candidates),'convertedItemCount':len(resources),
              'converterSources':[ref(Path(__file__).resolve()),ref(ROOT/'scripts/native-ui-format.py')],
              'newModelGeneration':False,'visualAccepted':False,'nativeRuntimeVerified':False},check)
    print(json.dumps({'ownCandidateIds':len(candidates),'convertedNativeIcons':len(resources),'pendingItems':len(pending),'pixelReplay':check}))


if __name__ == '__main__':
    main()
