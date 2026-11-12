"""Independent-manifest exports must not overwrite family selection or alias offsets."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('assets/items/head-adornments')
sys.path.insert(0, str(ROOT / 'scripts'))
module_spec = importlib.util.spec_from_file_location('head_world_export', ROOT / BASE / 'export_world_batch.py')
exporter = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(exporter)


class ManifestIsolationTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / '.artifacts'
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='world-export-test-', dir=scratch)
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.folder = self.root / BASE
        self.folder.mkdir(parents=True)
        contract = json.loads((ROOT / BASE / 'references/world/39/source-contract.json').read_text(encoding='utf-8'))
        doc = json.loads((ROOT / BASE / 'world-39-art.json').read_text(encoding='utf-8'))
        # Equal encoded raster payloads can legitimately have distinct positions.
        contract['frames'][15]['frameOffsetRaw'] = [35, -9]
        contract['frames'][15]['sourceFrameRecord']['frameOffset'] = [35, -9]
        self.write(BASE / 'references/world/39/source-contract.json', contract)
        entry = doc['items'][0]
        entry['frames'] = [frame for frame in entry['frames'] if frame['sourceFrameIndex'] in (12, 15)]
        alias = next(frame for frame in entry['frames'] if frame['sourceFrameIndex'] == 15)
        alias['frameOffsetRaw'] = [35, -9]
        alias['frameOffsetPxAtDensity4'] = [140, -36]
        alias['sourceNativeFrameRecord']['frameOffset'] = [35, -9]
        alias['positionWithinRawEnvelope'] = [10, 2]
        alias['sourceReference'] = {'file': 'source-position-15.png', 'sha256': 'position-specific-reference', 'record': 'source-position-15.json'}
        for frame in entry['frames']:
            frame.update({'visualAccepted': True, 'visualAcceptanceScope': 'static-export-raster',
                          'userReviewStatus': 'approved-static-visual',
                          'userVisualReviewRecord': 'previous-raster-review.json'})
        self.before = deepcopy(doc)
        self.write(BASE / 'world-art.json', doc)
        self.write(BASE / 'world-39-art.json', doc)
        mother = Image.new('RGBA', (100, 100))
        ImageDraw.Draw(mother).rectangle((20, 25, 79, 74), fill=(200, 180, 40, 255))
        mother.save(self.folder / 'fixture-mother.png')
        self.spec = {'source': (BASE / 'fixture-mother.png').as_posix(), 'version': 'test-independent',
                     'frames': [{'itemId': 39, 'sourceFrameIndex': 12, 'manualRect': [0, 0, 100, 100]}]}

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')

    def test_independent_manifest_refreshes_explicit_alias_and_preserves_source_position(self):
        self.spec['manifestPath'] = (BASE / 'world-39-art.json').as_posix()
        self.write('spec.json', self.spec)
        family_before = (self.folder / 'world-art.json').read_bytes()
        result = exporter.export_batch('spec.json', root=self.root)
        self.assertEqual((self.folder / 'world-art.json').read_bytes(), family_before)
        changed = json.loads((self.folder / 'world-39-art.json').read_text(encoding='utf-8'))
        frames = {frame['sourceFrameIndex']: frame for frame in changed['items'][0]['frames']}
        old = {frame['sourceFrameIndex']: frame for frame in self.before['items'][0]['frames']}
        for key in ('file', 'sha256', 'derivedFrom', 'qa'):
            self.assertEqual(frames[15][key], frames[12][key])
        self.assertEqual(frames[15]['operation']['originalPaintOperation'], frames[12]['operation'])
        for key in ('frameOffsetRaw', 'frameOffsetPxAtDensity4', 'sourceReference',
                    'sourceNativeFrameRecord', 'positionWithinRawEnvelope', 'rasterAliasOfSourceFrameIndex'):
            self.assertEqual(frames[15][key], old[15][key])
        for key in ('sourceNativeFrameRecord', 'imagePhaseRepresentativeIndex', 'rasterImageShared', 'positionWithinRawEnvelope'):
            self.assertEqual(frames[12][key], old[12][key])
        alias_sidecar = json.loads((self.root / frames[15]['provenanceRecord']).read_text(encoding='utf-8'))
        self.assertEqual(alias_sidecar, frames[15])
        self.assertEqual(result['synchronizedExplicitAliases'],
                         [{'itemId': 39, 'sourceFrameIndex': 15, 'representativeSourceFrameIndex': 12}])
        self.assertFalse(frames[12]['accepted'])
        self.assertFalse(frames[15]['runtimeAdopted'])
        for frame in frames.values():
            self.assertFalse(frame['visualAccepted'])
            self.assertEqual(frame['userReviewStatus'], 'pending')
            self.assertNotIn('userVisualReviewRecord', frame)
            self.assertNotIn('visualAcceptanceScope', frame)

    def test_default_destination_remains_family_manifest(self):
        self.write('spec.json', self.spec)
        independent_before = (self.folder / 'world-39-art.json').read_bytes()
        result = exporter.export_batch('spec.json', root=self.root)
        self.assertEqual(result['manifestPath'], (BASE / 'world-art.json').as_posix())
        self.assertEqual((self.folder / 'world-39-art.json').read_bytes(), independent_before)
        family = json.loads((self.folder / 'world-art.json').read_text(encoding='utf-8'))
        self.assertTrue(all(frame['file'].endswith('frame-012-test-independent.png')
                            for frame in family['items'][0]['frames']))


if __name__ == '__main__':
    unittest.main()
