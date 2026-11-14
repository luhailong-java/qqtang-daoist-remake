"""Read back installed native art batches without starting any client program."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT/'scripts/install-native-ui.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def verify(client, manifest_paths):
    package = installer.child(client,'data/object.pkg').read_bytes()
    index = installer.child(client,'data/object.idx').read_bytes()
    entries = installer.codec.reader.parse_index(index,len(package))['entries']
    by_path = {e['path'].replace('\\','/').lower():e for e in entries}
    seen, batches, resources, patched = set(), [], [], set()
    for path in manifest_paths:
        manifest = json.loads(path.read_bytes())
        contract_path = ROOT/manifest['sourceContract']['file']
        if record(contract_path) != manifest['sourceContract']:
            raise ValueError('Source contract differs')
        contract = json.loads(contract_path.read_bytes())
        sources = {e['nativePath']:e for e in contract['items']}
        count = 0
        for item in manifest['items']:
            key = item['nativePath'].lower()
            if key in seen:
                raise ValueError('Two active batches target the same native art')
            seen.add(key)
            expected = installer.native_replacement(item,sources[item['nativePath']])
            metadata,_ = installer.codec.reader.inspect_dimg(expected,metadata_only=True)
            previews = {e['index']:e for e in item['frames']}
            for frame in metadata['frames']:
                if frame['empty']:
                    continue
                start = frame['pixelDataOffset']
                pixels = installer.codec.reader.decode_frame_pixels(expected[start:start+frame['pixelByteLength']],
                                frame['pixelMode'],frame['width'],frame['height'])
                image = Image.frombytes('RGBA',(frame['width'],frame['height']),pixels)
                preview = previews[frame['index']]
                preview_path = ROOT/preview['file']
                if record(preview_path) != {'file':preview['file'],'sha256':preview['sha256']}:
                    raise ValueError('Native preview bytes differ')
                with Image.open(preview_path) as png:
                    if (png.mode,png.size,png.tobytes()) != (image.mode,image.size,image.tobytes()):
                        raise ValueError('Native preview differs from the installed encoded pixels')
            loose = installer.child(client,item['nativePath'])
            if item['sourceLoose']:
                if loose.read_bytes() != expected:
                    raise ValueError(f'Installed loose art differs: {item["nativePath"]}')
            elif loose.exists():
                raise ValueError('An unexpected loose file may shadow packed art')
            if item['sourcePacked']:
                actual,_ = installer.codec.reader.unpack_resource(package,by_path[key])
                if actual != expected:
                    raise ValueError(f'Installed packed art differs: {item["nativePath"]}')
                patched.add(key)
            count += len(item['frames'])
            resources.append({'nativePath':item['nativePath'],'sourceSha256':item['sourceSha256'],
                              'installedSha256':sha(expected),'sourcePacked':item['sourcePacked'],
                              'sourceLoose':item['sourceLoose'],'sourcePositions':len(item['frames']),
                              'containerNormalization':item.get('containerNormalization')})
        batches.append({'manifest':record(path),'nativeResources':len(manifest['items']),'sourcePositions':count})
    # The package baseline is inert source data; unchanged entries must remain exact.
    source_package = (ROOT/'.artifacts/reference-inputs/object.pkg').read_bytes()
    source_index = (ROOT/'.artifacts/reference-inputs/object.idx').read_bytes()
    old_entries = installer.codec.reader.parse_index(source_index,len(source_package))['entries']
    if len(old_entries) != len(entries) or not package.startswith(source_package):
        raise ValueError('Original package prefix or entry count changed')
    for before,after in zip(old_entries,entries,strict=True):
        if before['path'].replace('\\','/').lower() not in patched and before != after:
            raise ValueError('Unrelated package entry differs')
    with zipfile.ZipFile(ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as archive:
        original_exe = archive.read('QQTang-Local/runtime/client-patched/Client.exe')
    executable = installer.child(client,'Client.exe').read_bytes()
    if executable != original_exe:
        raise ValueError('Client.exe differs from the supplied baseline')
    return {'schemaVersion':1,'verifiedOn':'2026-11-14','clientRootAlias':'QQTang-Local/runtime/client-patched',
            'verification':'Static file readback, DIMG decode and source index comparison; no client executed',
            'batches':batches,'nativeResources':len(resources),
            'sourcePositions':sum(e['sourcePositions'] for e in resources),
            'packedResources':len(patched),'looseResources':sum(e['sourceLoose'] for e in resources),
            'unchangedPackedResources':len(entries)-len(patched),'originalPackagePrefixPreserved':True,
            'installedPackageSha256':sha(package),'installedIndexSha256':sha(index),
            'clientExeSha256':sha(executable),'clientExeUnchanged':True,
            'nativeRuntimeVerified':False,'userVisualAccepted':False,'resources':resources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,action='append',required=True)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = verify(args.client_root.resolve(strict=True),[p.resolve(strict=True) for p in args.manifest])
    if args.output:
        args.output.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k not in ('resources','batches')},ensure_ascii=False))


if __name__ == '__main__':
    main()
