"""One exact UI atlas →16 candidates; gate ALL visible ownership/cuts/outputs before writing any PNG.
No shared exporter, src, root art/UI README or Git changes.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,datetime
base=Path(__file__).resolve().parent;root=base.parents[2]
spec=json.loads((base/'ownership.json').read_text(encoding='utf-8'))
src=(root/spec['source']).resolve();assert src==root/'assets/ui/qdao-ui-semantic-extra-v1.png'
raw=src.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==spec['sourceSha256']
gen=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8'));assert gen['sha256']==sha
im=Image.open(src).convert('RGBA');assert list(im.size)==spec['actualNativeSize']==[1254,1254]
names=['friends','add-friend','remove-friend','private-chat','guild','task','backpack','warehouse','forge','compose','save-replay','cancel-replay','pet-card','fullscreen','mute','reconnect']
assert [p['id']for p in spec['parts']]==names
alpha=np.asarray(im.getchannel('A'));visible=alpha>=8;coverage=np.zeros(alpha.shape,dtype=np.uint8);masks=[];cuts=[]
for p in spec['parts']:
 mask=Image.new('L',im.size)
 if 'polygon'in p:ImageDraw.Draw(mask).polygon([tuple(q)for q in p['polygon']],fill=255)
 else:
  l,t,r,b=p['rect'];ImageDraw.Draw(mask).rectangle((l,t,r-1,b-1),fill=255)
 bits=np.asarray(mask)>0;coverage+=bits;interior=np.asarray(mask.filter(ImageFilter.MinFilter(3)))>0
 boundary=int(np.count_nonzero(visible&bits&~interior));masks.append(mask);cuts.append({'id':p['id'],'visiblePixelsOnOwnershipCut':boundary})
missing=int(np.count_nonzero(visible&(coverage==0)));multiple=int(np.count_nonzero(visible&(coverage>1)))
gate={'source':spec['source'],'sourceSha256':sha,'threshold':8,'parts':16,'visiblePixels':int(visible.sum()),'unassignedVisiblePixels':missing,'multiplyAssignedVisiblePixels':multiple,'partCutChecks':cuts,'all16SourceChecksPassed':not(missing or multiple or any(c['visiblePixelsOnOwnershipCut']for c in cuts)),'pngsWrittenBeforeAllChecks':0}
if not gate['all16SourceChecksPassed']:
 (base/'ownership-gate.json').write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
 raise ValueError('Visible source ownership/cut gate failed. No candidate PNGs written: '+json.dumps(gate))
prepared=[];records=[]
def edges(a):return{'left':sum(a.getpixel((0,y))>=8 for y in range(256)),'right':sum(a.getpixel((255,y))>=8 for y in range(256)),'top':sum(a.getpixel((x,0))>=8 for x in range(256)),'bottom':sum(a.getpixel((x,255))>=8 for x in range(256))}
for p,mask in zip(spec['parts'],masks):
 bits=np.asarray(mask)>0;region=im.copy();region.putalpha(Image.fromarray(np.where(bits,alpha,0).astype(np.uint8)))
 bounds=region.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
 if not bounds:raise ValueError('Empty owned semantic icon; no PNG written: '+p['id'])
 rect=[max(0,bounds[0]-8),max(0,bounds[1]-8),min(im.width,bounds[2]+8),min(im.height,bounds[3]+8)];crop=region.crop(rect)
 vw=bounds[2]-bounds[0];vh=bounds[3]-bounds[1];s=224/max(vw,vh)
 visible_target=[(256-vw*s)/2,(256-vh*s)/2];placement=[visible_target[0]-(bounds[0]-rect[0])*s,visible_target[1]-(bounds[1]-rect[1])*s]
 # A single exact isotropic affine transform keeps x/y scale equal, no separate rounded-axis fit.
 output=crop.convert('RGBa').transform((256,256),Image.Transform.AFFINE,(1/s,0,-placement[0]/s,0,1/s,-placement[1]/s),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA')
 a=output.getchannel('A');bb=a.point(lambda q:255 if q>=8 else 0).getbbox();outside=edges(a)
 if not bb or any(outside.values()):raise ValueError('Output border/empty gate failed; no PNG written: '+p['id'])
 target='assets/ui/semantic-extra/'+p['id']+'.png'
 rec={'id':p['id'],'row':p['row'],'column':p['column'],'file':target,'source':spec['source'],'sourceSha256':sha,'sourceNativeSize':[1254,1254],'sourceGenerationRecord':spec['source']+'.generation.json','sourceActualModel':gen.get('actualModel'),'sourceActualQuality':gen.get('actualQuality'),'operation':'Measured irregular source ownership, keep8 native pixels around alpha>=8 contour, exact isotropic premultiplied-alpha BICUBIC affine fit of visible silhouette to224 on256 transparent canvas. Not new image generation.','nativeROI':rect,'nativeROISize':list(crop.size),'sourceVisibleBounds':list(bounds),'ownership':{key:p[key]for key in['rect','polygon']if key in p},'ownedSourceAlpha8Pixels':int(np.count_nonzero(visible&bits)),'visiblePixelsOnOwnershipCut':0,'uniformScale':s,'placementXY':placement,'visibleFit':224,'outputCanvas':[256,256],'alphaExtrema':a.getextrema(),'alpha8BBoxLTRB':bb,'alpha8MarginsLTRB':[bb[0],bb[1],256-bb[2],256-bb[3]],'alpha8OuterEdges':outside,'newImageGeneration':False,'componentDeletion':False,'sourcePixelRepaint':False,'actual256ContactViewed':False,'runtimeAdopted':False,'clientApproved':False,'status':'exported_candidate_pending_visual_and_ui_use'}
 prepared.append((p['id'],output));records.append(rec)
gate['all16OutputChecksPassed']=True;gate['outputChecksBeforeAnyPNGWrite']=16
# Only now write all16 candidates and their provenance.
for(id,output),rec in zip(prepared,records):
 target=base/(id+'.png');output.save(target);rec['sha256']=hashlib.sha256(target.read_bytes()).hexdigest();target.with_suffix('.png.provenance.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contact=Image.new('RGB',(1024,1024),(246,240,222))
for i,(id,output)in enumerate(prepared):
 ivory=Image.new('RGBA',(256,256),(246,240,222,255));ivory.alpha_composite(output);contact.paste(ivory.convert('RGB'),((i%4)*256,(i//4)*256))
contact_path=base/'contact-ivory.png';contact.save(contact_path)
contact_path.with_suffix('.png.provenance.json').write_text(json.dumps({'derivedFrom':[{'file':r['file'],'sha256':r['sha256']}for r in records],'operation':'Unscaled256px-per-cell current16-icon ivory contact sheet only, no new generation or image editing.','sourceGenerationRecord':spec['source']+'.generation.json'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':spec['source'],'sourceSha256':sha,'sourceNativeSize':[1254,1254],'sourceGenerationRecord':spec['source']+'.generation.json','sourceActualModel':gen.get('actualModel'),'sourceActualQuality':gen.get('actualQuality'),'sourceImageCount':1,'generatedIconSheets':1,'derivedIcons':16,'newGenerationCallsThisExport':0,'ownershipSpec':'assets/ui/semantic-extra/ownership.json','gate':gate,'entries':records,'contactPreview':'assets/ui/semantic-extra/contact-ivory.png','runtimeAdopted':False,'clientApproved':False,'machineScope':'One specifically authorized current atlas only; no full-familyQA/test/browser/runtime/src/root-art/UI-README/Git change.'}
(base/'ownership-gate.json').write_text(json.dumps(gate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(base/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'icons':16,'sourceVisiblePixels':gate['visiblePixels'],'unassigned':missing,'multiple':multiple,'allCutsEmpty':True,'all16OutputChecksPassedBeforeWrite':True,'manifest':'assets/ui/semantic-extra/manifest.json','runtimeAdopted':False}))
