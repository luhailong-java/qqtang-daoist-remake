"""Keep source bank classification geometry; composite only new image RGB."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lava_source=OUT/'batch-03/sheet-v1.png';stone_source=OUT/'batch-02/sheet-v1.png'
lava_rect=[150,170,310,330];stone_rect=[1290,286,1440,436]
def texture(path,rect):
 im=Image.open(path).convert('RGBA').crop(rect);alpha=list(im.getchannel('A').getextrema());assert alpha[0]>=250
 im.putalpha(255);return im.convert('RGBa').resize((160,160),Image.Resampling.LANCZOS).convert('RGBA'),alpha
lava,lava_alpha=texture(lava_source,lava_rect);stone,stone_alpha=texture(stone_source,stone_rect)
elements={p['elementId']:p for p in read(ROOT/'assets/maps/production-index.json')['elements']}
art_path=OUT/'art.json';art=read(art_path);ids=[10002,10003,10004,10015,10016,10017];art['pieces']=[p for p in art['pieces']if p['elementId']not in ids]
records=[]
for ident in ids:
 e=elements[ident];ref=ROOT/e['referencePng']['file'];original=Image.open(ref).convert('RGBA');assert original.size==(40,40)and original.getchannel('A').getextrema()==(255,255)
 a=np.array(original).astype(np.float32);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];bank=(b>=12)|((g>=.32*r)&(r<180))
 mask=(bank.astype(np.uint8)*255);mask_image=Image.fromarray(mask,'L').resize((160,160),Image.Resampling.NEAREST)
 final=Image.composite(stone,lava,mask_image);target=OUT/'pieces'/f'{ident}-treasure-mask-v2.png';final.save(target)
 p={'elementId':ident,'idMapping':e['familyMappingStatus'],'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':160,'height':160,'worldFrameWidth':40,'worldFrameHeight':40,'exportDensity':4,
 'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourceReference':e['referencePng'],
 'derivedFrom':[{'file':lava_source.relative_to(ROOT).as_posix(),'sha256':sha(lava_source),'generationRecord':lava_source.relative_to(ROOT).as_posix()+'.generation.json','purpose':'new painted lava RGB'},
 {'file':stone_source.relative_to(ROOT).as_posix(),'sha256':sha(stone_source),'generationRecord':stone_source.relative_to(ROOT).as_posix()+'.generation.json','purpose':'new painted volcanic-stone RGB, no mushrooms in selected crop'},
 {'file':ref.relative_to(ROOT).as_posix(),'sha256':sha(ref),'purpose':'bank-versus-lava region mask only; no source RGB reused'}],
 'operation':{'type':'reference-region-mask-new-image-texture-composite','newModelGeneration':False,'resampled':True,'lavaSourceRectLTRB':lava_rect,'stoneSourceRectLTRB':stone_rect,'textureOriginalAlphaExtrema':{'lava':lava_alpha,'stone':stone_alpha},
 'alphaNormalization':'interior alpha>=250 to255; RGB unchanged','sourcePixelColoursReused':False,'maskClassifier':'bank: B>=12 or (G>=0.32R and R<180); complement lava','logicalMaskSize':[40,40],'logicalMaskSha256':hashlib.sha256(mask.tobytes()).hexdigest(),'maskResampler':'NEAREST','bankPixels':int(bank.sum()),'lavaPixels':int((~bank).sum())},
 'alphaExtrema':[255,255],'terrainOpaqueCanvasVerified':True,'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'seamlessVerified':False,
 'anchorStatus':'source render offset remains unverified','status':'painted-lava-composite-awaiting-region-seam-and-in-game-validation','warnings':['bank-mask-classification-needs-visual-comparison','tile-seams-not-yet-accepted']}
 save(Path(str(target)+'.source.json'),p);art['pieces'].append(p);records.append({'elementId':ident,'file':p['file'],'bankPixels':int(bank.sum())})
save(art_path,art);save(OUT/'batch-03/composite-qa.json',{'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'pieces':records,'sourceRgbCopied':False,'alphaVerified':True,'accepted':False,'pending':['reference mask classification','seams','in-game review']})
print(json.dumps({'family':'treasure','pieces':len(art['pieces']),'lavaComposites':len(ids),'sourceRgbCopied':False,'accepted':False}))
