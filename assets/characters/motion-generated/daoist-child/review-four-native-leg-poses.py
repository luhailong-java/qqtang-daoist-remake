"""Only four already-decoded tiny leg PNGs/common-canvas diagnostic insets."""
import pathlib,json,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
base=pathlib.Path(__file__).resolve().parent;out=base/'native-role9-evidence'
board=json.loads((out/'group0-four-phase-board.json').read_text(encoding='utf-8'))
assert board['selectedIndices']==[1,2,4,5]
crop=[34,60,66,84];scale=12;cellw=384;cellh=338
sheet=Image.new('RGB',(cellw*2,cellh*2),(246,240,222));draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=17);records=[]
for i,pose in enumerate(board['records']):
 leg=next(l for l in pose['layers']if l['layer']=='leg');p=pathlib.Path(leg['png']);raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==leg['pngSha256']
 im=Image.open(p).convert('RGBA');a=im.getchannel('A');remaining={(x,y)for y in range(im.height)for x in range(im.width)if a.getpixel((x,y))>=8};parts=[]
 while remaining:
  seed=remaining.pop();stack=[seed];component=[seed]
  while stack:
   x,y=stack.pop()
   for yy in range(max(0,y-1),min(im.height,y+2)):
    for xx in range(max(0,x-1),min(im.width,x+2)):
     q=(xx,yy)
     if q in remaining:remaining.remove(q);stack.append(q);component.append(q)
  xs=[q[0]for q in component];ys=[q[1]for q in component];ox,oy=leg['frameOffset'];parts.append({'alpha8PixelCount':len(component),'localBBoxLTRB':[min(xs),min(ys),max(xs)+1,max(ys)+1],'originalCanvasBBoxLTRB':[min(xs)+ox,min(ys)+oy,max(xs)+1+ox,max(ys)+1+oy]})
 parts.sort(key=lambda p:p['originalCanvasBBoxLTRB'][0])
 native=pathlib.Path(pose['diagnosticComposite']);nr=native.read_bytes();full=Image.open(native).convert('RGB');assert full.size==(100,100)
 inset=full.crop(crop).resize((cellw,288),Image.Resampling.NEAREST);x=(i%2)*cellw;y=(i//2)*cellh;sheet.paste(inset,(x,y+50));draw.text((x+9,y+8),f'E frame{pose["frameIndex"]}, phase{pose["phaseIndex"]}',font=font,fill=(50,60,55))
 records.append({'frameIndex':pose['frameIndex'],'phaseIndex':pose['phaseIndex'],'legOffset':leg['frameOffset'],'legNativeSize':leg['nativeSize'],'legEncodedPixelSha256':leg['encodedPixelSha256'],'legAlpha8Components':parts,'componentMeaning':'Screen-left/right components only. Persistent anatomical near/far identity not independently recoverable merely by sorting X.','diagnosticComposite':str(native),'diagnosticCompositeSha256':hashlib.sha256(nr).hexdigest()})
dest=out/'group0-e-lowerbody-12x.png';sheet.save(dest)
data={'sourceRoleId':9,'direction':'E','directionEvidence':'actual face0 nose/mouth point screen-right; face12 points left so group2 is W','selectedIndices':[1,2,4,5],'board':str(dest),'boardSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'derivedFromBoard':'assets/characters/motion-generated/daoist-child/native-role9-evidence/group0-four-phase-board.json','operation':'Shared fixed native100px-plane crop [34,60,66,84] for all four already-decoded diagnostic poses,12x NEAREST; no bbox fit, source repaint or mirroring. Alpha components inspect only four tiny leg layer PNGs.','referenceOnly':True,'records':records,'anatomicalNearFarChainProven':False,'timingMs':None,'runtimeEnabled':False}
(out/'group0-e-lowerbody-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'board':str(dest),'records':records},ensure_ascii=False))
