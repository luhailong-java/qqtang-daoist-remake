"""Verify/apply/restore one strict five-file inert native UI text-data plan.

Default verify never writes. No original program or bytecode is executed.
"""
import argparse
from importlib import util
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'assets/native-client-ui/brand-text-v1/manifest.json'
BACKUP_ROOT = ROOT / '.artifacts/native-client-ui-backup/brand-text-v1'


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


PLAN = module('brand_install_plan', 'assets/native-client-ui/brand-text-v1/build-plan.py')
io = PLAN.COLOR.io
digest, require = PLAN.digest, PLAN.require


def reject_reparse(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
            f'Reparse path is unsupported: {path.name}')


def checked_absolute(path):
    requested = Path(path).expanduser().absolute()
    for part in (requested, *requested.parents):
        reject_reparse(part)
    return requested


def child(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative and ':' not in relative
            and not any(part in ('', '.', '..') for part in relative.split('/')) and not relative.startswith('/'),
            'Invalid client-relative path')
    root = checked_absolute(root)
    result = root / relative
    current = result
    while current != root:
        reject_reparse(current)
        current = current.parent
    require(result.resolve().is_relative_to(root.resolve()), 'Native path escapes selected root')
    return result


def resolve_client(value):
    requested = checked_absolute(value)
    client = requested.resolve(strict=True)
    require(client.is_dir() and child(client, 'Client.exe').is_file(), 'Selected root lacks Client.exe')
    return client


def client_alias(client):
    return 'selected-client-' + digest(os.path.normcase(str(client)).encode())[:16]


def manifest_data():
    value = json.loads(MANIFEST.read_bytes())
    expected_inputs = {
        'builder': 'assets/native-client-ui/brand-text-v1/build-plan.py',
        'inertParser': 'scripts/read-legacy-ui-constants.py',
        'existingColorPatchScript': 'scripts/native-ui-color-data.py',
        'existingColorPatchManifest': 'assets/native-client-ui/text-color-v1/manifest.json',
        'sourceAudit': 'docs/native-ui-brand-text-20261114.json',
    }
    for key, relative in expected_inputs.items():
        require(value[key] == PLAN.record(ROOT / relative), f'Public brand dependency contract differs: {key}')
    require(value['id'] == 'native-ui-brand-text-v1' and value['moduleCount'] == 5 and
            value['displayConstantCount'] == 9 and value['verifiedUnchangedCodeScopeCount'] == 2257,
            'Public brand plan scope differs')
    require([item['module'] for item in value['items']] == list(PLAN.MODULES), 'Public brand module list differs')
    return value


def preflight(client, manifest):
    result = []
    for item in manifest['items']:
        name = item['module']
        relative = f'res/uiRes/{name}.pyc'
        require(item['nativePath'] == relative, 'Unexpected native module destination')
        raw = child(client, relative).read_bytes()
        before, after, proof = PLAN.prepare_module(name, raw)
        require(item['beforeSha256'] == digest(before) and item['afterSha256'] == digest(after)
                and item['proof'] == proof, 'Public brand module proof differs')
        result.append({'module': name, 'nativePath': relative, 'raw': raw, 'before': before, 'after': after,
                       'proof': proof, 'state': 'after' if raw == after else 'before'})
    return result


def public_report(client, manifest, rows, action, changed=0, backup_verified=False):
    states = {row['state'] for row in rows}
    files = [{'module': row['module'], 'nativePath': row['nativePath'],
              'actualSha256': digest(row['raw']), 'beforeSha256': digest(row['before']),
              'afterSha256': digest(row['after']), 'state': row['state'],
              'fullInertTreeProofVerified': True, 'allCoCodeAndUrlsUnchanged': True}
             for row in rows]
    return {'schemaVersion': 1, 'id': manifest['id'], 'clientRootAlias': client_alias(client),
            'action': action, 'state': next(iter(states)) if len(states) == 1 else 'mixed',
            'manifestSha256': digest(MANIFEST.read_bytes()), 'files': files,
            'verifiedFileCount': len(rows), 'verifiedUnchangedCodeScopeCount': sum(r['proof']['scopeCount'] for r in rows),
            'displayConstantCount': sum(r['proof']['changedDisplayConstants'] for r in rows),
            'verifiedUnchangedUrlConstantCount': sum(r['proof']['urlConstantCount'] for r in rows),
            'changedFileCount': changed, 'changed': changed != 0, 'backupVerified': backup_verified,
            'brandTextPresent': all(r['state'] == 'after' for r in rows),
            'actualUiMainSha256': next(digest(r['raw']) for r in rows if r['module'] == 'uiMain'),
            'uiMainColorIntermediateBaselineSha256': PLAN.MODULES['uiMain']['beforeSha256'],
            'upstreamColorPatchPreserved': True, 'nativeRuntimeVerified': False,
            'textWidthVerified': False, 'visualAccepted': False, 'clientCodeExecuted': False}


def secure_folder(client):
    base = checked_absolute(BACKUP_ROOT)
    base.mkdir(parents=True, exist_ok=True)
    folder = child(base, client_alias(client))
    folder.mkdir(exist_ok=True)
    child(folder, 'operation.lock')
    return folder.resolve(strict=True)


def verify_existing_backups(folder, rows):
    return all(child(folder, 'before/' + row['nativePath']).is_file() and
               child(folder, 'before/' + row['nativePath']).read_bytes() == row['before'] for row in rows)


def operate(client_root, action='verify'):
    require(action in ('verify', 'apply', 'restore'), 'Unknown brand data action')
    client = resolve_client(client_root)
    manifest = manifest_data()
    rows = preflight(client, manifest)
    if action == 'verify':
        return public_report(client, manifest, rows, action)
    io.check_stopped()
    folder = secure_folder(client)
    with PLAN.COLOR.operation_lock(folder):
        # Recheck all five files under the operation lock before backups or writes.
        rows = preflight(client, manifest)
        receipt_path = child(folder, 'receipt.json')
        if receipt_path.exists():
            previous = json.loads(receipt_path.read_bytes())
            require(previous['clientRoot'] == str(client) and previous['clientRootAlias'] == client_alias(client)
                    and previous['manifestSha256'] == digest(MANIFEST.read_bytes()), 'Private receipt belongs to another client/plan')
        backed_up = verify_existing_backups(folder, rows)
        for row in rows:
            existing = child(folder, 'before/' + row['nativePath'])
            if existing.exists():
                require(existing.read_bytes() == row['before'], 'Private original backup differs')
        if action == 'apply' and all(row['state'] == 'after' for row in rows) and not backed_up:
            # Recognize known bytes without claiming an actual backup exists.
            return public_report(client, manifest, rows, action, backup_verified=False)
        if action == 'restore':
            require(receipt_path.is_file() and backed_up, 'A verified private backup and receipt are required for restore')
        for row in rows:
            existing = child(folder, 'before/' + row['nativePath'])
            require(existing.exists() or action == 'apply' and row['raw'] == row['before'],
                    'Patched module without backup prevents transaction')
        for row in rows:
            backup = child(folder, 'before/' + row['nativePath'])
            if backup.exists():
                require(backup.read_bytes() == row['before'], 'Private original backup differs')
            else:
                require(action == 'apply' and row['raw'] == row['before'], 'Patched module without backup prevents transaction')
                require(child(client, row['nativePath']).read_bytes() == row['raw'], 'Client source changed before backup')
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup = child(folder, 'before/' + row['nativePath'])
                io.atomic_write(backup, row['raw'])
                require(backup.read_bytes() == row['before'], 'Private backup readback differs')
        require(verify_existing_backups(folder, rows), 'Private backups are incomplete')
        desired_key = 'after' if action == 'apply' else 'before'
        pending = [row for row in rows if row['raw'] != row[desired_key]]
        if not pending:
            return public_report(client, manifest, rows, action, backup_verified=True)
        executable_sha = digest(child(client, 'Client.exe').read_bytes())
        receipt = {'schemaVersion': 1, 'id': manifest['id'], 'clientRoot': str(client),
                   'clientRootAlias': client_alias(client), 'manifestSha256': digest(MANIFEST.read_bytes()),
                   'action': action, 'status': 'prepared',
                   'files': [{'module': r['module'], 'nativePath': r['nativePath'],
                              'beforeSha256': digest(r['before']), 'afterSha256': digest(r['after']),
                              'transactionPreimageSha256': digest(r['raw'])} for r in rows]}
        io.write_json(receipt_path, receipt)
        attempts = []
        try:
            for row in pending:
                io.check_stopped()
                target = child(client, row['nativePath'])
                require(target.read_bytes() == row['raw'], 'Client preimage changed before atomic replacement')
                # Record intent before writing: a helper may raise after replace.
                attempts.append(row)
                io.atomic_write(target, row[desired_key])
                require(child(client, row['nativePath']).read_bytes() == row[desired_key], 'Brand module write readback differs')
            final = preflight(client, manifest)
            require(all(r['raw'] == r[desired_key] for r in final), 'Brand transaction final readback differs')
            require(digest(child(client, 'Client.exe').read_bytes()) == executable_sha, 'Client executable changed during transaction')
            receipt['status'] = 'applied' if action == 'apply' else 'restored'
            io.write_json(child(folder, 'receipt.json'), receipt)
        except BaseException:
            # Only this transaction's attempted writes are eligible. Never
            # replace a competing writer's bytes or a file already rolled back.
            rollback_errors = []
            for row in reversed(attempts):
                try:
                    target = child(client, row['nativePath'])
                    if target.read_bytes() == row[desired_key]:
                        io.atomic_write(target, row['raw'])
                        require(child(client, row['nativePath']).read_bytes() == row['raw'], 'Brand rollback readback differs')
                except (OSError, ValueError) as error:
                    rollback_errors.append(str(error))
            if rollback_errors:
                raise RuntimeError('Brand transaction failed; rollback requires inspection: ' + ';'.join(rollback_errors))
            raise
        return public_report(client, manifest, final, action, len(pending), True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    action = 'apply' if args.apply else 'restore' if args.restore else 'verify'
    print(json.dumps(operate(args.client_root, action), ensure_ascii=False))


if __name__ == '__main__':
    main()
