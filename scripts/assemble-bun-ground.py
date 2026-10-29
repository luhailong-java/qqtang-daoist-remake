"""Reuse newly painted moss ground; reference advertisement RGB is not exported."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[1];folder=root/'assets/maps/bun'
inventory=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'));elements={p['elementId']:p for p in inventory['elements']}
art=json.loads((folder/'art.json').read_text(encoding='utf-8'));tile_entry=next(p for p in art['pieces']if p['elementId']==8011)
source=root/tile_entry['file'];tile=Image.open(source).convert('RGBA')
if tile.size!=(160,160)or tile.getchannel('A').getextrema()!=(255,255):raise ValueError('Requires verified opaque 160-square own ground')
ids=[8013,8024,8025,8026,8027,8028];art['pieces']=[p for p in art['pieces']if p['elementId']not in ids]
for ident in ids:
    entry=elements[ident];fw,fh=entry['selectedFrameSize'];out=Image.new('RGBA',(fw*4,fh*4))
    for y in range(0,out.height,160):
        for x in range(0,out.width,160):out.alpha_composite(tile,(x,y))
    target=folder/'pieces'/f'{ident}-moss-ground.png';out.save(target)
    record={'elementId':ident,'file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'width':out.width,'height':out.height,'worldFrameWidth':fw,'worldFrameHeight':fh,'exportDensity':4,
        'sourceFootprintCells':entry['footprintCells'],'sourceMapElemOffset':entry['mapElemOffsetRaw'],
        'derivedFrom':{'file':source.relative_to(root).as_posix(),'sha256':tile_entry['sha256'],'generationRecord':tile_entry['derivedFrom']['generationRecord'],'sourceRecord':source.relative_to(root).as_posix()+'.provenance.json'},
        'operation':{'type':'reuse-and-tile-original-painted-ground','newModelGeneration':False,'resampled':False,
            'referenceAdvertisementNotReproduced':ident!=8013,'referencePixelColoursReused':False,'paintedSourcePixelColoursReused':True,
            'tileCount':[fw//40,fh//40],'sourceGeometryChanged':False},'alphaExtrema':[255,255],
        'geometryAccepted':False,'accepted':False,'seamlessVerified':False,'status':'painted-ground-composite-awaiting-in-game-validation'}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');art['pieces'].append(record)
(folder/'art.json').write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'family':'bun','pieces':len(art['pieces']),'sourceRgbCopied':False,'accepted':False}))
