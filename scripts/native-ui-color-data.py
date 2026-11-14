"""Patch one pinned UI color integer as inert data; never load client code.

The default operation only validates. Source/target hashes, full inert trees,
and all 830 co_code strings are checked before either mutation or restoration.
Local receipts/backups live exclusively in the ignored .artifacts directory.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def own_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parser = own_module('color_inert_parser', 'scripts/read-legacy-ui-constants.py')
io = own_module('color_native_io', 'scripts/install-native-ui.py')
MANIFEST = ROOT / 'assets/native-client-ui/text-color-v1/manifest.json'
BACKUP_ROOT = ROOT / '.artifacts/native-client-ui-backup/text-color-v1'
NATIVE_PATH = 'res/uiRes/uiMain.pyc'
SOURCE_SHA = '18074d6e8e0e6cd0fdcb0d70eba6e94d3b512359c191b8a37030e017b2839411'
TARGET_SHA = '54b1bc67712edcf6ee4649effa9adf1e1d7b66174bd9bb637cbf3f90b02b9bf6'
BRAND_TEXT_SHA = '132ffe6179118c04c74a78c128acad027853eb4c65704e8b3ce20b09faf66d38'
FILE_BYTES = 301556
HEADER = bytes.fromhex('3bf20d0a029f924d')
START, END = 63481, 63485
OLD, NEW = bytes.fromhex('00000000'), bytes.fromhex('c8000000')
SCOPE = '?.UI.children.SysMsgbox.children.hyPerLink1'
EXPECTED_COLORS = {'drawcolor': ([0, 0, 255, 255], [200, 200, 255, 255]),
                   'textEdgeColor': ([255, 0, 0, 0], [255, 200, 200, 200])}
EXPECTED_USES = [30, 33, 51, 54, 57]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def code_nodes(node, parent=None):
    name = parser.text_value(node['name'])[0]
    scope = (parent + '.' if parent else '') + name
    yield scope, node
    for value in node['consts']:
        if isinstance(value, dict) and value.get('inertCodeNode'):
            yield from code_nodes(value, scope)


def constant_loads(node, index):
    # Decode instruction boundaries only; no client instruction is executed.
    raw, offset, extended, matches = node['bytecode'], 0, 0, []
    while offset < len(raw):
        start, opcode = offset, raw[offset]
        offset += 1
        argument = None
        if opcode >= 90:
            require(offset + 2 <= len(raw), 'Truncated inert instruction')
            argument = int.from_bytes(raw[offset:offset+2], 'little') + extended
            offset += 2
            extended = 0
        if opcode == 143:
            extended = argument << 16
        elif opcode == 100 and argument == index:
            matches.append(start)
    require(not extended, 'Dangling inert extended argument')
    return matches


def rgba(value):
    require(value.get('type') == 'tuple', 'Expected literal color tuple')
    require(all(v.get('type') == 'int' for v in value['values']), 'Expected integer color components')
    return [v['value'] for v in value['values']]


def prove_pair(before, after):
    require(len(before) == len(after) == FILE_BYTES, 'Pinned PYC length differs')
    require(before[:8] == after[:8] == HEADER, 'Pinned PYC header differs')
    require(digest(before) == SOURCE_SHA, 'Pinned original SHA256 differs')
    require(digest(after) == TARGET_SHA, 'Pinned patched SHA256 differs')
    require(before[START:END] == OLD and after[START:END] == NEW, 'Pinned integer payload differs')
    require(before[START-1:START] == b'i', 'Pinned marshal integer tag differs')
    require(before[:START] == after[:START] and before[END:] == after[END:], 'Bytes outside color payload changed')
    left, left_count = parser.decode(before)
    right, right_count = parser.decode(after)
    old_nodes, new_nodes = list(code_nodes(left)), list(code_nodes(right))
    require(len(old_nodes) == len(new_nodes) == 830, 'Pinned code scope count differs')
    require(left_count == right_count == 20766, 'Pinned complete parse object count differs')
    hashes, changes, target = [], [], None
    for (scope, old), (new_scope, new) in zip(old_nodes, new_nodes, strict=True):
        require(scope == new_scope, 'Inert scope order differs')
        require(old['bytecode'] == new['bytecode'], 'Client co_code changed')
        hashes.append({'scope': scope, 'sha256': digest(old['bytecode'])})
        old_assignments, new_assignments = parser.literal_assignments(old), parser.literal_assignments(new)
        require(len(old_assignments) == len(new_assignments), 'Literal assignment count differs')
        for old_store, new_store in zip(old_assignments, new_assignments, strict=True):
            if old_store != new_store:
                require(scope == SCOPE and old_store['name'] == new_store['name'], 'Unexpected changed literal assignment')
                attribute = old_store['name']
                require(attribute in EXPECTED_COLORS, 'Non-color literal assignment changed')
                require({k: v for k, v in old_store.items() if k != 'literalValue'} ==
                        {k: v for k, v in new_store.items() if k != 'literalValue'}, 'Literal assignment metadata changed')
                values = (rgba(old_store['literalValue']), rgba(new_store['literalValue']))
                require(values == EXPECTED_COLORS[attribute], 'Color value differs from plan')
                changes.append({'scope': scope, 'attribute': attribute, 'before': values[0], 'after': values[1]})
        if scope == SCOPE:
            require(target is None, 'Ambiguous hyperlink scope')
            target = new
            require(old['consts'][6] == 0 and new['consts'][6] == 200, 'Wrong color constant')
            require(constant_loads(old, 6) == EXPECTED_USES, 'Shared constant usages changed')
    require(target is not None and len(changes) == 2, 'Expected exactly two color assignments')
    # A recursive equality check covers *all* inert fields, including symbol
    # stores, URL/caption bytes, names, callbacks, line tables and nested consts.
    target['consts'] = target['consts'][:6] + (0,) + target['consts'][7:]
    require(left == right, 'An additional inert code field or constant changed')
    return {'sourceSha256': SOURCE_SHA, 'targetSha256': TARGET_SHA, 'fileBytes': FILE_BYTES,
            'completeByteConsumption': True, 'parsedObjects': left_count, 'scopeCount': len(hashes),
            'allCoCodeUnchanged': True, 'allOtherCodeFieldsUnchanged': True,
            'URLCaptionCallbacksAndNonColorLiteralsUnchanged': True,
            'scopeBytecodeHashListSha256': digest(canonical(hashes)),
            'literalAssignmentChanges': changes, 'constant6LoadOffsets': EXPECTED_USES,
            'changedByteOffsets': [i for i, (a, b) in enumerate(zip(before, after, strict=True)) if a != b],
            'thirdPartyCodeExecuted': False}


def prepare(current):
    sha = digest(current)
    require(sha in (SOURCE_SHA, TARGET_SHA), 'Client UI source is neither the pinned original nor this exact color patch')
    if sha == SOURCE_SHA:
        before, after = current, current[:START] + NEW + current[END:]
    else:
        before, after = current[:START] + OLD + current[END:], current
    proof = prove_pair(before, after)
    manifest = json.loads(MANIFEST.read_bytes())
    require(manifest['nativePath'] == NATIVE_PATH and manifest['proof'] == proof, 'Public color-data contract differs')
    require(manifest['source']['sha256'] == SOURCE_SHA and manifest['source']['fileBytes'] == FILE_BYTES and
            manifest['source']['headerHex'] == HEADER.hex() and manifest['targetSha256'] == TARGET_SHA and
            manifest['scope'] == SCOPE and manifest['constantIndex'] == 6, 'Public pinned source metadata differs')
    require(manifest['payload'] == {'start': START, 'end': END, 'beforeHex': OLD.hex(), 'afterHex': NEW.hex(),
                                   'marshalTagOffset': START-1, 'marshalTagHex': '69'}, 'Public payload contract differs')
    return before, after, proof


def verify_brand_overlay(current):
    """Read-only recognition of the exact downstream text-data version."""
    require(digest(current) == BRAND_TEXT_SHA, 'Unknown brand text overlay')
    brand = own_module('color_readonly_brand_plan', 'assets/native-client-ui/brand-text-v1/build-plan.py')
    brand_manifest_path = ROOT / 'assets/native-client-ui/brand-text-v1/manifest.json'
    brand_manifest = json.loads(brand_manifest_path.read_bytes())
    for key, relative in (
            ('builder', 'assets/native-client-ui/brand-text-v1/build-plan.py'),
            ('inertParser', 'scripts/read-legacy-ui-constants.py'),
            ('existingColorPatchScript', 'scripts/native-ui-color-data.py'),
            ('existingColorPatchManifest', 'assets/native-client-ui/text-color-v1/manifest.json'),
            ('sourceAudit', 'docs/native-ui-brand-text-20261114.json')):
        require(brand_manifest[key] == brand.record(ROOT / relative), 'Public brand overlay dependency differs')
    baseline, after, upstream_proof = brand.prepare_module('uiMain', current)
    item = next(i for i in brand_manifest['items'] if i['module'] == 'uiMain')
    require(digest(baseline) == TARGET_SHA and after == current and item['proof'] == upstream_proof
            and item['beforeSha256'] == TARGET_SHA and item['afterSha256'] == BRAND_TEXT_SHA,
            'Exact upstream brand/color relationship differs')
    _, _, color_proof = prepare(baseline)
    return color_proof, upstream_proof, digest(brand_manifest_path.read_bytes())


def resolve_client(value):
    requested = Path(value).expanduser().absolute()
    require(not requested.is_symlink() and not (requested.exists() and
            getattr(requested.stat(), 'st_file_attributes', 0) & 0x400), 'Reparse client root is unsupported')
    client = requested.resolve(strict=True)
    require(client.is_dir(), 'Client root is not a directory')
    require(io.child(client, 'Client.exe').is_file(), 'Selected root lacks Client.exe')
    require(io.child(client, NATIVE_PATH).is_file(), 'Selected root lacks the loose UI source')
    return client


def client_alias(client):
    return 'selected-client-' + digest(os.path.normcase(str(client)).encode())[:16]


@contextmanager
def operation_lock(folder):
    folder.mkdir(parents=True, exist_ok=True)
    # OS locks are released on process exit, including abnormal termination.
    with (folder / 'operation.lock').open('a+b') as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def operate(client_root, action='verify'):
    require(action in ('verify', 'apply', 'restore'), 'Unknown operation')
    client = resolve_client(client_root)
    native = io.child(client, NATIVE_PATH)
    initial = native.read_bytes()
    if digest(initial) == BRAND_TEXT_SHA:
        require(action == 'verify', 'Restore brand text first with native-ui-brand-data.py --restore before color apply/restore')
        color_proof, brand_proof, brand_manifest_sha = verify_brand_overlay(initial)
        return {'clientRootAlias': client_alias(client), 'nativePath': NATIVE_PATH, 'action': action,
                'state': 'patched-with-brand-text', 'actualUiMainSha256': digest(initial),
                'colorIntermediateBaselineSha256': TARGET_SHA,
                'upstreamBrandTextVerified': True, 'brandManifestSha256': brand_manifest_sha,
                'proof': color_proof, 'upstreamBrandTextProof': brand_proof,
                'nativeRuntimeVerified': False, 'visualAccepted': False}
    before, after, proof = prepare(initial)
    alias = client_alias(client)
    summary = {'clientRootAlias': alias, 'nativePath': NATIVE_PATH, 'action': action,
               'state': 'original' if initial == before else 'patched',
               'actualUiMainSha256': digest(initial), 'upstreamBrandTextVerified': False,
               'proof': proof, 'nativeRuntimeVerified': False, 'visualAccepted': False}
    if action == 'verify':
        return summary
    io.check_stopped()
    folder = BACKUP_ROOT / alias
    with operation_lock(folder):
        native = io.child(client, NATIVE_PATH)
        current = native.read_bytes()
        before, after, proof = prepare(current)
        original_file, receipt_file = folder / 'uiMain.original.pyc', folder / 'receipt.json'
        if original_file.exists():
            require(original_file.read_bytes() == before, 'Private original backup differs')
        elif action == 'apply' and current == before:
            io.atomic_write(original_file, before)
            require(original_file.read_bytes() == before, 'Private original backup verification failed')
        elif action == 'restore' and current == after:
            raise ValueError('A verified original backup is required for restore')
        # An already-patched file without this tool's backup is recognized but
        # not claimed as a backed-up installation. Never invent a backup.
        if current == after and action == 'apply' and not original_file.exists():
            return {**summary, 'state': 'patched', 'changed': False, 'backupVerified': False}
        desired = after if action == 'apply' else before
        receipt = {'schemaVersion': 1, 'clientRoot': str(client), 'clientRootAlias': alias,
                   'nativePath': NATIVE_PATH, 'sourceSha256': SOURCE_SHA, 'targetSha256': TARGET_SHA,
                   'manifestSha256': digest(MANIFEST.read_bytes()), 'action': action,
                   'status': 'prepared', 'proof': proof}
        io.write_json(receipt_file, receipt)
        # Revalidate path and exact preimage immediately before atomic replace.
        require(io.child(client, NATIVE_PATH) == native and native.read_bytes() == current,
                'Client source changed during preparation')
        changed = current != desired
        try:
            if changed:
                io.check_stopped()
                require(io.child(client, NATIVE_PATH) == native and native.read_bytes() == current,
                        'Client source changed before atomic replacement')
                io.atomic_write(native, desired)
            actual = native.read_bytes()
            require(actual == desired, 'Installed color bytes differ')
            prepare(actual)
            receipt['status'] = 'applied' if action == 'apply' else 'restored'
            io.write_json(receipt_file, receipt)
        except Exception:
            # Never overwrite unrelated external bytes during error recovery.
            actual = native.read_bytes()
            if actual != current and actual == desired:
                io.atomic_write(io.child(client, NATIVE_PATH), current)
                require(native.read_bytes() == current, 'Color transaction rollback verification failed')
            raise
        return {**summary, 'state': 'patched' if action == 'apply' else 'original',
                'actualUiMainSha256': digest(actual),
                'changed': changed, 'backupVerified': original_file.exists()}


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--client-root', type=Path, required=True)
    modes = arguments.add_mutually_exclusive_group()
    modes.add_argument('--apply', action='store_true')
    modes.add_argument('--restore', action='store_true')
    args = arguments.parse_args()
    try:
        result = operate(args.client_root, 'apply' if args.apply else 'restore' if args.restore else 'verify')
    except Exception as error:
        # Do not publish a full local client path through OS-error tracebacks.
        message = str(error) if isinstance(error, ValueError) else 'Local file operation failed; client paths are private.'
        print(json.dumps({'error': type(error).__name__, 'message': message}, ensure_ascii=False))
        raise SystemExit(1) from None
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
