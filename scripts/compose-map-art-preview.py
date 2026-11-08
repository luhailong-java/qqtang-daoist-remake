"""Assemble existing painted images at the renderer's candidate coordinates.
This is an art-layout preview, never a browser or gameplay verification.
"""
from pathlib import Path
import json,sys,hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1]
ident=sys.argv[1] if len(sys.argv)>1 else 'source-201'
plan_path=root/'.artifacts'/f'map-art-plan-{ident}.json'
plan=json.loads(plan_path.read_text(encoding='utf-8'))
density=2
im=Image.new('RGBA',(plan['width']*density,plan['height']*density),(229,233,214,255))
for item in plan['commands']:
    piece=Image.open(root/item['file']).convert('RGBA')
    piece=piece.resize((item['width']*density,item['height']*density),Image.Resampling.LANCZOS)
    im.alpha_composite(piece,(item['x']*density,item['y']*density))
target=root/'assets/maps/previews'/f'{ident}-painted-candidate.png'
target.parent.mkdir(parents=True,exist_ok=True)
im.convert('RGB').save(target)
record={'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'operation':'existing-image-composition-at-candidate-renderer-offsets','newModelGeneration':False,
    'previewDensity':density,'logicalSize':[plan['width'],plan['height']],
    'mapSourceSha256':plan['sourceMapSha256'],'drawPlan':plan_path.relative_to(root).as_posix(),
    'missingElementIds':plan['missingElementIds'],'geometryAccepted':False,'inGameVerified':False,
    'note':'场景美术排布检查图；不是运行截图，不替代浏览器操作验收。'}
target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
