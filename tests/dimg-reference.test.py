"""Artificial byte fixtures only; no original client code or images execute."""
import importlib.util
import hashlib
from pathlib import Path
import struct
import unittest
import zlib

spec = importlib.util.spec_from_file_location("our_dimg_reader", Path(__file__).resolve().parents[1] / "scripts/inspect-reference-dimg.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def dimg(mode, pixels, width=1, height=1, x=0, y=0, canvas=(1, 1), version=65536):
    return (b"QQF\x1aDIMG" + struct.pack("<8I", version, 24, 1, 1, 0, 0, *canvas)
            + struct.pack("<IiiI", 0, x, y, mode) + struct.pack("<3I", width, height, 0) + pixels)


class ReferenceDimgTests(unittest.TestCase):
    def test_known_pixel_encodings_and_plane_order(self):
        self.assertEqual(reader.decode_frame_pixels(bytes((3, 2, 1, 4)), 8, 1, 1), bytes((1, 2, 3, 4)))
        self.assertEqual(reader.decode_frame_pixels(bytes((3, 2, 1)), 16, 1, 1), bytes((1, 2, 3, 255)))
        # Two RGB565 little-endian words followed by the separate alpha plane.
        self.assertEqual(reader.decode_frame_pixels(bytes.fromhex("00f8e0072010"), 3, 2, 1), bytes((255, 0, 0, 255, 0, 255, 0, 128)))

    def test_uninitialized_canvas_is_recorded_without_allocation_or_anchor_guess(self):
        data = dimg(8, bytes((3, 2, 1, 255)), x=-4, y=17, canvas=(0xcccccccc, 0xcccccccc))
        metadata, frame = reader.inspect_dimg(data)
        self.assertFalse(metadata["declaredCanvasWithinBound"])
        self.assertEqual(metadata["declaredCanvas"], [0xcccccccc, 0xcccccccc])
        self.assertEqual(metadata["frames"][0]["frameOffset"], [-4, 17])
        self.assertEqual((frame["width"], frame["height"]), (1, 1))
        self.assertEqual(frame["pixels"], bytes((1, 2, 3, 255)))
        self.assertEqual(metadata["parsedByteLength"], len(data))

    def test_truncations_unknown_modes_dimensions_and_tail_fail_closed(self):
        data = dimg(8, bytes((3, 2, 1, 4)))
        for length in range(len(data)):
            with self.assertRaises(ValueError):
                reader.inspect_dimg(data[:length])
        for invalid in (data + b"\0", dimg(9, b"\0\0\0\0"), dimg(8, b"", width=4097), dimg(8, b"", height=0)):
            with self.assertRaises(ValueError):
                reader.inspect_dimg(invalid)

    def test_index_exact_boundaries_and_stream_size_are_enforced(self):
        raw = dimg(16, bytes((3, 2, 1)))
        compressed = zlib.compress(raw)
        name = b"object\\mapElem\\artificial\\elem1_stand.img"
        record = struct.pack("<H", len(name)) + name + struct.pack("<4I", 0, 0, len(raw), len(compressed))
        index = struct.pack("<4I", 100, 1, 16, len(record)) + record
        parsed = reader.parse_index(index, len(compressed))
        self.assertEqual(len(parsed["entries"]), 1)
        unpacked, _ = reader.unpack_resource(compressed, parsed["entries"][0])
        self.assertEqual(unpacked, raw)
        for invalid in (index[:-1], index + b"\0"):
            with self.assertRaises(ValueError):
                reader.parse_index(invalid, len(compressed))
        with self.assertRaises(ValueError):
            reader.parse_index(index, len(compressed) - 1)
        wrong_size = {**parsed["entries"][0], "rawByteLength": len(raw) - 1}
        with self.assertRaises(ValueError):
            reader.unpack_resource(compressed, wrong_size)
        with self.assertRaises(ValueError):
            reader.unpack_resource(compressed[:-1], parsed["entries"][0])

    def test_versioned_suffix_needs_explicit_reference_scope_and_preserves_unknown_bytes(self):
        prefix = dimg(8, bytes((3, 2, 1, 255)), version=65537)
        suffix = b"opaque-not-an-extra-frame\0\xff"
        data = prefix + suffix
        with self.assertRaises(ValueError):
            reader.inspect_dimg(data)
        metadata, frame = reader.inspect_dimg(data, reference_only_version65537_suffix=True)
        self.assertEqual(frame['pixels'], bytes((1, 2, 3, 255)))
        self.assertEqual(metadata['frameCount'], 1)
        self.assertEqual(len(metadata['frames']), 1)
        self.assertEqual(metadata['byteLength'], len(data))
        self.assertEqual(metadata['sha256'], hashlib.sha256(data).hexdigest())
        self.assertEqual(metadata['parsedByteLength'], len(prefix))
        self.assertEqual(metadata['trailingByteLength'], len(suffix))
        self.assertEqual(metadata['trailingBytesSha256'], hashlib.sha256(suffix).hexdigest())
        self.assertFalse(metadata['strictCompleteContainerAccepted'])
        self.assertTrue(metadata['referenceOnlyOpaqueVersionedSuffix'])

    def test_reference_suffix_option_does_not_bypass_version_or_frame_bounds(self):
        legacy = dimg(8, bytes((3, 2, 1, 255))) + b"opaque"
        with self.assertRaises(ValueError):
            reader.inspect_dimg(legacy, reference_only_version65537_suffix=True)
        invalids = [dimg(8, b'', width=4097, version=65537),
                    dimg(9, b'\0\0\0\0', version=65537),
                    dimg(8, bytes((3, 2, 1, 255)), version=65538),
                    dimg(8, bytes((3, 2, 1)), version=65537)]
        for invalid in invalids:
            with self.assertRaises(ValueError):
                reader.inspect_dimg(invalid, reference_only_version65537_suffix=True)

    def test_exact_length_version65537_retains_strict_complete_container_evidence(self):
        metadata, _ = reader.inspect_dimg(dimg(8, bytes((3, 2, 1, 255)), version=65537))
        self.assertTrue(metadata['strictCompleteContainerAccepted'])
        self.assertFalse(metadata['referenceOnlyOpaqueVersionedSuffix'])
        self.assertEqual(metadata['trailingByteLength'], 0)
        self.assertIsNone(metadata['trailingBytesSha256'])


if __name__ == "__main__":
    unittest.main()
