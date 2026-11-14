"""Decode explicitly selected room controls using the established native source reader."""
from pathlib import Path
import importlib.util
import json

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('room_source_reader', ROOT / 'assets/native-client-ui/core-reference/decode-references.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
reader.HERE = HERE
reader.PATHS = tuple('object/ui/room/' + name + '.img' for name in (
    'btn_selmode', 'btn_roomprop', 'btn_selmap', 'btn_ready', 'btn_start', 'btn_unready', 'btn_storage',
    'dlg_selmode', 'dlg_roomprop', 'dlg_selmap', 'btn_equipitem', 'btn_map', 'scl_block',
    'dlg_chatpanelsmall', 'dlg_chatpanelbig', 'tab_integration', 'tab_kin', 'tab_whisper',
))


def reference_boards(manifest):
    buttons = [r for r in manifest['resources'] if Path(r['nativePath']).stem.startswith('btn_') and r['metadata']['frameCount'] > 1]
    small = [r for r in manifest['resources'] if r not in buttons and not Path(r['nativePath']).stem.startswith('dlg_')]
    previews = []
    for items, name, stride in ((buttons, 'source-buttons.png', 175), (small, 'source-small-controls.png', 150)):
        board = Image.new('RGB', (1000, len(items) * stride + 15), '#d6d4cb')
        draw = ImageDraw.Draw(board)
        inputs = []
        for row, resource in enumerate(items):
            y = 12 + row * stride
            draw.text((10, y), resource['nativePath'], fill='#172a24')
            for index, frame in enumerate(resource['frames']):
                image = Image.open(ROOT / frame['file']).convert('RGBA')
                scale = 2 if image.width < 150 and image.height < 80 else 1
                image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
                x = 10 + index * 245
                draw.text((x, y + 20), str(index), fill='#172a24')
                board.paste(image, (x, y + 38), image)
                inputs.append({'file': frame['file'], 'sha256': frame['sha256'], 'nearestScale': scale})
        path = HERE / name
        board.save(path)
        previews.append({**reader.record(path), 'inputs': inputs})
    return previews


if __name__ == '__main__':
    reader.main()
    path = HERE / 'manifest.json'
    manifest = json.loads(path.read_bytes())
    inventory = json.loads((ROOT / 'references/qqtang-ui-data/native-ui-inventory.json').read_bytes())
    manifest['selectionScript'] = reader.record(Path(__file__).resolve())
    for resource in manifest['resources']:
        resource['pathLiteralOccurrences'] = [row for row in inventory['bindings']
            if row['canonicalPath'] == resource['nativePath']]
    manifest['previews'] = reference_boards(manifest)
    path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'manifest': reader.record(path), 'resources': len(manifest['resources']),
                      'frames': sum(len(r['frames']) for r in manifest['resources'])}))
