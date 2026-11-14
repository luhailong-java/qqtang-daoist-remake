"""Record direct color-name stores from inert native trade declarations."""
from pathlib import Path
import hashlib
import importlib.util
import json
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('deal_color_reader', ROOT/'scripts/read-legacy-ui-constants.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def lit(value):
    if value['type'] in ('tuple', 'list'):
        return [lit(v) for v in value['values']]
    return value.get('text', value.get('value'))


def scopes(node, parent=''):
    name = parser.text_value(node['name'])[0]
    scope = parent+'.'+name if parent else name
    yield scope, node
    for value in node['consts']:
        if isinstance(value, dict) and value.get('inertCodeNode'):
            yield from scopes(value, scope)


def direct_name_stores(node):
    raw, rows, offset, extended = node['bytecode'], [], 0, 0
    while offset < len(raw):
        start, opcode = offset, raw[offset]
        offset += 1
        argument = None
        if opcode >= 90:
            if offset+2 > len(raw):
                raise ValueError('Truncated inert instruction')
            argument = int.from_bytes(raw[offset:offset+2], 'little')+extended
            offset += 2
            extended = 0
        if opcode == 143:
            extended = argument << 16
        name = parser.text_value(node['names'][argument])[0] if opcode in (90, 101) else None
        rows.append({'offset': start, 'opcode': opcode, 'name': name})
    result = []
    for before, after in zip(rows, rows[1:]):
        if before['opcode'] == 101 and after['opcode'] == 90 and after['name'] in ('drawcolor','textEdgeColor'):
            result.append({'attribute': after['name'], 'globalName': before['name'],
                           'loadByteOffset': before['offset'], 'storeByteOffset': after['offset'],
                           'instructionHex': raw[before['offset']:after['offset']+3].hex()})
    return result


def main():
    source_path = HERE/'manifest.json'
    source = json.loads(source_path.read_bytes())
    modules, nodes = [], {}
    with ZipFile(ROOT/source['source']['archiveFile']) as archive:
        for name in ('uiMain','uiSelRoom'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            expected = next(row for row in source['source']['sourceModules'] if row['module'] == name)
            if sha(raw) != expected['sha256']:
                raise ValueError('Source color module differs')
            node, count = parser.decode(raw)
            modules.append({'module': name, 'sha256': sha(raw), 'parsedObjects': count, 'bytecodeExecuted': False})
            nodes[name] = node
    root_globals = {a['name']: lit(a['literalValue']) for a in parser.literal_assignments(nodes['uiMain'])}
    if root_globals['lightColor'] != [255,255,255,255] or root_globals['zoneChooseColor'] != [255,250,236,255]:
        raise ValueError('Expected native shared foreground literals')
    evidence = []
    for module, node in nodes.items():
        for scope, code in scopes(node):
            if not scope.startswith(('?.UI.children.C2CInvite','?.UI.children.C2CDealDlg',
                                     '?.UI_children_selRoom.children.pawnshop')):
                continue
            stores = direct_name_stores(code)
            if stores:
                for store in stores:
                    store['matchingUiMainGlobalLiteral'] = root_globals.get(store['globalName'])
                evidence.append({'module': module, 'scope': scope, 'bytecodeSha256': sha(code['bytecode']),
                                 'directNameStores': stores,
                                 'literalAssignments': {a['name']:lit(a['literalValue']) for a in parser.literal_assignments(code)}})
    bound = {r['nativePath'] for r in source['resources'] if r['sourceBindings']}
    result = {'schemaVersion':1, 'scope':'Direct LOAD_NAME / STORE_NAME foreground and edge declarations only',
              'sourceModules': modules, 'parser': record(ROOT/'scripts/read-legacy-ui-constants.py'),
              'sharedLiteralDefinitionModule': 'uiMain',
              'sharedColorLiterals': {k:root_globals[k] for k in ('lightColor','zoneChooseColor','maskColor')},
              'evidence':evidence,
              'sourcePathsWithBinding':len(bound),
              'sourcePathsWithoutBinding':[r['nativePath'] for r in source['resources'] if r['nativePath'] not in bound],
              'candidateLiveFieldBackground':'#254d42',
              'interpretation':'Direct symbol stores and uiMain color definitions are static evidence. Shared namespace loading, live runtime colors, and unbound cancel/confirm resources remain unverified.',
              'runtimeVerified':False, 'bytecodeExecuted':False}
    path = HERE/'contrast-evidence.json'
    path.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    source['contrastEvidence'] = record(path)
    source['contrastScript'] = record(Path(__file__))
    source_path.write_bytes((json.dumps(source,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'scopesWithDirectColors':len(evidence),'boundSourcePaths':len(bound),
                      'unboundSourcePaths':result['sourcePathsWithoutBinding']}))


if __name__ == '__main__':
    main()
