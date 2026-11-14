"""Synthetic own-file transaction fixtures; no original client runs or writes.

The prepare API is mocked only for transaction mechanics. The separate public
plan proves the exact source trees; an optional exact-source test repeats that
proof against the ignored pinned archive without touching an installed client.
"""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('brand_transaction', ROOT / 'scripts/native-ui-brand-data.py')
brand = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand)


class OwnFixtureTransactions(unittest.TestCase):
    def setUp(self):
        parent = ROOT / '.artifacts/native-ui-brand-data-tests'
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.folder = Path(self.temporary.name).resolve()
        self.assertTrue(self.folder.is_relative_to((ROOT / '.artifacts').resolve()))
        self.client = self.folder / 'client'
        self.client.mkdir()
        (self.client / 'Client.exe').write_bytes(b'Own inert fixture marker. Never executed.')
        self.manifest = copy.deepcopy(json.loads(brand.MANIFEST.read_bytes()))
        self.pairs = {}
        self.native = {}
        for item in self.manifest['items']:
            name = item['module']
            before = ('OWN fixture ' + name + ' existing color retained / before').encode()
            after = ('OWN fixture ' + name + ' existing color retained / after display text').encode()
            proof = copy.deepcopy(item['proof'])
            proof.update(beforeSha256=brand.digest(before), afterSha256=brand.digest(after),
                         beforeByteLength=len(before), afterByteLength=len(after))
            self.pairs[name] = (before, after, proof)
            item.update(beforeSha256=brand.digest(before), afterSha256=brand.digest(after), proof=proof)
            path = self.client / item['nativePath']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(before)
            self.native[name] = path
        manifest_path = self.folder / 'manifest.json'
        manifest_path.write_text(json.dumps(self.manifest), encoding='utf-8')

        def prepare(name, raw):
            before, after, proof = self.pairs[name]
            if raw not in (before, after):
                raise ValueError('Fixture unknown preimage')
            return before, after, copy.deepcopy(proof)

        self.patches = [patch.object(brand, 'MANIFEST', manifest_path),
                        patch.object(brand, 'BACKUP_ROOT', self.folder / 'backup'),
                        patch.object(brand.PLAN, 'prepare_module', side_effect=prepare),
                        patch.object(brand.io, 'check_stopped')]
        self.mocks = [p.start() for p in self.patches]
        self.stopped = self.mocks[-1]

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temporary.cleanup()

    def assert_all(self, state):
        for name, path in self.native.items():
            self.assertEqual(path.read_bytes(), self.pairs[name][0 if state == 'before' else 1])

    def private(self):
        return brand.BACKUP_ROOT / brand.client_alias(self.client.resolve())

    def test_default_verify_read_only_and_public_receipt_fields(self):
        result = brand.operate(self.client)
        self.assert_all('before')
        self.assertFalse(brand.BACKUP_ROOT.exists())
        self.stopped.assert_not_called()
        self.assertEqual(result['verifiedUnchangedCodeScopeCount'], 2257)
        self.assertEqual(result['verifiedFileCount'], 5)
        self.assertEqual(result['displayConstantCount'], 9)
        self.assertTrue(result['upstreamColorPatchPreserved'])
        self.assertNotIn(str(self.client), json.dumps(result))
        self.assertNotIn('clientRoot', result)

    def test_apply_repeat_restore_repeat_and_private_backups(self):
        for action, state, count in [('apply', 'after', 5), ('apply', 'after', 0),
                                     ('restore', 'before', 5), ('restore', 'before', 0)]:
            result = brand.operate(self.client, action)
            self.assert_all(state)
            self.assertEqual(result['changedFileCount'], count)
            self.assertTrue(result['backupVerified'])
        for name, path in self.native.items():
            relative = path.relative_to(self.client)
            self.assertEqual((self.private() / 'before' / relative).read_bytes(), self.pairs[name][0])
        self.assertEqual(json.loads((self.private() / 'receipt.json').read_bytes())['status'], 'restored')

    def test_full_five_file_preflight_rejects_unknown_last_file_before_backup(self):
        self.native['uiShop'].write_bytes(b'Unknown competing bytes')
        with self.assertRaisesRegex(ValueError, 'unknown preimage'):
            brand.operate(self.client, 'apply')
        self.assertFalse(brand.BACKUP_ROOT.exists())
        self.assertEqual(self.native['levelCFG'].read_bytes(), self.pairs['levelCFG'][0])

    def test_known_after_without_backup_is_not_claimed_backed_up(self):
        for name, path in self.native.items():
            path.write_bytes(self.pairs[name][1])
        result = brand.operate(self.client, 'apply')
        self.assertFalse(result['backupVerified'])
        self.assertFalse(result['changed'])
        with self.assertRaisesRegex(ValueError, 'verified private backup'):
            brand.operate(self.client, 'restore')
        self.assert_all('after')

    def test_mixed_unbacked_after_rejected_before_backup_or_target_writes(self):
        self.native['uiShop'].write_bytes(self.pairs['uiShop'][1])
        with self.assertRaisesRegex(ValueError, 'without backup'):
            brand.operate(self.client, 'apply')
        self.assertFalse((self.private() / 'before').exists())
        self.assertEqual(self.native['levelCFG'].read_bytes(), self.pairs['levelCFG'][0])

    def test_running_client_blocks_before_backup(self):
        self.stopped.side_effect = ValueError('Close Client.exe')
        with self.assertRaisesRegex(ValueError, 'Close Client.exe'):
            brand.operate(self.client, 'apply')
        self.assert_all('before')
        self.assertFalse(brand.BACKUP_ROOT.exists())

    def test_failure_after_second_replace_rolls_back_only_attempted_writes(self):
        real = brand.io.atomic_write
        count = 0
        def fail(path, data):
            nonlocal count
            real(path, data)
            if path in self.native.values() and data in [p[1] for p in self.pairs.values()]:
                count += 1
                if count == 2:
                    raise OSError('Injected failure after second replacement')
        with patch.object(brand.io, 'atomic_write', side_effect=fail):
            with self.assertRaises(OSError):
                brand.operate(self.client, 'apply')
        self.assert_all('before')
        self.assertEqual(brand.operate(self.client, 'apply')['state'], 'after')

    def test_restore_failure_rolls_back_to_transaction_after_preimages(self):
        brand.operate(self.client, 'apply')
        real = brand.io.atomic_write
        count = 0
        def fail(path, data):
            nonlocal count
            real(path, data)
            if path in self.native.values() and data in [p[0] for p in self.pairs.values()]:
                count += 1
                if count == 2:
                    raise OSError('Injected restore failure')
        with patch.object(brand.io, 'atomic_write', side_effect=fail):
            with self.assertRaises(OSError):
                brand.operate(self.client, 'restore')
        self.assert_all('after')
        self.assertEqual(brand.operate(self.client, 'restore')['state'], 'before')

    def test_competing_preimage_between_writes_is_preserved(self):
        real = brand.io.atomic_write
        external = b'OWN competing external edit'
        def compete(path, data):
            real(path, data)
            if path == self.native['levelCFG'] and data == self.pairs['levelCFG'][1]:
                self.native['uiMain'].write_bytes(external)
        with patch.object(brand.io, 'atomic_write', side_effect=compete):
            with self.assertRaisesRegex(ValueError, 'preimage changed'):
                brand.operate(self.client, 'apply')
        self.assertEqual(self.native['uiMain'].read_bytes(), external)
        self.assertEqual(self.native['levelCFG'].read_bytes(), self.pairs['levelCFG'][0])

    def test_rollback_does_not_overwrite_external_edit_to_attempted_file(self):
        real = brand.io.atomic_write
        external = b'OWN external edit after replacement'
        def compete(path, data):
            real(path, data)
            if path == self.native['levelCFG'] and data == self.pairs['levelCFG'][1]:
                path.write_bytes(external)
                raise OSError('Competing writer after replace')
        with patch.object(brand.io, 'atomic_write', side_effect=compete):
            with self.assertRaises(OSError):
                brand.operate(self.client, 'apply')
        self.assertEqual(self.native['levelCFG'].read_bytes(), external)
        self.assertEqual(self.native['uiMain'].read_bytes(), self.pairs['uiMain'][0])

    def test_final_receipt_failure_rolls_back_and_prepared_receipt_can_recover(self):
        real = brand.io.write_json
        def fail(path, data):
            if data.get('status') == 'applied':
                raise OSError('Final receipt failure')
            real(path, data)
        with patch.object(brand.io, 'write_json', side_effect=fail):
            with self.assertRaises(OSError):
                brand.operate(self.client, 'apply')
        self.assert_all('before')
        self.assertEqual(json.loads((self.private() / 'receipt.json').read_bytes())['status'], 'prepared')
        self.native['levelCFG'].write_bytes(self.pairs['levelCFG'][1])
        self.native['uiMain'].write_bytes(self.pairs['uiMain'][1])
        self.assertEqual(brand.operate(self.client, 'restore')['changedFileCount'], 2)
        self.assert_all('before')

    def test_tampered_backup_and_wrong_client_receipt_rejected(self):
        brand.operate(self.client, 'apply')
        backup = self.private() / 'before/res/uiRes/uiMain.pyc'
        backup.write_bytes(b'bad backup')
        with self.assertRaises(ValueError):
            brand.operate(self.client, 'restore')
        self.assert_all('after')
        backup.write_bytes(self.pairs['uiMain'][0])
        p = self.private() / 'receipt.json'
        value = json.loads(p.read_bytes());value['clientRoot'] = 'another client'
        p.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'another client/plan'):
            brand.operate(self.client, 'restore')
        self.assert_all('after')

    def test_os_lock_blocks_concurrent_operation(self):
        folder = brand.secure_folder(self.client.resolve())
        with brand.PLAN.COLOR.operation_lock(folder):
            with self.assertRaises(OSError):
                brand.operate(self.client, 'apply')
        self.assert_all('before')
        self.assertEqual(brand.operate(self.client, 'apply')['state'], 'after')

    def test_path_traversal_and_reparse_root_rejected(self):
        for relative in ('../outside', '/outside', 'C:/outside', 'res\\uiRes\\a', 'res//a', './a'):
            with self.assertRaises(ValueError):
                brand.child(self.client, relative)
        real_lstat = Path.lstat
        def reparse_fixture(path, *args, **kwargs):
            info = real_lstat(path, *args, **kwargs)
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400) if path == self.client else info
        with patch.object(Path, 'lstat', reparse_fixture):
            with self.assertRaisesRegex(ValueError, 'Reparse'):
                brand.operate(self.client)

    def test_actual_symlink_fixture_rejected_when_os_permits(self):
        link = self.folder / 'client-link'
        try:
            link.symlink_to(self.client, target_is_directory=True)
        except OSError:
            self.skipTest('OS does not grant symlink fixture permission')
        with self.assertRaisesRegex(ValueError, 'Reparse'):
            brand.operate(link)

    def test_public_contract_tamper_rejected_before_client_changes(self):
        manifest = json.loads(brand.MANIFEST.read_bytes())
        manifest['items'][-1]['proof']['scopeCount'] -= 1
        brand.MANIFEST.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'proof differs'):
            brand.operate(self.client, 'apply')
        self.assert_all('before')
        self.assertFalse(brand.BACKUP_ROOT.exists())


@unittest.skipUnless(brand.PLAN.ARCHIVE.is_file(), 'Exact source proof requires ignored pinned archive')
class ExactSourceContract(unittest.TestCase):
    def test_prepare_before_after_works_without_archive_or_source_pair_cache(self):
        pairs = {name: brand.PLAN.pinned_pair(name) for name in brand.PLAN.MODULES}
        brand.PLAN.pinned_pair.cache_clear()
        brand.PLAN.verify_archive.cache_clear()
        missing = ROOT / '.artifacts/native-ui-brand-data-tests/nonexistent-source.zip'
        with patch.object(brand.PLAN, 'ARCHIVE', missing), \
             patch.object(brand.PLAN, 'pinned_pair', side_effect=AssertionError('Runtime used source pair cache')), \
             patch.object(brand.PLAN, 'verify_archive', side_effect=AssertionError('Runtime used archive')):
            for name, (before, after, expected) in pairs.items():
                self.assertEqual(brand.PLAN.prepare_module(name, before), (before, after, expected))
                self.assertEqual(brand.PLAN.prepare_module(name, after), (before, after, expected))

    def test_five_before_after_pairs_and_uncolored_uimain_rejected(self):
        counts = edits = 0
        for name in brand.PLAN.MODULES:
            before, after, proof = brand.PLAN.pinned_pair(name)
            self.assertEqual(brand.PLAN.prepare_module(name, before), brand.PLAN.prepare_module(name, after))
            counts += proof['scopeCount'];edits += proof['changedDisplayConstants']
            self.assertTrue(proof['afterTreeWithOnlyAuthorizedTextRestoredEqualsBeforeTree'])
            self.assertTrue(proof['allUrlsUnchanged'])
        self.assertEqual((counts, edits), (2257, 9))
        import zipfile
        with zipfile.ZipFile(brand.PLAN.ARCHIVE) as z:
            raw = z.read(brand.PLAN.PREFIX + 'res/uiRes/uiMain.pyc')
        with self.assertRaisesRegex(ValueError, 'differs from both'):
            brand.PLAN.prepare_module('uiMain', raw)

    def test_real_inert_five_module_fixture_roundtrip_and_readonly_color_overlay(self):
        parent = ROOT / '.artifacts/native-ui-brand-real-fixtures'
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            folder = Path(temp).resolve()
            self.assertTrue(folder.is_relative_to((ROOT / '.artifacts').resolve()))
            client = folder / 'client'
            client.mkdir()
            (client / 'Client.exe').write_bytes(b'Own fixture marker; never executed')
            for name in brand.PLAN.MODULES:
                before, _, _ = brand.PLAN.pinned_pair(name)
                path = client / f'res/uiRes/{name}.pyc'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(before)
            color = brand.PLAN.COLOR
            with patch.object(brand, 'BACKUP_ROOT', folder / 'brand-backup'), \
                 patch.object(color, 'BACKUP_ROOT', folder / 'color-backup'), \
                 patch.object(brand.io, 'check_stopped'), \
                 patch('zipfile.ZipFile', side_effect=AssertionError('Runtime/restore must not open source archive')):
                self.assertEqual(brand.operate(client)['state'], 'before')
                applied = brand.operate(client, 'apply')
                self.assertEqual(applied['state'], 'after')
                self.assertEqual(applied['actualUiMainSha256'], color.BRAND_TEXT_SHA)
                self.assertEqual(brand.operate(client, 'apply')['changedFileCount'], 0)
                snapshot = {p: p.read_bytes() for p in (client / 'res/uiRes').glob('*.pyc')}
                readonly = color.operate(client)
                self.assertEqual(readonly['state'], 'patched-with-brand-text')
                self.assertEqual(readonly['actualUiMainSha256'], color.BRAND_TEXT_SHA)
                self.assertEqual(readonly['colorIntermediateBaselineSha256'], color.TARGET_SHA)
                self.assertTrue(readonly['upstreamBrandTextVerified'])
                self.assertTrue(readonly['upstreamBrandTextProof']['afterTreeWithOnlyAuthorizedTextRestoredEqualsBeforeTree'])
                self.assertFalse(color.BACKUP_ROOT.exists())
                for action in ('apply', 'restore'):
                    with self.assertRaisesRegex(ValueError, 'Restore brand text first'):
                        color.operate(client, action)
                for path, data in snapshot.items():
                    self.assertEqual(path.read_bytes(), data)
                restored = brand.operate(client, 'restore')
                self.assertEqual(restored['state'], 'before')
                self.assertEqual(restored['actualUiMainSha256'], color.TARGET_SHA)
                self.assertEqual(color.operate(client)['state'], 'patched')
                self.assertEqual(brand.operate(client, 'restore')['changedFileCount'], 0)


if __name__ == '__main__':
    unittest.main()
