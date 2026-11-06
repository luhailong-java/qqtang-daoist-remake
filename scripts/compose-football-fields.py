"""New painted turf/chalk; source pixels supply only white-line geometry masks."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
root=Path(__file__).resolve().parents[1];folder=root/'assets/maps/bomb';source=folder/'props-a-v1.png'
atlas=Image.open(source).convert('RGBA');ui=root/'assets/ui/controls/input-normal.png';paper=Image.open(ui).convert('RGBA')
light=atlas.crop((90,90,430,430)).convert('RGBa').resize((160,160),Image.Resampling.LANCZOS).convert('RGBA');light.putalpha(255)
dark=atlas.crop((595,90,935,430)).convert('RGBa').resize((160,160),Image.Resampling.LANCZOS).convert('RGBA');dark.putalpha(255)
chalk=paper.crop((70,45,225,85)).resize((155,40),Image.Resampling.LANCZOS);chalk.putalpha(255)
inventory=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'));by_id={p['elementId']:p for p in inventory['elements']}
art=json.loads((folder/'art.json').read_text(encoding='utf-8'));art['pieces']=[p for p in art['pieces'] if p['elementId']not in [7012,7013,7014]]
for ident in [7012,7013,7014]:
    ref=root/by_id[ident]['referencePng']['file'];pixels=np.array(Image.open(ref).convert('RGB')).astype(float);r,g,b=pixels[:,:,0],pixels[:,:,1],pixels[:,:,2]
    lines=(r>170)&(g>170)&(b>150)&(abs(r-g)<40)&(abs(b-g)<65)
    if ident==7014:lines[432:505,320:515]=False # Source advertisement; field lines lie outside this measured region.
    mask=Image.fromarray((lines*255).astype(np.uint8),'L').resize((2400,2080),Image.Resampling.NEAREST)
    grass=Image.new('RGBA',(2400,2080));ivory=Image.new('RGBA',grass.size)
    for y in range(0,2080,160):
        for x in range(0,2400,160):grass.alpha_composite(light if (x//160)%2==0 else dark,(x,y))
    for y in range(0,2080,40):
        for x in range(0,2400,155):ivory.alpha_composite(chalk,(x,y))
    final=Image.composite(ivory,grass,mask)
    target=folder/'pieces'/f'{ident}-football-field.png';final.save(target)
    origins=[{'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'generationRecord':source.relative_to(root).as_posix()+'.generation.json','purpose':'new painted grass RGB'},
        {'file':ui.relative_to(root).as_posix(),'sha256':hashlib.sha256(ui.read_bytes()).hexdigest(),'generationRecord':'assets/ui/qdao-ui-controls-v3.png.generation.json','purpose':'new painted ivory line texture RGB'},
        {'file':ref.relative_to(root).as_posix(),'sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'purpose':'source field-line mask geometry only, no RGB copied'}]
    record={'elementId':ident,'idMapping':'candidate-filename-inference','file':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'width':2400,'height':2080,'worldFrameWidth':600,'worldFrameHeight':520,'exportDensity':4,'derivedFrom':origins,
        'operation':{'type':'AI-image-textures-composited-through-reference-line-mask','newModelGeneration':False,'resampled':True,'sourcePixelColoursReused':False,
            'logicalMaskSize':[600,520],'logicalMaskSha256':hashlib.sha256((lines*255).astype(np.uint8).tobytes()).hexdigest(),
            'lineClassifier':'R>170,G>170,B>150,abs(R-G)<40,abs(B-G)<65','linePixelCount':int(lines.sum()),
            'grassStripeWidthLogicalPixels':40,'grassStripesStatus':'visual candidate, exact source colour segmentation not asserted',
            'sourceAdvertisementRegionExcluded':[320,432,515,505] if ident==7014 else None},
        'alphaExtrema':list(final.getchannel('A').getextrema()),'geometryAccepted':False,'seamlessVerified':False,
        'status':'painted-field-composite-candidate-awaiting-mask-and-in-game-validation',
        'warnings':['line-classification-and-turf-joins-await-visual-validation']+(['source-advertisement-removed-from-surface-paint-not-map-geometry']if ident==7014 else [])}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');art['pieces'].append(record)
(folder/'art.json').write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'bombPieces':len(art['pieces']),'sourceRgbCopied':False,'geometryAccepted':False}))
