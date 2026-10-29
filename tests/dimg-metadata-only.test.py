"""Metadata-only artificial byte fixtures. Written during hold; NOT RUN."""
from pathlib import Path
from unittest.mock import patch
import importlib.util,struct,unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
reader=load('our_metadata_dimg_reader',ROOT/'scripts/inspect-reference-dimg.py')
cli=load('our_bounded_metadata_cli',ROOT/'references/qqtang-map-data/motion-contract/inspect-packed-metadata.py')

def image_frame(payload=b'\x03\x02\x01\xff',mode=8,width=1,height=1,offset=(-2,3),marker=0):
    return struct.pack('<IiiI',marker,*offset,mode)+struct.pack('<3I',width,height,0)+payload
def empty_frame(offset=(0,0)):
    return struct.pack('<IiiI',0,*offset,0)
def container(frames,version=65536,directions=1,suffix=b''):
    return b'QQF\x1aDIMG'+struct.pack('<8I',version,24,len(frames),directions,0,0,1,1)+b''.join(frames)+suffix

class MetadataOnlyDimgTests(unittest.TestCase):
    def inspect_without_decode(self,data,**kwargs):
        with patch.object(reader,'decode_frame_pixels',side_effect=AssertionError('must never decode'))as decoder:
            metadata,visible=reader.inspect_dimg(data,metadata_only=True,**kwargs)
            decoder.assert_not_called()
        self.assertIsNone(visible)
        self.assertFalse(metadata['pixelDecodePerformed'])
        self.assertEqual(metadata['pixelPayloadValidation'],'unknown')
        self.assertEqual(metadata['visibleAlpha'],'unknown')
        self.assertFalse(metadata['runtimeUsable'])
        self.assertFalse(metadata['strictCompleteContainerAccepted'])
        self.assertTrue(all('decodedRgbaSha256'not in f for f in metadata['frames']))
        self.assertTrue(all('visibleBoundingBox'not in f for f in metadata['frames']))
        return metadata

    def test_offsets_empty_marker_payload_hash_and_eof_without_rgba(self):
        payload=b'\x03\x02\x01\xff'
        data=container([empty_frame(),image_frame(payload,offset=(-7,9)),image_frame(payload,offset=(11,-5))])
        result=self.inspect_without_decode(data)
        self.assertTrue(result['frames'][0]['empty'])
        self.assertEqual(result['frames'][1]['frameOffset'],[-7,9])
        self.assertEqual(result['frames'][2]['frameOffset'],[11,-5])
        self.assertEqual(result['frames'][1]['encodedPixelSha256'],reader.sha256(payload))
        self.assertEqual(result['parsedByteLength'],len(data))
        self.assertTrue(result['strictDeclaredStructureAccepted'])

    def test_supported_encoded_payload_lengths_do_not_decode(self):
        for mode,payload in [(3,b'\x00\x00\x20'),(0x11000000,b'\x00\x00\x20'),(8,b'\x01\x02\x03\x04'),(16,b'\x01\x02\x03')]:
            with self.subTest(mode=mode):
                result=self.inspect_without_decode(container([image_frame(payload,mode=mode)]))
                self.assertEqual(result['frames'][0]['pixelByteLength'],len(payload))

    def test_default_still_decodes_first_nonempty_frame(self):
        data=container([empty_frame(),image_frame()])
        result,visible=reader.inspect_dimg(data)
        self.assertEqual(visible['index'],1)
        self.assertEqual(visible['pixels'],b'\x01\x02\x03\xff')
        self.assertIn('decodedRgbaSha256',result['frames'][1])
        self.assertNotIn('metadataOnly',result)
        self.assertTrue(result['strictCompleteContainerAccepted'])

    def test_all_structurally_empty_allowed_only_for_metadata(self):
        data=container([empty_frame(),empty_frame((2,-3))])
        result=self.inspect_without_decode(data)
        self.assertTrue(all(f['empty']for f in result['frames']))
        with self.assertRaisesRegex(ValueError,'no visible frame'):
            reader.inspect_dimg(data)

    def test_structural_rejections_remain_in_metadata_mode(self):
        bad=[container([image_frame(payload=b'\x00')]),
             container([image_frame(mode=999)]),
             container([image_frame(width=0,height=1)]),
             container([image_frame(marker=7)]),
             container([image_frame()])[:-3],
             container([image_frame()],directions=2),
             container([image_frame()],suffix=b'unexpected')]
        for data in bad:
            with self.subTest(data=data[:40]):
                with patch.object(reader,'decode_frame_pixels',side_effect=AssertionError('must not decode')):
                    with self.assertRaises(ValueError):
                        reader.inspect_dimg(data,metadata_only=True)

    def test_explicit65537_suffix_kept_opaque_without_rgba(self):
        data=container([image_frame()],version=65537,suffix=b'opaque suffix')
        with self.assertRaisesRegex(ValueError,'unrecognized trailing bytes'):
            reader.inspect_dimg(data,metadata_only=True)
        result=self.inspect_without_decode(data,reference_only_version65537_suffix=True)
        self.assertEqual(result['trailingByteLength'],13)
        self.assertEqual(result['trailingBytesSha256'],reader.sha256(b'opaque suffix'))
        self.assertFalse(result['strictDeclaredStructureAccepted'])
        self.assertTrue(result['referenceOnlyOpaqueVersionedSuffix'])

    def test_payload_identity_and_offset_identity_are_separate(self):
        result=self.inspect_without_decode(container([image_frame(offset=(0,0)),image_frame(offset=(0,0)),image_frame(offset=(1,0)),empty_frame()]))
        raster=cli.groups(result['frames'])
        poses=cli.groups(result['frames'],True)
        self.assertEqual([g['frameIndices']for g in raster],[[0,1,2]])
        self.assertEqual([g['frameIndices']for g in poses],[[0,1],[2]])
        self.assertFalse(raster[0]['allOffsetsEqual'])
        self.assertIsNone(raster[0]['visuallyDistinctFromOtherGroups'])

if __name__=='__main__':
    unittest.main()
