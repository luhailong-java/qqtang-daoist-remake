"""Refresh current map candidates from pinned721+52 source data. Never write source PNGs."""
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'references/qqtang-map-data/visual-reference/families/index.json'
EXTRA = ROOT / 'references/qqtang-map-data/visual-reference/binary-supplement/art-reference-index.json'
OUTPUT = ROOT / 'assets/maps/production-index.json'

def read(path):
    return json.loads(path.read_bytes())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def write(path, doc):
    old = path.read_bytes() if path.exists() else b''
    text = json.dumps(doc, ensure_ascii=False, indent=2) + '\n'
    if old.count(b'\r\n') == old.count(b'\n') and b'\n' in old:
        text = text.replace('\n', '\r\n')
    path.write_bytes(text.encode('utf-8'))

def source_visible(image):
    bbox = image.getchannel('A').getbbox()
    if not bbox:
        raise ValueError('Supplement reference is empty')
    crop = image.crop(bbox)
    pixels = bytearray(crop.tobytes())
    for pos in range(0, len(pixels), 4):
        if pixels[pos + 3] == 0:
            pixels[pos:pos + 3] = b'\0\0\0'
    return sha(struct.pack('<2I', crop.width, crop.height) + pixels), list(bbox)

def refresh(check=False):
    legacy, extra = read(BASE), read(EXTRA)
    binary_path = ROOT / 'references/qqtang-map-data/binary-properties-inspection.json'
    binary = read(binary_path)
    if len(legacy['elements']) != 721 or binary['sharedPythonDefinitionCount'] != 721 or binary['fieldDifferenceCount']:
        raise ValueError('Pinned721 shared-field comparison differs')
    if len(extra['elements']) != 52 or {e['elementId'] for e in extra['elements']} != set(binary['additionalIds']):
        raise ValueError('Explicit52 supplemental references differ')
    manifest_paths = sorted((ROOT / 'assets/maps').glob('*/art.json'))
    map_paths = sorted((ROOT / 'references/qqtang-map-data/maps').glob('*.json'))
    correction_path = ROOT / 'docs/map-art-evidence-20261112/source-metadata-corrections.json'
    fixed_inputs = [BASE, EXTRA, binary_path, ROOT / 'references/qqtang-map-data/elements.json', ROOT / 'assets/maps/source-elements-supplement.json', correction_path]
    metadata_paths = set()
    for mp in manifest_paths:
        for piece in read(mp)['pieces']:
            for candidate in (piece.get('provenanceRecord'), piece['file'] + '.provenance.json', piece['file'] + '.source.json'):
                if candidate and (ROOT / candidate).is_file():
                    metadata_paths.add(ROOT / candidate)
                    break
            origins = piece['derivedFrom'] if isinstance(piece['derivedFrom'], list) else [piece['derivedFrom']]
            metadata_paths.update(ROOT / origin['generationRecord'] for origin in origins if origin.get('generationRecord'))
    inputs = [{'file': rel(p), 'sha256': sha(p.read_bytes())} for p in fixed_inputs + manifest_paths + map_paths + sorted(metadata_paths)]
    fingerprint = sha(json.dumps(inputs, separators=(',', ':')).encode('utf-8'))
    current = read(OUTPUT) if OUTPUT.exists() else {}
    # Stable, already-verified input SHAs reuse the current coverage snapshot.
    # PNG byte validation also remains in runtime loading and inventory tests.
    if current.get('inputFingerprint') == fingerprint:
        count = sum(len(read(mp)['pieces']) for mp in manifest_paths)
        if len(current['elements']) != 773 or current['summary']['paintedCandidateCount'] != count:
            raise ValueError('Current indexed quantities differ')
        print(json.dumps({'definitions': 773, 'candidates': count, 'unchanged': True, 'checkOnly': check, 'priorPngShaEvidenceReused': True}))
        return
    painted, manifest_inputs = {}, []
    verified_candidates = {entry['elementId']: entry.get('runtimeOriginalArt') for entry in current.get('elements', [])}
    for mp in manifest_paths:
        manifest = read(mp)
        if manifest.get('tilePixels') != 40:
            raise ValueError('Map logical cell specification changed: ' + rel(mp))
        manifest_inputs.append({'file': rel(mp), 'sha256': sha(mp.read_bytes())})
        for piece in manifest['pieces']:
            ident = piece['elementId']
            if ident in painted:
                raise ValueError('Duplicate painted element: ' + str(ident))
            prior_paint = verified_candidates.get(ident)
            reusable_png = prior_paint and prior_paint['file'] == piece['file'] and prior_paint['sha256'] == piece['sha256']
            if not reusable_png and sha((ROOT / piece['file']).read_bytes()) != piece['sha256']:
                raise ValueError('Candidate PNG SHA differs: ' + piece['file'])
            origins = piece['derivedFrom'] if isinstance(piece['derivedFrom'], list) else [piece['derivedFrom']]
            for origin in origins:
                prior_origins = prior_paint.get('origins', []) if prior_paint else []
                reusable_origin = any(old.get('file') == origin.get('file') and old.get('sha256') == origin.get('sha256') for old in prior_origins)
                if not reusable_origin and origin.get('file') and origin.get('sha256') and sha((ROOT / origin['file']).read_bytes()) != origin['sha256']:
                    raise ValueError('Paint origin SHA differs: ' + origin['file'])
                if origin.get('generationRecord') and not (ROOT / origin['generationRecord']).is_file():
                    raise ValueError('Generation record missing')
            provenance = next((p for p in [piece.get('provenanceRecord'), piece['file'] + '.provenance.json', piece['file'] + '.source.json'] if p and (ROOT / p).is_file()), None)
            if not provenance:
                raise ValueError('Per-piece provenance missing')
            record = read(ROOT / provenance)
            if record.get('elementId') != ident or record.get('sha256') != piece['sha256']:
                raise ValueError('Per-piece provenance differs: ' + provenance)
            painted[ident] = (piece, provenance)
    if check:
        raise ValueError('Current773 coverage requires refresh')
    result = deepcopy(legacy)
    entries = {e['elementId']: e for e in result['elements']}
    groups = {g['visibleContentSha256']: g for g in result['visualGroups']}
    cached = {e['elementId']: e for e in current.get('elements', [])}
    usage, map_rows = defaultdict(list), []
    for mp in map_paths:
        source = read(mp)
        used = sorted({v for layer in source['layers'] for v in layer['values'] if v > 0})
        association = {'file': mp.stem + '.map', 'catalogIds': [e['id'] for e in source.get('catalogEntries', [])], 'families': sorted({e['family'] for e in source.get('catalogEntries', [])})}
        for ident in used:
            usage[ident].append(association)
        map_rows.append({'file': association['file'], 'sourceJson': rel(mp), 'sourceJsonSha256': sha(mp.read_bytes()), 'width': source['header']['width'], 'height': source['header']['height'], 'usedElementIds': used, 'catalogIds': association['catalogIds']})
    for src in extra['elements']:
        e, ident = deepcopy(src), src['elementId']
        if ident in entries:
            raise ValueError('Supplement overlaps721')
        png = e['referencePng']
        if sha((ROOT / png['file']).read_bytes()) != png['sha256']:
            raise ValueError('Source PNG SHA differs')
        prior = cached.get(ident)
        if prior and prior.get('referenceInputPng') == png:
            visible, bbox, rgba = prior['visibleContentSha256'], prior['visibleBoundingBox'], prior['decodedRgbaSha256']
        else:
            from PIL import Image
            image = Image.open(ROOT / png['file']).convert('RGBA')
            visible, bbox = source_visible(image)
            rgba = sha(image.tobytes())
        group = groups.get(visible)
        if group is None:
            group = {'id': 'visual-' + visible[:16], 'visibleContentSha256': visible, 'representativeElementId': ident, 'representativeFamily': e['family'], 'file': png['file'], 'sha256': png['sha256'], 'reusedExistingReference': False, 'nativeFrameSize': e['selectedFrameSize'], 'elementIds': [], 'families': [], 'referenceInventory': 'binary-supplement'}
            groups[visible] = group
        group['elementIds'].append(ident)
        if e['family'] not in group['families']:
            group['families'].append(e['family'])
        first = next(f for f in e['dimg']['frames'] if not f.get('empty'))
        e.update({'className': None, 'theme': '坦克场景' if e['family'] == 'tank' else '探险场景', 'referenceStatus': 'decoded-candidate', 'dimgSha256': e['dimg']['sha256'], 'dimgByteLength': e['dimg']['byteLength'], 'dimgVersion': e['dimg']['version'], 'dimgFrameCount': e['dimg']['frameCount'], 'dimgDirections': e['dimg']['directions'], 'declaredCanvasRaw': e['dimg']['declaredCanvas'], 'declaredCanvasWithinBound': e['dimg']['declaredCanvasWithinBound'], 'selectedFrame': first['index'], 'selectedFrameOffsetRaw': first['frameOffset'], 'decodedRgbaSha256': rgba, 'visibleContentSha256': visible, 'visibleBoundingBox': bbox, 'visualGroupId': group['id'], 'referenceInputPng': deepcopy(png), 'referencePng': {'file': group['file'], 'sha256': group['sha256'], 'representativeElementId': group['representativeElementId'], 'nativeFrameSize': group['nativeFrameSize'], 'sameNativeFrameExtent': group['nativeFrameSize'] == e['selectedFrameSize']}, 'anchorStatus': 'unverified-not-applied', 'newModelGeneration': False, 'geometryAccepted': False, 'referenceOnly': True, 'definitionSource': 'binary-property-supplement'})
        entries[ident] = e
    if len(entries) != 773 or set(painted) - set(entries):
        raise ValueError('Explicit773 definition set differs')
    for ident, entry in entries.items():
        entry.update({'usedByMaps': usage[ident], 'usedByMapCount': len(usage[ident]), 'geometryAccepted': False})
        pair = painted.get(ident)
        if not pair:
            entry.update({'runtimeOriginalArt': None, 'productionStatus': 'pending'})
            continue
        piece, provenance = pair
        if [piece['worldFrameWidth'], piece['worldFrameHeight']] != entry['selectedFrameSize']:
            raise ValueError('Native frame differs: ' + str(ident))
        for key in ('sourceMapElemOffset', 'sourceMapElemOffsetRaw', 'mapElemOffsetRaw'):
            if key in piece and piece[key] != entry['mapElemOffsetRaw']:
                raise ValueError('Target source offset cache differs: ' + str(ident))
        for key in ('sourceGridAttr', 'gridAttr'):
            if key in piece and piece[key] != entry['gridAttr']:
                raise ValueError('Target source GridAttr cache differs: ' + str(ident))
        origins = piece['derivedFrom'] if isinstance(piece['derivedFrom'], list) else [piece['derivedFrom']]
        generation = [o['generationRecord'] for o in origins if o.get('generationRecord')]
        entry.update({'productionStatus': 'painted-candidate-awaiting-validation', 'runtimeOriginalArt': {'file': piece['file'], 'sha256': piece['sha256'], 'generationRecord': generation[0], 'generationRecords': generation, 'origins': origins, 'provenanceRecord': provenance, 'provenanceSha256': sha((ROOT / provenance).read_bytes()), 'artManifest': f"assets/maps/{entry['family']}/art.json", 'status': piece['status'], 'geometryAccepted': False, 'accepted': False}})
    families, old_families = [], {f['family']: f for f in legacy['families']}
    for family in sorted({e['family'] for e in entries.values()}):
        rows = [e for e in entries.values() if e['family'] == family]
        f = deepcopy(old_families.get(family, {'family': family, 'theme': '坦克场景', 'mappingStatus': 'explicit-source-supplement-candidate', 'contactSheet': None}))
        made = sum(e.get('runtimeOriginalArt') is not None for e in rows)
        f.update({'elementCount': len(rows), 'candidateMatchedCount': len(rows), 'uniqueVisiblePictureCount': len({e['visibleContentSha256'] for e in rows}), 'uniqueDimgCount': len({e['dimgSha256'] for e in rows}), 'paintedCandidateCount': made, 'pendingCount': len(rows) - made, 'acceptedCount': 0, 'footprintCounts': dict(Counter('x'.join(map(str, e['footprintCells'])) for e in rows))})
        families.append(f)
    for row in map_rows:
        row['missingDefinitionIds'] = sorted(set(row['usedElementIds']) - set(entries))
        row['missingCandidateIds'] = sorted(set(row['usedElementIds']) - set(painted))
    result.update({'schemaVersion': 2, 'generatedOn': datetime.now(timezone.utc).date().isoformat(), 'capturedAtUtc': datetime.now(timezone.utc).isoformat(), 'purpose': 'current-773-definition-candidate-production-index-not-visual-acceptance', 'elements': sorted(entries.values(), key=lambda e: e['elementId']), 'families': families, 'visualGroups': list(groups.values()), 'originalArtManifestInputs': manifest_inputs, 'unknownSourceElementIds': [], 'previouslyUnknownSourceElementIds': legacy['unknownSourceElementIds'], 'legacyReferenceInventory': {'file': rel(BASE), 'sha256': sha(BASE.read_bytes()), 'elementCount': 721, 'unchanged': True}, 'binarySupplement': {'definitionCount': 52, 'referenceIndex': rel(EXTRA), 'referenceIndexSha256': sha(EXTRA.read_bytes()), 'sourcePropertiesSha256': binary['sourceSha256'], 'unserializedFieldsUnknown': ['canDoSpecial', 'canHide'], 'runtimeDefinitionSupplement': 'assets/maps/source-elements-supplement.json'}, 'sourceMetadataCorrectionReceipt': {'file': rel(correction_path), 'sha256': sha(correction_path.read_bytes()), 'fieldCorrections': 29, 'remainingKnownCacheDifferences': 0}, 'inputFingerprint': fingerprint, 'refreshInputs': inputs})
    result['summary'].update({'elementCount': 773, 'baselinePythonDefinitionCount': 721, 'additionalBinaryDefinitionCount': 52, 'familyCount': 19, 'decodedCandidateCount': 773, 'uniqueDimgCount': len({e['dimgSha256'] for e in entries.values()}), 'uniqueVisiblePictureCount': len(groups), 'savedReferencePngCount': len(groups), 'supplementReferencePngCount': 52, 'paintedCandidateCount': len(painted), 'pendingCount': 773 - len(painted), 'acceptedCount': 0, 'paintedCandidateCoveragePercent': round(len(painted) / 773 * 100, 2), 'acceptedCoveragePercent': 0, 'unknownSourceElementIdCount': 0, 'sourceMapFileCount': len(map_rows), 'sourceMapsWithAllReferencedDefinitions': sum(not m['missingDefinitionIds'] for m in map_rows), 'sourceMapsWithAllReferencedCandidateArt': sum(not m['missingCandidateIds'] for m in map_rows), 'sourceMetadataCacheCorrections': 29})
    result['limitations'] += ['Current773 candidate refresh leaves historical721 reference JSON/PNG unchanged. Additional flags stay null; no visual, timing, original-client or native-mechanism acceptance is implied.', 'Twenty-nine inherited metadata fields were restored from target source records; PNGs, source map coordinates and collision bytes were not changed.']
    registry_path = ROOT / 'assets/maps/runtime-manifests.json'
    registry = read(registry_path)
    registry.update({'manifests': [m['file'] for m in manifest_inputs], 'status': '773-painted-first-frame-candidates-awaiting-user-and-runtime-validation', 'elementCount': 773, 'definitionSupplement': 'assets/maps/source-elements-supplement.json'})
    scene = {'schemaVersion': 1, 'scope': 'all377 source map files, first-frame art coverage only; not rule/playability/original-client acceptance', 'sourceMapCount': len(map_rows), 'elementDefinitionCount': 773, 'maps': map_rows, 'mapsWithMissingDefinitions': sum(bool(m['missingDefinitionIds']) for m in map_rows), 'mapsWithMissingCandidateArt': sum(bool(m['missingCandidateIds']) for m in map_rows), 'accepted': False}
    write(OUTPUT, result)
    write(registry_path, registry)
    write(ROOT / 'assets/maps/scene-art-coverage.json', scene)
    print(json.dumps({'definitions': 773, 'candidates': len(painted), 'runtimeManifests': len(manifest_inputs), 'sourceMaps': len(map_rows), 'unchanged': False, 'sourceReferencePngsWritten': 0}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate input fingerprint/current coverage without writing')
    options = parser.parse_args()
    refresh(options.check)
