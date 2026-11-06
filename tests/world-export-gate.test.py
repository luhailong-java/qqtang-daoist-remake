from pathlib import Path
import sys
import unittest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from painted_crop_gate import validate_visible_boundaries


class CropGateTests(unittest.TestCase):
    def test_two_isolated_objects_are_unchanged(self):
        image = Image.new('RGBA', (20, 10))
        image.putpixel((5, 5), (200, 180, 50, 255))
        image.putpixel((15, 5), (30, 90, 70, 255))
        before = image.tobytes()
        validate_visible_boundaries(image, [[0, 0, 10, 10], [10, 0, 20, 10]])
        self.assertEqual(before, image.tobytes())

    def test_bad_last_crop_is_rejected_in_preflight(self):
        image = Image.new('RGBA', (20, 10))
        image.putpixel((5, 5), (200, 180, 50, 255))
        image.putpixel((10, 5), (30, 90, 70, 255))
        with self.assertRaisesRegex(ValueError, 'crop 1'):
            validate_visible_boundaries(image, [[0, 0, 10, 10], [10, 0, 20, 10]])

    def test_declared_alpha_threshold(self):
        image = Image.new('RGBA', (10, 10))
        image.putpixel((0, 5), (255, 30, 0, 15))
        validate_visible_boundaries(image, [[0, 0, 10, 10]])
        image.putpixel((0, 5), (255, 30, 0, 16))
        with self.assertRaises(ValueError):
            validate_visible_boundaries(image, [[0, 0, 10, 10]])

    def test_invisible_colored_rgb_is_not_a_background(self):
        image = Image.new('RGBA', (10, 10), (120, 70, 20, 0))
        image.putpixel((5, 5), (20, 90, 50, 255))
        validate_visible_boundaries(image, [[0, 0, 10, 10]])


if __name__ == '__main__':
    unittest.main()
