"""Inert constant proof and isolated install/restore regression checks.

No original PYC is distributed with tests. Exact-source tests use the pinned
ignored local reference archive when present; CI still checks public metadata.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('color_data', ROOT/'scripts/native-ui-color-data.py')
color = importlib.util.module_from_spec(spec)
spec.loader.exec_module(color)
ARCHIVE = ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
MEMBER = 'QQTang-Local/runtime/client-patched/res/uiRes/uiMain.pyc'


class PublicColorContract(unittest.TestCase):
    def test_public_manifest_pins_single_payload_and_no_client_path(self):
        raw = color.MANIFEST.read_bytes()
        manifest = json.loads(raw)
        self.assertEqual(manifest['payload'], {'start':63481, 'end':63485, 'beforeHex':'00000000',
                         'afterHex':'c8000000', 'marshalTagOffset':63480, 'marshalTagHex':'69'})
        self.assertEqual(manifest['source']['sha256'], color.SOURCE_SHA)
        self.assertEqual(manifest['targetSha256'], color.TARGET_SHA)
        self.assertEqual(manifest['proof']['scopeCount'], 830)
        self.assertEqual(manifest['proof']['changedByteOffsets'], [63481])
        self.assertFalse(manifest['thirdPartyPycIncluded'])
        self.assertNotIn(b'C:\\', raw)
        self.assertNotIn(b'clientRoot"', raw)
        plan = ROOT/manifest['plan']['file']
        self.assertEqual(hashlib.sha256(plan.read_bytes()).hexdigest(), manifest['plan']['sha256'])

    def test_unknown_source_rejected_before_parsing(self):
        with self.assertRaisesRegex(ValueError, 'neither the pinned original'):
            color.prepare(b'not client code')


@unittest.skipUnless(ARCHIVE.is_file(), 'Exact source requires ignored local pinned archive')
class IsolatedColorInstall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ARCHIVE) as archive:
            cls.original = archive.read(MEMBER)
        if color.digest(cls.original) != color.SOURCE_SHA:
            raise ValueError('Local fixture source hash differs')
        cls.patched = cls.original[:color.START]+color.NEW+cls.original[color.END:]

    def setUp(self):
        fixture_root = ROOT/'.artifacts/native-ui-color-data-tests'
        fixture_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=fixture_root)
        self.folder = Path(self.temporary.name).resolve()
        self.assertTrue(self.folder.is_relative_to((ROOT/'.artifacts').resolve()))
        self.client = self.folder/'client'
        self.native = self.client/color.NATIVE_PATH
        self.native.parent.mkdir(parents=True)
        (self.client/'Client.exe').write_bytes(b'inert fixture marker; never executed')
        self.native.write_bytes(self.original)
        self.backup_patch = patch.object(color, 'BACKUP_ROOT', self.folder/'backup')
        self.backup_patch.start()
        self.stopped_patch = patch.object(color.io, 'check_stopped')
        self.stopped = self.stopped_patch.start()

    def tearDown(self):
        self.stopped_patch.stop()
        self.backup_patch.stop()
        # TemporaryDirectory removes only this already-verified .artifacts child.
        self.temporary.cleanup()

    def test_complete_inert_proof_and_only_expected_assignments(self):
        proof = color.prove_pair(self.original, self.patched)
        self.assertEqual(proof, json.loads(color.MANIFEST.read_bytes())['proof'])
        self.assertEqual(color.digest(self.patched), color.TARGET_SHA)
        self.assertEqual(proof['parsedObjects'], 20766)
        self.assertEqual(proof['constant6LoadOffsets'], [30,33,51,54,57])
        self.assertEqual([v['attribute'] for v in proof['literalAssignmentChanges']], ['drawcolor','textEdgeColor'])

    def test_default_verify_is_read_only_and_does_not_require_stopped(self):
        result = color.operate(self.client)
        self.assertEqual(result['state'], 'original')
        self.assertFalse(color.BACKUP_ROOT.exists())
        self.stopped.assert_not_called()
        self.assertNotIn('clientRoot', result)
        self.assertNotIn(str(self.client), json.dumps(result))
        self.assertEqual(self.native.read_bytes(), self.original)

    def test_apply_repeat_restore_repeat_and_private_backup(self):
        for action, expected, changed in [('apply',self.patched,True),('apply',self.patched,False),
                                          ('restore',self.original,True),('restore',self.original,False)]:
            result = color.operate(self.client, action)
            self.assertEqual(self.native.read_bytes(), expected)
            self.assertEqual(result['changed'], changed)
            self.assertTrue(result['backupVerified'])
        folder = color.BACKUP_ROOT/color.client_alias(self.client)
        self.assertEqual((folder/'uiMain.original.pyc').read_bytes(), self.original)
        receipt = json.loads((folder/'receipt.json').read_bytes())
        self.assertEqual(receipt['status'], 'restored')
        self.assertEqual(receipt['clientRoot'], str(self.client))

    def test_unknown_modified_source_and_tampered_backup_are_rejected(self):
        color.operate(self.client, 'apply')
        folder = color.BACKUP_ROOT/color.client_alias(self.client)
        (folder/'uiMain.original.pyc').write_bytes(b'bad backup')
        with self.assertRaisesRegex(ValueError, 'backup differs'):
            color.operate(self.client, 'restore')
        self.assertEqual(self.native.read_bytes(), self.patched)
        self.native.write_bytes(self.patched+b'unknown modification')
        with self.assertRaisesRegex(ValueError, 'neither the pinned original'):
            color.operate(self.client, 'apply')

    def test_already_patched_without_tool_backup_is_not_claimed_backed_up(self):
        self.native.write_bytes(self.patched)
        result = color.operate(self.client, 'apply')
        self.assertFalse(result['backupVerified'])
        self.assertFalse(result['changed'])
        with self.assertRaisesRegex(ValueError, 'backup is required'):
            color.operate(self.client, 'restore')
        self.assertEqual(self.native.read_bytes(), self.patched)

    def test_client_running_blocks_mutation_before_backup(self):
        self.stopped.side_effect = ValueError('Close Client.exe')
        with self.assertRaisesRegex(ValueError, 'Close Client.exe'):
            color.operate(self.client, 'apply')
        self.assertEqual(self.native.read_bytes(), self.original)
        self.assertFalse(color.BACKUP_ROOT.exists())

    def test_failure_after_replace_rolls_back_exact_preimage(self):
        real_write = color.io.atomic_write
        def fail_after_replace(path, data):
            real_write(path, data)
            if path == self.native and data == self.patched:
                raise OSError('simulated failure after atomic replacement')
        with patch.object(color.io, 'atomic_write', side_effect=fail_after_replace):
            with self.assertRaises(OSError):
                color.operate(self.client, 'apply')
        self.assertEqual(self.native.read_bytes(), self.original)
        result = color.operate(self.client, 'apply')
        self.assertEqual(result['state'], 'patched')

    def test_restore_failure_rolls_back_to_preexisting_patch(self):
        color.operate(self.client, 'apply')
        real_write = color.io.atomic_write
        def fail_restore(path, data):
            real_write(path, data)
            if path == self.native and data == self.original:
                raise OSError('simulated restore failure after atomic replacement')
        with patch.object(color.io, 'atomic_write', side_effect=fail_restore):
            with self.assertRaises(OSError):
                color.operate(self.client, 'restore')
        self.assertEqual(self.native.read_bytes(), self.patched)
        self.assertEqual(color.operate(self.client, 'restore')['state'], 'original')

    def test_os_lock_prevents_concurrent_apply_and_releases_after_failure(self):
        folder = color.BACKUP_ROOT/color.client_alias(self.client)
        with color.operation_lock(folder):
            with self.assertRaises(OSError):
                color.operate(self.client, 'apply')
        self.assertEqual(self.native.read_bytes(), self.original)
        self.assertEqual(color.operate(self.client, 'apply')['state'], 'patched')

    def test_receipt_failure_rolls_back_and_prepared_receipt_recovers(self):
        real_json = color.io.write_json
        def fail_final_receipt(path, data):
            if data['status'] == 'applied':
                raise OSError('simulated final receipt write failure')
            real_json(path, data)
        with patch.object(color.io, 'write_json', side_effect=fail_final_receipt):
            with self.assertRaises(OSError):
                color.operate(self.client, 'apply')
        self.assertEqual(self.native.read_bytes(), self.original)
        folder = color.BACKUP_ROOT/color.client_alias(self.client)
        self.assertEqual(json.loads((folder/'receipt.json').read_bytes())['status'], 'prepared')
        # Simulated process termination after replacement, before final receipt.
        self.native.write_bytes(self.patched)
        self.assertEqual(color.operate(self.client, 'restore')['state'], 'original')

    def test_external_change_during_second_stop_check_is_not_overwritten(self):
        external = self.original+b'external edit'
        def mutate_after_check():
            if self.stopped.call_count == 2:
                self.native.write_bytes(external)
        self.stopped.side_effect = mutate_after_check
        with self.assertRaisesRegex(ValueError, 'changed before atomic'):
            color.operate(self.client, 'apply')
        self.assertEqual(self.native.read_bytes(), external)

    def test_public_manifest_tampering_and_outside_payload_change_rejected(self):
        wrong = bytearray(self.patched)
        wrong[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'patched SHA256 differs'):
            color.prove_pair(self.original, bytes(wrong))
        altered = json.loads(color.MANIFEST.read_bytes())
        altered['proof']['scopeCount'] = 829
        manifest = self.folder/'tampered-manifest.json'
        manifest.write_text(json.dumps(altered))
        with patch.object(color, 'MANIFEST', manifest):
            with self.assertRaisesRegex(ValueError, 'contract differs'):
                color.operate(self.client, 'apply')
        self.assertEqual(self.native.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
