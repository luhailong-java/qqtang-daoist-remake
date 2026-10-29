"""Review only one explicitly selected1–6 PNG export batch; no whole-category scan."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
key=sys.argv[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'))
spec=read(OUT/f'exports/world-{key}.json');assert 1<=len(spec['frames'])<=6
world=read(OUT/'world-art.json');records=[]
for source in spec['frames']:
    item=next(x for x in world['items']if x['itemId']==source['itemId'])
    record=next(x for x in item['frames']if x['sourceFrameIndex']==source['sourceFrameIndex'])
    records.append(record)
cell_w=max(r['width']for r in records)+16;cell_h=max(r['height']for r in records)+16
board=Image.new('RGBA',(cell_w*3,cell_h*2),(80,90,100,255));observations=[]
for n,r in enumerate(records):
    path=ROOT/r['file'];image=Image.open(path).convert('RGBA')
    assert image.size==tuple(q*4 for q in r['logicalFrameSize'])
    assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
    board.alpha_composite(image,(n%3*cell_w+8,n//3*cell_h+8))
    op=r['operation'];box=op['generatedContentBBoxAt16'];rect=op['sourceCellRectLTRB']
    edge_touch=box[0]==0 or box[1]==0 or box[2]==rect[2]-rect[0]or box[3]==rect[3]-rect[1]
    observations.append({'sourceFrameIndex':r['sourceFrameIndex'],'file':r['file'],'sha256':r['sha256'],
                         'actualExportSize':list(image.size),'logicalFrameSize':r['logicalFrameSize'],'exportDensity':4,
                         'frameOffsetRaw':r['frameOffsetRaw'],'aspectDeviation':r['qa']['relativeAspectDeviation'],
                         'sourceMotherBBoxTouchesCell':edge_touch,'alphaExtrema':list(image.getchannel('A').getextrema()),
                         'accepted':False})
destination=OUT/f'exports/{key}-gray-composite-inspection.png';board.convert('RGB').save(destination)
record={'scope':'selected1–6 currently exported PNGs only, not full QA','operation':'normal-size alpha composite onto neutral gray for inspection only; no new generated art',
        'derivedFrom':observations,'preview':destination.relative_to(ROOT).as_posix(),'newModelGeneration':False,'accepted':False,'runtimeAdopted':False}
Path(str(destination)+'.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/f'exports/{key}-export-observations.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'batch':key,'frames':observations,'preview':destination.relative_to(ROOT).as_posix()}))
