"""A user may approve fixed static PNGs without approving their animation/runtime."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from head_world_visual_review import EXCLUDED_SCOPES, validate_static_visual_review


class StaticVisualReceiptTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / '.artifacts'
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix='static-visual-review-test-', dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'frame.png').write_bytes(b'fixed static raster bytes')
        (self.root / 'preview.png').write_bytes(b'fixed review preview bytes')
        digest = lambda name: hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        self.frame = {'sourceFrameIndex': 12, 'imagePhaseRepresentativeIndex': 12,
                      'file': 'frame.png', 'sha256': digest('frame.png'),
                      'accepted': False, 'geometryAccepted': False, 'runtimeAdopted': False,
                      'visualAccepted': True, 'visualAcceptanceScope': 'static-export-raster',
                      'userReviewStatus': 'approved-static-visual', 'userVisualReviewRecord': 'receipt.json'}
        self.receipt = {'schemaVersion': 1, 'reviewType': 'user-static-visual', 'status': 'approved',
                        'scope': 'static-export-raster', 'preview': {'file': 'preview.png', 'sha256': digest('preview.png')},
                        'assets': [{'itemId': 39, 'sourceFrameIndex': 12, 'sourcePositions': [12, 15],
                                    'file': 'frame.png', 'sha256': digest('frame.png')}],
                        'exclusions': sorted(EXCLUDED_SCOPES),
                        'source': {'question': '请审核本批8张候选画面。', 'answer': '本批画面通过，时序和挂点仍待验。'}}
        self.write_receipt()

    def write_receipt(self):
        (self.root / 'receipt.json').write_text(json.dumps(self.receipt), encoding='utf-8')

    def validate(self, frame=None):
        return validate_static_visual_review(self.frame if frame is None else frame, 39, self.root)

    def test_representative_and_explicit_alias_are_approved_for_static_visuals(self):
        self.assertTrue(self.validate())
        alias = deepcopy(self.frame)
        alias['sourceFrameIndex'] = 15
        self.assertTrue(self.validate(alias))
        self.receipt['assets'][0]['sourcePositions'] = [12]
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, 'uniquely approve'):
            self.validate(alias)

    def test_unreviewed_false_needs_no_receipt_but_true_requires_one(self):
        (self.root / 'receipt.json').unlink()
        pending = deepcopy(self.frame)
        pending.update({'visualAccepted': False, 'userReviewStatus': 'pending'})
        pending.pop('userVisualReviewRecord')
        pending.pop('visualAcceptanceScope')
        self.assertFalse(self.validate(pending))
        with self.assertRaises(FileNotFoundError):
            self.validate()

    def test_receipt_cannot_cover_another_item_representative_file_or_hash(self):
        variants = [('itemId', 408), ('sourceFrameIndex', 13), ('file', 'other.png'), ('sha256', '0' * 64)]
        original = deepcopy(self.receipt)
        for key, value in variants:
            with self.subTest(binding=key):
                self.receipt = deepcopy(original)
                self.receipt['assets'][0][key] = value
                self.write_receipt()
                with self.assertRaises(ValueError):
                    self.validate()

    def test_changed_raster_or_preview_invalidates_the_fixed_review(self):
        (self.root / 'frame.png').write_bytes(b'changed after approval')
        with self.assertRaisesRegex(ValueError, 'raster bytes changed'):
            self.validate()
        (self.root / 'frame.png').write_bytes(b'fixed static raster bytes')
        (self.root / 'preview.png').write_bytes(b'changed preview')
        with self.assertRaisesRegex(ValueError, 'preview SHA'):
            self.validate()

    def test_nonstatic_scope_or_missing_explicit_user_answer_is_rejected(self):
        wrong_frame = deepcopy(self.frame)
        wrong_frame['visualAcceptanceScope'] = 'complete-animation'
        with self.assertRaisesRegex(ValueError, 'scope/status'):
            self.validate(wrong_frame)
        self.receipt['scope'] = 'complete-animation'
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, 'static-raster review'):
            self.validate()
        self.receipt['scope'] = 'static-export-raster'
        self.receipt['source']['answer'] = ''
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, 'question/answer'):
            self.validate()

    def test_static_approval_cannot_approve_geometry_animation_or_runtime(self):
        for flag in ('accepted', 'geometryAccepted', 'runtimeAdopted', 'completeAnimationAccepted'):
            with self.subTest(flag=flag):
                broader = deepcopy(self.frame)
                broader[flag] = True
                with self.assertRaisesRegex(ValueError, flag):
                    self.validate(broader)


if __name__ == '__main__':
    unittest.main()
