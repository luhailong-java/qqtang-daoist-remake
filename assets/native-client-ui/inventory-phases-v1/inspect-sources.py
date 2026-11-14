"""Read the five native multi-state inventory sources as inert image data."""
from pathlib import Path
from importlib import util
import json
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = util.spec_from_file_location('native_inventory_base', ROOT / 'scripts/build-native-inventory-art.py')
base = util.module_from_spec(spec)
spec.loader.exec_module(base)
IDS = (27061, 27073, 9011, 9012, 9013)


def main():
    with base.ARCHIVE.open('rb') as stream:
        if base.hashlib.file_digest(stream, 'sha256').hexdigest() != base.ARCHIVE_SHA:
            raise ValueError('Pinned archive changed')
    catalog = {i['item_id']: i for i in json.loads(base.CATALOG.read_bytes())['items']}
    own = {}
    own_manifests = []
    for name in ('skills', 'platform'):
        path = ROOT / f'assets/items/{name}/art.json'
        own_manifests.append(base.ref(path))
        own.update({i['itemId']: i for i in json.loads(path.read_bytes())['items'] if i['itemId'] in IDS})
    sheet = Image.new('RGB', (2800, len(IDS)*320), '#ebe5d3')
    draw = ImageDraw.Draw(sheet)
    items = []
    with zipfile.ZipFile(base.ARCHIVE) as archive:
        for row, item_id in enumerate(IDS):
            paths = [p for p in catalog[item_id]['installed_files'] if p.startswith('res/uiRes/icon/') and p.endswith('.img')]
            if len(paths) != 1:
                raise ValueError('No exact installed IMG for selected inventory item')
            path = paths[0]
            member = 'QQTang-Local/runtime/client-patched/' + path
            raw = archive.read(member)
            metadata, _ = base.codec.reader.inspect_dimg(raw, metadata_only=True)
            if metadata['trailingByteLength']:
                raise ValueError('Unexpected opaque trailing data')
            frames = []
            draw.text((10, row*320+8), f'{item_id} / {path}', fill='#264e40')
            item_board = Image.new('RGB', (1100, ((metadata['frameCount']+4)//5)*240), '#ebe5d3')
            item_draw = ImageDraw.Draw(item_board)
            for frame in metadata['frames']:
                if frame['empty']:
                    raise ValueError('Unexpected empty source phase')
                offset = frame['pixelDataOffset']
                pixels = base.codec.reader.decode_frame_pixels(raw[offset:offset+frame['pixelByteLength']],
                                                              frame['pixelMode'], frame['width'], frame['height'])
                image = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
                destination = HERE / 'source' / str(item_id) / f'{frame["index"]:02}.png'
                base.save_image(destination, image, False)
                canvas = Image.new('RGBA', tuple(metadata['declaredCanvas']))
                canvas.alpha_composite(image, tuple(frame['frameOffset']))
                cell = canvas.resize((canvas.width*4, canvas.height*4), Image.Resampling.NEAREST)
                col = frame['index']
                sheet.paste(cell, (10+col*280, row*320+35), cell)
                draw.text((10+col*280, row*320+300), f'f{col} {image.width}x{image.height} {frame["frameOffset"]}', fill='#264e40')
                enlarged = canvas.resize((canvas.width*3, canvas.height*3), Image.Resampling.NEAREST)
                item_board.paste(enlarged, (col%5*220+8, col//5*240+25), enlarged)
                item_draw.text((col%5*220+8, col//5*240+6), f'{item_id} source f{col}', fill='#264e40')
                frames.append({**base.ref(destination), 'index': col, 'decodedRgbaSha256': base.sha(pixels),
                               'nativeSize': list(image.size), 'frameOffset': frame['frameOffset'],
                               'pixelMode': frame['pixelMode'], 'alphaExtrema': list(image.getchannel('A').getextrema())})
            item_contact = HERE / 'source' / str(item_id) / 'all-phases.png'
            base.save_image(item_contact, item_board, False)
            item = own[item_id]
            if base.ref(ROOT/item['file'])['sha256'] != item['sha256']:
                raise ValueError('Own inventory candidate digest changed')
            items.append({'itemId': item_id, 'category': catalog[item_id]['category'],
                          'resourceId': catalog[item_id]['resource_id'], 'sourceName': catalog[item_id]['name'],
                          'nativePath': path, 'sourceArchiveMember': member, 'sourceSha256': base.sha(raw),
                          'metadata': metadata, 'frames': frames, 'sourceContact': base.ref(item_contact),
                          'ownCandidate': {**base.ref(ROOT/item['file']), 'projectDisplayName': item.get('projectDisplayName'),
                                           'sourceProvenanceRecord': base.ref((ROOT/item['file']).with_suffix('.png.provenance.json'))}})
    contact = HERE / 'source-all-phases.png'
    base.save_image(contact, sheet, False)
    contract = {'schemaVersion': 1, 'sourceArchiveSha256': base.ARCHIVE_SHA, 'catalog': base.ref(base.CATALOG),
                'ownCandidateManifests': own_manifests, 'sourceInspector': base.ref(Path(__file__).resolve()),
                'items': items, 'sourceContact': base.ref(contact), 'sourceFrameDurationMs': None,
                'sourceClientMutated': False, 'sourcePixelsForReferenceOnly': True}
    base.save_json(HERE / 'source-contract.json', contract, False)
    print(json.dumps({'items': len(items), 'sourcePositions': sum(len(i['frames']) for i in items)}))


if __name__ == '__main__':
    main()
