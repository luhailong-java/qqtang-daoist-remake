"""Evidence boundary fixtures for inventory icons and the one unresolved stand fallback."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reference_contract', ROOT / 'scripts/inventory_reference_contract.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
catalog = {row['item_id']: row for row in json.loads((ROOT / 'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))['items']}
art = {row['itemId']: row for row in json.loads((ROOT / 'assets/items/eye-adornments/art.json').read_text(encoding='utf-8'))['items']}
exception = json.loads((ROOT / 'assets/items/eye-adornments/source-exceptions.json').read_text(encoding='utf-8'))['exceptions'][0]


class SourceEvidenceTests(unittest.TestCase):
    def evidence(self, ident):
        entry = copy.deepcopy(art[ident])
        record = json.loads((ROOT / (entry['sourceReference'] + '.source.json')).read_text(encoding='utf-8'))
        return entry, copy.deepcopy(catalog[ident]), record

    def test_real_inventory_member(self):
        entry, original, record = self.evidence(4500)
        self.assertEqual(module.validate_source_reference(entry, original, record, record['sha256']), 'inventory')

    def test_explicit_stand_is_counted_separately(self):
        entry, original, record = self.evidence(3767)
        self.assertEqual(module.validate_source_reference(entry, original, record, record['sha256'], exception), 'stand-exception')

    def test_stand_without_fixed_exception_is_rejected(self):
        entry, original, record = self.evidence(3767)
        with self.assertRaisesRegex(ValueError, 'no implicit stand fallback'):
            module.validate_source_reference(entry, original, record, record['sha256'])

    def test_available_inventory_cannot_be_replaced_by_stand(self):
        entry, original, record = self.evidence(3767)
        original['installed_files'].append('res/uiRes/icon/eye/found.img')
        with self.assertRaisesRegex(ValueError, 'available inventory'):
            module.validate_source_reference(entry, original, record, record['sha256'], exception)

    def test_wrong_file_bytes_are_rejected(self):
        entry, original, record = self.evidence(4500)
        with self.assertRaisesRegex(ValueError, 'file/hash'):
            module.validate_source_reference(entry, original, record, '0' * 64)

    def test_unverified_mapping_cannot_be_claimed_verified(self):
        entry, original, record = self.evidence(3767)
        entry['inventoryMappingVerified'] = True
        with self.assertRaisesRegex(ValueError, 'must remain false'):
            module.validate_source_reference(entry, original, record, record['sha256'], exception)

    def test_different_stand_frame_cannot_reuse_exception(self):
        entry, original, record = self.evidence(3767)
        record['sourceFrameIndex'] = 1
        with self.assertRaisesRegex(ValueError, 'fixed evidence'):
            module.validate_source_reference(entry, original, record, record['sha256'], exception)


if __name__ == '__main__':
    unittest.main()
