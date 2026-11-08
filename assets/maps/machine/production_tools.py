"""Data/provenance/image assembly checks only. Painting uses image_gen separately."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,sys,copy,shutil,datetime
ROOT=Path(__file__).resolve().parents[3]
FOLDER=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bounds(image):return image.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox()
inventory={e['elementId']:e for e in read(ROOT/'assets/maps/production-index.json')['elements']}
manifest=read(FOLDER/'art.json')
if sys.argv[1]=='enrich':
    spec=read(ROOT/sys.argv[2]);ids={e['elementId']for e in spec['items']}
    record_path=ROOT/(spec['source']+'.generation.json');record=read(record_path)
    for ref in record['references']:
        if '/references/structure-'in ref['path'].replace('\\','/'):ref['purpose']='exact source structure/aspect reference only; not runtime art'
        elif '/props-'in ref['path'].replace('\\','/'):ref['purpose']='previous original-painted family material/finish reference'
    write(record_path,record)
    for p in manifest['pieces']:
        if p['elementId']not in ids:continue
        e=inventory[p['elementId']];original=Image.open(ROOT/e['referencePng']['file']).convert('RGBA')
        mother=Image.open(ROOT/spec['source']).convert('RGBA');crop=mother.crop(p['operation']['sourceRectLTRB']);ob=bounds(original);gb=bounds(crop)
        oa=(ob[2]-ob[0])/(ob[3]-ob[1]);ga=(gb[2]-gb[0])/(gb[3]-gb[1]);error=abs(ga/oa-1)
        p.update({'sourceReference':e['referencePng'],'footprintCells':e['footprintCells'],'sourceGridAttr':e['gridAttr'],'sourceMapElemOffsetRaw':e['mapElemOffsetRaw'],'sourceFrameOffsetRaw':e['selectedFrameOffsetRaw'],'accepted':False,
            'qa':{'sourceVisibleAspect':oa,'generatedVisibleAspect':ga,'relativeAspectDeviation':error,'coreTouchesCellEdge':False,'warnings':['source-id-lookup-and-render-anchor-unverified','original-map-geometry-and-in-game-validation-pending']+(['visible-proportions-differ-more-than-10-percent']if error>.1 else [])}})
        p['visibleAspectRatioRelativeError']=error;p['warnings']=p['qa']['warnings']
        if p['operation']['type']=='crop-opaque-square-texture-uniform-resize':
            p['operation']['originalCropAlphaExtrema']=list(crop.getchannel('A').getextrema());p['operation']['referenceAlphaExtrema']=list(original.getchannel('A').getextrema())
        write(ROOT/(p['file']+'.provenance.json'),p)
    manifest['pieces'].sort(key=lambda p:p['elementId']);write(FOLDER/'art.json',manifest)
    print(json.dumps({'enriched':len(ids),'pieces':len(manifest['pieces'])}))
elif sys.argv[1]in('audit','alias'):
    source={k:v for k,v in inventory.items()if v['family']==FOLDER.name};painted={p['elementId']:p for p in manifest['pieces']};aliases=[]
    for ident,e in source.items():
        if ident in painted:continue
        representative=next((key for key,p in painted.items()if source[key]['referencePng']['sha256']==e['referencePng']['sha256']and source[key]['selectedFrameSize']==e['selectedFrameSize']),None)
        if representative is None:continue
        p=copy.deepcopy(painted[representative]);target=FOLDER/'pieces'/f'{ident}-{FOLDER.name}-source-alias-v1.png';shutil.copyfile(ROOT/p['file'],target)
        p.update({'elementId':ident,'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'sourceReference':e['referencePng'],'footprintCells':e['footprintCells'],'sourceGridAttr':e['gridAttr'],'sourceMapElemOffsetRaw':e['mapElemOffsetRaw'],'sourceFrameOffsetRaw':e['selectedFrameOffsetRaw'],'sourcePictureAliasOfElementId':representative,'accepted':False})
        p['operation']={'type':'same-source-picture-original-paint-reuse','newModelGeneration':False,'resampled':False,'sourcePaintedFile':painted[representative]['file'],'sourcePaintedSha256':painted[representative]['sha256']}
        write(target.with_suffix('.png.provenance.json'),p);painted[ident]=p;manifest['pieces'].append(p);aliases.append({'elementId':ident,'representative':representative})
    manifest['pieces'].sort(key=lambda p:p['elementId']);write(FOLDER/'art.json',manifest)
    if sys.argv[1]=='alias':
        print(json.dumps({'family':FOLDER.name,'painted':len(painted),'required':len(source),'newAliases':aliases,'fullAuditDeferred':True}));raise SystemExit(0)
    errors=[];warnings=[]
    for ident,p in painted.items():
        e=source[ident];path=ROOT/p['file'];im=Image.open(path);rec=path.with_suffix('.png.provenance.json');original=Image.open(ROOT/e['referencePng']['file']).convert('RGBA')
        tests={'hash':sha(path)==p['sha256'],'size':im.size==tuple(v*4 for v in e['selectedFrameSize']),'rgba':im.mode=='RGBA','provenance':rec.is_file(),'footprint':p.get('footprintCells')==e['footprintCells'],'gridattr':p.get('sourceGridAttr')==e['gridAttr'],'offset':p.get('sourceMapElemOffsetRaw')==e['mapElemOffsetRaw'],'not-accepted':p.get('geometryAccepted')is False}
        for test,ok in tests.items():
            if not ok:errors.append({'elementId':ident,'check':test,'file':p['file']})
        deviation=p.get('qa',{}).get('relativeAspectDeviation',p.get('visibleAspectRatioRelativeError',0))
        if deviation>.1:warnings.append({'elementId':ident,'check':'visible-aspect-deviation','value':deviation,'threshold':.1,'file':p['file']})
        if p.get('qa',{}).get('coreTouchesCellEdge'):warnings.append({'elementId':ident,'check':'core-touches-source-cell-edge','value':True,'threshold':False,'file':p['file']})
        if original.getchannel('A').getextrema()==(255,255):
            alpha=im.getchannel('A');edge=[alpha.crop((0,0,im.width,1)),alpha.crop((0,im.height-1,im.width,im.height)),alpha.crop((0,0,1,im.height)),alpha.crop((im.width-1,0,im.width,im.height))]
            if any(x.getextrema()[0]<255 for x in edge):warnings.append({'elementId':ident,'check':'opaque-reference-outer-edge-has-transparency','value':alpha.getextrema()[0],'threshold':255,'file':p['file']})
    sheets=[]
    for f in sorted(FOLDER.glob('*.png.generation.json')):
        d=read(f);sheets.append({'file':d['file'],'size':[d['width'],d['height']],'generationRecord':f.relative_to(ROOT).as_posix()})
    qa={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'family':FOLDER.name,'sourceDefinitions':len(source),'paintedDefinitions':len(painted),'pending':sorted(set(source)-set(painted)),'acceptedCount':0,'generatedSheets':sheets,'newAliases':aliases,'errors':errors,'unpassedChecks':warnings,'globalUnpassedChecks':['source-lookup-and-anchor-unverified','internal-region-and-silhouette-match-pending','seams-and-repeat-pending','in-game-and-original-client-comparison-pending']}
    write(FOLDER/'qa.json',qa)
    cols=4;cw,ch=420,300;rows=(len(painted)+cols-1)//cols;board=Image.new('RGB',(cols*cw,rows*ch),(242,238,224));draw=ImageDraw.Draw(board);font=ImageFont.load_default(size=15)
    for n,(ident,p)in enumerate(sorted(painted.items())):
        x=n%cols*cw;y=n//cols*ch;draw.text((x+10,y+8),f'{ident} source | original paint candidate',fill=(25,55,40),font=font)
        for k,im in enumerate([Image.open(ROOT/source[ident]['referencePng']['file']).convert('RGBA'),Image.open(ROOT/p['file']).convert('RGBA')]):
            scale=min(185/im.width,245/im.height);im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS);board.paste(im,(x+k*210+(210-im.width)//2,y+40+(245-im.height)//2),im)
    board.save(FOLDER/'candidate-contact.png');write(FOLDER/'candidate-contact.png.source.json',{'operation':'source-and-current-painted-image-inspection-composite','newModelGeneration':False,'file':(FOLDER/'candidate-contact.png').relative_to(ROOT).as_posix(),'sha256':sha(FOLDER/'candidate-contact.png'),'notRuntimeArt':True,'inputs':[{'file':p['file'],'sha256':p['sha256']}for p in painted.values()]})
    lines=[f'# {FOLDER.name} 原创场景候选','',f"{qa['checkedAt'][:10]}：{len(painted)}/{len(source)}源元素定义已有候选，{len(sheets)}张内置生成母图，全部accepted:false。不是原版认证或整图验收。",'','## 来源与导出','','每次生图均实际附源结构参考和邮件／组队两张主风格图，按道家Q版高清手绘制作。实际型号与质量宿主未披露，逐图记null。原帧尺寸×4为加工导出，不是原生4倍模型细节。占地、GridAttr和偏移保留，生成、裁切、缩放与图片复用分别记录。','','- art.json：当前候选和逐件来源。','- pieces/*.provenance.json：源矩形、缩放、alpha及检查。','- *.generation.json：逐图实际输入、输出、配置与未知字段。','- qa.json：完整技术错误和未通过项。','- candidate-contact.png：源／新画并排检查图，不是游戏截图。','','## 具体未通过','','|ID|检查|值|门槛|文件|','|---|---|---:|---:|---|']
    for w in warnings:lines.append(f"|{w['elementId']}|{w['check']}|{w['value']}|{w['threshold']}|{Path(w['file']).name}|")
    lines+=['','源ID真实查找、锚点、内部轮廓区界、接缝与运行尺度仍待验；粗比例低于阈值也不能视为正式通过。浏览器终验由主项目协调，不写入虚假通过。']
    (FOLDER/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps({'family':FOLDER.name,'painted':len(painted),'required':len(source),'errors':errors,'warnings':len(warnings)}))
    if errors:raise SystemExit(1)
