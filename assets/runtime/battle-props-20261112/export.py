"""Register native builtin output and export three original static battle props."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import datetime,hashlib,json,sys
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,j):p.write_bytes((json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode())
submission=BASE/'builtin-submission-v1.json';request=read(submission);returned=read(BASE/'builtin-result-v1.json')
mother=BASE/'master-v1.png';image=Image.open(mother).convert('RGBA')
assert image.size==(1536,1024),'Measure and explicitly update rects for a different native return'
config=ROOT/'config/image-generation.json';prompt=BASE/'master-v1.prompt.txt'
gen={'schemaVersion':1,'file':rel(mother),'sha256':sha(mother),'width':image.width,'height':image.height,'format':'PNG',
 'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeEvidence':'UTC registration after tool return; provider creation timestamp not exposed',
 'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':read(config),
 'configSource':{'file':rel(config),'sha256':sha(config)},'modelQualityReverifiedOn':'2026-11-12',
 'submittedParameters':{k:v for k,v in request['input'].items()if k!='prompt'}|{'model':None,'quality':None},
 'prompt':request['input']['prompt'],'exactPrompt':request['input']['prompt'],'promptFile':rel(prompt),'promptFileSha256':sha(prompt),
 'submittedPromptSha256':hashlib.sha256(request['input']['prompt'].encode()).hexdigest(),
 'builtinSubmissionEvidence':{'file':rel(submission),'sha256':sha(submission)},'evidence':returned,
 'references':[{'path':rel(Path(p)),'purpose':'established Daoist Q hand-painted style only','sha256':sha(Path(p))}for p in request['input']['referenced_image_paths']],
 'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin has no model/quality selectors and returned no verifiable values',
 'operation':'native returned PNG copied without raster edits','visualAccepted':False,'runtimeAdopted':False,'accepted':False}
save(Path(str(mother)+'.generation.json'),gen)
sys.path.insert(0,str(ROOT/'scripts'))
from painted_crop_gate import validate_visible_boundaries
rects=[[n*512,0,(n+1)*512,512]for n in range(3)]
validate_visible_boundaries(image,rects,threshold=16)
pieces=[]
bounds={'needle':{'pickup':[54,54]},'shield':{'pickup':[54,54]},'bun':{'pickup':[64,64],'base':[80,80],'carrying':[35,35]}}
for slot,rect in zip(['needle','shield','bun'],rects):
 crop=image.crop(rect);box=crop.getchannel('A').point(lambda a:255 if a>=16 else 0).getbbox();assert box
 content=crop.crop(box);scale=min(220/content.width,220/content.height)
 extent=(round(content.width*scale),round(content.height*scale));paint=content.convert('RGBa').resize(extent,Image.Resampling.LANCZOS).convert('RGBA')
 position=((256-extent[0])//2,(256-extent[1])//2);out=Image.new('RGBA',(256,256));out.alpha_composite(paint,position)
 target=BASE/(slot+'.png');out.save(target);sidecar=Path(str(target)+'.provenance.json')
 record={'slot':slot,'file':rel(target),'sha256':sha(target),'width':256,'height':256,'generationRecord':rel(mother)+'.generation.json',
 'provenanceRecord':rel(sidecar),'sourceEntityId':None,'sceneId':None,'nativeQQTangFrameSize':None,
 'sourceMappingStatus':'original presentation skin for current technical renderer slots; no native source ID inferred',
 'inheritedRenderBoundsAtDraft64Cell':bounds[slot],
 'derivedFrom':{'file':rel(mother),'sha256':sha(mother),'generationRecord':rel(mother)+'.generation.json'},
 'operation':{'type':'alpha16-bbox-crop-uniform-fit-centred-transparent-canvas','sourceRectLTRB':rect,'contentBBoxWithinRect':list(box),
 'uniformScale':scale,'scaledExtent':list(extent),'placement':list(position),'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False},
 'alphaExtrema':list(out.getchannel('A').getextrema()),'visualAccepted':False,'geometryAccepted':False,'runtimeAdopted':False,'accepted':False,'userReviewStatus':'pending'}
 assert record['alphaExtrema'][0]==0 and record['alphaExtrema'][1]>=16
 save(sidecar,record);pieces.append(record)
manifest={'schemaVersion':1,'purpose':'original static render art for current game slots; not original QQTang source mapping or final acceptance',
 'pieces':pieces,'visualAccepted':False,'geometryAccepted':False,'runtimeAdopted':False,'accepted':False,'userReviewStatus':'pending'}
save(BASE/'manifest.json',manifest)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
board=Image.new('RGB',(880,3*180+70),'#f6f0df');draw=ImageDraw.Draw(board)
draw.text((14,10),'对局原创道具 · 32/48/54/64px · 人审待定',fill='#214a3d',font=font)
draw.text((14,36),'沿用当前技术稿显示框；非原版ID、挂点、时序或手游实机验收',fill='#214a3d',font=font)
preview_records=[]
for row,piece in enumerate(pieces):
 im=Image.open(ROOT/piece['file']).convert('RGBA');y=70+row*180
 draw.text((12,y+5),piece['slot'],fill='#214a3d',font=font)
 for side,color in enumerate(['#f6f0df','#183e37']):
  draw.rectangle((80+side*400,y,479+side*400,y+179),fill=color)
  for col,size in enumerate([32,48,54,64]):
   thumb=im.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
   x=80+side*400+col*100+(100-size)//2;top=y+35+(70-size)//2;board.paste(thumb,(x,top),thumb)
   draw.text((88+side*400+col*100,y+125),str(size)+'px',fill='#214a3d'if side==0 else'#f6f0df',font=font)
 preview_records.append({'file':piece['file'],'sha256':piece['sha256'],'provenanceRecord':piece['provenanceRecord']})
preview=BASE/'review-mobile.png';board.save(preview)
save(Path(str(preview)+'.source.json'),{'file':rel(preview),'sha256':sha(preview),'derivedFrom':preview_records,
 'operation':'diagnostic premultiplied-alpha downscale and two-background alpha composites only','sizes':[32,48,54,64],
 'newModelGeneration':False,'userReviewStatus':'pending','visualAccepted':False,'runtimeAdopted':False})
print(json.dumps({'manifest':rel(BASE/'manifest.json'),'slots':[p['slot']for p in pieces],'pngs':3,'nativeMotherSize':list(image.size),'userReviewStatus':'pending'}))
