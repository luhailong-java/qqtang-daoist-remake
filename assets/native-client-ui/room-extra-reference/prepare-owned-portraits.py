"""Re-export existing approved portrait ROIs at512px, without model calls."""
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    mapping_path = HERE / 'roster-mapping-audit.json'
    mapping = json.loads(mapping_path.read_bytes())
    manifest_path = ROOT / mapping['projectPortraitManifest']['file']
    portraits = {p['sourceRoleId']: p for p in json.loads(manifest_path.read_bytes())['entries']}
    items = []
    for role in mapping['entries']+mapping['pveAdditionalEntries']:
        source = portraits[role['sourceRoleId']]
        master_path = ROOT / source['sourceMaster']
        if record(master_path)['sha256'] != source['sourceMasterSha256']:
            raise ValueError('Original own master changed')
        with Image.open(master_path) as opened:
            master = opened.convert('RGBA')
        box = source['sourceCropLTRB']
        extent = tuple(v*2 for v in source['resampledCropSize'])
        placement = tuple(v*2 for v in source['placementXY'])
        crop = master.crop(box)
        if extent[0] > crop.width or extent[1] > crop.height:
            raise ValueError('Existing portrait ROI would be upscaled')
        scaled = crop.convert('RGBa').resize(extent, Image.Resampling.LANCZOS).convert('RGBA')
        out = Image.new('RGBA', (512, 512))
        out.alpha_composite(scaled, placement)
        path = HERE / 'own-busts' / f'{role["nativeAlias"]}-512.png'
        if check:
            with Image.open(path) as old:
                if old.convert('RGBA').tobytes() != out.tobytes():
                    raise ValueError('Own portrait ROI export changed')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            out.save(path)
        items.append({**record(path), 'sourceRoleId': role['sourceRoleId'], 'nativeAlias': role['nativeAlias'],
                      'identityId': role['identityId'], 'projectName': role['projectName'],
                      'sourceMaster': record(master_path), 'sourceMasterRecord': role['masterSourceRecord'],
                      'existingPortrait': role['portrait'], 'existingPortraitSourceRecord': role['portraitSourceRecord'],
                      'cropSourceBox': box, 'uniformScale': extent[0]/crop.width,
                      'resampledCropSize': list(extent), 'placementXY': list(placement), 'canvas': [512,512],
                      'operation': 'Existing portrait-approved ROI; direct premultiplied LANCZOS from own master, at twice existing portrait canvas scale',
                      'newModelGeneration': False, 'visualAccepted': False, 'nativeRuntimeVerified': False})
    result = {'schemaVersion': 1, 'scope': 'Twenty existing own identity portrait ROIs, directly derived at512px for native UI packing',
              'mappingContract': record(mapping_path), 'portraitManifest': record(manifest_path),
              'converter': record(Path(__file__).resolve()), 'items': items,
              'nativeBuildInvokesImageModel': False, 'newCharacters': 0, 'visualAccepted': False}
    target = HERE / 'owned-portrait-derivations.json'
    raw = (json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    if check:
        if target.read_bytes() != raw:
            raise ValueError('Own portrait derivative record changed')
    else:
        target.write_bytes(raw)
    print(json.dumps({'existingOwnPortraitRois':len(items),'canvas':512,'readOnlyReplay':check}))


if __name__ == '__main__':
    main()
