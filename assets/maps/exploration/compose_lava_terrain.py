"""Generate no pixels: assemble new painted textures through source masks."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=read(ROOT/'assets/maps/production-index.json');entries={p['elementId']:p for p in inventory['elements']}
art_path=OUT/'art.json';art=read(art_path);painted={p['elementId']:p for p in art['pieces']}
lava_record=painted[16028];stone_record=painted[16010]
lava_file=ROOT/lava_record['file'];stone_file=ROOT/stone_record['file']
lava=Image.open(lava_file).convert('RGBA');stone=Image.open(stone_file).convert('RGBA')
assert lava.size==stone.size==(160,160)and lava.getchannel('A').getextrema()==stone.getchannel('A').getextrema()==(255,255)
# The texture master is retained even though element16028's runtime entry below
# becomes an exact source-frame composite. It remains a necessary image input.
ids=list(range(16026,16039));art['pieces']=[p for p in art['pieces']if p['elementId']not in ids];items=[]
for ident in ids:
 e=entries[ident];ref=ROOT/e['referencePng']['file'];original=Image.open(ref).convert('RGBA');assert original.size==(40,40)
 a=np.array(original).astype(np.float32);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 molten=(r>2*g)&(r>60)
 mask=(molten.astype(np.uint8)*255);smooth_mask=Image.fromarray(mask,'L').resize((160,160),Image.Resampling.LANCZOS)
 final=Image.composite(lava,stone,smooth_mask);final.putalpha(original.getchannel('A').resize((160,160),Image.Resampling.LANCZOS))
 target=OUT/'pieces'/f'{ident}-exploration-terrain-v2.png';final.save(target)
 p={'elementId':ident,'idMapping':e['familyMappingStatus'],'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':160,'height':160,'worldFrameWidth':40,'worldFrameHeight':40,'exportDensity':4,
 'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourceReference':e['referencePng'],
 'derivedFrom':[{'file':lava_file.relative_to(ROOT).as_posix(),'sha256':sha(lava_file),'generationRecord':lava_record['derivedFrom']['generationRecord'],'sourceRecord':lava_file.relative_to(ROOT).as_posix()+'.source.json','purpose':'new hand-painted molten material RGB'},
 {'file':stone_file.relative_to(ROOT).as_posix(),'sha256':sha(stone_file),'generationRecord':stone_record['derivedFrom']['generationRecord'],'sourceRecord':stone_file.relative_to(ROOT).as_posix()+'.source.json','purpose':'new hand-painted dark earth/basalt RGB'},
 {'file':ref.relative_to(ROOT).as_posix(),'sha256':sha(ref),'purpose':'source molten/crust classification and alpha geometry only, no source RGB colours copied'}],
 'operation':{'type':'source-region-mask-new-texture-image-assembly','newModelGeneration':False,'resampled':True,'sourcePixelColoursReused':False,
 'maskClassifier':'molten R>2G and R>60; complementary opaque region dark crust/bank','logicalMaskSize':[40,40],'logicalMaskSha256':hashlib.sha256(mask.tobytes()).hexdigest(),'materialMaskResampler':'LANCZOS',
 'sourceAlphaResampler':'LANCZOS','sourceAlphaSHA256':hashlib.sha256(original.getchannel('A').tobytes()).hexdigest(),'sourceAlphaExtrema':list(original.getchannel('A').getextrema()),'moltenPixelCount':int(molten.sum())},
 'alphaExtrema':list(final.getchannel('A').getextrema()),'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'seamlessVerified':False,'anchorStatus':'source render offset unverified',
 'status':'painted-terrain-composite-awaiting-mask-alpha-seam-and-in-game-validation','warnings':['classification-material-and-alpha-shape-await-visual-comparison','all-tile-joins-await-validation']}
 save(Path(str(target)+'.source.json'),p);art['pieces'].append(p);items.append({'elementId':ident,'file':p['file'],'moltenPixels':int(molten.sum()),'alphaExtrema':p['alphaExtrema']})
save(art_path,art);save(OUT/'terrain-composites.json',{'createdAtUTC':datetime.now(timezone.utc).isoformat(),'items':items,'newGenerations':0,'sourceRgbCopied':False,'sourceMaskAndAlphaUsed':True,'accepted':False,'qa':'full family QA deferred during reserved heavy-job window'})
print(json.dumps({'family':'exploration','candidates':len(art['pieces']),'lavaTerrainComposites':len(ids),'newModelGenerations':0,'accepted':False}))
