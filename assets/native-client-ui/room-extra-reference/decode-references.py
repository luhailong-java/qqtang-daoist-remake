"""Decode source room-extra controls and their static source-module coordinates."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PATHS = [
    "object/ui/room/btn_check.img",
    "object/ui/room/btn_leftRole.img",
    "object/ui/room/btn_playerDown.img",
    "object/ui/room/btn_playerUp.img",
    "object/ui/room/btn_rightRole.img",
    "object/ui/room/char/bbl.img",
    "object/ui/room/char/boy.img",
    "object/ui/room/char/cl.img",
    "object/ui/room/char/dlg_roleAttr.img",
    "object/ui/room/char/ge.img",
    "object/ui/room/char/girl.img",
    "object/ui/room/char/hwz.img",
    "object/ui/room/char/hy.img",
    "object/ui/room/char/icon_117.img",
    "object/ui/room/char/icon_118.img",
    "object/ui/room/char/icon_119.img",
    "object/ui/room/char/icon_124.img",
    "object/ui/room/char/icon_125.img",
    "object/ui/room/char/icon_67.img",
    "object/ui/room/char/icon_69.img",
    "object/ui/room/char/icon_72.img",
    "object/ui/room/char/icon_73.img",
    "object/ui/room/char/icon_75.img",
    "object/ui/room/char/icon_77.img",
    "object/ui/room/char/icon_78.img",
    "object/ui/room/char/icon_79.img",
    "object/ui/room/char/icon_81.img",
    "object/ui/room/char/icon_85.img",
    "object/ui/room/char/icon_bbl.img",
    "object/ui/room/char/icon_boy.img",
    "object/ui/room/char/icon_cbz.img",
    "object/ui/room/char/icon_cl.img",
    "object/ui/room/char/icon_ge.img",
    "object/ui/room/char/icon_girl.img",
    "object/ui/room/char/icon_hwz.img",
    "object/ui/room/char/icon_hy.img",
    "object/ui/room/char/icon_kl.img",
    "object/ui/room/char/icon_ld.img",
    "object/ui/room/char/icon_mly.img",
    "object/ui/room/char/icon_nz.img",
    "object/ui/room/char/icon_random.img",
    "object/ui/room/char/icon_tb.img",
    "object/ui/room/char/icon_tt.img",
    "object/ui/room/char/icon_wll.img",
    "object/ui/room/char/icon_xq.img",
    "object/ui/room/char/icon_xwk.img",
    "object/ui/room/char/icon_xxm.img",
    "object/ui/room/char/icon_xz.img",
    "object/ui/room/char/icon_yd.img",
    "object/ui/room/char/icon_yy.img",
    "object/ui/room/char/icon_zjl.img",
    "object/ui/room/char/img_roleBomb.img",
    "object/ui/room/char/img_rolePower.img",
    "object/ui/room/char/img_roleSpeed.img",
    "object/ui/room/char/kl.img",
    "object/ui/room/char/ld.img",
    "object/ui/room/char/mly.img",
    "object/ui/room/char/name_bbl.img",
    "object/ui/room/char/name_boy.img",
    "object/ui/room/char/name_cl.img",
    "object/ui/room/char/name_ge.img",
    "object/ui/room/char/name_girl.img",
    "object/ui/room/char/name_hwz.img",
    "object/ui/room/char/name_hy.img",
    "object/ui/room/char/name_kl.img",
    "object/ui/room/char/name_ld.img",
    "object/ui/room/char/name_mly.img",
    "object/ui/room/char/name_nz.img",
    "object/ui/room/char/name_tb.img",
    "object/ui/room/char/name_tt.img",
    "object/ui/room/char/name_wll.img",
    "object/ui/room/char/name_xq.img",
    "object/ui/room/char/name_xwk.img",
    "object/ui/room/char/name_yd.img",
    "object/ui/room/char/name_yy.img",
    "object/ui/room/char/nz.img",
    "object/ui/room/char/tb.img",
    "object/ui/room/char/tt.img",
    "object/ui/room/char/wll.img",
    "object/ui/room/char/xq.img",
    "object/ui/room/char/xwk.img",
    "object/ui/room/char/yd.img",
    "object/ui/room/char/yy.img",
    "object/ui/room/dlg_helpKB.img",
    "object/ui/room/dlg_matchroom.img",
    "object/ui/room/dlg_roleProp.img",
    "object/ui/room/equipTip.img",
    "object/ui/room/img_master.img",
    "object/ui/room/img_popo.img",
    "object/ui/room/img_ready.img",
    "object/ui/room/img_roomStop.img",
    "object/ui/room/leftTip.img",
    "object/ui/room/map/btn_bomb.img",
    "object/ui/room/map/btn_box.img",
    "object/ui/room/map/btn_bun.img",
    "object/ui/room/map/btn_desert.img",
    "object/ui/room/map/btn_field.img",
    "object/ui/room/map/btn_machine.img",
    "object/ui/room/map/btn_match.img",
    "object/ui/room/map/btn_mine.img",
    "object/ui/room/map/btn_pig.img",
    "object/ui/room/map/btn_pve.img",
    "object/ui/room/map/btn_rand.img",
    "object/ui/room/map/btn_sculpture.img",
    "object/ui/room/map/btn_snow.img",
    "object/ui/room/map/btn_tank.img",
    "object/ui/room/map/btn_town.img",
    "object/ui/room/map/btn_treasure.img",
    "object/ui/room/map/btn_water.img",
    "object/ui/room/mask_equip.img",
    "object/ui/room/mask_speaker.img",
    "object/ui/room/rightTip.img",
    "object/ui/room/tab_normalChar.img",
    "object/ui/room/tab_vipChar.img",
    "object/ui/room/teamColorStrip.img"
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


def symbolic_assignments(node, parent=None):
    """Recognize adjacent LOAD_NAME/STORE_NAME only; never execute client bytes."""
    scope = (parent+'.' if parent else '')+parser.text_value(node['name'])[0]
    data, offset, previous = node['bytecode'], 0, None
    found = []
    while offset < len(data):
        start = offset
        opcode = data[offset]
        offset += 1
        argument = None
        if opcode >= 90:
            if offset+2 > len(data):
                raise ValueError('Truncated symbolic source instruction')
            argument = int.from_bytes(data[offset:offset+2], 'little')
            offset += 2
        if opcode == 90 and previous and previous[0] == 101:
            target = parser.text_value(node['names'][argument])[0]
            symbol = parser.text_value(node['names'][previous[1]])[0]
            if '.UI_children_room.' in scope and target in ('drawcolor', 'textEdgeColor'):
                found.append({'scope': scope, 'sourceFirstLine': node['firstLine'],
                              'bytecodeSha256': sha(data), 'loadByteOffset': previous[2],
                              'storeByteOffset': start, 'symbol': symbol, 'target': target,
                              'instructionsHex': data[previous[2]:offset].hex(),
                              'recognizer': 'Adjacent LOAD_NAME / STORE_NAME only', 'bytecodeExecuted': False})
        previous = (opcode, argument, start)
    for value in node['consts']:
        if isinstance(value, dict) and value.get('inertCodeNode'):
            found.extend(symbolic_assignments(value, scope))
    return found


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
    symbolic_colors = []
    dynamic_bindings = []
    with zipfile.ZipFile(archive_path) as archive:
        for name in ('uiMain', 'uiRoom', 'uiShop'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            node, count = parser.decode(raw)
            scopes = parser.collect(node)
            symbolic_colors.extend(symbolic_assignments(node))
            for scope in scopes:
                strings = [c.get('text') for c in scope['constants'] if c['type'] == 'bytes']
                references = [s for s in strings if s and s.startswith('object/ui/room/')]
                if references:
                    dynamic_bindings.append({'module': name, 'scope': scope['scope'],
                                             'sourceFirstLine': scope['firstLine'],
                                             'bytecodeSha256': scope['bytecodeSha256'],
                                             'directStringConstants': references, 'referencedNames': scope['names'],
                                             'bytecodeExecuted': False, 'activeControlFlowConfirmed': False})
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
                raise ValueError('Unexpected empty source control frame')
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
    row_heights = [320 if max(f['nativeSize'][1] for f in r['frames']) > 100 else 120 for r in resources]
    board = Image.new('RGB', (1200, sum(row_heights)), '#ddd8c9')
    draw = ImageDraw.Draw(board)
    y = 0
    for resource, height in zip(resources, row_heights, strict=True):
        draw.text((8, y+5), resource['nativePath'], fill='#254b3d')
        for frame in resource['frames']:
            image = Image.open(ROOT / frame['file']).convert('RGBA')
            ratio = min(2, 250/image.width, (height-45)/image.height)
            extent = (max(1, round(image.width*ratio)), max(1, round(image.height*ratio)))
            sample = image.resize(extent, Image.Resampling.NEAREST)
            x = 12+frame['sourceFrameIndex']*290
            board.paste(sample, (x, y+24), sample)
            draw.text((x, y+height-15), f"f{frame['sourceFrameIndex']} offset{frame['frameOffsetRaw']}", fill='#254b3d')
        y += height
    contact = HERE / 'source-contact.png'
    board.save(contact)
    result = {'schemaVersion': 1, 'scope': 'Room-extra control native source rasters and literal placement evidence',
              'inventory': record(inventory_path), 'sourceArchiveSha256': inventory['sourceArchive']['sha256'],
              'package': record(package_path), 'index': record(index_path), 'decoder': record(Path(__file__).resolve()),
              'sourceModules': module_records, 'sourceScopes': source_scopes, 'resources': resources,
              'symbolicColorAssignments': symbolic_colors, 'dynamicResourceReferences': dynamic_bindings,
              'sourceContact': record(contact), 'sourcePixelsOnly': True,
              'sourceClientMutated': False, 'nativeRuntimeVerified': False}
    HERE.mkdir(exist_ok=True)
    (HERE / 'manifest.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'resources': len(resources), 'sourceScopes': len(source_scopes), 'manifest': record(HERE / 'manifest.json')}))


if __name__ == '__main__':
    main()
