"""Decode selected remaining native lobby controls and their literal UI source scopes."""
from pathlib import Path
import importlib.util
import json
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('lobby_native_reader', ROOT / 'assets/native-client-ui/core-reference/decode-references.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
reader.HERE = HERE
reader.PATHS = tuple('object/ui/selsect/' + name + '.img' for name in (
    'btn_practice', 'btn_syssetup', 'tab_practice', 'tab_greenhand', 'tab_match', 'tab_party', 'btn_choose',
)) + tuple('object/ui/selroom/' + name + '.img' for name in (
    'tab_chat', 'tab_explore', 'tab_honor', 'tab_item', 'tab_noitem', 'tab_player', 'tab_friend', 'tab_allkinmember',
    'btn_shop', 'btn_match', 'dlg_pwroom', 'map/dlg_mapfilter', 'btn_mapfilter',
))


def scopes_from_modules():
    modules, scopes = [], []
    archive_path = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
    with zipfile.ZipFile(archive_path) as archive:
        for name in ('uiSelSect', 'uiSelRoom'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            node, count = reader.parser.decode(raw)
            module_scopes = reader.parser.collect(node)
            modules.append({'module': name, 'archiveMember': member, 'sourceBytes': len(raw), 'sourceSha256': reader.sha(raw),
                            'parsedObjects': count, 'codeScopeCount': len(module_scopes), 'bytecodeExecuted': False})
            for scope in module_scopes:
                assignments = {a['name']: reader.literal(a['literalValue']) for a in scope['literalAssignments']}
                if assignments:
                    scopes.append({'module': name, 'scope': scope['scope'], 'sourceFirstLine': scope['firstLine'],
                                   'bytecodeSha256': scope['bytecodeSha256'], 'literalAssignments': assignments,
                                   'activeControlFlowConfirmed': False})
    return modules, scopes


def contrast_evidence(scopes):
    with zipfile.ZipFile(ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as archive:
        member = 'QQTang-Local/runtime/client-patched/res/uiRes/uiTemplate.pyc'
        raw = archive.read(member)
        node, _ = reader.parser.decode(raw)
        defaults = []
        for scope in reader.parser.collect(node):
            if scope['scope'] in ('?.TEdit', '?.TEditPassword', '?.TLabel'):
                defaults.append({'scope': scope['scope'], 'literalAssignments': {
                    a['name']: reader.literal(a['literalValue']) for a in scope['literalAssignments']}})
        template_source = {'archiveMember': member, 'sha256': reader.sha(raw), 'classes': defaults}
        raw = archive.read('QQTang-Local/runtime/client-patched/res/uiRes/uiSelRoom.pyc')
        root, _ = reader.parser.decode(raw)

    def find_code(code, parent=''):
        name = reader.parser.text_value(code['name'])[0]
        scope = parent + '.' + name if parent else name
        if scope == '?.UI_children_selRoom.children.pwRoom.children':
            return code
        for value in code['consts']:
            if isinstance(value, dict) and value.get('inertCodeNode'):
                found = find_code(value, scope)
                if found:
                    return found
        return None

    parent = find_code(root)
    bytecode = parent['bytecode']
    names = [reader.parser.text_value(value)[0] for value in parent['names']]
    if not (bytecode[9] == 101 and names[int.from_bytes(bytecode[10:12], 'little')] == 'TEditPassword' and
            bytecode[24] == 89 and bytecode[25] == 90 and names[int.from_bytes(bytecode[26:28], 'little')] == 'pw'):
        raise ValueError('Password class construction differs')
    white = [scope for scope in scopes if scope['scope'].endswith(('mapMode0.children.name', 'mapFilterBtn.children.text'))]
    if not all(scope['literalAssignments']['drawcolor'] == [255, 255, 255, 255] for scope in white) or len(white) != 2:
        raise ValueError('Map filter explicit text color differs')
    return {'templateDefaults': template_source, 'passwordClassConstruction': {
        'parentScope': '?.UI_children_selRoom.children.pwRoom.children', 'parentBytecodeSha256': reader.sha(bytecode),
        'className': 'pw', 'baseName': 'TEditPassword', 'loadBaseOffset': 9, 'buildClassOffset': 24, 'storeNameOffset': 25,
        'instructionBytes6To28Hex': bytecode[6:28].hex(), 'bytecodeExecuted': False}, 'mapFilterWhiteTextBindings': white}


def contacts(manifest):
    chosen = [r for r in manifest['resources'] if not Path(r['nativePath']).stem.startswith('dlg_')]
    board = Image.new('RGB', (1050, len(chosen) * 150 + 12), '#d6d4cb')
    draw = ImageDraw.Draw(board)
    inputs = []
    for row, resource in enumerate(chosen):
        y = 8 + row * 150
        draw.text((10, y), resource['nativePath'], fill='#172a24')
        for i, frame in enumerate(resource['frames']):
            image = Image.open(ROOT / frame['file']).convert('RGBA')
            image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)
            x = 10 + i * 250
            draw.text((x, y + 18), str(i), fill='#172a24')
            board.paste(image, (x, y + 33), image)
            inputs.append({'file': frame['file'], 'sha256': frame['sha256'], 'nearestScale': 2})
    path = HERE / 'source-controls.png'
    board.save(path)
    return [{**reader.record(path), 'inputs': inputs}]


if __name__ == '__main__':
    reader.main()
    path = HERE / 'manifest.json'
    manifest = json.loads(path.read_bytes())
    modules, scopes = scopes_from_modules()
    manifest['sourceModules'] = modules
    manifest['sourceScopes'] = scopes
    manifest['contrastEvidence'] = contrast_evidence(scopes)
    inventory = json.loads((ROOT / 'references/qqtang-ui-data/native-ui-inventory.json').read_bytes())
    for resource in manifest['resources']:
        native_path = resource['nativePath']
        resource['sourceBindings'] = [s for s in scopes if any(isinstance(v, str) and v.replace('\\', '/').lower() == native_path
                                                              for v in s['literalAssignments'].values())]
        resource['pathLiteralOccurrences'] = [b for b in inventory['bindings'] if b['canonicalPath'] == native_path]
    manifest['selectionScript'] = reader.record(Path(__file__).resolve())
    manifest['previews'] = contacts(manifest)
    path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'resources': len(manifest['resources']), 'frames': sum(len(r['frames']) for r in manifest['resources']),
                      'manifest': reader.record(path)}))
