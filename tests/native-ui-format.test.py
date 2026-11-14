"""Native pixel encoding regression checks without importing or launching a client."""
import importlib.util
from pathlib import Path
import struct
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('codec', ROOT/'scripts/native-ui-format.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)


class NativeUiPixels(unittest.TestCase):
    def container(self, mode):
        width, height = 5, 3
        header = b'QQF\x1aDIMG' + struct.pack('<8I', 65536, 24, 2, 1, 123, 456, 13, 17)
        frame = struct.pack('<IiiI3I', 0, -7, 9, mode, width, height, 2*width)
        plane = bytes(width * height * (4 if mode == 8 else 3))
        empty = struct.pack('<IiiI', 0, 2, 3, 0)
        return header + frame + plane + empty

    def test_all_modes_keep_offsets_unknown_fields_and_empty_positions(self):
        for mode in (3, 0x11000000, 8, 16):
            with self.subTest(mode=mode):
                original = self.container(mode)
                image = Image.new('RGBA', (5, 3), (38, 127, 213, 255))
                output, metadata, decoded = codec.replace_frames(original, {0: image})
                frame = metadata['frames'][0]
                start, end = frame['pixelDataOffset'], frame['pixelDataOffset']+frame['pixelByteLength']
                self.assertEqual(len(output), len(original))
                self.assertEqual(output[:start], original[:start])
                self.assertEqual(output[end:], original[end:])
                actual = decoded[0][1].getpixel((0, 0))
                self.assertTrue(all(abs(a-b) <= 4 for a,b in zip(actual, (38,127,213,255), strict=True)))
                self.assertEqual(metadata['frames'][1]['frameOffset'], [2,3])

    def test_rgb565_alpha_plane_spans_all_original_33_levels(self):
        image = Image.new('RGBA', (33, 1))
        for x in range(33):
            image.putpixel((x, 0), (56, 184, 92, round(x*255/32)))
        encoded = codec.encode_pixels(image, 3)
        self.assertEqual(encoded[66:], bytes(range(33)))
        decoded = codec.reader.decode_frame_pixels(encoded, 3, 33, 1)
        self.assertEqual(decoded[3], 0)
        self.assertEqual(decoded[-1], 255)

    def test_partial_or_resized_replacements_and_transparency_for_opaque_mode_fail(self):
        original = self.container(8)
        for pictures in ({}, {0: Image.new('RGBA', (6,3))}, {0: Image.new('RGBA',(5,3)),1:Image.new('RGBA',(5,3))}):
            with self.assertRaises(ValueError):
                codec.replace_frames(original, pictures)
        with self.assertRaises(ValueError):
            codec.encode_pixels(Image.new('RGBA',(5,3),(0,0,0,0)),16)


if __name__ == '__main__':
    unittest.main()
