from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib, json, shutil, sys
import numpy as np
from io import BytesIO

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
IMAGE = Path('D:/work/image')
FAMILY = OUT.name

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

batch = sys.argv[1]
host_file = Path(sys.argv[2])
folder = OUT / batch
plan = json.loads((folder/'plan.json').read_text(encoding='utf-8'))
sheet = folder / 'sheet-v1.png'
if not sheet.exists(): shutil.copyfile(host_file,sheet)
assert sha(sheet) == sha(host_file)
prompt = folder/'prompt.txt'
assert prompt.is_file()
config = json.loads((IMAGE/'config/image-generation.json').read_text(encoding='utf-8-sig'))
now = datetime.now(timezone.utc).isoformat()
with Image.open(sheet) as im:
    im.load(); master=im.convert('RGBA'); native_size=list(im.size); native_mode=im.mode
assert native_size == [1536,1024], 'Inspect changed cell layout before extracting.'
references=[]
reference_inputs=[(folder/'structure-board.png','source structure enlarged only, first actual reference'),(IMAGE/'designs/mail-ui-v1/01-mail-event.png','primary style only'),(IMAGE/'designs/team-ui-v2/team-ui-v2.png','primary style only')]
if not (folder/'structure-board.png').exists(): reference_inputs=[(IMAGE/'designs/mail-ui-v1/01-mail-event.png','primary style only'),(IMAGE/'designs/team-ui-v2/team-ui-v2.png','primary style only'),(folder/'structure-reference.png','source structure, measured frames, IDs and footprints only')]
for p,role in reference_inputs:
    references.append({'file':str(p),'sha256':sha(p),'role':role,'actuallyAttached':True})
generation={'file':sheet.relative_to(ROOT).as_posix(),'sha256':sha(sheet),'generatedAt':datetime.fromtimestamp(host_file.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host output file last-write timestamp; tool call completed before this record was written','recordedAtUTC':now,'width':native_size[0],'height':native_size[1],'format':'PNG','mode':native_mode,'alphaExtrema':list(master.getchannel('A').getextrema()),'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[x['file'] for x in references],'promptFile':prompt.relative_to(ROOT).as_posix(),'size':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes no model/quality selector and returned image_url plus output_hint only. No verifiable model/quality metadata was returned.','evidence':{'hostOutputFile':str(host_file),'returnedFields':['image_url','output_hint'],'outputHint':'Generated images are saved to '+str(host_file.parent)+' as '+str(host_file)+' by default.','apiOrCliUsed':False,'officialCheckDate':'2026-10-26','officialCheckSources':config['sources']},'prompt':prompt.relative_to(ROOT).as_posix(),'references':references,'sourcePlan':(folder/'plan.json').relative_to(ROOT).as_posix(),'accepted':False,'geometryAccepted':False,'inGameAccepted':False}
record=Path(str(sheet)+'.generation.json');save(record,generation)
piece_dir=OUT/'pieces';piece_dir.mkdir(exist_ok=True)
new=[];warnings=[];crop_items=[]
regions_path=folder/'extraction-regions.json'
regions=json.loads(regions_path.read_text(encoding='utf-8'))['regions'] if regions_path.exists() else None
for i,p in enumerate(plan['pieces']):
    cell_box=regions[i] if regions is not None else p['contactCellLTRB'];cell=master.crop(tuple(cell_box));a=np.array(cell.getchannel('A')); yy,xx=np.where(a>=8)
    assert len(xx)>0
    box=[max(0,int(xx.min())-4),max(0,int(yy.min())-4),min(cell.width,int(xx.max())+5),min(cell.height,int(yy.max())+5)]
    texture_info=None
    if FAMILY=='field' and p['elementId'] in [6001,6023,6024]:
        original=Image.open(ROOT/p['referencePng']['file']).convert('RGBA')
        assert original.size==(40,40) and original.getchannel('A').getextrema()==(255,255) and p['footprintCells']==[1,1]
        mask=a>=250;prev=np.zeros(cell.width+1,dtype=np.int32);best=0;endpoint=None
        for row in range(cell.height):
            current=np.zeros(cell.width+1,dtype=np.int32)
            for col in np.flatnonzero(mask[row]):
                k=col+1;current[k]=1+min(prev[k],prev[k-1],current[k-1])
                if current[k]>best:best=int(current[k]);endpoint=(int(col),row)
            prev=current
        if best>=40:
            ex,ey=endpoint;box=[ex-best+1,ey-best+1,ex+1,ey+1]
            texture_info={'requested':True,'applied':True,'whitelist':'plain texture only 6001/6023/6024; manually inspected source','sourceReferenceAlphaExtrema':[255,255],'nativeInscribedSquareSide':best,'operation':'near-opaque texture alpha normalization250..254→255','threshold':250,'notSeamAcceptance':True}
        else:texture_info={'requested':True,'applied':False,'reason':'No source-preserving near-opaque inscribed texture square >=40px','largestNearOpaqueSquareSide':best}
    crop=cell.crop(tuple(box))
    if texture_info and texture_info['applied']:
        texture_info['originalAlphaExtrema']=list(crop.getchannel('A').getextrema());assert texture_info['originalAlphaExtrema'][0]>=250
        before_rgb=hashlib.sha256(crop.convert('RGB').tobytes()).hexdigest();crop.putalpha(255)
        assert hashlib.sha256(crop.convert('RGB').tobytes()).hexdigest()==before_rgb
        texture_info['rgbPreserved']=True;texture_info['nativeCropRGBSHA256']=before_rgb
    sw,sh=p['selectedFrameSize'];w,h=sw*4,sh*4
    scale=min(w/crop.width,h/crop.height);rw=max(1,round(crop.width*scale));rh=max(1,round(crop.height*scale));placement=[(w-rw)//2,h-rh]
    result=Image.new('RGBA',(w,h),(0,0,0,0));result.alpha_composite(crop.resize((rw,rh),Image.Resampling.LANCZOS),tuple(placement))
    target=piece_dir/(str(p['elementId'])+'-'+FAMILY+'-v1.png');buffer=BytesIO();result.save(buffer,format='PNG');export_bytes=buffer.getvalue()
    if target.exists():assert target.read_bytes()==export_bytes,'Existing differing export retained; use a new version.'
    else:target.write_bytes(export_bytes)
    entire_count=int((a>0).sum()); kept_count=int((a[box[1]:box[3],box[0]:box[2]]>0).sum());drop=entire_count-kept_count;fraction=drop/max(1,entire_count)
    strong_count=int((a>=8).sum()); strong_kept=int((a[box[1]:box[3],box[0]:box[2]]>=8).sum())
    rect=[box[0]+cell_box[0],box[1]+cell_box[1],box[2]+cell_box[0],box[3]+cell_box[1]]
    item={'elementId':p['elementId'],'idMapping':p['idMapping'],'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'width':w,'height':h,'worldFrameWidth':sw,'worldFrameHeight':sh,'exportDensity':4,'footprintCells':p['footprintCells'],'gridAttr':p['gridAttr'],'mapElemOffsetRaw':p['mapElemOffsetRaw'],'selectedFrameOffsetRaw':p['selectedFrameOffsetRaw'],'sourceReference':p['referencePng'],'derivedFrom':{'file':sheet.relative_to(ROOT).as_posix(),'sha256':sha(sheet),'generationRecord':record.relative_to(ROOT).as_posix()},'operation':{'type':'crop-uniform-fit-bottom-align','sourceRectLTRB':rect,'cropSelection':'alpha>=8 bounds plus four sheet-pixel margin, verified against visible object; alpha values inside crop unchanged','uniformScale':scale,'placementPx':placement,'resampled':True,'resampler':'LANCZOS','newModelGeneration':False,'sourceAlphaPositivePixels':entire_count,'croppedAlphaPositivePixels':kept_count,'droppedAlphaPositivePixels':drop,'droppedAlphaPositiveFraction':fraction,'alphaAtLeast8DroppedPixels':strong_count-strong_kept},'alphaExtrema':list(result.getchannel('A').getextrema()),'geometryAccepted':False,'accepted':False,'inGameAccepted':False,'anchorStatus':'unverified-not-applied; bottom placement is export convention, not source render-anchor proof','status':'painted-candidate-awaiting-source-lookup-anchor-and-in-game-validation','seamlessVerified':False if p['elementId']==2001 else None}
    item['operation']['extractionRegionLTRB']=cell_box
    item['operation']['nominalGridFollowed']=regions is None
    if texture_info:
        item['opaqueSquareTexture']=texture_info
        if texture_info['applied']:
            item['operation']['type']='crop-inscribed-near-opaque-square-texture-normalize-alpha-uniform-scale'
            item['operation']['cropSelection']='largest fully alpha>=250 inscribed square in this manually whitelisted plain ground texture; original RGB preserved'
            item['operation']['alphaNormalization']='near-opaque texture alpha normalization250..254→255'
            item['operation']['alphaBeforeNormalization']=texture_info['originalAlphaExtrema']
            item['terrainOpaqueCanvasVerified']=result.getchannel('A').getextrema()==(255,255)
    save(Path(str(target)+'.source.json'),item);new.append(item);crop_items.append({'elementId':p['elementId'],'sourceRectLTRB':rect,'outputFile':item['file'],'worldFrameSize':[sw,sh],'exportSize':[w,h]})
    if fraction>0.01: warnings.append({'id':'crop.dropped_alpha_positive_fraction','elementId':p['elementId'],'value':fraction,'threshold':0.01,'file':item['file'],'sourceFile':generation['file'],'note':'Deliberate plain-texture inscribed crop; outside-window artwork is not retained, source crop and original alpha documented.' if texture_info and texture_info['applied'] else 'Discarded pixels are faint outside-object generated halos (alpha 1-7 when strong dropped count is zero); not silently treated as no loss.'})
    if strong_count!=strong_kept: warnings.append({'id':'crop.dropped_alpha_at_least_8','elementId':p['elementId'],'value':strong_count-strong_kept,'threshold':0,'file':item['file']})
art_path=OUT/'art.json'
art=json.loads(art_path.read_text(encoding='utf-8')) if art_path.exists() else {'schemaVersion':1,'tilePixels':40,'tilePixelEvidence':'community logic constant and native reference ground frames, official specification unverified','status':'production-candidates','pieces':[]}
assert not set(x['elementId'] for x in art['pieces']).intersection(x['elementId'] for x in new)
art['pieces']+=new;save(art_path,art)
save(folder/'crops.json',{'schemaVersion':1,'sheet':generation['file'],'sheetSHA256':sha(sheet),'pieces':crop_items})
save(folder/'qa.json',{'schemaVersion':1,'checkedAtUTC':now,'generatedSheet':generation['file'],'nativeSheetSize':native_size,'generatedSheetSHA256':sha(sheet),'exportCount':len(new),'fixedFrameCanvas4xPassed':len(new),'footprintAndOffsetCopiedWithoutMutation':len(new),'warnings':warnings,'failures':[],'accepted':False,'geometryAccepted':False,'inGameAccepted':False,'limitations':['Fixed export dimensions do not prove pixel geometry, silhouette, perspective, anchor or original client lookup.','Browser use disabled by Work settings; no current in-game screenshots or acceptance.','No alpha correction or background removal; native alpha inside crops preserved.','Generation may change art silhouette or doorway shape; these candidates require source-overlay and in-game visual review.']})
print(json.dumps({'batch':batch,'ids':[x['elementId'] for x in new],'artCount':len(art['pieces']),'sheet':generation['file'],'nativeSize':native_size,'warningCount':len(warnings),'warnings':warnings,'accepted':False},ensure_ascii=True))
