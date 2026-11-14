"""Independent on-disk native-byte/alpha/state QA; never installs or runs client."""
import argparse
import hashlib
from importlib import util
import json
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    result = util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


CODEC = load_module('shopextra_qa_native_codec', 'scripts/native-ui-format.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decoded(raw, frame):
    start = frame['pixelDataOffset']
    pixels = CODEC.reader.decode_frame_pixels(raw[start:start + frame['pixelByteLength']],
                frame['pixelMode'], frame['width'], frame['height'])
    return Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    source_path, candidate_path = HERE / 'manifest.json', HERE / 'candidate-manifest.json'
    source, candidate = json.loads(source_path.read_bytes()), json.loads(candidate_path.read_bytes())
    src = {item['nativePath']: item for item in source['resources']}
    rows = {item['nativePath']: item for item in candidate['items']}
    require(len(src) == len(rows) == 112 and src.keys() == rows.keys(), '112 source/candidate paths differ')
    require(not set(rows).intersection(source['excludedExistingPaths']), 'Existing20 controls overlap')
    package_path = ROOT / source['sourcePackage']['file']
    require(record(package_path) == source['sourcePackage'], 'Pinned package changed')
    for ref in candidate['referenceContracts'] + candidate['paintInputs'] + candidate['structuralAlphaInputs']:
        require(sha((ROOT / ref['file']).read_bytes()) == ref['sha256'], 'Referenced input changed: ' + ref['file'])
    package = package_path.read_bytes()
    structural = redraw = actual_exact = positions = changed_alpha = 0
    multi_states, decoded_images, roster_ids = [], {}, []
    for native, item in rows.items():
        before, _ = CODEC.reader.unpack_resource(package, src[native]['packageEntry'])
        after = (ROOT / item['file']).read_bytes()
        require(sha(before) == src[native]['sourceSha256'], 'Source resource hash differs')
        require(sha(after) == item['sha256'] and before != after, 'Candidate absent/unchanged')
        bm, _ = CODEC.reader.inspect_dimg(before, metadata_only=True)
        am, _ = CODEC.reader.inspect_dimg(after, metadata_only=True)
        require(bm == src[native]['metadata'], 'Source metadata differs from captured contract')
        def geometry(value):
            return {key: ([{k: v for k, v in frame.items() if k != 'encodedPixelSha256'}
                           for frame in val] if key == 'frames' else val)
                    for key, val in value.items() if key != 'sha256'}
        require(geometry(bm) == geometry(am), 'Exact native header/frame geometry changed')
        masked_before, masked_after = bytearray(before), bytearray(after)
        images = []
        for frame, stored in zip((f for f in am['frames'] if not f['empty']), item['frames'], strict=True):
            index, start, length = frame['index'], frame['pixelDataOffset'], frame['pixelByteLength']
            masked_before[start:start + length] = bytes(length)
            masked_after[start:start + length] = bytes(length)
            original, picture = decoded(before, frame), decoded(after, frame)
            require(sha(picture.tobytes()) == stored['decodedRgbaSha256'], 'Decoded native pixels differ')
            require(CODEC.encode_pixels(picture, frame['pixelMode']) == after[start:start + length], 'Encode/decode replay differs')
            with Image.open(ROOT / stored['file']) as png:
                require(png.mode == 'RGBA' and png.size == picture.size and png.tobytes() == picture.tobytes(), 'Native decoded PNG differs')
            with Image.open(ROOT / src[native]['frames'][index]['file']) as png:
                require(png.tobytes() == original.tobytes(), 'Source reference PNG differs')
            difference = ImageChops.difference(original.getchannel('A'), picture.getchannel('A'))
            box = difference.getbbox()
            require((list(box) if box else None) == stored['changedAlphaBBoxXYXY'], 'Alpha ROI evidence differs')
            require(sum(v != 0 for v in difference.tobytes()) == stored['changedAlphaPixelCount'], 'Alpha changed count differs')
            if stored['alphaPolicy'] == 'source':
                require(box is None, 'Structural source alpha differs')
                structural += 1
            else:
                require(stored['alphaRedrawRoiXYXY'] == [0, 0, frame['width'], frame['height']] and stored['alphaRedrawReason'], 'Cosmetic alpha exception missing bounds/reason')
                redraw += 1
            actual_exact += box is None
            changed_alpha += stored['changedAlphaPixelCount']
            require(picture.getchannel('A').getextrema()[1] >= 8, 'Invisible candidate frame')
            positions += 1
            images.append(picture)
        require(masked_before == masked_after, 'Nonpixel native bytes changed')
        decoded_images[native] = images
        if len(images) > 1:
            # Original cropped slots can differ in dimensions/offsets. This QA
            # counts actual bitmap distinctions without renaming engine states.
            distinct = len({(p.size, sha(p.tobytes())) for p in images})
            require(distinct == len(images), 'A source multi-position family collapsed into duplicate images: ' + native)
            multi_states.append({'nativePath': native, 'positions': len(images), 'distinctDecodedBitmaps': distinct})
        if item['family'] == 'character-banner':
            allocation = item['verifiedProjectRoleAllocation']
            roster_ids.append(allocation['sourceRoleId'])
            require(item['ownPortraitDerivative']['cropXYXY'] == [0, 72, 256, 216], 'Own portrait derivative evidence changed')
    require((positions, structural, redraw) == (168, 98, 70), 'Native positions/alpha counts differ')
    require(len(roster_ids) == len(set(roster_ids)) == 18, 'Confirmed18 distinct character allocations differ')
    digits = [decoded_images[f'object/ui/shop/wareAttr/{n}.img'][0] for n in range(10)]
    require(len({(p.size, sha(p.tobytes())) for p in digits}) == 10, 'Ten separate digit symbols collapsed')
    radio = decoded_images['object/ui/shop/secrecyValidate/btn_ratio.img']
    require(radio[0].getpixel((7, 7))[:3] != radio[2].getpixel((7, 7))[:3], 'Hollow and filled radio center collapsed')
    require(len(candidate['previews']) == len(source['sourceBoards']) == 14, 'All-state board pagination differs')
    for ref in candidate['previews'] + source['sourceBoards']:
        require(record(ROOT / ref['file']) == {key: ref[key] for key in ('file', 'sha256')}, 'All-state preview changed')
    output = {
        'schemaVersion': 1, 'scope': 'All112 shop-extra native images and168 source positions; excludes existing20 controls',
        'source': record(source_path), 'candidate': record(candidate_path), 'verifier': record(Path(__file__)),
        'nativeResourceCount': len(rows), 'nativeFramePositions': positions,
        'allNativeMetadataAndNonpixelBytesEqual': True, 'nativeDecodedPngAndReencodeReplayEqual': True,
        'exactStructuralAlphaPositions': structural, 'cosmeticAlphaRedrawPolicyPositions': redraw,
        'actualExactAlphaPositions': actual_exact, 'changedAlphaPixelCount': changed_alpha,
        'confirmedDistinctCharacterAllocations': len(roster_ids), 'distinctNumericSymbols': 10,
        'multiPositionFamilies': multi_states, 'hollowFilledRadioRgbDistinctionPreserved': True,
        'sourceAllStatePages': 14, 'candidateLightDarkAllStatePages': 14,
        'staticImagesActuallyViewedByAgent': True,
        'staticReviewMethod': 'view_image of14 source boards,14 decoded candidate boards, own18 portrait board/grid and source alpha diagnostics; changed banner/radio pages re-viewed after correction',
        'sourceTimingVerified': False, 'nativeRuntimeVerified': False, 'visualAccepted': False,
        'installedToClient': False, 'nativeProgramExecuted': False, 'providedDirectoryWritten': False,
        'limitations': ['Static raster review is not user visual acceptance or a runtime screenshot',
                        'Four unmatched literal/template paths retain unknown live binding',
                        'Live text widths, callbacks, animation speed, payment execution and tooltip placement remain unverified']}
    encoded = (json.dumps(output, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = HERE / 'qa-result.json'
    if check:
        require(path.read_bytes() == encoded, 'QA proof replay differs')
    else:
        path.write_bytes(encoded)
    print(json.dumps({'resources': len(rows), 'positions': positions, 'structuralAlpha': structural,
                      'cosmeticRedraws': redraw, 'independentNativeReplay': True, 'readOnlyCheck': check}))


if __name__ == '__main__':
    main()
