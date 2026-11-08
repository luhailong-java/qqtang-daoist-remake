"""Preflight six measured ownership crops, use unchanged common exporter, inspect current six outputs."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,sys,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];batch=sys.argv[1]
spec_path=ROOT/f'docs/eye-adornments-{batch}-export.json';spec=json.loads(spec_path.read_text(encoding='utf-8'))
if spec['assetDirectory']!='assets/items/eye-adornments' or not 1<=len(spec['items'])<=6:raise ValueError('Wrong scope')
im=Image.open(ROOT/spec['source']).convert('RGBA');m=np.asarray(im.getchannel('A'))>=8;H,W=m.shape
ownership=np.zeros((H,W),np.uint8);checks=[]
for item in spec['items']:
 l,t,r,b=item['rect']
 if not(0<=l<r<=W and 0<=t<b<=H):raise ValueError('ROI outside native canvas')
 v=m[t:b,l:r];boundary=int(v[0].sum()+v[-1].sum()+v[:,0].sum()+v[:,-1].sum())
 if boundary:raise ValueError(f'Visible cut boundary for{item["itemId"]}:{boundary}')
 ownership[t:b,l:r]+=1;checks.append({'itemId':item['itemId'],'rect':item['rect'],'alpha8BoundaryPixels':boundary,'alpha8VisiblePixels':int(v.sum())})
missing=int((m&(ownership==0)).sum());duplicate=int((m&(ownership>1)).sum())
if missing or duplicate:raise ValueError(f'Unsafe source ownership missing{missing}/duplicate{duplicate}')
gate={'source':spec['source'],'sha256':hashlib.sha256((ROOT/spec['source']).read_bytes()).hexdigest(),
 'sourceAlpha8OwnedOnce':int(m.sum()),'unassignedVisiblePixels':missing,'duplicateVisiblePixels':duplicate,'items':checks,
 'operation':'All current batch source ownership and empty-cut checks completed before calling unchanged common exporter.'}
(ROOT/f'docs/eye-adornments-{batch}-ownership.json').write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
im.close()
subprocess.run([sys.executable,str(ROOT/'scripts/export-item-art.py'),str(spec_path.relative_to(ROOT))],cwd=ROOT,check=True)
art_path=ROOT/spec['assetDirectory']/'art.json';art=json.loads(art_path.read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'references/qqtang-item-data/catalog.json').read_text(encoding='utf-8'))
selected=[];contact=Image.new('RGB',(768,560),(248,242,225));draw=ImageDraw.Draw(contact)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
for i,item in enumerate(spec['items']):
 entry=next(x for x in art['items']if x['itemId']==item['itemId']);source=next(x for x in catalog['items']if x['item_id']==item['itemId'])
 entry.update({'resourceId':source['resource_id'],'accepted':False,'worldAccepted':False,'stateAccepted':False,'runtimeAccepted':False,
  'batch':batch,'sourceReference':item['sourceReference'],'sourceReferenceKind':item.get('sourceReferenceKind','declared inventory icon'),'inventoryMappingVerified':item.get('inventoryMappingVerified')})
 output=Image.open(ROOT/entry['file']).convert('RGBA');a=np.asarray(output.getchannel('A'));v=a>=8
 edges={'top':int(v[0].sum()),'right':int(v[:,-1].sum()),'bottom':int(v[-1].sum()),'left':int(v[:,0].sum())}
 if any(edges.values()):raise ValueError('Unexpected256 outer border: '+str(item['itemId']))
 bg=Image.new('RGBA',(256,256),(248,242,225,255));bg.alpha_composite(output)
 x=(i%3)*256;y=(i//3)*280;contact.paste(bg.convert('RGB'),(x,y));draw.text((x+8,y+258),str(item['itemId'])+' '+item['displayName'],font=font,fill='#244f44')
 entry['batchTechnicalAlphaCheck']={'outerAlpha8':edges,'currentBatchOnly':True,'smallUiReviewed':False}
 (ROOT/entry['file']).with_suffix('.png.provenance.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 selected.append({'itemId':entry['itemId'],'file':entry['file'],'sha256':entry['sha256'],'outerAlpha8':edges})
 output.close()
art['items'].sort(key=lambda x:x['itemId']);art.update({'accepted':False,'worldAccepted':False,'stateAccepted':False,'runtimeAccepted':False})
art_path.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=ROOT/spec['assetDirectory']/'qa'/f'eye-adornments-{batch}-contact-256.png';out.parent.mkdir(exist_ok=True);contact.save(out)
out.with_suffix('.png.source.json').write_text(json.dumps({'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'derivedFrom':selected,'operation':'Unscaled current six256PNG ivory contact with24px labels; no extra generation/full-category scan.',
 'newModelGeneration':False,'actualVisualViewed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'currentBatch':batch,'totalInventoryCandidates':len(art['items']),'contact':str(out),'newModelGeneration':False,'accepted':False}))
