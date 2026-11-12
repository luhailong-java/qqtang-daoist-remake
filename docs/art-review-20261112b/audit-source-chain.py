"""Bounded file/provenance checks for the two 2026-11-12 continuation items."""
from pathlib import Path
import datetime, hashlib, json, subprocess
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def rel(p): return p.relative_to(ROOT).as_posix()
def path(s):
    p=(ROOT/s).resolve()
    if not p.is_relative_to(ROOT): raise ValueError('Project path escaped')
    return p
def require(condition, message):
    if not condition: raise ValueError(message)
def components_at_16(image):
    width,height=image.size
    mask=bytearray(image.getchannel('A').point(lambda a:255 if a>=16 else 0).tobytes())
    count=0
    for start in range(len(mask)):
        if not mask[start]: continue
        count+=1; mask[start]=0; pending=[start]
        while pending:
            index=pending.pop(); x=index%width; y=index//width
            for yy in range(max(0,y-1),min(height,y+2)):
                for xx in range(max(0,x-1),min(width,x+2)):
                    neighbor=yy*width+xx
                    if mask[neighbor]: mask[neighbor]=0; pending.append(neighbor)
    return count
def main():
    fullp=path('assets/items/head-adornments/world-art.json'); full=read(fullp)
    base_bytes=subprocess.check_output(['git','show','84dcf46f910f331066cc587c472147f017d8fc10:'+rel(fullp)],cwd=ROOT)
    baseline=json.loads(base_bytes)
    require({k:v for k,v in full.items() if k!='items'}=={k:v for k,v in baseline.items() if k!='items'},'Existing family root fields changed')
    require({x['itemId']for x in full['items']}=={x['itemId']for x in baseline['items']}|{407,2000},'Unexpected family item change')
    for old in baseline['items']:
        require(next(x for x in full['items']if x['itemId']==old['itemId'])==old,'Existing family item changed')
    items=[]; generators={}; selected_mothers=set(); frames_checked=0
    for ident,count in [(407,18),(2000,24)]:
        mp=path(f'assets/items/head-adornments/world-{ident}-art.json'); doc=read(mp)
        require(len(doc['items'])==1,'Independent manifest contains another item')
        item=doc['items'][0]
        require(item==next(x for x in full['items']if x['itemId']==ident),'Independent/full item mismatch')
        require([f['sourceFrameIndex']for f in item['frames']]==list(range(24)),'Incomplete source position order')
        require(len({f['sha256']for f in item['frames']})==count,'Unexpected different PNG count')
        contract=read(path(item['sourceContract']))
        unique_files={}
        for frame in item['frames']:
            original=contract['frames'][frame['sourceFrameIndex']]
            require(frame['logicalFrameSize']==original['nativeFrameSize'],'Logical size changed')
            require(frame['frameOffsetRaw']==original['frameOffsetRaw'],'Source raw offset changed')
            require(all(frame.get(k) is False for k in ['visualAccepted','geometryAccepted','runtimeAdopted','accepted']),'New candidate was approved')
            require(frame.get('frameDurationMs') is None and frame.get('directionSemantic') is None,'Unknown timing/direction invented')
            p=path(frame['file']); require(sha(p)==frame['sha256'],'Export PNG hash mismatch')
            with Image.open(p)as im:
                require(im.mode=='RGBA' and list(im.size)==[n*4 for n in original['nativeFrameSize']],'Export dimensions/mode wrong')
                extrema=list(im.getchannel('A').getextrema())
                require(extrema[0]==0 and extrema[1]>=16,'No transparent/visible export pixels')
                components=components_at_16(im) if ident==2000 else None
                if ident==2000: require(components==5,'Five-heart export does not have five separated alpha components')
            pr=path(frame['provenanceRecord']); require(read(pr)==frame,'Per-position provenance mismatch')
            d=frame['derivedFrom']; require(sha(path(d['file']))==d['sha256'],'Mother image mismatch')
            selected_mothers.add(rel(path(d['file'])))
            gp=path(d['generationRecord']); generators[rel(gp)]=read(gp)
            unique_files[rel(p)]={'file':rel(p),'sha256':frame['sha256'],'extent':[frame['width'],frame['height']],'alphaExtrema':extrema,'componentsAtAlpha16':components}
            frames_checked+=1
        require(all(f['qa']['relativeAspectDeviation']<=.1 for f in item['frames']),'Aspect threshold exceeded')
        previews=[]
        for name in [f'{ident}-candidate-contact.png',f'{ident}-mobile-32-48-64.png']:
            p=OUT/name; r=read(Path(str(p)+'.source.json'))
            require(sha(p)==r.get('sha256',r.get('previewSha256')),'Preview PNG mismatch')
            if 'manifestSha256'in r: require(sha(mp)==r['manifestSha256'],'Preview independent manifest changed')
            require(r.get('userReviewStatus')=='pending','Preview falsely approved')
            previews.append({'file':rel(p),'sha256':sha(p)})
        items.append({'itemId':ident,'sourcePositions':24,'uniqueExportPngs':count,'independentManifest':rel(mp),'manifestSha256':sha(mp),'previews':previews,'exports':list(unique_files.values())})
    # Every retained generated take, including the two known rejected first takes.
    for gp in path('assets/items/head-adornments/world').glob('world-*.png.generation.json'):
        if gp.name.startswith(('world-407-','world-2000-')) and gp.name!='world-2000-a-v1.png.generation.json':
            generators[rel(gp)]=read(gp)
    generated=[]
    for name,g in sorted(generators.items()):
        p=path(g['file']); require(sha(p)==g['sha256'],'Generated master mismatch')
        with Image.open(p)as im: require(list(im.size)==[g['width'],g['height']] and im.mode=='RGBA','Native mother dimensions/mode mismatch')
        require(g.get('actualModel') is None and g.get('actualQuality') is None,'Unverified actual model/quality filled')
        submitted=g['submittedParameters']; require(submitted.get('model') is None and submitted.get('quality') is None,'Unexposed selector claimed')
        require(submitted.get('transparent_background') is True,'Actual alpha request missing')
        text=g.get('exactPrompt',g.get('submittedPrompt',g.get('prompt')))
        require(isinstance(text,str),'Exact submitted prompt missing')
        require(hashlib.sha256(text.encode()).hexdigest()==g['submittedPromptSha256'],'Exact submitted prompt hash mismatch')
        require(sha(path(g['promptFile']))==g['promptFileSha256'],'Prompt file changed')
        for ref in g['references']: require(sha(path(ref['path']))==ref['sha256'],'Generation reference changed')
        edit=g.get('editOf')
        if edit:
            require(sha(path(edit['file']))==edit['sha256'],'Edit target changed')
            if edit.get('generationRecordSha256'): require(sha(path(edit['generationRecord']))==edit['generationRecordSha256'],'Edit target generation record changed')
        generated.append({'file':g['file'],'sha256':g['sha256'],'generationRecord':name,'generationRecordSha256':sha(path(name)),'referencedByCurrentCandidates':rel(p) in selected_mothers,'actualModel':None,'actualQuality':None})
    calls=read(OUT/'407-builtin-submissions.json')['calls']
    for c in calls:
        g=read(path('assets/items/head-adornments/world/world-'+c['key']+'.png.generation.json'))
        require(g['exactPrompt']==c['input']['prompt'],'407 actual tool prompt differs')
        require(c['input']['transparent_background'] is True,'407 alpha request differs')
        actual=[str(path(r['path'])).replace('\\','/')for r in g['references']]
        require(actual==c['input']['referenced_image_paths'],'407 actual tool reference order differs')
    heart_calls=read(OUT/'2000-builtin-submissions.json')['entries']
    require(len(heart_calls)==14,'Missing heart tool submission evidence')
    for c in heart_calls:
        g=read(path(c['file']+'.generation.json'))
        require(g['exactPrompt']==c['prompt'],'2000 actual tool prompt differs')
        require(g['submittedPromptSha256']==c['actualSubmittedPromptSha256'],'2000 actual prompt hash differs')
        require(c['submittedParameters']['transparent_background'] is True,'2000 alpha request differs')
        actual=[str(path(r['path'])).replace('\\','/')for r in g['references']]
        require(actual==c['submittedParameters']['referenced_image_paths'],'2000 actual tool reference order differs')
    approved=[]
    for item in baseline['items']:
        for f in item['frames']:
            if f.get('visualAccepted') is True:
                p=path(f['file']); require(sha(p)==f['sha256'],'Previously approved pixels changed')
                approved.append({'itemId':item['itemId'],'sourceFrameIndex':f['sourceFrameIndex'],'file':f['file'],'sha256':f['sha256']})
    result={'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'48 source positions of two new items, their retained generated masters and diagnostic previews; file/data checks only','sourcePositionsChecked':frames_checked,'newUniqueExportPngs':42,'items':items,'generatedMasters':generated,'existingFamilyItemsUnchanged':len(baseline['items']),'priorStaticApprovedPositionsUnchanged':approved,'fullManifestSha256':sha(fullp),'visualAccepted':False,'runtimeAdopted':False,'errors':[]}
    target=OUT/'source-chain-file-audit.json'; target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sourcePositions':frames_checked,'generatedMasters':len(generated),'priorApprovedPositions':len(approved),'newUniquePngs':42,'errors':[]}))
if __name__=='__main__':main()
