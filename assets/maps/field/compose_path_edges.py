"""Source ground supplies classification geometry only; all RGB is new art."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sheet=OUT/'batch-04/sheet-v1.png';master=Image.open(sheet).convert('RGBA')
rect=[190,120,350,280];soil=master.crop(rect);alpha=list(soil.getchannel('A').getextrema())
assert alpha[0]>=250;soil.putalpha(255)
grass_file=OUT/'pieces/6023-field-v1.png';grass=Image.open(grass_file).convert('RGBA');assert grass.size==(160,160)and grass.getchannel('A').getextrema()==(255,255)
grass_record=read(Path(str(grass_file)+'.source.json'))
inventory=read(ROOT/'assets/maps/production-index.json');elements={p['elementId']:p for p in inventory['elements']}
art_path=OUT/'art.json';art=read(art_path);ids=list(range(6017,6023));art['pieces']=[p for p in art['pieces']if p['elementId']not in ids]
reports=[]
for ident in ids:
 e=elements[ident];ref=ROOT/e['referencePng']['file'];original=Image.open(ref).convert('RGBA');assert original.size==(40,40)and original.getchannel('A').getextrema()==(255,255)
 a=np.array(original).astype(np.int16);path_region=a[:,:,0]>a[:,:,1]+8
 mask=(path_region.astype(np.uint8)*255);mask_image=Image.fromarray(mask,'L').resize((160,160),Image.Resampling.NEAREST)
 final=Image.composite(soil,grass,mask_image);target=OUT/'pieces'/f'{ident}-field-mask-v2.png';final.save(target)
 item={'elementId':ident,'idMapping':e['familyMappingStatus'],'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':160,'height':160,'worldFrameWidth':40,'worldFrameHeight':40,'exportDensity':4,
 'footprintCells':e['footprintCells'],'gridAttr':e['gridAttr'],'mapElemOffsetRaw':e['mapElemOffsetRaw'],'selectedFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourceReference':e['referencePng'],
 'derivedFrom':[{'file':sheet.relative_to(ROOT).as_posix(),'sha256':sha(sheet),'generationRecord':sheet.relative_to(ROOT).as_posix()+'.generation.json','purpose':'new hand-painted sand RGB'},
 {'file':grass_file.relative_to(ROOT).as_posix(),'sha256':sha(grass_file),'generationRecord':grass_record['derivedFrom']['generationRecord'],'sourceRecord':grass_file.relative_to(ROOT).as_posix()+'.source.json','purpose':'new hand-painted grass RGB'},
 {'file':ref.relative_to(ROOT).as_posix(),'sha256':sha(ref),'purpose':'source path-versus-grass classification geometry only; source RGB never reused'}],
 'operation':{'type':'reference-region-mask-new-image-texture-composite','newModelGeneration':False,'resampled':True,'soilSourceRectLTRB':rect,'soilOriginalAlphaExtrema':alpha,'soilAlphaNormalization':'interior alpha>=250 to255; RGB unchanged','sourcePixelColoursReused':False,
 'maskClassifier':'path region: R > G + 8; complementary pixels are grass','logicalMaskSize':[40,40],'logicalMaskSha256':hashlib.sha256(mask.tobytes()).hexdigest(),'maskResampler':'NEAREST','pathPixels':int(path_region.sum()),'grassPixels':int((~path_region).sum())},
 'alphaExtrema':[255,255],'terrainOpaqueCanvasVerified':True,'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'anchorStatus':'source render offset remains unverified','seamlessVerified':False,
 'status':'painted-ground-composite-awaiting-region-seam-and-in-game-validation','warnings':['classification-mask-visual-comparison-pending','tiled-seams-not-yet-accepted']}
 save(Path(str(target)+'.source.json'),item);art['pieces'].append(item);reports.append({'elementId':ident,'pathPixels':int(path_region.sum()),'file':item['file']})
save(art_path,art)
gen_path=Path(str(sheet)+'.generation.json');gen=read(gen_path);gen['references'][0]['purpose']='source structure only';gen['evidence']['officialCheckDate']='2026-10-28';gen['evidence']['officialCheckRecord']='docs/IMAGE_CONFIG_VERIFICATION_20261028.md';save(gen_path,gen)
save(OUT/'batch-04/composite-qa.json',{'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'pieces':reports,'sourceRgbCopied':False,'alphaVerified':True,'accepted':False,'pending':['classification masks need visual comparison','seams and game rendering']})
print(json.dumps({'fieldPieces':len(art['pieces']),'groundComposites':len(ids),'sourceRgbCopied':False,'geometryAccepted':False}))
