"""Native pixel encoding regression checks without importing or launching a client."""
import importlib.util
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('codec', ROOT/'scripts/native-ui-format.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
install_spec = importlib.util.spec_from_file_location('installer', ROOT/'scripts/install-native-ui.py')
installer = importlib.util.module_from_spec(install_spec)
install_spec.loader.exec_module(installer)


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

    def test_inventory_normalization_requires_exact_source_contract_and_geometry(self):
        # One declared frame with an opaque newer-container tail, never executed.
        base = self.container(8)[:-16]
        base = bytearray(base)
        struct.pack_into('<I',base,16,1)
        output = bytes(base)
        struct.pack_into('<I',base,8,65537)
        original = bytes(base) + b'opaque native suffix'
        metadata,_ = codec.reader.inspect_dimg(original,metadata_only=True,reference_only_version65537_suffix=True)
        normalization = {'sourceVersion':65537,'targetVersion':65536,
                         'removedOpaqueTailBytes':metadata['trailingByteLength'],
                         'sourceOpaqueTailSha256':metadata['trailingBytesSha256']}
        previous_root = installer.ROOT
        with tempfile.TemporaryDirectory() as directory:
            installer.ROOT = Path(directory)
            patch = installer.ROOT/'icon.img'
            def item_for(data, **changes):
                patch.write_bytes(data)
                return {'file':'icon.img','sha256':installer.digest(data),
                        'nativePath':'res/uiRes/icon/eye/eye80.img',
                        'containerNormalization':normalization,**changes}
            try:
                self.assertEqual(installer.native_replacement(item_for(output),{'metadata':metadata}),output)
                invalid_normalization = {**normalization,'removedOpaqueTailBytes':0}
                for changes in ({'nativePath':'object/ui/common/icon.img'},
                                {'containerNormalization':invalid_normalization}):
                    with self.assertRaisesRegex(ValueError,'Unsupported native container'):
                        installer.native_replacement(item_for(output,**changes),{'metadata':metadata})
                moved = bytearray(output)
                struct.pack_into('<i',moved,44,-6)
                with self.assertRaisesRegex(ValueError,'geometry changed'):
                    installer.native_replacement(item_for(bytes(moved)),{'metadata':metadata})
            finally:
                installer.ROOT = previous_root

    def test_game_masks_keep_the_original_alpha_after_native_encoding(self):
        manifest = json.loads((ROOT/'assets/native-client-ui/login-v1/manifest.json').read_bytes())
        references = {e['purpose']:e for e in manifest['structuralAlphaInputs'] if e['group']=='game-controls'}
        items = [e for e in manifest['items'] if e['rendererKind']=='game-alpha']
        self.assertEqual({e['caption'] for e in items},set(references))
        self.assertEqual(len(references),9)
        for item in items:
            with self.subTest(nativePath=item['nativePath']):
                source = references[item['caption']]
                raw = (ROOT/item['file']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])
                metadata,_ = codec.reader.inspect_dimg(raw,metadata_only=True)
                frame = metadata['frames'][0]
                start = frame['pixelDataOffset']
                decoded = codec.reader.decode_frame_pixels(raw[start:start+frame['pixelByteLength']],
                            frame['pixelMode'],frame['width'],frame['height'])
                image = Image.frombytes('RGBA',(frame['width'],frame['height']),decoded)
                path = ROOT/source['file']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),source['sha256'])
                with Image.open(path) as original:
                    self.assertEqual(image.getchannel('A').tobytes(),original.getchannel('A').tobytes())

    def test_shared_message_body_supports_declared_black_and_blue_text(self):
        def color_from(module,scope_name):
            data = json.loads((ROOT/f'references/qqtang-ui-data/constants/{module}.json').read_bytes())
            scope = next(s for s in data['scopes'] if s['scope']==scope_name)
            value = next(v['literalValue'] for v in scope['literalAssignments'] if v['name']=='drawcolor')
            return tuple(v['value'] for v in value['values'])[:3]
        def luminance(rgb):
            values = [c/255 for c in rgb]
            linear = [v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
            return sum(weight*v for weight,v in zip((0.2126,0.7152,0.0722),linear,strict=True))
        colors = (color_from('uiTemplate','?.TLabel'),
                  color_from('uiMain','?.UI.children.SysMsgbox.children.hyPerLink1'))
        path = ROOT/'assets/native-client-ui/login-v1/decoded/object__ui__common__dlg_msgBox-00.png'
        with Image.open(path) as image:
            background = luminance(image.getpixel((184,140))[:3])
        for color in colors:
            foreground = luminance(color)
            contrast = (max(background,foreground)+0.05)/(min(background,foreground)+0.05)
            self.assertGreaterEqual(contrast,4.5)


if __name__ == '__main__':
    unittest.main()
