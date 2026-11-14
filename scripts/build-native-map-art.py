"""Export existing full-frame map candidates into their original packed DIMG resources.

This is a format conversion, not map lookup, timing, geometry or visual acceptance.
No package, installed client, UI resource or source art is modified.
"""
import argparse
from collections import Counter
import hashlib
from importlib import util
import io
import json
from pathlib import Path
import zlib
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'assets/native-client-maps/town-common-v1'
PLAN = ROOT / 'docs/native-map-conversion-plan-20261114.json'
ARCHIVE = ROOT / '.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
PREFIX = 'QQTang-Local/runtime/client-patched/'
spec = util.spec_from_file_location('native_map_codec', ROOT / 'scripts/native-ui-format.py')
codec = util.module_from_spec(spec)
spec.loader.exec_module(codec)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path, expected=None):
    result = {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}
    if expected is not None and result['sha256'] != expected:
        raise ValueError(f'Input hash changed: {path}')
    return result


def save_bytes(path, content, check):
    if check:
        if path.read_bytes() != content:
            raise ValueError(f'Native map byte replay differs: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def save_json(path, value, check):
    content = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    save_bytes(path, content, check)


def save_image(path, picture, check):
    # Compare the actual reproducible PNG bytes as well as its decoded RGBA pixels.
    stream = io.BytesIO()
    picture.save(stream, format='PNG', optimize=True)
    content = stream.getvalue()
    save_bytes(path, content, check)
    with Image.open(path) as actual:
        if (actual.mode, actual.size, actual.tobytes()) != (picture.mode, picture.size, picture.tobytes()):
            raise ValueError(f'Native map PNG pixels differ: {path}')


def alpha_stats(picture):
    alpha = picture.getchannel('A')
    histogram = alpha.histogram()
    bounds = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
    return {'extrema': list(alpha.getextrema()), 'alpha8BoundingBox': list(bounds) if bounds else None,
            'transparentPixelCount': histogram[0], 'fullyOpaquePixelCount': histogram[255],
            'totalPixels': picture.width * picture.height}


def evidence_files(value):
    """Hash recorded paint/alias evidence, following only declared provenance JSONs."""
    found, expanded = {}, set()
    expand_keys = {'generationRecord', 'generationRecords', 'provenanceRecord', 'provenance',
                   'sequenceManifest', 'sourceExportRecord', 'reusedFromCandidateSequence'}

    def add(filename, expected=None, expand=False):
        if not isinstance(filename, str) or not filename.startswith(('assets/', 'references/')):
            return
        filename = filename.split('#', 1)[0]
        path = ROOT / filename
        if not path.is_file():
            raise ValueError(f'Recorded paint evidence is missing: {filename}')
        record = ref(path, expected)
        previous = found.setdefault(filename, record)
        if previous != record:
            raise ValueError(f'Conflicting paint evidence: {filename}')
        if expand and path.suffix == '.json' and filename not in expanded:
            expanded.add(filename)
            visit(json.loads(path.read_bytes()))

    def visit(node, key=None):
        if isinstance(node, dict):
            if isinstance(node.get('file'), str):
                add(node['file'], node.get('sha256'), key in expand_keys)
            for name, child in node.items():
                if name != 'file':
                    visit(child, name)
        elif isinstance(node, list):
            for child in node:
                visit(child, key)
        elif isinstance(node, str) and key in expand_keys:
            add(node, expand=True)
        elif isinstance(node, str) and key in {'selectedNativeAtlas', 'sourceFrameEvidence', 'sourceFrameReference'}:
            add(node)

    visit(value)
    return [found[key] for key in sorted(found)]


def lineage(record):
    result = {'planCandidateLineage': record['candidateLineage']}
    if record['candidateRepresentation'] == 'complete-sequence-candidate':
        sequence_ref = record['candidateLineage']['sequenceManifest']
        path = ROOT / sequence_ref['file']
        ref(path, sequence_ref['sha256'])
        sequence = json.loads(path.read_bytes())
        if sequence['sourceRawSHA256'] != record['sourceSha256']:
            raise ValueError('Sequence source identity changed')
        if sequence['sourceFrameIndices'] != [f['sourceFrameIndex'] for f in record['sourceFrames']]:
            raise ValueError('Sequence no longer covers all source frame positions')
        result['sequenceManifestRecord'] = sequence
        result['sequenceFramesByIndex'] = {f['sourceFrameIndex']: f for f in sequence['frames']}
    else:
        proof_ref = record['candidateLineage']['provenance']
        path = ROOT / proof_ref['file']
        ref(path, proof_ref['sha256'])
        result['paintedFrameProvenance'] = json.loads(path.read_bytes())
    result['verifiedPaintEvidenceFiles'] = evidence_files(result)
    return result


def unchanged_nonpixel(original, output, frames):
    cursor = 0
    for frame in frames:
        if frame['empty']:
            continue
        start = frame['pixelDataOffset']
        if original[cursor:start] != output[cursor:start]:
            raise ValueError('A native map header, offset, mode or other nonpixel byte changed')
        cursor = start + frame['pixelByteLength']
    if len(original) != len(output) or original[cursor:] != output[cursor:]:
        raise ValueError('Native map container extent or suffix changed')


def convert(record, package, entries, check):
    path = record['nativePath']
    entry = entries[path.lower()]
    if entry != record['sourcePackageEntry']:
        raise ValueError(f'Packed source entry changed: {path}')
    original, compressed_sha = codec.reader.unpack_resource(package, entry)
    if (sha(original), compressed_sha) != (record['sourceSha256'], record['compressedSha256']):
        raise ValueError(f'Packed source identity changed: {path}')
    metadata, _ = codec.reader.inspect_dimg(original, metadata_only=True)
    if not metadata['strictDeclaredStructureAccepted'] or metadata['trailingByteLength']:
        raise ValueError(f'Native framing requires explicit additional handling: {path}')
    if (metadata['declaredCanvas'], metadata['frameCount'], metadata['directions'], metadata['version']) != (
            record['sourceDeclaredCanvas'], record['sourceDeclaredFrameCount'],
            record['sourceDirections'], record['sourceDimgVersion']):
        raise ValueError('Source map declaration changed')
    paint_lineage = lineage(record)
    checks = {f['sourceFrameIndex']: f['candidate'] for f in record['candidateFrameChecks']}
    source_frames = {f['sourceFrameIndex']: f for f in record['sourceFrames']}
    if set(checks) != {f['index'] for f in metadata['frames'] if not f['empty']}:
        raise ValueError('Missing or duplicate original map frame positions')
    pictures, frame_origins = {}, {}
    for native in metadata['frames']:
        index = native['index']
        source_frame = source_frames[index]
        if (source_frame['size'], source_frame['frameOffsetRaw'], source_frame['empty'], source_frame['pixelMode']) != (
                [native['width'], native['height']], native['frameOffset'], native['empty'], native['pixelMode']):
            raise ValueError('Source per-frame dimensions, offset, empty slot or pixel mode changed')
        if native['empty']:
            continue
        candidate = checks[index]
        candidate_ref = ref(ROOT / candidate['file'], candidate['sha256'])
        size = (native['width'], native['height'])
        expected = (size[0] * 4, size[1] * 4)
        declared = candidate['declaredMetadata']
        if candidate['exportDensity'] != 4 or declared.get('sourceFrameOffset', native['frameOffset']) != native['frameOffset']:
            raise ValueError('Candidate export density or registered raw offset changed')
        if declared.get('sourceMapElemOffset', record['mapElemOffsetRaw']) != record['mapElemOffsetRaw']:
            raise ValueError('Candidate map element offset changed')
        sequence_frame = paint_lineage.get('sequenceFramesByIndex', {}).get(index)
        if sequence_frame is not None:
            exported = sequence_frame['exports']['4']
            if (exported['file'], exported['sha256'], sequence_frame['sourceFrameSize'], sequence_frame['sourceFrameOffset']) != (
                    candidate['file'], candidate['sha256'], list(size), native['frameOffset']):
                raise ValueError('Sequence candidate mapping or original offset changed')
        with Image.open(ROOT / candidate['file']) as picture:
            if picture.mode != 'RGBA' or picture.size != expected or list(picture.size) != candidate['actualPixelSize']:
                raise ValueError('Candidate must retain its complete original registered density4 extent')
            if alpha_stats(picture) != candidate['alpha']:
                raise ValueError('Candidate alpha no longer matches the technical plan')
            # Never crop visible alpha or fit inventory artwork here. All placement is
            # already baked into the complete registered source-size density4 frame.
            replacement = picture.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
        if alpha_stats(replacement) != candidate['nativeDownsampleAlpha'] or sha(replacement.tobytes()) != candidate['nativeDownsampleRgbaSha256']:
            raise ValueError('Whole-frame native downsample differs from the technical rehearsal')
        pictures[index] = replacement
        frame_origins[index] = {
            'derivedFrom': candidate_ref, 'candidatePlanCheck': candidate,
            'candidateSequenceFrameRecord': sequence_frame,
            'operation': {'type': 'whole registered density4 map frame to native 1x',
                          'inputSize': list(expected), 'outputSize': list(size),
                          'uniformScale': 0.25, 'sourceRectLTRB': [0, 0, *expected],
                          'placementPx': [0, 0], 'resampler': 'premultiplied-alpha LANCZOS',
                          'alphaCropPerformed': False, 'inventoryFitPerformed': False, 'newModelGeneration': False}}
    output, _, decoded = codec.replace_frames(original, pictures)
    unchanged_nonpixel(original, output, metadata['frames'])
    rehearsal = record['nativeCodecRehearsal']
    if len(output) != rehearsal['candidateEncodedBytes'] or sha(output) != rehearsal['candidateEncodedSha256']:
        raise ValueError('Native encoded bytes differ from the technical rehearsal')
    compressed = zlib.compress(output)
    if zlib.decompress(compressed) != output:
        raise ValueError('Native replacement zlib round trip failed')
    patch = HERE / 'patch' / path
    save_bytes(patch, output, check)
    output_metadata, _ = codec.reader.inspect_dimg(output, metadata_only=True)
    output_frames = {f['index']: f for f in output_metadata['frames']}
    frames = []
    for native, picture in decoded:
        index = native['index']
        preview = HERE / 'decoded' / Path(path).with_suffix('') / f'frame-{index:03}.png'
        save_image(preview, picture, check)
        pixel_start = native['pixelDataOffset']
        roundtrip = codec.reader.decode_frame_pixels(output[pixel_start:pixel_start + native['pixelByteLength']],
                                                     native['pixelMode'], native['width'], native['height'])
        if roundtrip != picture.tobytes():
            raise ValueError('Encoded native map pixel replay differs')
        frames.append({**ref(preview), 'index': index, 'sourceFrameIndex': index, 'empty': False,
                       'width': native['width'], 'height': native['height'], 'pixelMode': native['pixelMode'],
                       'frameOffset': native['frameOffset'], 'sourceEncodedPixelSha256': native['encodedPixelSha256'],
                       'encodedPixelSha256': output_frames[index]['encodedPixelSha256'],
                       'decodedRgbaSha256': sha(picture.tobytes()), 'decodedAlpha': alpha_stats(picture),
                       'sourceFrameDurationMs': None, **frame_origins[index]})
    for native in metadata['frames']:
        if native['empty']:
            frames.append({'index': native['index'], 'sourceFrameIndex': native['index'], 'empty': True,
                           'width': native['width'], 'height': native['height'], 'pixelMode': native['pixelMode'],
                           'frameOffset': native['frameOffset'], 'sourceFrameDurationMs': None})
    frames.sort(key=lambda f: f['index'])
    eligible = not record['visualAlphaWarnings']
    native_alpha_matches = all(
        (source_frames[f['index']]['decodedAlpha']['extrema'] == [255, 255]) ==
        (f['decodedAlpha']['extrema'] == [255, 255]) and
        source_frames[f['index']]['decodedAlpha']['alpha8BoundingBox'] == f['decodedAlpha']['alpha8BoundingBox']
        for f in frames if not f['empty'])
    if eligible and not native_alpha_matches:
        raise ValueError('Default subset alpha class or envelope changed after native pixel quantization')
    source = {'nativePath': path, 'elementId': record['elementId'], 'sourceSha256': sha(original),
              'compressedSha256': compressed_sha, 'sourcePackageEntry': entry, 'sourcePacked': True,
              'sourceLoose': False, 'metadata': metadata, 'conversionPlanRecord': record,
              'candidateEvidence': {key: value for key, value in paint_lineage.items() if key != 'sequenceFramesByIndex'}}
    resource = {**ref(patch), 'nativePath': path, 'elementId': record['elementId'], 'family': record['family'],
                'sourceSha256': sha(original), 'sourceCompressedSha256': compressed_sha,
                'sourcePacked': True, 'sourceLoose': False, 'sourcePackageEntry': entry,
                'sourceDeclaredCanvas': metadata['declaredCanvas'], 'sourceFrameOrder': [f['index'] for f in frames],
                'frames': frames, 'candidateRepresentation': record['candidateRepresentation'],
                'candidateLineage': record['candidateLineage'],
                'verifiedPaintEvidenceFiles': paint_lineage['verifiedPaintEvidenceFiles'],
                'sourceIdenticalFramePairs': rehearsal['sourceIdenticalFramePairs'],
                'sourceMapElemOffsetRaw': record['mapElemOffsetRaw'], 'sourceFootprintCells': record['footprintCells'],
                'sourceGridAttr': record['gridAttr'], 'bindingStatus': record['bindingStatus'],
                'combinedRenderOriginKnown': False, 'combinedRenderOrigin': None, 'sourceFrameDurationMs': None,
                'nativeTimingVerified': False, 'nativeRuntimeVerified': False, 'visualAccepted': False,
                'geometryAccepted': False, 'accepted': False, 'technicalFormatVerified': True,
                'nonpixelSourceBytesPreserved': True, 'containerNormalization': None,
                'visualAlphaWarnings': record['visualAlphaWarnings'], 'defaultInstallEligible': eligible,
                'nativeDecodedAlphaClassAndEnvelopeMatchSource': native_alpha_matches,
                'defaultInstallEligibilityVerifiedAfterNativeEncoding': eligible and native_alpha_matches,
                'defaultInstallEligibilityIsVisualAcceptance': False,
                'nativeEncodedRoundTripVerified': True, 'packageCompressionRoundTripVerified': True}
    return source, resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Replay all encodings and verify existing outputs without writing')
    check = parser.parse_args().check
    plan = json.loads(PLAN.read_bytes())
    inputs = [ref(PLAN)]
    for expected in plan['inputs']:
        inputs.append(ref(ROOT / expected['file'], expected['sha256']))
    with ARCHIVE.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != plan['sourceArchiveSha256']:
            raise ValueError('Pinned reference archive changed')
    package_path = ROOT / '.artifacts/reference-inputs/object.pkg'
    index_path = ROOT / '.artifacts/reference-inputs/object.idx'
    package, index = package_path.read_bytes(), index_path.read_bytes()
    with zipfile.ZipFile(ARCHIVE) as archive:
        # Source bytes must be exactly the pinned, read-only client package pair.
        if archive.read(PREFIX + 'data/object.pkg') != package or archive.read(PREFIX + 'data/object.idx') != index:
            raise ValueError('Extracted packed sources differ from the pinned client archive')
    entries = {entry['path'].replace(chr(92), '/').lower(): entry
               for entry in codec.reader.parse_index(index, len(package))['entries']}
    passed = [r for r in plan['records'] if r['technicalPreflightPassed']]
    excluded = [r for r in plan['records'] if not r['technicalPreflightPassed']]
    if [r['elementId'] for r in passed] != plan['technicalConvertibleElementIds'] or len(passed) != 120:
        raise ValueError('Map conversion plan scope changed')
    if [r['elementId'] for r in excluded] != list(range(17024, 17030)):
        raise ValueError('Missing sequence exclusions changed')
    if len({r['nativePath'].lower() for r in passed}) != len(passed):
        raise ValueError('Duplicate native map destinations')
    sources, resources = [], []
    for record in passed:
        source, resource = convert(record, package, entries, check)
        sources.append(source)
        resources.append(resource)
    warnings = [r for r in resources if r['visualAlphaWarnings']]
    opaque_warning = [r for r in resources if any('source-opaque-candidate-transparency' in w for w in r['visualAlphaWarnings'])]
    envelope_warning = [r for r in resources if any('visible-alpha-envelope' in w for w in r['visualAlphaWarnings'])]
    defaults = [r for r in resources if r['defaultInstallEligible']]
    positions = sum(len(r['frames']) for r in resources)
    if (positions, len(opaque_warning), len(envelope_warning), len(defaults)) != (224, 13, 59, 52):
        raise ValueError('Frame count or source alpha/envelope warning partition changed')
    contract_path = HERE / 'source-contract.json'
    save_json(contract_path, {
        'schemaVersion': 1, 'scope': 'Exact original packed native map containers and painted candidate lineage',
        'sourceArchive': plan['sourceArchiveInput'], 'sourceArchiveIdentity': plan['sourceIdentity'],
        'sourceArchiveSha256': plan['sourceArchiveSha256'],
        'sourcePackage': ref(package_path), 'sourceIndex': ref(index_path), 'conversionPlan': ref(PLAN),
        'items': sources, 'excludedUnexportedPlanRecords': excluded,
        'sourceTimingVerified': False, 'nativeRuntimeVerified': False, 'visualAccepted': False,
        'providedClientReadOrMutated': False, 'sourceArchiveExecuted': False}, check)
    manifest = {
        'schemaVersion': 1, 'scope': 'Native town/common map candidate format export; no installation or formal acceptance',
        'sourceContract': ref(contract_path), 'inputManifestsAndSources': inputs, 'items': resources,
        'candidateDefinitionCount': len(plan['records']), 'convertedNativeResourceCount': len(resources),
        'convertedByFamily': dict(sorted(Counter(r['family'] for r in resources).items())),
        'singleFrameNativeResources': sum(len(r['frames']) == 1 for r in resources),
        'completeSequenceNativeResources': sum(len(r['frames']) > 1 for r in resources),
        'sourceFramePositions': positions, 'decodedNonemptyPositions': sum(not f['empty'] for r in resources for f in r['frames']),
        'defaultInstallElementIds': [r['elementId'] for r in defaults],
        'defaultInstallNativePaths': [r['nativePath'] for r in defaults],
        'defaultInstallResourceCount': len(defaults),
        'defaultInstallEligibilityVerifiedAfterNativeEncoding': True,
        'defaultInstallSourceFramePositions': sum(len(r['frames']) for r in defaults),
        'defaultInstallPolicy': 'Only items with defaultInstallEligible=true: source/candidate alpha class and alpha>=8 envelope match the plan. This is not visual, geometry, lookup, timing or runtime acceptance. Other exports require explicit review before inclusion.',
        'visualAlphaWarningResourceCount': len(warnings),
        'sourceOpaqueCandidateTransparentWarningResourceCount': len(opaque_warning),
        'sourceVisibleAlphaEnvelopeWarningResourceCount': len(envelope_warning),
        'visualAlphaWarningResources': [{'elementId': r['elementId'], 'nativePath': r['nativePath'],
                                        'warnings': r['visualAlphaWarnings']} for r in warnings],
        'excludedUnexportedElementIds': [r['elementId'] for r in excluded],
        'excludedUnexportedResources': [{'elementId': r['elementId'], 'nativePath': r['nativePath'],
                                       'sourceSha256': r['sourceSha256'], 'technicalFailures': r['technicalFailures']} for r in excluded],
        'exportDensity': 1, 'sourceCandidateDensity': 4, 'newModelGeneration': False,
        'converterSources': [ref(Path(__file__).resolve()), ref(ROOT / 'scripts/native-ui-format.py'),
                             ref(ROOT / 'scripts/inspect-reference-dimg.py')],
        'nativeFrameStructurePreserved': True, 'nonpixelSourceBytesPreserved': True,
        'alphaCropPerformed': False, 'inventoryFitPerformed': False, 'formalAcceptanceIsNotAFormatGate': True,
        'allConvertedResourcesPacked': True, 'sourceTimingVerified': False, 'nativeRuntimeVerified': False,
        'sourceFrameDurationMs': None, 'combinedRenderOrigin': None, 'geometryAccepted': False,
        'visualAccepted': False, 'accepted': False, 'installedToClient': False,
        'nativeFilesWritten': True, 'providedClientMutated': False, 'existingUiPackageMutated': False,
        'packageIntegrationBoundary': plan['packageIntegrationBoundary'], 'allMapArtComplete': False}
    save_json(HERE / 'manifest.json', manifest, check)
    print(json.dumps({'nativeResources': len(resources), 'sourcePositions': positions,
                      'defaultInstallResources': len(defaults), 'defaultInstallPositions': manifest['defaultInstallSourceFramePositions'],
                      'sourceOpaqueWarnings': len(opaque_warning), 'visibleEnvelopeWarnings': len(envelope_warning),
                      'nativeStructureAndPixelsVerified': True, 'pixelReplay': check, 'installed': False}))


if __name__ == '__main__':
    main()
