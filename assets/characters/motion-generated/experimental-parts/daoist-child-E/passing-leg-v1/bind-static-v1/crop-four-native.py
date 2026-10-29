"""Only this current atlas, four true native ownership crops, no registration."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
BASE=Path(__file__).resolve().parent
ROOT=next(p for p in BASE.parents if (p/'package.json').is_file() and (p/'src').is_dir())
src=BASE.parent/'passing-leg-v1.png';raw=src.read_bytes();digest=hashlib.sha256(raw).hexdigest()
if digest!='f35ce07c273f96d048344c1f1b55e71caf5ebc90eb1e16be1d12fd79ed5fc11e':raise ValueError('Source changed')
im=Image.open(src).convert('RGBA');a=np.asarray(im.getchannel('A'));count=int((a>=8).sum())
staged=[];records=[];owned=0
for i,ident in enumerate(['near_R_planted','near_R_raised','far_L_planted','far_L_raised']):
    cell=[(i%2)*768,(i//2)*512,(i%2+1)*768,(i//2+1)*512]
    l,t,r,b=cell;v=a[t:b,l:r]>=8
    if any([v[0].any(),v[-1].any(),v[:,0].any(),v[:,-1].any()]):raise ValueError('Unsafe ownership boundary')
    yy,xx=np.nonzero(v);owned+=int(len(xx))
    roi=[l+max(0,int(xx.min())-8),t+max(0,int(yy.min())-8),l+min(768,int(xx.max())+9),t+min(512,int(yy.max())+9)]
    crop=im.crop(roi);p=BASE/(ident+'.png')
    rec={'partId':ident,'file':p.relative_to(ROOT).as_posix(),'source':src.relative_to(ROOT).as_posix(),
      'sourceSha256':digest,'sourceCanvasSize':[1536,1024],'sourceGenerationRecord':(str(src.relative_to(ROOT)).replace('\\','/')+'.generation.json'),
      'ownershipCell':cell,'sourceROI':roi,'nativeCropSize':list(crop.size),'sourceAlpha8Pixels':int(len(xx)),
      'operation':'Complete owned native crop with8px margin where the cell allows. No resize, mirror, warp, registration or source alpha edit.',
      'pivot':None,'manualLandmarks':None,'runtimeAdopted':False}
    records.append(rec);staged.append((p,crop))
if owned!=count or owned!=237849:raise ValueError('Ownership incomplete')
for (p,crop),rec in zip(staged,records):
    crop.save(p);rec['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    p.with_suffix('.png.source.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
(BASE/'native-crops.json').write_text(json.dumps({'source':str(src.relative_to(ROOT)).replace('\\','/'),
 'sourceSha256':digest,'sourceAlpha8OwnedOnce':owned,'unassignedVisiblePixels':0,'duplicateOwnership':0,'parts':records},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'nativeCrops':[{k:r[k]for k in['partId','sourceROI','nativeCropSize']}for r in records], 'ownedAlpha8':owned}))
