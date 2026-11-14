"""Verify, install, or restore a native art batch in a user-selected QQTang client directory."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import uuid
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native_ui_format', ROOT/'scripts/native-ui-format.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
BACKUP = ROOT/'.artifacts/native-client-ui-backup/review-v1'
MANIFEST_PATH = ROOT/'assets/native-client-bundle/review-v1/manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file': str(path), 'sha256': digest(path.read_bytes())}


def read(path):
    return json.loads(path.read_bytes())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def atomic_write(path, data):
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_bytes(data)
        if temporary.read_bytes() != data:
            raise ValueError('Staged write differs')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def check_stopped():
    if os.name != 'nt':
        return
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Client.exe', '/FO', 'CSV', '/NH'],
                            capture_output=True, check=True)
    if b'"client.exe"' in result.stdout.lower():
        raise ValueError('Close Client.exe before replacing its native image package')


def child(root, relative):
    if '\\' in relative or '..' in relative.split('/') or ':' in relative:
        raise ValueError('Invalid client-relative file path')
    path = root/relative
    if not path.resolve().is_relative_to(root):
        raise ValueError('Native file escapes client directory')
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink() or (parent.exists() and getattr(parent.stat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Reparse point in native client path')
    return path


def native_replacement(item, source):
    replacement = (ROOT/item['file']).read_bytes()
    if digest(replacement) != item['sha256']:
        raise ValueError('Native patch image differs')
    inspected, _ = codec.reader.inspect_dimg(replacement, metadata_only=True)
    original = source['metadata']
    normalization = item.get('containerNormalization')
    expected_length = original['byteLength']
    expected_version = original['version']
    if normalization:
        if (not item['nativePath'].startswith('res/uiRes/icon/') or original['frameCount'] != 1
                or original['version'] != 65537 or not original['trailingByteLength']
                or normalization.get('sourceVersion') != 65537 or normalization.get('targetVersion') != 65536
                or normalization.get('removedOpaqueTailBytes') != original['trailingByteLength']
                or normalization.get('sourceOpaqueTailSha256') != original['trailingBytesSha256']):
            raise ValueError('Unsupported native container normalization')
        expected_length = original['parsedByteLength']
        expected_version = 65536
    if len(replacement) != expected_length or inspected['version'] != expected_version:
        raise ValueError('Native image length changed')
    header_keys = ('frameInfoSize', 'directions', 'declaredCanvas', 'unknownHeaderWordsAt24And28')
    if any(inspected[key] != original[key] for key in header_keys) or len(inspected['frames']) != len(original['frames']):
        raise ValueError('Native header or frame count changed')
    frame_keys = ('frameOffset', 'width', 'height', 'pixelMode', 'empty', 'rawMarker', 'unknownImageHeaderWord')
    for old, new in zip(original['frames'], inspected['frames'], strict=True):
        if any(old.get(key) != new.get(key) for key in frame_keys):
            raise ValueError('Native source geometry changed')
    return replacement


def prepare_loose(client, manifest, contract):
    sources = {entry['nativePath']:entry for entry in contract['items']}
    files, destinations = {}, set()
    for item in manifest['items']:
        if item['sourcePacked'] or not item['sourceLoose']:
            raise ValueError('Loose-only batch has a packaged resource')
        native_path = item['nativePath']
        if native_path.lower() in destinations:
            raise ValueError('Duplicate native destination in loose batch')
        destinations.add(native_path.lower())
        original = child(client,native_path).read_bytes()
        if digest(original) != item['sourceSha256']:
            raise ValueError(f'Loose native source changed: {native_path}')
        files[native_path] = native_replacement(item,sources[native_path])
    summary = {'sourceManifestSha256':digest(MANIFEST_PATH.read_bytes()), 'clientRoot':str(client),
               'nativeResources':len(files), 'patchedPackedResources':0, 'patchedLooseResources':len(files),
               'nativeRuntimeVerified':False,
               'files':{name:{'beforeSha256':digest(child(client,name).read_bytes()),'afterSha256':digest(data)}
                        for name,data in files.items()}}
    return files,summary


def prepare(client):
    manifest = read(MANIFEST_PATH)
    contract_path = ROOT/manifest['sourceContract']['file']
    if digest(contract_path.read_bytes()) != manifest['sourceContract']['sha256']:
        raise ValueError('Native source contract differs')
    contract = read(contract_path)
    if not any(item['sourcePacked'] for item in manifest['items']):
        return prepare_loose(client,manifest,contract)
    package_path, index_path = child(client, 'data/object.pkg'), child(client, 'data/object.idx')
    package, index = package_path.read_bytes(), index_path.read_bytes()
    for value, expected in ((package, contract['sourcePackage']['sha256']), (index, contract['sourceIndex']['sha256'])):
        if digest(value) != expected:
            raise ValueError('Installed object package differs from the pinned unmodified base')
    entries = codec.reader.parse_index(index, len(package))['entries']
    by_path = {e['path'].replace('\\', '/').lower():e for e in entries}
    output_package, output_index = bytearray(package), bytearray(index)
    replacements, loose, destinations = {}, {}, set()
    for item in manifest['items']:
        if item['nativePath'].lower() in destinations:
            raise ValueError('Duplicate native destination in package batch')
        destinations.add(item['nativePath'].lower())
        source = next(r for r in contract['items'] if r['nativePath'] == item['nativePath'])
        replacement = native_replacement(item,source)
        if not item['sourceLoose'] and child(client, item['nativePath']).exists():
            raise ValueError('An extra loose UI file could shadow the selected package resource')
        if item['sourcePacked']:
            entry = by_path[item['nativePath'].lower()]
            original, _ = codec.reader.unpack_resource(package, entry)
            if digest(original) != item['sourceSha256']:
                raise ValueError('Packed native image differs from the source contract')
            compressed = zlib.compress(replacement, level=9)
            offset = len(output_package)
            output_package.extend(compressed)
            pointer = entry['indexOffset'] + 2 + len(entry['path'].encode('gb18030')) + 4
            struct.pack_into('<3I', output_index, pointer, offset, len(replacement), len(compressed))
            replacements[item['nativePath'].lower()] = replacement
        if item['sourceLoose']:
            target = child(client, item['nativePath'])
            if digest(target.read_bytes()) != item['sourceSha256']:
                raise ValueError('Loose native image differs from the source contract')
            loose[item['nativePath']] = replacement
    output_package, output_index = bytes(output_package), bytes(output_index)
    inspected_entries = codec.reader.parse_index(output_index, len(output_package))['entries']
    # Every old compressed stream stays untouched. Replaced streams must unpack to the own IMG.
    for before, after in zip(entries, inspected_entries, strict=True):
        key = before['path'].replace('\\', '/').lower()
        if key in replacements:
            if codec.reader.unpack_resource(output_package, after)[0] != replacements[key]:
                raise ValueError('Native package replacement does not unpack correctly')
        elif before != after:
            raise ValueError('An unrelated native package index entry changed')
    if not output_package.startswith(package):
        raise ValueError('Original package prefix changed')
    files = {'data/object.pkg': output_package, 'data/object.idx': output_index, **loose}
    summary = {'sourceManifestSha256': digest(MANIFEST_PATH.read_bytes()), 'clientRoot': str(client),
               'nativeResources': len(manifest['items']), 'patchedPackedResources': len(replacements),
               'patchedLooseResources': len(loose), 'unchangedPackedResources':len(entries)-len(replacements),
               'originalPackagePrefixPreserved': True, 'nativeRuntimeVerified':False,
               'files': {name: {'beforeSha256': digest(child(client,name).read_bytes()), 'afterSha256':digest(data)}
                         for name, data in files.items()}}
    return files, summary


def restore(client):
    receipt = read(BACKUP/'receipt.json')
    if receipt['clientRoot'] != str(client):
        raise ValueError('Backup belongs to another client directory')
    payload = {}
    for name, info in receipt['files'].items():
        path = child(client, name)
        content = child(BACKUP.resolve(), name).read_bytes()
        if digest(content) != info['beforeSha256'] or digest(path.read_bytes()) not in (info['beforeSha256'], info['afterSha256']):
            raise ValueError('Changed destination or backup prevents safe restore')
        payload[name] = content
    # Restore the original index first. Both package versions contain the complete original prefix.
    ordered = [name for name in ('data/object.idx','data/object.pkg') if name in payload]
    ordered.extend(name for name in payload if name not in ordered)
    for name in ordered:
        atomic_write(child(client,name), payload[name])
    receipt['restored'] = True
    write_json(BACKUP/'receipt.json', receipt)
    print(json.dumps({'restoredFiles':len(payload), 'clientRoot':str(client)}))


def main():
    global BACKUP, MANIFEST_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root', type=Path, required=True, help='The actual runtime/client-patched directory')
    parser.add_argument('--manifest', type=Path, default=MANIFEST_PATH, help='Prepared native art manifest')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--restore', action='store_true')
    options = parser.parse_args()
    MANIFEST_PATH = options.manifest.resolve(strict=True)
    client = options.client_root.resolve(strict=True)
    BACKUP = ROOT/'.artifacts/native-client-ui-backup'/MANIFEST_PATH.parent.name/digest(str(client).encode())[:16]
    if not child(client,'Client.exe').is_file():
        raise ValueError('This is not a native client root')
    check_stopped()
    if options.restore:
        restore(client)
        return
    if (BACKUP/'receipt.json').exists():
        previous = read(BACKUP/'receipt.json')
        if previous['clientRoot'] == str(client) and all(digest(child(client,n).read_bytes()) == r['afterSha256'] for n,r in previous['files'].items()):
            if previous['sourceManifestSha256'] == digest(MANIFEST_PATH.read_bytes()):
                print(json.dumps({'alreadyInstalled':True,'nativeResources':previous['nativeResources']}))
                return
            if not options.apply:
                raise ValueError('A newer batch is available. Use --apply to upgrade the installed native art')
            restore(client)
    files, summary = prepare(client)
    if options.apply:
        BACKUP.mkdir(parents=True,exist_ok=True)
        if (BACKUP/'receipt.json').exists() and not read(BACKUP/'receipt.json').get('restored'):
            raise ValueError('A previous interrupted install requires restore before retry')
        for name, data in files.items():
            target = child(BACKUP.resolve(),name)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(child(client,name),target)
            if digest(target.read_bytes()) != summary['files'][name]['beforeSha256']:
                raise ValueError('Original backup differs')
        write_json(BACKUP/'receipt.json',summary)
        try:
            # Package first keeps the original index usable at every boundary.
            for name, data in files.items():
                atomic_write(child(client,name),data)
        except BaseException:
            restore(client)
            raise
        if not all(digest(child(client,n).read_bytes())==v['afterSha256'] for n,v in summary['files'].items()):
            restore(client)
            raise ValueError('Installed art bytes differ')
    report = {**summary,'applied':options.apply,'verifiedFileCount':len(files)}
    report.pop('files')
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    main()
