"""Six exact source region masks, new painted RGB. Not a model generation."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
art=read(OUT/'art.json');painted={p['elementId']:p for p in art['pieces']}
inventory=read(ROOT/'assets/maps/production-index.json');entries={p['elementId']:p for p in inventory['elements']}
sheet=OUT/'batch-09/sheet-v1.png';master=Image.open(sheet).convert('RGBA')
materials={};material_records=[]
for name,rect in [('sand',[100,590,420,910]),('grass',[610,590,930,910])]:
 crop=master.crop(rect);alpha=list(crop.getchannel('A').getextrema());assert alpha[0]>=250
 rgbhash=hashlib.sha256(crop.convert('RGB').tobytes()).hexdigest();crop.putalpha(255)
 assert hashlib.sha256(crop.convert('RGB').tobytes()).hexdigest()==rgbhash
 materials[name]=crop.resize((160,160),Image.Resampling.LANCZOS)
 material_records.append({'material':name,'sheetRectLTRB':rect,'nativeCropSize':[320,320],'sourceAlphaExtrema':alpha,'alphaNormalization':'250..254 to255 only within inspected plain material crop','nativeCropRGBSHA256':rgbhash,'rgbPreservedBeforeResize':True,'uniformScale':0.5,'resampler':'LANCZOS'})
ids=list(range(16117,16123));art['pieces']=[p for p in art['pieces']if p['elementId']not in ids];rows=[]
for ident in ids:
 e=entries[ident];ref=ROOT/e['referencePng']['file'];source=Image.open(ref).convert('RGBA');assert source.size==(40,40)
 a=np.array(source);grass=a[:,:,1]>a[:,:,0];mask=grass.astype(np.uint8)*255
 final=Image.composite(materials['grass'],materials['sand'],Image.fromarray(mask).resize((160,160),Image.Resampling.NEAREST))
 final.putalpha(source.getchannel('A').resize((160,160),Image.Resampling.NEAREST));assert final.getchannel('A').getextrema()==(255,255)
 target=OUT/'pieces'/f'{ident}-exploration-path-v2.png';final.save(target)
 p={'elementId':ident,'idMapping':e['familyMappingStatus'],'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':160,'height':160,'worldFrameWidth':40,'worldFrameHeight':40,'exportDensity':4,'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourceReference':e['referencePng'],
 'derivedFrom':[{'file':sheet.relative_to(ROOT).as_posix(),'sha256':sha(sheet),'generationRecord':'assets/maps/exploration/batch-09/sheet-v1.png.generation.json','purpose':'new painted sand/grass RGB material masters only'},{'file':ref.relative_to(ROOT).as_posix(),'sha256':sha(ref),'purpose':'exact grass/sand region mask and alpha, original RGB not copied'}],
 'operation':{'type':'source-region-mask-new-texture-image-assembly','newModelGeneration':False,'resampled':True,'sourcePixelColoursReused':False,'materialSources':material_records,'maskClassifier':'grass G>R; complement golden sand','sourceLogicalMaskSize':[40,40],'logicalMaskSha256':hashlib.sha256(mask.tobytes()).hexdigest(),'sourceMaskResampler':'NEAREST4x','sourceAlphaExtrema':list(source.getchannel('A').getextrema()),'grassPixels':int(grass.sum())},
 'alphaExtrema':[255,255],'terrainOpaqueCanvasVerified':True,'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'seamlessVerified':False,'anchorStatus':'source render offset unverified','status':'painted-garden-path-composite-awaiting-mask-seam-and-in-game-validation','warnings':['source pixel-stepped material boundary intentionally preserved; artistic smoothing not performed','all-tile-joins-await-validation','new grass master has small warm-yellow botanical accents; style/identity acceptance pending']}
 save(Path(str(target)+'.source.json'),p);art['pieces'].append(p);rows.append({'elementId':ident,'file':p['file'],'grassPixels':int(grass.sum()),'alphaExtrema':[255,255]})
save(OUT/'art.json',art);save(OUT/'garden-path-composites.json',{'createdAtUTC':datetime.now(timezone.utc).isoformat(),'items':rows,'materialSources':material_records,'newGenerations':0,'sourceRgbCopied':False,'accepted':False,'qa':'single current six-piece production batch only; full-family QA deferred'})
print(json.dumps({'family':'exploration','candidates':len(art['pieces']),'opaqueGardenPathExports':len(rows),'accepted':False}))
