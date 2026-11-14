"""Read native role-name/ID list literals, join existing project identity allocation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARSER = load('room_roster_inert', 'scripts/read-legacy-ui-constants.py')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def adjacent_literal_stores(node):
    """Recognize literals plus list/tuple constructors and STORE_NAME/GLOBAL."""
    data, offset, stack, stores = node['bytecode'], 0, [], {}
    while offset < len(data):
        at, opcode = offset, data[offset]
        offset += 1
        argument = None
        if opcode >= 90:
            argument = int.from_bytes(data[offset:offset+2], 'little')
            offset += 2
        if opcode == 100:
            stack.append((node['consts'][argument], at))
        elif opcode in (102, 103):
            if argument > len(stack):
                stack = []
                continue
            part = stack[-argument:] if argument else []
            if argument:
                del stack[-argument:]
            values = [v for v, _ in part]
            stack.append((tuple(values) if opcode == 102 else values, part[0][1] if part else at))
        elif opcode in (90, 97):
            if len(stack) == 1:
                value, start = stack[0]
                name = PARSER.text_value(node['names'][argument])[0]
                stores[name] = {'value': value, 'byteStart': start, 'byteEnd': offset,
                                'byteSha256': sha(data[start:offset]), 'storeOpcode': opcode}
            stack = []
        else:
            stack = []
    return stores


def json_value(value):
    if isinstance(value, bytes):
        return value.decode('ascii')
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return value


def main():
    portrait_path = ROOT / 'assets/characters/portraits-candidates/manifest.json'
    allocation_path = ROOT / 'assets/characters/motion-generated/roster-skin-mapping-20261028.json'
    portraits = json.loads(portrait_path.read_bytes())
    allocation = json.loads(allocation_path.read_bytes())
    with ARCHIVE.open('rb') as stream:
        archive_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    if archive_sha != 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7':
        raise ValueError('Pinned source archive changed')
    modules = {}
    with zipfile.ZipFile(ARCHIVE) as archive:
        for name in ('uiRoom', 'uiShop', 'uiGame'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            tree, count = PARSER.decode(raw)
            modules[name] = {'raw': raw, 'tree': tree, 'scopes': PARSER.collect(tree),
                             'record': {'module': name, 'archiveMember': member, 'sourceSha256': sha(raw),
                                        'parsedObjects': count, 'bytecodeExecuted': False}}
    room = adjacent_literal_stores(modules['uiRoom']['tree'])
    names = json_value(room['RoleNameList']['value'])
    ids = json_value(room['RoleIDList']['value'])
    if names != [['random','boy','girl','xwk','tt','xq','cl','bbl','hy','mly','hwz','yd','ld','ge','tb'], ['kl','nz','wll','yy']]:
        raise ValueError('Native role alias list changed')
    if ids != [[23,9,22,1,2,3,4,5,6,7,8,18,19,20,21],[13,14,15,16]]:
        raise ValueError('Native source role ID list changed')
    shop = adjacent_literal_stores(modules['uiShop']['tree'])['charIconList']
    shop_aliases = json_value(shop['value'])
    pve = adjacent_literal_stores(modules['uiGame']['tree'])['g_RoleNameList']
    pve_aliases = json_value(pve['value'])
    if pve_aliases != ['', 'xwk','tt','xq','cl','bbl','hy','mly','hwz','boy','cbz','xz','ls','kl','nz','wll','yy','','yd','ld','ge','tb','girl']:
        raise ValueError('Native PVE role ID alias tuple changed')
    expected_shop = ['xwk','tt','xq','cl','bbl','hy','mly','hwz','boy','','','','kl','nz','wll','yy','','yd','ld','ge','tb','girl']
    if shop_aliases != expected_shop:
        raise ValueError('Native shop character alias index changed')
    own_by_id = {p['sourceRoleId']: p for p in portraits['entries']}
    allocations = {p['sourceRoleId']: p for p in allocation['slots']}
    joined = []
    for group, (group_names, group_ids) in enumerate(zip(names, ids, strict=True)):
        for position, (alias, role_id) in enumerate(zip(group_names, group_ids, strict=True)):
            if role_id == 23:
                continue
            own = own_by_id[role_id]
            allocated = allocations[role_id]['appearance']
            if own['identityId'] != allocated['identityId'] or own['sourceMaster'] != allocated['master']:
                raise ValueError('Existing project sourceRoleId identity allocation changed')
            if record(ROOT / own['file'])['sha256'] != own['sha256'] or record(ROOT / own['sourceMaster'])['sha256'] != own['sourceMasterSha256']:
                raise ValueError('Own portrait or full master differs')
            shop_indices = [i+1 for i, name in enumerate(shop_aliases) if name == alias]
            if shop_indices != [role_id]:
                raise ValueError('Shop alias index does not match the independently paired native role ID')
            joined.append({'sourceRoleId': role_id, 'nativeAlias': alias, 'nativeRoomGroupIndex': group,
                           'nativeRoomPosition': position, 'nativeShopOneBasedRoleIndex': shop_indices[0],
                           'identityId': own['identityId'], 'projectName': own['name'], 'uiShortName': own['name'],
                           'portrait': record(ROOT / own['file']), 'portraitSourceRecord': record(ROOT / own['sourceRecord']),
                           'master': record(ROOT / own['sourceMaster']),
                           'masterSourceRecord': record(ROOT / own['sourceGenerationOrProvenanceRecord']),
                           'roomPaths': [f'object/ui/room/char/{alias}.img', f'object/ui/room/char/icon_{alias}.img', f'object/ui/room/char/name_{alias}.img'],
                           'shopPath': f'object/ui/shop/charIcon/{alias}.img',
                           'appearanceAllocation': 'Existing project-authored identity allocation, not Tencent identity/name recognition',
                           'visualAccepted': False, 'nativeRuntimeVerified': False})
    evidence = []
    for mod, target_scopes in {'uiRoom': ['?.ui_UpdateRole','?.UI_children_room.children.role1.OnMouseMoveIn'],
                               'uiShop': ['?.getCharIconName'],
                               'uiGame': ['?.ui_InitPVEPlayer', '?.ui_InitPVEBoss']}.items():
        for scope in target_scopes:
            found = next(s for s in modules[mod]['scopes'] if s['scope'] == scope)
            evidence.append({'module': mod, 'scope': scope, 'sourceFirstLine': found['firstLine'],
                             'bytecodeSha256': found['bytecodeSha256'], 'referencedNames': found['names'],
                             'directStringConstants': [c.get('text') for c in found['constants'] if c['type'] == 'bytes'],
                             'bytecodeExecuted': False})
    pve_extra = []
    for role_id in (10, 11):
        own = own_by_id[role_id]
        if own['identityId'] != allocations[role_id]['appearance']['identityId']:
            raise ValueError('PVE additional project identity allocation changed')
        if record(ROOT / own['file'])['sha256'] != own['sha256'] or record(ROOT / own['sourceMaster'])['sha256'] != own['sourceMasterSha256']:
            raise ValueError('Additional own portrait or master differs')
        alias = pve_aliases[role_id]
        pve_extra.append({'sourceRoleId': role_id, 'nativeAlias': alias, 'nativePveRoleIndex': role_id,
                          'identityId': own['identityId'], 'projectName': own['name'], 'uiShortName': own['name'],
                          'portrait': record(ROOT / own['file']), 'portraitSourceRecord': record(ROOT / own['sourceRecord']),
                          'master': record(ROOT / own['sourceMaster']),
                          'masterSourceRecord': record(ROOT / own['sourceGenerationOrProvenanceRecord']),
                          'roomPaths': [f'object/ui/room/char/icon_{alias}.img'], 'shopPath': None,
                          'appearanceAllocation': 'Existing project sourceRoleId appearance allocation; native PVE alias proven by exact tuple index',
                          'visualAccepted': False, 'nativeRuntimeVerified': False})
    result = {'schemaVersion': 1, 'scope': 'Exact native role alias-to-sourceRoleId positional proof plus existing project appearance allocation',
              'builder': record(Path(__file__).resolve()), 'sourceArchiveSha256': archive_sha,
              'sourceModules': [v['record'] for v in modules.values()],
              'sourceRoomLists': {key: {**{k:v for k,v in room[key].items() if k != 'value'},
                                       'value': json_value(room[key]['value'])} for key in ('RoleNameList','RoleIDList')},
              'sourceShopAliasList': {**{k:v for k,v in shop.items() if k != 'value'}, 'value': shop_aliases},
              'sourcePveAliasTuple': {**{k:v for k,v in pve.items() if k != 'value'}, 'value': pve_aliases},
              'dynamicUseEvidence': evidence, 'projectIdentityAllocation': record(allocation_path),
              'projectPortraitManifest': record(portrait_path), 'mappedConcreteRoleCount': len(joined)+len(pve_extra),
              'nativeRoomAndShopListRoleCount': len(joined), 'entries': joined, 'pveAdditionalEntries': pve_extra,
              'randomPlaceholder': {'sourceRoleId':23, 'nativeAlias':'random', 'independentCharacter':False},
              'ownExtraIdsOutsideTheseNativeRoomAndShopLists': sorted(set(own_by_id)-{p['sourceRoleId'] for p in joined}),
              'extraNativeIconNumericSuffixesNotMappedByTheseLists': [67,69,72,73,75,77,78,79,81,85,117,118,119,124,125],
              'unlistedAliasesRequireSeparateEvidence': ['xxm','zjl'],
              'sourceRoleTimingOrNativeRuntimeVerified': False, 'visualAccepted': False}
    HERE.mkdir(parents=True, exist_ok=True)
    target = HERE / 'roster-mapping-audit.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'mappedConcreteRoles':len(joined)+len(pve_extra), 'ownExtraIds':result['ownExtraIdsOutsideTheseNativeRoomAndShopLists'], 'file':record(target)}))


if __name__ == '__main__':
    main()
