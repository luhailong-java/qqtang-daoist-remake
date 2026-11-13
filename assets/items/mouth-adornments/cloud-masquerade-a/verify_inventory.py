"""Verify the source and replay this six-item batch without writing files."""
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDS = [1230, 1232, 1233, 1234, 1306, 1307]


def data(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check_file(record):
    path = ROOT / record['file']
    if sha(path.read_bytes()) != record['sha256']:
        raise ValueError(f'SHA mismatch: {path}')
    return path


def verify():
    manifest = data(HERE / 'art.json')
    contract = data(HERE / 'source-contract.json')
    generated = data(HERE / 'masks-a-v1.png.generation.json')
    sources = contract['items']
    if manifest['category'] != 'mouth' or manifest['sourceCategoryTotal'] != 145:
        raise ValueError('Wrong inventory scope')
    if [e['itemId'] for e in sources] != IDS or [e['itemId'] for e in manifest['items']] != IDS:
        raise ValueError('Wrong source or destination ID order')
    if manifest['accepted'] or manifest['runtimeAdopted'] or manifest['visualAccepted']:
        raise ValueError('Unexpected approval')
    args = data(check_file(generated['exactSubmittedArgs']))
    prompt_file = check_file(generated['exactPromptUtf8'])
    if prompt_file.read_bytes() != args['input']['prompt'].encode():
        raise ValueError('Prompt differs from exact submitted arguments')
    if generated['actualModel'] is not None or generated['actualQuality'] is not None:
        raise ValueError('Unsupported claim of actual model or quality')
    if args['route'] != 'builtin' or args['input']['transparent_background'] is not True:
        raise ValueError('Wrong route or transparency request')
    for entry in generated['references']:
        check_file(entry)
    board_path = HERE / 'references/source-six-board.png'
    check_file(data(Path(str(board_path) + '.source.json')))
    archive_record = sources[0]['sourceArchive']
    archive_path = ROOT / archive_record['file']
    with archive_path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != archive_record['sha256']:
            raise ValueError('Fixed archive SHA mismatch')
    catalog_path = ROOT / sources[0]['catalog']
    catalog_bytes = catalog_path.read_bytes()
    if sha(catalog_bytes) != sources[0]['catalogSha256']:
        raise ValueError('Catalog SHA mismatch')
    inventory = [e for e in json.loads(catalog_bytes)['items'] if e['category'] == 'mouth']
    if len(inventory) != manifest['sourceCategoryTotal']:
        raise ValueError('Catalog total differs from manifest')
    catalog = {e['item_id']: e for e in inventory}
    reader_spec = importlib.util.spec_from_file_location('mouth_inventory_verify', ROOT / 'scripts/inspect-reference-dimg.py')
    reader = importlib.util.module_from_spec(reader_spec)
    reader_spec.loader.exec_module(reader)
    with ZipFile(archive_path) as archive, Image.open(check_file(generated)) as atlas:
        if atlas.mode != 'RGBA' or atlas.size != (1536, 1024):
            raise ValueError('Native atlas specification differs')
        alpha = atlas.getchannel('A')
        for samples in generated['eyeHoleSamples']:
            values = [alpha.getpixel(tuple(point)) for point in samples['samplesXY']]
            if values != samples['alpha'] or max(values) >= 8:
                raise ValueError('Atlas eye-hole alpha differs')
        for source, item in zip(sources, manifest['items'], strict=True):
            source_id = source['itemId']
            original = catalog[source_id]
            if original['resource_id'] != source['resourceId'] or source['catalogInstalledFile'] not in original['installed_files']:
                raise ValueError(f'{source_id}: inventory ID-to-member mapping differs')
            if source['sourceMember'] != 'QQTang-Local/runtime/client-patched/' + source['catalogInstalledFile']:
                raise ValueError(f'{source_id}: source member path differs')
            raw = archive.read(source['sourceMember'])
            if sha(raw) != source['sourceMemberSha256']:
                raise ValueError(f'{source_id}: source member SHA mismatch')
            metadata, _ = reader.inspect_dimg(raw, metadata_only=True)
            frame = next(entry for entry in metadata['frames'] if not entry['empty'])
            if frame != source['sourceFrameRecord'] or frame['frameOffset'] != item['sourceInventoryFrameOffsetRaw']:
                raise ValueError(f'{source_id}: source metadata differs')
            offset = frame['pixelDataOffset']
            pixels = reader.decode_frame_pixels(raw[offset:offset + frame['pixelByteLength']],
                                                frame['pixelMode'], frame['width'], frame['height'])
            with Image.open(check_file(source)) as source_png:
                if source_png.size != tuple(item['sourceInventoryNativeFrameSize']) or source_png.tobytes() != pixels:
                    raise ValueError(f'{source_id}: source PNG differs from decoded archive raster')
            op = item['operation']
            cell = atlas.crop(op['sourceCellRect'])
            mask = cell.getchannel('A')
            w, h = cell.size
            edge_max = [mask.crop(rect).getextrema()[1] for rect in ((0, 0, 1, h), (0, 0, w, 1), (w - 1, 0, w, h), (0, h - 1, w, h))]
            if edge_max != op['sourceCellEdgeAlphaMax'] or max(edge_max) >= 8:
                raise ValueError(f'{source_id}: alpha crosses crop boundary')
            bbox = mask.point(lambda value: 255 if value >= 16 else 0).getbbox()
            if list(bbox) != op['contentBoxWithinCell']:
                raise ValueError(f'{source_id}: content bounds differ')
            content = cell.crop(bbox)
            scale = 224 / max(content.size)
            if scale != op['uniformScale']:
                raise ValueError(f'{source_id}: scale differs')
            content = content.convert('RGBa').resize(tuple(round(v * scale) for v in content.size),
                                                      Image.Resampling.LANCZOS).convert('RGBA')
            expected = Image.new('RGBA', (256, 256))
            expected.alpha_composite(content, tuple(op['placementPx']))
            with Image.open(check_file(item)) as actual:
                if actual.mode != 'RGBA' or actual.size != (256, 256) or actual.tobytes() != expected.tobytes():
                    raise ValueError(f'{source_id}: PNG pixels differ from replay')
                output_alpha = actual.getchannel('A')
                box = output_alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
                if min(box[0], box[1], 256 - box[2], 256 - box[3]) < 16:
                    raise ValueError(f'{source_id}: visible output inset below 16 px')
            if item != data(ROOT / item['provenanceRecord']):
                raise ValueError(f'{source_id}: sidecar and manifest differ')
            if item['accepted'] or item['visualAccepted'] or item['runtimeAdopted'] or item['worldMapped']:
                raise ValueError(f'{source_id}: unsupported approval or world mapping')
    for entry in manifest['previews']:
        preview_path = check_file(entry)
        if entry != data(Path(str(preview_path) + '.source.json')):
            raise ValueError('Preview provenance differs')
    return {
        'schemaVersion': 1, 'itemIds': IDS, 'sourceCategoryCount': len(inventory),
        'checkedSourceMembers': len(sources), 'checkedExports': len(manifest['items']),
        'pixelReplayExact': True, 'checkedPreviews': len(manifest['previews']),
        'generationSha256': generated['sha256'], 'manifestSha256': sha((HERE / 'art.json').read_bytes()),
        'eyeHoleAlpha': [e['alpha'] for e in generated['eyeHoleSamples']],
        'maximumCropEdgeAlpha': max(max(e['operation']['sourceCellEdgeAlphaMax']) for e in manifest['items']),
        'minimumOutputAlpha8InsetPx': min(e['alpha8InsetPx'] for e in manifest['items']),
        'technicalFileChecksPassed': True, 'errors': [], 'visualAccepted': False,
        'runtimeAdopted': False, 'worldCandidatePositions': 0,
    }


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
