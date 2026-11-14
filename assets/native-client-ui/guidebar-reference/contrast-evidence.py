"""Read menu text-color stores and simple class construction as inert bytecode."""
from pathlib import Path
import hashlib
import importlib.util
import json
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('guidebar_pyc', ROOT / 'scripts/read-legacy-ui-constants.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def literal(value):
    if value['type'] in ('tuple', 'list'):
        return [literal(item) for item in value['values']]
    return value.get('text', value.get('value'))


def find_code(node, target, parent=''):
    name = parser.text_value(node['name'])[0]
    scope = parent + '.' + name if parent else name
    if scope == target:
        return node
    for value in node['consts']:
        if isinstance(value, dict) and value.get('inertCodeNode'):
            found = find_code(value, target, scope)
            if found:
                return found
    return None


def instructions(code):
    rows, offset = [], 0
    while offset < len(code['bytecode']):
        start = offset
        opcode = code['bytecode'][offset]
        offset += 1
        argument = None
        if opcode >= 90:
            argument = int.from_bytes(code['bytecode'][offset:offset + 2], 'little')
            offset += 2
        row = {'offset': start, 'opcode': opcode, 'argument': argument}
        if opcode in (90, 101):
            row['name'] = parser.text_value(code['names'][argument])[0]
        rows.append(row)
    return rows


def main():
    with ZipFile(ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip') as archive:
        main_bytes = archive.read('QQTang-Local/runtime/client-patched/res/uiRes/uiMain.pyc')
        template_bytes = archive.read('QQTang-Local/runtime/client-patched/res/uiRes/uiTemplate.pyc')
    root, _ = parser.decode(main_bytes)
    template, _ = parser.decode(template_bytes)
    globals_ = {a['name']: literal(a['literalValue']) for a in parser.literal_assignments(root)}
    if globals_['lightColor'] != [255, 255, 255, 255]:
        raise ValueError('Expected native lightColor literal')
    scope = '?.UI.children.playerMenu.children'
    parent = find_code(root, scope)
    ops = instructions(parent)
    classes = []
    for index, op in enumerate(ops):
        if op['opcode'] != 90 or index == 0 or ops[index - 1]['opcode'] != 89:
            continue
        tuple_index = next(i for i in range(index - 2, -1, -1) if ops[i]['opcode'] == 102)
        base = ops[tuple_index - 1]
        if base['opcode'] != 101 or ops[tuple_index]['argument'] != 1:
            raise ValueError('Expected simple one-base native menu class')
        classes.append({'className': op['name'], 'baseName': base['name'],
                        'loadBaseOffset': base['offset'], 'buildClassOffset': ops[index - 1]['offset'],
                        'storeClassOffset': op['offset'],
                        'instructionWindowHex': parent['bytecode'][base['offset']:op['offset'] + 3].hex()})
    message = find_code(root, scope + '.messageBtn')
    msg_ops = instructions(message)
    store = next(i for i, op in enumerate(msg_ops) if op.get('name') == 'drawcolor' and op['opcode'] == 90)
    if msg_ops[store - 1].get('name') != 'lightColor' or msg_ops[store - 1]['opcode'] != 101:
        raise ValueError('Expected direct drawcolor=lightColor native menu store')
    stores = {a['name']: literal(a['literalValue']) for a in parser.literal_assignments(message)}
    if stores['textEdgeType'] != -1:
        raise ValueError('Expected no native menu text edge')
    if any(row['baseName'] not in ('TButton', 'messageBtn') for row in classes):
        raise ValueError('Unknown menu caption inheritance')
    defaults = []
    for node in parser.collect(template):
        if node['scope'] in ('?.TLabel', '?.TEdit', '?.TButton'):
            defaults.append({'scope': node['scope'], 'literalAssignments': {
                a['name']: literal(a['literalValue']) for a in node['literalAssignments']}})
    result = {'schemaVersion': 1, 'operation': 'Bounded inert code-tree and instruction reading only',
              'sourceModules': [{'module': 'uiMain', 'sha256': sha(main_bytes)},
                                {'module': 'uiTemplate', 'sha256': sha(template_bytes)}],
              'templateDefaults': defaults, 'menuParentScope': scope,
              'parentBytecodeSha256': sha(parent['bytecode']), 'classConstruction': classes,
              'messageBtnDrawcolor': {'globalName': 'lightColor', 'rgba': globals_['lightColor'],
                                     'loadOffset': msg_ops[store - 1]['offset'],
                                     'storeOffset': msg_ops[store]['offset'], 'textEdgeType': stores['textEdgeType'],
                                     'bytecodeSha256': sha(message['bytecode'])},
              'candidateBackgrounds': {'contextMenu': '#224a3b', 'contextHover': '#2b5743',
                                      'systemMenu': 'pale painted paper with baked control captions'},
              'bytecodeExecuted': False, 'runtimeVerified': False}
    path = HERE / 'contrast-evidence.json'
    path.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
    manifest_path = HERE / 'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    manifest['contrastEvidence'] = {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}
    manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'nativeMenuClasses': len(classes), 'drawcolor': globals_['lightColor'], 'textEdgeType': -1}))


if __name__ == '__main__':
    main()
