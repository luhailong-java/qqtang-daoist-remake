"""Only this one16-semantic atlas; bounded alpha projection for manual ownership."""
from PIL import Image
import pathlib,json,hashlib,numpy as np
base=pathlib.Path(__file__).resolve().parent;root=base.parents[2]
src=root/'assets/ui/qdao-ui-semantic-extra-v1.png';raw=src.read_bytes();gen=json.loads(pathlib.Path(str(src)+'.generation.json').read_text(encoding='utf-8'));assert hashlib.sha256(raw).hexdigest()==gen['sha256']
im=Image.open(src).convert('RGBA');assert im.size==(1254,1254);a=np.asarray(im.getchannel('A'));v=a>=8
def runs(values,start,stop):
 result=[];begin=None
 for i in range(start,stop):
  if values[i]==0:
   if begin is None:begin=i
  elif begin is not None:result.append([begin,i]);begin=None
 if begin is not None:result.append([begin,stop])
 return result
row=v.sum(axis=1);bands=[[0,350],[350,650],[650,950],[950,1254]];rows=[]
for top,bottom in bands:
 cols=v[top:bottom].sum(axis=0);rows.append({'yBand':[top,bottom],'blankColumns':{str([l,r]):runs(cols,l,r)for l,r in[[290,380],[600,690],[900,980]]}})
forge=[]
for y in range(650,950,25):
 cols=v[y:y+25].sum(axis=0);forge.append({'yBand':[y,y+25],'zeroColumnRuns300to390':runs(cols,300,390)})
data={'source':'assets/ui/qdao-ui-semantic-extra-v1.png','sha256':gen['sha256'],'sourceGenerationRecord':'assets/ui/qdao-ui-semantic-extra-v1.png.generation.json','size':[1254,1254],'alphaExtrema':[int(a.min()),int(a.max())],'alpha8OuterEdges':{'left':int(v[:,0].sum()),'right':int(v[:,-1].sum()),'top':int(v[0].sum()),'bottom':int(v[-1].sum())},'blankRowRuns':{str([l,r]):runs(row,l,r)for l,r in[[290,380],[610,690],[900,990]]},'rowBandColumnRuns':rows,'columnBandBlankRows900to990':[{'xBand':[l,r],'blankRows':runs(v[:,l:r].sum(axis=1),900,990)}for l,r in[[0,325],[325,635],[635,945],[945,1254]]],'forgeComposeQuarterBands':forge,'scope':'Single current source alpha measurement only, not final ownership/export/acceptance; no nominal equal slicing.'}
(base/'source-measurement.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
