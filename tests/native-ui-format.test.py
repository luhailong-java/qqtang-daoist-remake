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


def luminance(rgb):
    values = [c/255 for c in rgb]
    linear = [v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(weight*v for weight,v in zip((0.2126,0.7152,0.0722),linear,strict=True))


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

    def test_shared_message_body_supports_the_explicit_global_light_text(self):
        sources = json.loads((ROOT/'assets/native-client-ui/core-reference/manifest.json').read_bytes())
        scope = next(s for s in sources['sourceScopes'] if s['module']=='uiMain' and s['scope']=='?')
        color = scope['literalAssignments']['zoneChooseColor'][:3]
        path = ROOT/'assets/native-client-ui/login-v1/decoded/object__ui__common__dlg_msgBox-00.png'
        with Image.open(path) as image:
            background = luminance(image.getpixel((184,140))[:3])
        style = json.loads((ROOT/'assets/native-client-ui/text-color-v1/manifest.json').read_bytes())
        link = next(v['after'][:3] for v in style['proof']['literalAssignmentChanges'] if v['attribute']=='drawcolor')
        for foreground_color in (color,link):
            foreground = luminance(foreground_color)
            contrast = (max(background,foreground)+0.05)/(min(background,foreground)+0.05)
            self.assertGreaterEqual(contrast,4.5)

    def test_entry_status_mask_and_verification_text_surface(self):
        folder = ROOT/'assets/native-client-ui/entry-controls-reference'
        manifest = json.loads((folder/'candidate-manifest.json').read_bytes())
        item = next(e for e in manifest['items'] if e['rendererKind']=='entry-state-strip')
        raw = (ROOT/item['file']).read_bytes()
        metadata,_ = codec.reader.inspect_dimg(raw,metadata_only=True)
        frame = metadata['frames'][0]
        start = frame['pixelDataOffset']
        decoded = codec.reader.decode_frame_pixels(raw[start:start+frame['pixelByteLength']],
                    frame['pixelMode'],frame['width'],frame['height'])
        native = Image.frombytes('RGBA',(frame['width'],frame['height']),decoded)
        source = manifest['structuralAlphaInputs'][0]
        self.assertEqual(hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest(),source['sha256'])
        with Image.open(ROOT/source['file']) as original:
            self.assertEqual(native.getchannel('A').tobytes(),original.getchannel('A').tobytes())
        evidence = json.loads((folder/'input-color-evidence.json').read_bytes())
        declarations = json.loads((ROOT/'references/qqtang-ui-data/constants/uiLogin.json').read_bytes())
        scope = next(s for s in declarations['scopes'] if s['scope']==evidence['scope'])
        self.assertEqual(scope['bytecodeSha256'],evidence['sourceBytecodeSha256'])
        self.assertEqual([x['name'] for x in evidence['symbolAssignment']],['darkColor','drawcolor'])
        item = next(e for e in manifest['items'] if e['rendererKind']=='entry-verify-panel')
        with Image.open(ROOT/item['frames'][0]['file']) as image:
            background = luminance(image.getpixel((100,132))[:3])
        for color in (evidence['sharedUiMainDarkColor'][:3],(0,0,0)):
            foreground = luminance(color)
            self.assertGreaterEqual((background+0.05)/(foreground+0.05),4.5)

    def test_chat_storage_and_browser_alpha_survives_the_central_export(self):
        manifest = json.loads((ROOT/'assets/native-client-ui/login-v1/manifest.json').read_bytes())
        for group, expected_count in (('chat-controls',65),('storage-task',27),('web-controls',24)):
            references = {e['purpose']:e for e in manifest['structuralAlphaInputs'] if e['group']==group}
            self.assertEqual(len(references),expected_count)
            checked = 0
            for item in manifest['items']:
                kind = item['rendererKind']
                fixed = {'storage-selection':'selection','storage-shadow':'shadow','storage-grid-room':'room-grid'}
                whole_family = group in ('chat-controls','web-controls')
                if whole_family and not kind.startswith(group.split('-')[0]+'-'):
                    continue
                if group=='storage-task' and kind not in (*fixed,'storage-nav','storage-task-step'):
                    continue
                raw = (ROOT/item['file']).read_bytes()
                metadata,_ = codec.reader.inspect_dimg(raw,metadata_only=True)
                for frame in metadata['frames']:
                    purpose = (f'{kind}-{frame["index"]:02}' if whole_family else
                               fixed[kind] if kind in fixed else f'{item["caption"]}-{frame["index"]}')
                    source = references[purpose]
                    start = frame['pixelDataOffset']
                    decoded = codec.reader.decode_frame_pixels(raw[start:start+frame['pixelByteLength']],
                                frame['pixelMode'],frame['width'],frame['height'])
                    native = Image.frombytes('RGBA',(frame['width'],frame['height']),decoded)
                    path = ROOT/source['file']
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),source['sha256'])
                    with self.subTest(nativePath=item['nativePath'],frame=frame['index']),Image.open(path) as original:
                        self.assertEqual(native.getchannel('A').tobytes(),original.getchannel('A').tobytes())
                    checked += 1
            self.assertEqual(checked,expected_count)

    def test_forge_removes_old_interior_glyph_alpha_with_a_bounded_exception(self):
        manifest = json.loads((ROOT/'assets/native-client-ui/login-v1/manifest.json').read_bytes())
        references = {e['purpose']:e for e in manifest['structuralAlphaInputs'] if e['group']=='forge-controls'}
        self.assertEqual(len(references),52)
        changes = manifest['alphaNormalizations']
        self.assertEqual(len(changes),1)
        self.assertEqual(changes[0]['rendererKind'],'forge-confirm-panel')
        self.assertEqual(changes[0]['sourceRoiXYXY'],[6,5,221,107])
        checked = 0
        for item in manifest['items']:
            if not item['rendererKind'].startswith('forge-'):
                continue
            raw = (ROOT/item['file']).read_bytes()
            metadata,_ = codec.reader.inspect_dimg(raw,metadata_only=True)
            for frame in metadata['frames']:
                source = references[f'{item["rendererKind"]}-{frame["index"]:02}']
                with Image.open(ROOT/source['file']) as original:
                    expected = bytearray(original.getchannel('A').tobytes())
                if item['rendererKind']=='forge-confirm-panel':
                    for y in range(5,107):
                        start = y*frame['width']+6
                        expected[start:start+215] = b'\xff'*215
                start = frame['pixelDataOffset']
                pixels = codec.reader.decode_frame_pixels(raw[start:start+frame['pixelByteLength']],
                            frame['pixelMode'],frame['width'],frame['height'])
                with self.subTest(nativePath=item['nativePath'],frame=frame['index']):
                    self.assertEqual(pixels[3::4],bytes(expected))
                checked += 1
        self.assertEqual(checked,52)

    def test_loose_batches_reject_windows_case_collisions_before_writing(self):
        raw = self.container(8)
        metadata,_ = codec.reader.inspect_dimg(raw,metadata_only=True)
        previous_root = installer.ROOT
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = root/'client'
            name = 'res/uiRes/icon/eye/eye80.img'
            native = client/name
            native.parent.mkdir(parents=True)
            native.write_bytes(raw)
            installer.ROOT = root
            (root/'patch.img').write_bytes(raw)
            item = {'nativePath':name,'file':'patch.img','sha256':installer.digest(raw),
                    'sourceSha256':installer.digest(raw),'sourcePacked':False,'sourceLoose':True}
            other = {**item,'nativePath':name.upper()}
            contract = {'items':[{'nativePath':e['nativePath'],'metadata':metadata} for e in (item,other)]}
            try:
                with self.assertRaisesRegex(ValueError,'Duplicate native destination'):
                    installer.prepare_loose(client,{'items':[item,other]},contract)
                self.assertEqual(native.read_bytes(),raw)
            finally:
                installer.ROOT = previous_root

    def test_region_backgrounds_support_the_declared_light_global_color(self):
        root = ROOT/'assets/native-client-ui/login-v1/decoded'
        sources = json.loads((ROOT/'assets/native-client-ui/core-reference/manifest.json').read_bytes())
        scope = next(s for s in sources['sourceScopes'] if s['module']=='uiMain' and s['scope']=='?')
        foreground = luminance(scope['literalAssignments']['zoneChooseColor'][:3])
        # sect1.name assigns zoneChooseColor; -1 frames expose the screen background.
        for filename,point in (('object__ui__bg__bg_selSect-00.png',(500,180)),
                               ('object__ui__selSect__img_sect-00.png',(40,14))):
            with self.subTest(filename=filename),Image.open(root/filename) as image:
                red,green,blue,alpha = image.getpixel(point)
                # Test the lightest possible underlay when the painted row has partial alpha.
                opacity = alpha/255
                background = luminance(tuple(round(c*opacity+255*(1-opacity)) for c in (red,green,blue)))
                self.assertGreaterEqual((max(foreground,background)+0.05)/(min(foreground,background)+0.05),4.5)


if __name__ == '__main__':
    unittest.main()
