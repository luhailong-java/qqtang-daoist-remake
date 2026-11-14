"""Decode selected shop control rasters and static source-module coordinates."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PATHS = [
    "object/ui/shop/btn_buy.img",
    "object/ui/shop/btn_cancelEquip.img",
    "object/ui/shop/btn_collect.img",
    "object/ui/shop/btn_donate.img",
    "object/ui/shop/btn_forge.img",
    "object/ui/shop/btn_recycler.img",
    "object/ui/shop/btn_repair.img",
    "object/ui/shop/btn_require.img",
    "object/ui/shop/btn_resume.img",
    "object/ui/shop/btn_saveEquip.img",
    "object/ui/shop/btn_storage.img",
    "object/ui/shop/tab_advice.img",
    "object/ui/shop/tab_func.img",
    "object/ui/shop/tab_adorn.img",
    "object/ui/shop/tab_equip.img",
    "object/ui/shop/tab_pet.img",
    "object/ui/shop/tab_zizuan.img",
    "object/ui/shop/tab_itemFunc.img",
    "object/ui/shop/tab_itemAdorn.img",
    "object/ui/shop/tab_itemEquip.img"
]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


reader = load('core_dimg_reader', 'scripts/inspect-reference-dimg.py')
parser = load('core_pyc_reader', 'scripts/read-legacy-ui-constants.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def literal(value):
    if value['type'] in ('tuple', 'list'):
        return [literal(v) for v in value['values']]
    return value.get('text', value.get('value'))


def main():
    inventory_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    archive_path = ROOT / inventory['sourceArchive']['file']
    with archive_path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != inventory['sourceArchive']['sha256']:
            raise ValueError('Pinned source archive differs')
    package_path = ROOT / '.artifacts/reference-inputs/object.pkg'
    index_path = ROOT / '.artifacts/reference-inputs/object.idx'
    package, index = package_path.read_bytes(), index_path.read_bytes()
    if sha(package) != inventory['package']['sha256'] or sha(index) != inventory['index']['sha256']:
        raise ValueError('Pinned package differs')
    entries = reader.parse_index(index, len(package))['entries']
    by_path = {e['path'].replace('\\', '/').lower(): e for e in entries}
    module_records = []
    source_scopes = []
    with zipfile.ZipFile(archive_path) as archive:
        for name in ('uiShop',):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            node, count = parser.decode(raw)
            scopes = parser.collect(node)
            module_records.append({'module': name, 'archiveMember': member, 'sourceBytes': len(raw), 'sourceSha256': sha(raw),
                                   'parsedObjects': count, 'codeScopeCount': len(scopes), 'bytecodeExecuted': False})
            for scope in scopes:
                assignments = {a['name']: literal(a['literalValue']) for a in scope['literalAssignments']}
                if assignments:
                    source_scopes.append({'module': name, 'scope': scope['scope'], 'sourceFirstLine': scope['firstLine'],
                                          'bytecodeSha256': scope['bytecodeSha256'], 'literalAssignments': assignments,
                                          'activeControlFlowConfirmed': False})
    resources = []
    for path in PATHS:
        entry = by_path[path.lower()]
        raw, compressed_sha = reader.unpack_resource(package, entry)
        expected = next(r for r in inventory['resources'] if r['canonicalPath'] == path.lower() and r['storage'] == 'packed')
        if sha(raw) != expected['sourceSha256'] or compressed_sha != expected['compressedSha256']:
            raise ValueError('Source resource differs')
        metadata, _ = reader.inspect_dimg(raw, metadata_only=True, reference_only_version65537_suffix=True)
        images = []
        for frame in metadata['frames']:
            if frame['empty']:
                raise ValueError('Unexpected empty shop reference frame')
            offset = frame['pixelDataOffset']
            pixels = reader.decode_frame_pixels(raw[offset:offset + frame['pixelByteLength']], frame['pixelMode'], frame['width'], frame['height'])
            image = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
            destination = HERE / 'frames' / f'{Path(path).stem}-{frame["index"]:03}.png'
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(destination)
            if Image.open(destination).convert('RGBA').tobytes() != pixels:
                raise ValueError('Saved reference differs')
            images.append({**record(destination), 'sourceFrameIndex': frame['index'], 'nativeSize': list(image.size),
                           'frameOffsetRaw': frame['frameOffset'], 'decodedRgbaSha256': sha(pixels),
                           'alphaExtrema': list(image.getchannel('A').getextrema())})
        bindings = []
        for scope in source_scopes:
            if any(isinstance(v, str) and v.replace('\\', '/').lower() == path.lower() for v in scope['literalAssignments'].values()):
                bindings.append(scope)
        resources.append({'nativePath': path, 'sourceSha256': sha(raw), 'compressedSha256': compressed_sha,
                          'packageEntry': entry, 'metadata': metadata, 'frames': images, 'sourceBindings': bindings})
    contact = Image.new('RGB', (1200, len(resources)*100), '#d9d9d9')
    draw = ImageDraw.Draw(contact)
    for row, resource in enumerate(resources):
        draw.text((8, row*100+5), resource['nativePath'], fill='#152d29')
        for frame in resource['frames']:
            image = Image.open(ROOT / frame['file']).convert('RGBA')
            rendered = image.resize((image.width*2, image.height*2), Image.Resampling.NEAREST)
            contact.paste(rendered, (15+frame['sourceFrameIndex']*260, row*100+25), rendered)
            draw.text((15+frame['sourceFrameIndex']*260, row*100+84),
                      f"f{frame['sourceFrameIndex']} offset {frame['frameOffsetRaw']}", fill='#152d29')
    contact_path = HERE / 'source-contact.png'
    contact.save(contact_path)
    result = {'schemaVersion': 1, 'scope': 'Shop control source rasters and static literal placement evidence',
              'inventory': record(inventory_path), 'sourceArchiveSha256': inventory['sourceArchive']['sha256'],
              'package': record(package_path), 'index': record(index_path), 'decoder': record(Path(__file__).resolve()),
              'sourceModules': module_records, 'sourceScopes': source_scopes, 'resources': resources,
              'sourceContact': record(contact_path),
              'sourcePixelsOnly': True, 'sourceClientMutated': False, 'nativeRuntimeVerified': False}
    HERE.mkdir(exist_ok=True)
    (HERE / 'manifest.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'resources': len(resources), 'sourceScopes': len(source_scopes), 'manifest': record(HERE / 'manifest.json')}))


if __name__ == '__main__':
    main()
