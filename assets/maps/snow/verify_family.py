from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import hashlib,json,math
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
FAMILY=OUT.name
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
art=json.loads((OUT/'art.json').read_text(encoding='utf-8'))
index=json.loads((ROOT/'assets/maps/production-index.json').read_text(encoding='utf-8'))
source={e['elementId']:e for e in index['elements'] if e.get('family')==FAMILY}
pieces=sorted(art['pieces'],key=lambda x:x['elementId'])
assert len({p['elementId'] for p in pieces})==len(pieces)
failures=[];warnings=[];inputs=[];checks=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
cols=7;cw=240;ch=250
canvas=Image.new('RGB',(cols*cw,80+math.ceil(len(pieces)/cols)*ch),'#f4f3ed');draw=ImageDraw.Draw(canvas)
draw.text((18,12),FAMILY.upper()+' | SOURCE REFERENCE (left) / OWN PAINTED CANDIDATE (right)',fill='#184536',font=font)
draw.text((18,42),'Mechanical equal-frame comparison; inspection scaling only. Geometry, anchors, tile seams and in-game acceptance FALSE.',fill='#a14426',font=small)
for i,p in enumerate(pieces):
    eid=p['elementId'];s=source[eid];file=ROOT/p['file'];sidecar=Path(str(file)+'.source.json')
    assert sha(file)==p['sha256'] and sidecar.is_file()
    assert all(p[k]==s[k] for k in ['footprintCells','gridAttr','mapElemOffsetRaw','selectedFrameOffsetRaw'])
    with Image.open(file) as im: im.load();new=im.convert('RGBA')
    assert new.size==(s['selectedFrameSize'][0]*4,s['selectedFrameSize'][1]*4)
    assert not p['geometryAccepted'] and not p['accepted']
    old=Image.open(ROOT/s['referencePng']['file']).convert('RGBA')
    def bounds(im):
        yy,xx=np.where(np.array(im.getchannel('A'))>=8)
        return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
    ob,nb=bounds(old),bounds(new);old_aspect=(ob[2]-ob[0])/(ob[3]-ob[1]);new_aspect=(nb[2]-nb[0])/(nb[3]-nb[1]);aspect_error=abs(new_aspect/old_aspect-1)
    if aspect_error>0.05: warnings.append({'id':'visible.aspect_relative_difference','elementId':eid,'value':aspect_error,'threshold':0.05,'file':p['file'],'sourceFile':s['referencePng']['file'],'note':'Pixel envelope aspect differs; fixed canvas does not prove source silhouette.'})
    ground=(eid in [2001,2013,2017,2018] or eid>=2020 and eid not in [2040,2041]) if FAMILY=='snow' else False
    if ground:
        a=np.array(new.getchannel('A'));edge=np.concatenate([a[0,:],a[-1,:],a[:,0],a[:,-1]]);n=int((edge<8).sum())
        if n: warnings.append({'id':'terrain.transparent_outer_edge_pixels','elementId':eid,'value':n,'threshold':0,'file':p['file'],'note':'Export has transparent margin/edge pixels. Full-fill terrain and seam acceptance NOT passed.'})
    checks.append({'elementId':eid,'file':p['file'],'sha256':sha(file),'frameCanvas4x':True,'definitionMetadataRetained':True,'sourceVisibleBoundsAlpha8':ob,'candidateVisibleBoundsAlpha8':nb,'visibleAspectRelativeDifference':aspect_error,'geometryAccepted':False})
    inputs.append({'file':p['file'],'sha256':sha(file),'sourceReference':s['referencePng']})
    x=i%cols*cw;y=80+i//cols*ch;draw.rectangle((x+1,y+1,x+cw-2,y+ch-2),outline='#bac7bd')
    draw.text((x+10,y+10),str(eid)+' | '+str(old.width)+'x'+str(old.height)+' | '+str(s['footprintCells']),fill='#203f34',font=small)
    scale=min(2,100/old.width,170/old.height);w,h=round(old.width*scale),round(old.height*scale)
    for image,left in [(old.resize((w,h),Image.Resampling.NEAREST),x+10),(new.resize((w,h),Image.Resampling.LANCZOS),x+130)]:
        top=y+210-h;canvas.paste(image,(left,top),image)
    draw.text((x+10,y+220),'REF ONLY',fill='#8b4a31',font=small);draw.text((x+130,y+220),'CANDIDATE',fill='#174a37',font=small)
preview=OUT/'comparison-overview.png';canvas.save(preview)
save(Path(str(preview)+'.source.json'),{'file':preview.relative_to(ROOT).as_posix(),'sha256':sha(preview),'operation':'mechanical source/candidate side-by-side contact, equal reference-frame inspection scale, no model generation','width':canvas.width,'height':canvas.height,'inputs':inputs,'newModelGeneration':False})
crop_warnings=[]
for qp in sorted(OUT.glob('batch-*/qa.json')):
    q=json.loads(qp.read_text(encoding='utf-8'));crop_warnings.extend(q['warnings'])
generations=sorted(OUT.glob('batch-*/sheet-v1.png.generation.json'))
report={'schemaVersion':1,'family':FAMILY,'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'sourceDefinitionCount':len(source),'paintedCandidateDefinitions':len(pieces),'remainingWithoutCandidate':sorted(set(source)-{p['elementId'] for p in pieces}),'uniquePaintedPictureHashes':len({p['sha256'] for p in pieces}),'nativeGenerationSheetCount':len(generations),'generationFailureCount':0,'technicalFileAndMetadataChecks':len(checks),'technicalFailures':failures,'visualWarnings':warnings,'cropWarnings':crop_warnings,'accepted':False,'geometryAccepted':False,'seamlessVerified':False,'inGameAccepted':False,'checks':checks,'preview':preview.relative_to(ROOT).as_posix(),'limitations':['Candidate coverage is not visual/geometry acceptance.','Bounds-aspect diagnostic does not compare detailed silhouette or road masks.','All family/element lookups remain candidate and source authenticity unverified.','Browser is disabled in Work settings; no game-integration acceptance.']}
save(OUT/'validation.json',report)
lines=['# '+FAMILY+' 地图美术候选交付','',f'2026-10-26：现有源定义 {len(source)} 项，本目录已有 {len(pieces)} 项候选、{len(set(p["sha256"] for p in pieces))} 张不同画面、{len(generations)} 张内置生成母图。生成入口失败 0 次。**accepted／geometryAccepted／seamlessVerified／inGameAccepted 全为 false。**','',
'[源图／自有候选并排概览](comparison-overview.png) · [逐件清单](art.json) · [本族核验](validation.json)','',
'原始 frame 尺寸乘四作为导出画布，footprintCells、gridAttr、mapElemOffsetRaw、selectedFrameOffsetRaw 原样保留。裁切与统一缩放是派生处理，不是模型原生细节或几何验收；没有修改任何地图文件、全局生产索引或客户端代码。当前底图边缘有透明留白，部分可见外形比例与源不同，需后续返修／拼接核验，不能投入最终地图验收。','',
'每次生图前实际重读 image 的 AGENTS、统一配置及执行策略，实际附上邮件主参考、组队主参考和该批结构 contact。配置快照目标 gpt-image-2.5-sunburst／max；工具没有 model／quality 参数，返回未披露这两个字段，所有实际提交／返回型号和质量仍为 null。官方核对依据：[模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)、[图像参数](https://developers.openai.com/api/reference/resources/images/methods/generate)。本任务未用 API／CLI 生图。','',
'## 母图与记录','', '| 批次 | 元素 ID | 原生母图 | 记录与裁切 |','|---|---|---|---|']
for gp in generations:
    q=json.loads((gp.parent/'plan.json').read_text(encoding='utf-8'));bn=gp.parent.name
    lines.append(f'| {bn} | '+', '.join(str(p['elementId']) for p in q['pieces'])+f' | [{bn}/sheet-v1.png]({bn}/sheet-v1.png) | [generation]({bn}/sheet-v1.png.generation.json) · [crops]({bn}/crops.json) · [qa]({bn}/qa.json) |')
lines+=['','Snow 的 2012 与 2003 是源 visibleContentSHA／frame 尺寸已核对的同图别名，复用已新画的 2003 PNG，2012 自身规则字段单独保留；没有额外模型生成。' if FAMILY=='snow' else '',
'','## 未通过的检查，逐条记录','', '以下 WARN 不是通过记录。alpha-positive 裁切告警统计的是所有 alpha>0 像素；每批 qa 另外记录 alpha>=8 实物像素丢失数。极低 alpha 的外光晕没有静默改成“无损”。可见比例与地面边缘诊断详见 validation.json。','', '| id | 元素 | value | threshold | 文件 |','|---|---:|---:|---:|---|']
for w in crop_warnings+warnings: lines.append('| '+w['id']+' | '+str(w['elementId'])+' | '+str(w['value'])+' | '+str(w['threshold'])+' | `'+w['file']+'` |')
lines+=['','当前技术核验只证明文件可读、SHA 正确、画布及规则元数据保留。原版文件身份、ID 查找、细分轮廓、建筑入口、纹理遮挡、无缝、碰撞与实机视觉仍未通过。角色与其他地图族不在本目录的修改范围。','',
'## 诊断与边界','', 'doctor.json 保留本任务依赖诊断，host_image 可用。Bundled Python 的 path／scipy／stdout／files 项为 WARN，resvg、FFmpeg、API keys 和 Grok 为 MISSING；本任务仅作 PNG 素材与内置生成，不安装这些无关依赖、不验证收费路线。没有运行视频或 SVG 生图。','']
(OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'family':FAMILY,'definitions':len(source),'candidates':len(pieces),'missing':report['remainingWithoutCandidate'],'uniqueHashes':report['uniquePaintedPictureHashes'],'nativeSheets':len(generations),'technicalChecks':len(checks),'cropWarningCount':len(crop_warnings),'visualWarningCount':len(warnings),'accepted':False,'preview':str(preview)},ensure_ascii=True))
