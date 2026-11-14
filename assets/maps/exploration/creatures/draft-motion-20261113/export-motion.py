"""Register and verify original pose candidates for two local draft creatures."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / 'package.json').is_file())
POSES = ('stand', 'step-left', 'step-right', 'windup', 'release', 'recoil')
POSE_NAMES = ('待机', '左脚着地', '右脚着地', '蓄势', '挥杖', '受击')
GROUPS = (
    ('sprout', '初芽团精', 30000, 0.47, (270, 246, 239, 267, 762 - 512, 252)),
    ('lingzhi', '灵芝盘翁', 30006, 0.44, (252, 249, 243, 260, 260, 258)),
)


def read(path):
    return json.loads(path.read_bytes())


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def check_record(data):
    if record(ROOT / data['file'])['sha256'] != data['sha256']:
        raise ValueError(f"Source changed: {data['file']}")


def save_json(path, data, verify):
    if verify:
        if read(path) != data:
            raise ValueError(f'Metadata replay differs: {path}')
    else:
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def save_image(path, image, verify):
    if verify:
        with Image.open(path) as previous:
            if previous.mode != image.mode or previous.size != image.size or previous.tobytes() != image.tobytes():
                raise ValueError(f'Pixel replay differs: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, optimize=True)


def alpha_box(image):
    return image.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()


def resize(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def read_generation(key):
    path = HERE / f'{key}-atlas.png.generation.json'
    data = read(path)
    for ref in (data, data['exactSubmittedArgs'], data['exactPromptUtf8'], data['returnedToolEvidence'], *data['references']):
        check_record(ref)
    args = read(ROOT / data['exactSubmittedArgs']['file'])
    if (not args['transparent_background'] or (ROOT / data['exactPromptUtf8']['file']).read_bytes() != args['prompt'].encode()
            or data['actualModel'] is not None or data['actualQuality'] is not None):
        raise ValueError(f'Generation record is incomplete: {key}')
    with Image.open(ROOT / data['file']) as image:
        if image.mode != 'RGBA' or image.size != (1536, 1024) or image.size != (data['width'], data['height']):
            raise ValueError(f'Unexpected atlas dimensions or mode: {key}')
        return image.copy(), data, record(path)


def pose_frame(key, index, name, scale, root_x, atlas_info, verify):
    atlas, generation, generation_record = atlas_info
    x, y = index % 3 * 512, index // 3 * 512
    cell_rect = (x, y, x + 512, y + 512)
    cell = atlas.crop(cell_rect)
    edge = max(cell.getchannel('A').crop(rect).getextrema()[1] for rect in
               [(0, 0, 1, 512), (0, 0, 512, 1), (511, 0, 512, 512), (0, 511, 512, 512)])
    box = alpha_box(cell)
    if box is None or edge >= 8 or min(box[0], box[1], 512 - box[2], 512 - box[3]) < 8:
        raise ValueError(f'Pose touches atlas boundary: {key} {name}')
    l, t, r, b = box
    if not l < root_x < r:
        raise ValueError(f'Horizontal reference outside pose: {key} {name}')
    width, height = round((r-l)*scale), round((b-t)*scale)
    bottom = 226 - (8 if key == 'sprout' and name == 'recoil' else 0)
    placement = (128 - round((root_x-l)*scale), bottom - height)
    if min(*placement, 256 - placement[0] - width, 256 - bottom) < 4:
        raise ValueError(f'Pose falls outside its review canvas: {key} {name}')
    out = Image.new('RGBA', (256, 256))
    out.alpha_composite(resize(cell.crop(box), (width, height)), placement)
    path = HERE / key / f'{name}.png'
    save_image(path, out, verify)
    provenance_path = path.with_suffix('.png.provenance.json')
    info = {
        **record(path), 'pose': name, 'projectDisplayName': POSE_NAMES[index],
        'width': 256, 'height': 256, 'alphaExtrema': list(out.getchannel('A').getextrema()),
        'alpha8BBox': list(alpha_box(out)),
        'derivedFrom': {k: generation[k] for k in ('file', 'sha256')}, 'generationRecord': generation_record,
        'provenanceRecord': provenance_path.relative_to(ROOT).as_posix(),
        'operation': {'sourceCellLTRB': list(cell_rect), 'alpha8BoxWithinCell': list(box), 'maximumEdgeAlpha': edge,
                      'uniformScale': scale, 'sourceRootXWithinCellForPreview': root_x, 'placementPx': list(placement),
                      'previewBaselineY': bottom, 'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False},
        'sourceFrameIndex': None, 'sourceTimingMs': None, 'nativeActorAnchor': None,
        'visualAccepted': False, 'runtimeAdopted': False,
    }
    save_json(provenance_path, info, verify)
    return info, out


def preview(key, frames, verify):
    sizes = [32, 48, 64, 128]
    col = 172
    board = Image.new('RGB', (col * len(POSES), 416), '#f6f0df')
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 208, board.width-1, 415), fill='#183e37')
    font = ImageFont.load_default(size=15)
    for index, (info, image) in enumerate(frames):
        x = col * index
        for shift, ink in [(0, '#214a3d'), (208, '#f4ead3')]:
            draw.text((x+18, shift+7), info['pose'], font=font, fill=ink)
            for size, left in zip(sizes, [10, 48, 102, 22], strict=True):
                rendered = resize(image, (size, size))
                y = shift + (26 + (64 - size)//2 if size < 128 else 78)
                board.paste(rendered, (x + left, y), rendered)
    path = HERE / f'{key}-contact.png'
    save_image(path, board, verify)
    return {**record(path), 'sizesPx': sizes, 'backgrounds': ['#f6f0df', '#183e37'],
            'newModelGeneration': False, 'runtimeScreenshot': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    verify = parser.parse_args().check
    atlas = {key: read_generation(key) for key in ('sprout', 'lingzhi', 'sprout_fix')}
    master_path = HERE.parent / 'art.json'
    masters = {e['entityId']: e for e in read(master_path)['masters']}
    entries = []
    for key, name, catalog_id, scale, roots in GROUPS:
        master = masters[catalog_id]
        check_record(master)
        frames = [pose_frame(key, i, pose, scale, roots[i], atlas['sprout_fix' if key == 'sprout' and pose == 'release' else key], verify)
                  for i, pose in enumerate(POSES)]
        if len({info['sha256'] for info, _ in frames}) != len(POSES):
            raise ValueError(f'Duplicate pose in {key}')
        entries.append({'id': key, 'projectDisplayName': name, 'artworkCatalogId': catalog_id,
                        'sourceEntityId': None, 'sourcePlaybackVerified': False, 'originalMaster': master['file'],
                        'frames': [info for info, _ in frames], 'preview': preview(key, frames, verify),
                        'visualAccepted': False, 'runtimeAdopted': False})
    save_json(HERE / 'manifest.json', {'schemaVersion': 1, 'scope': 'local draft creature pose candidates',
                                     'catalog': record(master_path), 'entries': entries}, verify)
    print('12 distinct registered RGBA poses. Pixel replay: ' + str(verify))


if __name__ == '__main__':
    main()
