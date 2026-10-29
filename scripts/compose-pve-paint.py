"""Compose newly painted textures through source regions; no reference RGB exported.

Run for a bounded selected set of IDs. These are image composites, not new model
generations. The source alpha/region classification and texture joins require
visual review; no accepted flag is inferred from file production.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
import numpy as np

root=Path(__file__).resolve().parents[1];folder=root/'assets/maps/pve'
inventory=json.loads((root/'assets/maps/production-index.json').read_text(encoding='utf-8'))
elements={item['elementId']:item for item in inventory['elements']}
source=folder/'cliff-textures-v1.png';sheet=Image.open(source).convert('RGBA')
rects={'face':[75,65,475,465],'shadow':[570,65,970,465],'jade':[1055,65,1455,465],
       'floor':[75,550,475,950],'water':[570,550,970,950],'bank':[1055,550,1455,950]}
textures={};alpha_ranges={}
for name,rect in rects.items():
    im=sheet.crop(rect);alpha_ranges[name]=list(im.getchannel('A').getextrema())
    # These are interior material swatches, not silhouette sprites. The native
    # return has uniform near-opaque alpha248..253 even far from every edge.
    # Normalize only this expressly opaque material; final shape alpha comes
    # from the independent source mask and remains unchanged.
    if alpha_ranges[name][0]<245:raise ValueError(f'Texture crop includes transparent edge: {name}')
    im.putalpha(255);textures[name]=im.convert('RGBa').resize((160,160),Image.Resampling.LANCZOS).convert('RGBA')
art_path=folder/'art.json';art=json.loads(art_path.read_text(encoding='utf-8'))if art_path.exists()else{'schemaVersion':1,'tilePixels':40,'status':'production-candidates','pieces':[]}
ids=[int(value)for value in sys.argv[1:]]
if not 1<=len(ids)<=6:raise ValueError('Process one to six explicitly selected elements per invocation')
result=[]
for ident in ids:
    entry=elements[ident]
    if entry['family']!='pve' or ident in[18201,18202,18203,18204,18242]:raise ValueError('Uses separate native paint or explicit visible alias')
    reference=root/entry['referencePng']['file'];original=Image.open(reference).convert('RGBA')
    fw,fh=entry['selectedFrameSize']
    if original.size!=(fw,fh):raise ValueError('Reference representative extent differs; inspect alias first')
    pixels=np.asarray(original).astype(np.float32);r,g,b,a=[pixels[:,:,i]for i in range(4)]
    if ident>=18229:
        labels=np.zeros((fh,fw),dtype=np.uint8);labels[(r>90)&(g>140)]=1
        palette=['water','bank'];classifier='water default; pale shore highlight R>90 and G>140; source alpha retained'
    elif ident>=18200:
        labels=np.zeros((fh,fw),dtype=np.uint8);labels[(g>=167)&(r>=65)&(b>=150)]=1
        palette=['floor','jade'];classifier='jade region G>=167,R>=65,B>=150; complementary slate ground'
    else:
        labels=np.zeros((fh,fw),dtype=np.uint8);labels[g>=90]=1;labels[g>=128]=2;labels[(g>=167)&(r>=65)&(b>=150)]=3
        palette=['shadow','face','floor','jade'];classifier='shadow G<90; face90<=G<128; floorG>=128; jadeG>=167,R>=65,B>=150'
    size=(fw*4,fh*4);out=Image.new('RGBA',size);mask_base=Image.fromarray(labels,'L').resize(size,Image.Resampling.NEAREST)
    for index,name in enumerate(palette):
        paint=Image.new('RGBA',size)
        for y in range(0,size[1],160):
            for x in range(0,size[0],160):paint.alpha_composite(textures[name],(x,y))
        mask=mask_base.point(lambda value:255 if value==index else 0)
        out=Image.composite(paint,out,mask)
    alpha=original.getchannel('A').resize(size,Image.Resampling.NEAREST);out.putalpha(alpha)
    target=folder/'pieces'/f'{ident}-painted-region-v1.png';target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
    record={'elementId':ident,'idMapping':'candidate-filename-inference','file':target.relative_to(root).as_posix(),
        'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':size[0],'height':size[1],
        'worldFrameWidth':fw,'worldFrameHeight':fh,'exportDensity':4,'sourceFootprintCells':entry['footprintCells'],
        'sourceMapElemOffset':entry['mapElemOffsetRaw'],'derivedFrom':[
            {'file':source.relative_to(root).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'generationRecord':source.relative_to(root).as_posix()+'.generation.json','purpose':'newly painted texture RGB'},
            {'file':reference.relative_to(root).as_posix(),'sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
             'purpose':'source alpha and classified region geometry only; no reference RGB exported'}],
        'operation':{'type':'AI-painted-textures-through-reference-region-and-alpha-masks','newModelGeneration':False,
            'resampled':True,'textureSourceRects':{key:rects[key]for key in palette},'textureSourceAlpha':{key:alpha_ranges[key]for key in palette},
            'textureAlphaNormalization':'interior opaque material alpha>=245 normalized to255; measured source ranges retained; original source-mask alpha unchanged',
            'classifier':classifier,'logicalRegionSha256':hashlib.sha256(labels.tobytes()).hexdigest(),
            'logicalAlphaSha256':hashlib.sha256(original.getchannel('A').tobytes()).hexdigest(),
            'maskResize':'NEARESTx4','textureResize':'uniform premultiplied-alpha LANCZOS to160px per40logicalpx',
            'referencePixelColoursReused':False,'mapCellFootprintCollisionChanged':False},
        'alphaExtrema':list(alpha.getextrema()),'geometryAccepted':False,'accepted':False,'seamlessVerified':False,
        'status':'painted-region-composite-awaiting-classification-seam-and-in-game-review',
        'warnings':['source-region-classification-not-visually-accepted','original-alpha-resolution-resampled-not-native-HD-contour','texture-joins-not-yet-verified']}
    target.with_suffix('.png.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    art['pieces']=[piece for piece in art['pieces']if piece['elementId']!=ident];art['pieces'].append(record);result.append(ident)
art_path.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'family':'pve','writtenIds':result,'total':len(art['pieces']),'accepted':False}))
