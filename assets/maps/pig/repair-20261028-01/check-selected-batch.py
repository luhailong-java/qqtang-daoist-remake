"""Necessary six-image comparison for only9012/8015/8016, no family scan."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
inventory={p['elementId']:p for p in json.loads((ROOT/'assets/maps/production-index.json').read_text(encoding='utf-8'))['elements']}
targets=[('pig',9012),('bun',8015),('bun',8016)]
canvas=Image.new('RGB',(1536,640),(226,229,225));draw=ImageDraw.Draw(canvas);rows=[]
for i,(family,ident)in enumerate(targets):
    manifest=ROOT/f'assets/maps/{family}/art.json';art=json.loads(manifest.read_text(encoding='utf-8'))
    current=next(p for p in art['pieces']if p['elementId']==ident);entry=inventory[ident]
    source=ROOT/entry['referencePng']['file'];file=ROOT/current['file']
    assert current['worldFrameWidth']==entry['selectedFrameSize'][0] and current['worldFrameHeight']==entry['selectedFrameSize'][1]
    assert current['sourceFootprintCells']==entry['footprintCells'] and current['sourceMapElemOffset']==entry['mapElemOffsetRaw']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==current['sha256']
    with Image.open(source)as s,Image.open(file)as n:
        old=s.convert('RGBA');new=n.convert('RGBA');assert new.size==tuple(v*4 for v in old.size)
        threshold=new.getchannel('A').point(lambda a:255 if a>8 else 0);bbox=threshold.getbbox()
        checks={'outputNativeSize':list(new.size),'sourceFrameSize':list(old.size),'outputAlphaExtrema':list(new.getchannel('A').getextrema()),'outputAlpha8BBox':list(bbox),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest()}
        if ident==8015:checks['bottomCenterGapRGBA']=list(new.getpixel((80,130)))
        if ident==8016:
            checks['topCenterGapRGBA']=list(new.getpixel((80,8)));checks['bottomCenterPanelRGBA']=list(new.getpixel((80,130)))
        x=i*512;draw.text((x+20,20),f'ID {ident}  SOURCE x4 / CURRENT x1',fill=(30,50,40))
        draw.text((x+20,45),f'ratio error {current["visibleAspectRatioRelativeError"]*100:.2f}% / not accepted',fill=(70,70,70))
        canvas.paste(old.resize(new.size,Image.Resampling.NEAREST),(x+50,105),old.resize(new.size,Image.Resampling.NEAREST))
        canvas.paste(new,(x+280,105),new)
        # Dark-background copy is diagnostic compositing only, not a new game asset.
        draw.rectangle((x+24,360,x+488,616),fill=(33,46,44));canvas.paste(new,(x+170,380),new)
    current['sourceGridAttr']=entry['gridAttr']
    current['unchangedSourceLogicEvidence']={'footprint':entry['footprintCells'],'offset':entry['mapElemOffsetRaw'],'gridAttr':entry['gridAttr'],'lifeTime':entry['lifeTime'],'canMove':entry['canMove']}
    current['singleBatchCheck']='assets/maps/pig/repair-20261028-01/selected-batch-check.json'
    Path(str(file)+'.provenance.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows.append({'elementId':ident,'currentFile':current['file'],'visibleAspectRatioRelativeError':current['visibleAspectRatioRelativeError'],'unchangedFootprintOffsetGridAttr':True,'geometryAccepted':False,'checks':checks})
canvas.save(OUT/'selected-batch-preview.png')
report={'onlySelectedIDs':[9012,8015,8016],'distinctImagesDecoded':6,'fullFamilyQA':False,'buildOrRuntimeTest':False,'nonUniformScaleUsed':False,'newGameLogicAdded':False,'geometryAccepted':False,'rows':rows,'preview':'assets/maps/pig/repair-20261028-01/selected-batch-preview.png','previewOperation':'diagnostic alpha compositing of existing source and current exported PNG; no new art generation'}
(OUT/'selected-batch-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
