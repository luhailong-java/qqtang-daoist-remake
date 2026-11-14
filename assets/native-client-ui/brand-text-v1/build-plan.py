"""Build/prove nine GBK display-constant edits as inert serialized data only.

This file never executes/imports client code, constructs CodeType objects,
installs candidates or touches the user-provided client directory.
"""
import argparse
from collections import Counter
import copy
from functools import lru_cache
import hashlib
from importlib import util
import json
from pathlib import Path
import struct
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
PRIVATE = ROOT / '.artifacts/native-client-brand-text-v1'
AUDIT = ROOT / 'docs/native-ui-brand-text-20261114.json'
PREFIX = 'QQTang-Local/runtime/client-patched/'
MODULES = {
    'levelCFG': {'archiveSha256': '9170cd4c0e9b686c14e131290be67a2a906974d6828ef69ef669252016022656', 'scopeCount': 11},
    'uiMain': {'archiveSha256': '18074d6e8e0e6cd0fdcb0d70eba6e94d3b512359c191b8a37030e017b2839411', 'scopeCount': 830,
               'beforeSha256': '54b1bc67712edcf6ee4649effa9adf1e1d7b66174bd9bb637cbf3f90b02b9bf6'},
    'uiRoom': {'archiveSha256': 'ce34a19a8924595fb3659ef3938216ad1fc8a21f4d8dee5c52ce5234d3239064', 'scopeCount': 506},
    'uiSelSect': {'archiveSha256': 'f2d66e23622f9adabc33ecde4dd7a5c9c1170c96fa02273ddc6517fb8f968118', 'scopeCount': 112},
    'uiShop': {'archiveSha256': 'a81d44cbaf696ee8ed4e51a0e97d45678dafea74d4be9282abcc96d8ec4bb406', 'scopeCount': 798},
}
EDITS = (
    ('levelCFG', '?.LevelCfg', 182, 'QQ堂平民', '灵葫道友'),
    ('levelCFG', '?.LevelCfg', 201, 'QQ堂英雄', '灵葫真人'),
    ('levelCFG', '?.LevelCfg', 209, '酷比大天使', '灵葫大天师'),
    ('uiMain', '?.PlayerWord', 12, '恭喜你们已经成为QQ堂合法夫妻!', '恭喜你们已在灵葫仙境结为道侣!'),
    ('uiMain', '?.UI.children.C2CDealDlg.children.NegotiateBtn.OnClick', 5,
     '您的酷比宝石不足,本次出价没有成功', '您的灵玉不足，本次出价未成功。'),
    ('uiRoom', '?.UI_children_room.children.selMapDlg.children.sel.OnClick', 6,
     'QQTang 温馨提示', '灵葫温馨提示'),
    ('uiSelSect', '?.UI_children_selSect.children.billboard', 13,
     '    QQ堂， 即将推出!', '    灵葫大作战，欢迎道友！'),
    ('uiShop', '?.UI_children_shop.children.functionTab.OnClick', 8, '酷比宝石', '灵玉'),
    ('uiShop', '?.UI_children_shop.children.ware1.children.buyA.OnClick', 23, '酷比宝石', '灵玉'),
)


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


PARSER = module('brand_inert_reader', 'scripts/read-legacy-ui-constants.py')
COLOR = module('brand_existing_color_contract', 'scripts/native-ui-color-data.py')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}


class SpanReader(PARSER.Reader):
    """The existing bounded inert grammar plus exact byte-string field spans."""
    def __init__(self, data):
        super().__init__(data)
        self.byte_strings = {}

    def object(self, depth=0):
        start = self.offset
        tag = self.data[start:start + 1]
        value = super().object(depth)
        if tag == b's':
            require(isinstance(value, bytes), 'Expected an inert byte-string value')
            self.byte_strings[id(value)] = {'start': start + 8, 'end': self.offset + 8,
                                            'value': value, 'tag': tag}
        return value


def parse(raw):
    require(isinstance(raw, bytes) and len(raw) <= 1024 * 1024, 'Expected bounded serialized PYC bytes')
    require(raw[:4] == bytes.fromhex('3bf20d0a'), 'Expected pinned legacy PYC magic')
    reader = SpanReader(raw[8:])
    tree = reader.object()
    require(reader.offset == len(reader.data) and isinstance(tree, dict) and tree.get('inertCodeNode'),
            'Complete inert tree parse failed')
    return tree, reader


def nodes(tree, parent=None):
    name = PARSER.text_value(tree['name'])[0]
    scope = (parent + '.' if parent else '') + name
    yield scope, tree
    for value in tree['consts']:
        if isinstance(value, dict) and value.get('inertCodeNode'):
            yield from nodes(value, scope)


def node_map(tree):
    rows = list(nodes(tree))
    counts, seen, result = Counter(scope for scope, _ in rows), Counter(), {}
    for scope, node in rows:
        # uiRoom has eight sibling filterMap lambdas with the same printable
        # scope. Keep every code object in source order, never collapse them.
        seen[scope] += 1
        key = scope if counts[scope] == 1 else scope + '#occurrence=' + str(seen[scope])
        result[key] = node
    require(len(rows) == len(result), 'Ambiguous inert scope occurrence keys')
    return result


def url_literals(tree):
    result = []

    def visit(value, scope, path):
        if isinstance(value, bytes):
            lowered = value.lower()
            if any(token in lowered for token in (b'http://', b'https://', b'http%3a', b'https%3a', b'www.')):
                result.append({'scope': scope, 'constantIndexPath': path,
                               'sha256': digest(value), 'byteLength': len(value)})
        elif isinstance(value, (tuple, list)):
            for index, child in enumerate(value):
                visit(child, scope, path + [index])
        elif isinstance(value, dict) and not value.get('inertCodeNode'):
            for key in sorted(value):
                visit(value[key], scope, path + [key])

    for scope, node in nodes(tree):
        for index, value in enumerate(node['consts']):
            visit(value, scope, [index])
    return result


def selected_edits(module_name):
    require(module_name in MODULES, 'Module is outside the five-module display-only plan')
    return [row for row in EDITS if row[0] == module_name]


def encode_field(value):
    return b's' + struct.pack('<i', len(value)) + value


def field_for(raw, reader, value):
    field = reader.byte_strings.get(id(value))
    require(field is not None and field['value'] is value and field['tag'] == b's', 'No exact target constant byte-string span')
    require(raw[field['start']:field['end']] == encode_field(value), 'Serialized target field does not match the inert constant')
    return field


def replace_fields(raw, changes):
    changes.sort()
    require(all(a[1] <= b[0] for a, b in zip(changes, changes[1:])), 'Overlapping serialized display fields')
    output, cursor = bytearray(), 0
    for start, end, encoded in changes:
        output.extend(raw[cursor:start])
        output.extend(encoded)
        cursor = end
    output.extend(raw[cursor:])
    return bytes(output)


def make_after(module_name, before):
    tree, reader = parse(before)
    scopes = node_map(tree)
    changes = []
    audit = json.loads(AUDIT.read_bytes())
    audit_rows = {(r['module'], r['scope'], r['location']): r for r in audit['literalOccurrences']}
    for _, scope, index, old_text, new_text in selected_edits(module_name):
        require(scope in scopes, 'Pinned display scope missing')
        node = scopes[scope]
        old, new = old_text.encode('gbk'), new_text.encode('gbk')
        require(node['consts'][index] == old and type(node['consts'][index]) is bytes, 'Pinned display constant differs')
        require(not any(token in old.lower() for token in (b'http', b'www.')), 'A URL cannot be a display edit target')
        source = audit_rows[(module_name, scope, f'constant[{index}]')]
        require(source['literal']['sha256'] == digest(old) and source['sourceBytecodeSha256'] == digest(node['bytecode']),
                'Display audit evidence differs')
        span = field_for(before, reader, node['consts'][index])
        changes.append((span['start'], span['end'], encode_field(new)))
    return replace_fields(before, changes)


def restore_display_fields(module_name, candidate):
    tree, reader = parse(candidate)
    scopes = node_map(tree)
    changes = []
    for _, scope, index, old_text, new_text in selected_edits(module_name):
        require(scope in scopes, 'Exact display scope missing from after input')
        value = scopes[scope]['consts'][index]
        require(type(value) is bytes and value == new_text.encode('gbk'), 'Exact after display constant differs')
        span = field_for(candidate, reader, value)
        changes.append((span['start'], span['end'], encode_field(old_text.encode('gbk'))))
    return replace_fields(candidate, changes)


def without_fields(raw, ranges, prefix):
    result, cursor = bytearray(), 0
    for change in sorted(ranges, key=lambda r: r[prefix + 'Start']):
        start, end = change[prefix + 'Start'], change[prefix + 'End']
        require(cursor <= start <= end <= len(raw), 'Invalid reversible serialized span')
        result.extend(raw[cursor:start])
        cursor = end
    result.extend(raw[cursor:])
    return bytes(result)


def prove_pair(module_name, before, after):
    left, left_reader = parse(before)
    right, right_reader = parse(after)
    old_nodes, new_nodes = node_map(left), node_map(right)
    expected = MODULES[module_name]
    require(digest(before) == expected.get('beforeSha256', expected['archiveSha256']), 'Before input is not the pinned compatible version')
    require(list(old_nodes) == list(new_nodes) and len(old_nodes) == expected['scopeCount'], 'Inert scope sequence/count changed')
    require(left_reader.objects == right_reader.objects, 'Inert object count changed')
    require(before[:8] == after[:8], 'PYC header or timestamp changed')
    normalized = copy.deepcopy(right)
    restored_nodes = node_map(normalized)
    ranges = []
    for _, scope, index, old_text, new_text in selected_edits(module_name):
        old, new = old_text.encode('gbk'), new_text.encode('gbk')
        require(old_nodes[scope]['consts'][index] == old and new_nodes[scope]['consts'][index] == new,
                'A target display value is not exact')
        a = field_for(before, left_reader, old_nodes[scope]['consts'][index])
        b = field_for(after, right_reader, new_nodes[scope]['consts'][index])
        values = restored_nodes[scope]['consts']
        restored_nodes[scope]['consts'] = values[:index] + (old,) + values[index + 1:]
        ranges.append({'scope': scope, 'constantIndex': index, 'encoding': 'GBK',
                       'beforeText': old_text, 'afterText': new_text,
                       'beforeStart': a['start'], 'beforeEnd': a['end'],
                       'afterStart': b['start'], 'afterEnd': b['end'],
                       'beforePayloadByteLength': len(old), 'afterPayloadByteLength': len(new),
                       'beforeSerializedFieldHex': encode_field(old).hex(), 'afterSerializedFieldHex': encode_field(new).hex(),
                       'sourceBytecodeSha256': digest(old_nodes[scope]['bytecode'])})
    require(normalized == left, 'Inert tree differs beyond the authorized display constants')
    code_hashes = []
    for scope, old_node in old_nodes.items():
        require(old_node['bytecode'] == new_nodes[scope]['bytecode'], 'An original co_code byte changed')
        code_hashes.append({'scope': scope, 'sha256': digest(old_node['bytecode'])})
    old_outside, new_outside = without_fields(before, ranges, 'before'), without_fields(after, ranges, 'after')
    require(old_outside == new_outside, 'Serialized bytes outside display-string fields changed')
    urls_before, urls_after = url_literals(left), url_literals(right)
    require(urls_before == urls_after, 'URL constant data changed')
    # Direct local range reversal proves reversibility of variable-length edits.
    reverse, cursor = bytearray(), 0
    for change in sorted(ranges, key=lambda r: r['afterStart']):
        reverse.extend(after[cursor:change['afterStart']])
        reverse.extend(bytes.fromhex(change['beforeSerializedFieldHex']))
        cursor = change['afterEnd']
    reverse.extend(after[cursor:])
    require(bytes(reverse) == before, 'Local serialized text reversal did not restore exact before bytes')
    return {'beforeSha256': digest(before), 'afterSha256': digest(after),
            'beforeByteLength': len(before), 'afterByteLength': len(after),
            'headerHex': before[:8].hex(), 'completeByteConsumption': True,
            'parsedObjects': left_reader.objects, 'scopeCount': len(old_nodes),
            'changedDisplayConstants': len(ranges), 'reversibleStringFields': sorted(ranges, key=lambda r: r['beforeStart']),
            'allCoCodeUnchanged': True, 'allOtherInertFieldsUnchanged': True,
            'afterTreeWithOnlyAuthorizedTextRestoredEqualsBeforeTree': True,
            'serializedBytesOutsideTargetFieldsIdentical': True,
            'serializedOutsideFieldsSha256': digest(old_outside),
            'scopeBytecodeHashListSha256': digest(json.dumps(code_hashes, sort_keys=True, separators=(',', ':')).encode()),
            'urlConstantCount': len(urls_before), 'urlConstants': urls_before, 'allUrlsUnchanged': True,
            'reverseRangesRestoreExactBeforeBytes': True,
            'uiMainColorVersionPreserved': module_name == 'uiMain',
            'thirdPartyCodeExecuted': False, 'nativeRuntimeVerified': False, 'textWidthVerified': False}


@lru_cache(maxsize=1)
def verify_archive():
    with ARCHIVE.open('rb') as stream:
        require(hashlib.file_digest(stream, 'sha256').hexdigest() == ARCHIVE_SHA, 'Pinned archive changed')
    return True


@lru_cache(maxsize=5)
def pinned_pair(module_name):
    selected_edits(module_name)
    verify_archive()
    with zipfile.ZipFile(ARCHIVE) as archive:
        raw = archive.read(PREFIX + f'res/uiRes/{module_name}.pyc')
    require(digest(raw) == MODULES[module_name]['archiveSha256'], 'Pinned module archive source changed')
    if module_name == 'uiMain':
        _, before, color_proof = COLOR.prepare(raw)
        require(digest(before) == MODULES[module_name]['beforeSha256'] and color_proof['allCoCodeUnchanged'],
                'Compatible existing uiMain color patch was not preserved')
    else:
        before = raw
    after = make_after(module_name, before)
    proof = prove_pair(module_name, before, after)
    return before, after, proof


def prepare_module(module_name, raw_bytes):
    """Return canonical(before,after,proof) for an exact pinned before OR after.

    uiMain accepts only the already-color-patched before54b1bc... or this plan's
    after. The original uncolored ZIP uiMain is deliberately rejected here.
    No client path, executable loading or mutation is part of this API.
    """
    selected_edits(module_name)
    require(isinstance(raw_bytes, bytes), 'Expected existing module bytes')
    expected = MODULES[module_name]
    before_sha = expected.get('beforeSha256', expected['archiveSha256'])
    if digest(raw_bytes) == before_sha:
        before = raw_bytes
        after = make_after(module_name, before)
    else:
        try:
            before = restore_display_fields(module_name, raw_bytes)
            require(digest(before) == before_sha, 'Restored before SHA differs')
            after = make_after(module_name, before)
            require(raw_bytes == after, 'After differs from canonical exact serialized text edits')
        except (ValueError, IndexError, KeyError):
            raise ValueError('Input differs from both pinned before and planned after') from None
    proof = prove_pair(module_name, before, after)
    return before, after, proof


def save_bytes(path, value, check):
    if check:
        require(path.read_bytes() == value, f'Candidate replay differs: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only complete proof/candidate/manifest replay')
    check = parser.parse_args().check
    items = []
    for module_name in MODULES:
        before, after, proof = pinned_pair(module_name)
        require(prepare_module(module_name, before) == prepare_module(module_name, after), 'Idempotent prepare API differs by input state')
        for rejected in (before + b'\0', after[:-1] + bytes((after[-1] ^ 1,))):
            try:
                prepare_module(module_name, rejected)
            except ValueError:
                pass
            else:
                raise ValueError('Unknown external bytes were accepted')
        native_path = f'res/uiRes/{module_name}.pyc'
        private_file = PRIVATE / 'after' / native_path
        save_bytes(private_file, after, check)
        items.append({'module': module_name, 'nativePath': native_path,
                      'sourceArchiveMember': PREFIX + native_path,
                      'sourceArchiveOriginalSha256': MODULES[module_name]['archiveSha256'],
                      'beforeSha256': digest(before), 'afterSha256': digest(after),
                      'privateCandidate': record(private_file), 'proof': proof,
                      'installedToClient': False, 'textWidthVerified': False, 'nativeRuntimeVerified': False})
    # Prevent accidentally accepting ZIP uiMain and overwriting its installed color patch.
    with zipfile.ZipFile(ARCHIVE) as archive:
        uncolored = archive.read(PREFIX + 'res/uiRes/uiMain.pyc')
    try:
        prepare_module('uiMain', uncolored)
    except ValueError:
        pass
    else:
        raise ValueError('Uncolored uiMain input was accepted')
    require(sum(i['proof']['scopeCount'] for i in items) == 2257 and sum(i['proof']['changedDisplayConstants'] for i in items) == 9,
            'Authorized nine-display/five-module/2257-scope plan changed')
    manifest = {'schemaVersion': 1, 'id': 'native-ui-brand-text-v1',
                'scope': 'Nine non-URL display-byte-string edits across five native UI modules; candidate plan only',
                'sourceArchiveSha256': ARCHIVE_SHA, 'sourceAudit': record(AUDIT), 'items': items,
                'moduleCount': 5, 'displayConstantCount': 9, 'verifiedUnchangedCodeScopeCount': 2257,
                'builder': record(Path(__file__).resolve()), 'inertParser': record(ROOT / 'scripts/read-legacy-ui-constants.py'),
                'existingColorPatchScript': record(ROOT / 'scripts/native-ui-color-data.py'),
                'existingColorPatchManifest': record(ROOT / 'assets/native-client-ui/text-color-v1/manifest.json'),
                'api': 'prepare_module(module_name,raw_bytes) -> (before_bytes,after_bytes,proof); exact pinned before or pinned after only',
                'offsetConvention': 'Absolute serialized PYC byte offsets, half-open; each range includes tag s, signed little-endian length, GBK payload',
                'bytecodeModified': False, 'allOtherInertFieldsUnchanged': True, 'allUrlsUnchanged': True,
                'uiMainBeforeMustBeExistingColorVersion': MODULES['uiMain']['beforeSha256'],
                'uncoloredUiMainInputRejected': True, 'unknownOrTamperedInputRejected': True,
                'prepareApplyRestoreRequireSourceArchive': False,
                'sourceArchiveRequiredOnlyForBuildingOriginalSourcePlan': True,
                'privatePycCandidatesOnly': True, 'thirdPartyPycIncludedInPublicAssets': False,
                'providedDirectoryReadOrMutated': False, 'installedToClient': False,
                'nativeRuntimeVerified': False, 'textWidthVerified': False, 'visualAccepted': False,
                'remainingScope': 'URLs, window/launcher branding, executable strings, other PYC data and GBK12 glyph coverage are outside this plan'}
    save_bytes(HERE / 'manifest.json', (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'), check)
    print(json.dumps({'modules': 5, 'displayEdits': 9, 'unchangedCodeScopes': 2257,
                      'fullTreeProof': True, 'urlsUnchanged': True, 'existingColorVersionPreserved': True,
                      'readOnlyReplay': check, 'installed': False}))


if __name__ == '__main__':
    main()
