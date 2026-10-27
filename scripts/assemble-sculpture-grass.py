"""Reuse original painted grass via explicit image assembly, never new AI art."""
from pathlib import Path
from PIL import Image
import hashlib,json

root=Path(__file__).resolve().parents[1]
folder=root/'assets/maps/sculpture'
source=root/'assets/maps/bomb/pieces/7001-turf-light.png'
source_record=json.loads(source.with_suffix('.png.provenance.json').read_text(encoding='utf-8'))
image=Image.open(source).convert('RGBA')
if image.size!=(160,160):raise ValueError('Expected retained 40-logical-pixel painted grass tile at density4')
inventory=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))
elements={entry['elementId']:entry for entry in inventory['elements']}
art=json.loads((folder/'art.json').read_text(encoding='utf-8'))
ids=[12001,12005,12022]
art['pieces']=[p for p in art['pieces']if p['elementId']not in ids]
for ident in ids:
    entry=elements[ident];fw,fh=entry['selectedFrameSize']
    if fw%40 or fh%40:raise ValueError('Cannot tile a partial source cell')
    final=Image.new('RGBA',(fw*4,fh*4))
    for y in range(0,fh*4,160):
        for x in range(0,fw*4,160):final.alpha_composite(image,(x,y))
    target=folder/'pieces'/f'{ident}-painted-grass.png';final.save(target)
    record={'elementId':ident,'file':target.relative_to(root).as_posix(),
        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':final.width,'height':final.height,
        'worldFrameWidth':fw,'worldFrameHeight':fh,'exportDensity':4,
        'sourceFootprintCells':entry['footprintCells'],'sourceMapElemOffset':entry['mapElemOffsetRaw'],
        'derivedFrom':{'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'generationRecord':source_record['derivedFrom']['generationRecord'],'sourceRecord':source.relative_to(root).as_posix()+'.provenance.json'},
        'operation':{'type':'reuse-and-tile-original-painted-image','newModelGeneration':False,'resampled':False,
            'tilePixels':[160,160],'tileCount':[fw//40,fh//40],'referencePixelColoursReused':False,'paintedSourcePixelColoursReused':True,
            'referenceAdvertisementNotReproduced':ident==12022},
        'alphaExtrema':list(final.getchannel('A').getextrema()),'geometryAccepted':False,'accepted':False,
        'status':'painted-texture-reuse-candidate-awaiting-theme-seam-and-in-game-validation','seamlessVerified':False}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    art['pieces'].append(record)
(folder/'art.json').write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'family':'sculpture','pieces':len(art['pieces']),'newModelGeneration':False}))
