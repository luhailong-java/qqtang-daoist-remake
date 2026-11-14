"""Decode the remaining game HUD and replay controls as inert source data."""
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('game_source',ROOT/'assets/native-client-ui/core-reference/decode-references.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
reader.HERE = HERE
inventory = json.loads((ROOT/'references/qqtang-ui-data/native-ui-inventory.json').read_bytes())
reader.PATHS = tuple(r['canonicalPath'] for r in inventory['resources']
                     if r['storage'] == 'packed' and r['canonicalPath'].startswith('object/ui/game/')
                     and not r['canonicalPath'].endswith('/dlg_playerlist.img'))


def main():
    reader.main()
    path = HERE/'manifest.json'
    manifest = json.loads(path.read_bytes())
    manifest['selectionScript'] = reader.record(Path(__file__).resolve())
    boards = []
    for group in ('controls','surfaces'):
        rows = [r for r in manifest['resources'] if (r['metadata']['frameCount'] > 1) == (group == 'controls')]
        height = sum(max(55,max(f['nativeSize'][1] for f in r['frames']) * (2 if group=='controls' else 1)) + 45 for r in rows)
        board = Image.new('RGB',(1100,height),'#d8d5c8')
        draw = ImageDraw.Draw(board)
        top = 0
        for resource in rows:
            resource['pathLiteralOccurrences'] = [r for r in inventory['bindings'] if r['canonicalPath']==resource['nativePath']]
            draw.text((8,top+5),resource['nativePath'],fill='#183d30')
            scale = 2 if group == 'controls' else 1
            for column,frame in enumerate(resource['frames']):
                with Image.open(ROOT/frame['file']) as image:
                    image = image.resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST)
                    x = 8 + column*260
                    draw.text((x,top+20),str(frame['sourceFrameIndex']),fill='#183d30')
                    board.paste(image,(x,top+40),image)
            top += max(55,max(f['nativeSize'][1] for f in resource['frames'])*scale)+45
        target = HERE/f'source-{group}.png'
        board.save(target)
        boards.append(reader.record(target))
    manifest['previews'] = boards
    path.write_bytes((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'gameResources':len(manifest['resources']),
                      'sourcePositions':sum(len(r['frames']) for r in manifest['resources'])}))


if __name__ == '__main__':
    main()
