"""Save current 1–6 supplemental map paints and preserve binary evidence/unknowns."""
from pathlib import Path
from PIL import Image
import json,sys,subprocess,shutil
OUT=Path(__file__).resolve().parent;FAMILY=OUT.parent;ROOT=OUT.parents[3];key,host=sys.argv[1:3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec_path=OUT/f'exports/batch-{key}.json';spec=read(spec_path);source=ROOT/spec['source'];existing=host=='--existing'
if not existing:shutil.copyfile(host,source)
refs=spec.get('referencePaths',[str(OUT/f'references/structure-{key}.png'),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']+spec.get('extraReferences',[]))
node='C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if not existing:subprocess.run([node,str(ROOT/'scripts/register-generated-image.mjs'),spec['source'],str((OUT/f'prompts/batch-{key}.prompt.txt').relative_to(ROOT)),host,*refs],cwd=ROOT,check=True)
record=source.with_suffix('.png.generation.json');d=read(record);d['submittedParameters']['transparent_background']=spec.get('transparent',True);d['references'][0]['purpose']='exact decoded source-frame structure and geometry reference only; no runtime source pixels'
for ref in d['references'][3:]:ref['purpose']='own project character identity reference'if'own-four-characters'in ref['path']else'previous original-painted world finish reference'
write(record,d)
if spec.get('editTarget') and not existing:subprocess.run([node,str(ROOT/'scripts/mark-generation-edit.mjs'),spec['source'],spec['editTarget']],cwd=ROOT,check=True)
mother=Image.open(source).convert('RGBA');w,h=mother.size
for n,item in enumerate(spec['items']):
    if not item.get('manualRect') and 'rect'in item:continue
    item['rect']=item.get('manualRect',[round(n%3*w/3),round(n//3*h/2),round((n%3+1)*w/3),round((n//3+1)*h/2)])
write(spec_path,spec);subprocess.run([sys.executable,str(ROOT/'scripts/export-map-art-batch.py'),str(spec_path.relative_to(ROOT))],cwd=ROOT,check=True)
index={e['elementId']:e for e in read(ROOT/spec['extraInventory'])['elements']};manifest=FAMILY/'art.json';art=read(manifest);ids={e['elementId']for e in spec['items']};qa=[]
for piece in art['pieces']:
    if piece['elementId']not in ids:continue
    e=index[piece['elementId']];original=Image.open(ROOT/e['referencePng']['file']).convert('RGBA');crop=mother.crop(piece['operation']['sourceRectLTRB'])
    ob=original.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();gb=crop.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();oa=(ob[2]-ob[0])/(ob[3]-ob[1]);ga=(gb[2]-gb[0])/(gb[3]-gb[1]);error=abs(ga/oa-1)
    warnings=['source-image-id-and-client-anchor-unverified','internal-silhouette-and-original-map-render-unverified']+(['visible-aspect-deviation-over-10-percent']if error>.1 else[])
    piece.update({'accepted':False,'sourceReference':e['referencePng'],'footprintCells':e['footprintCells'],'sourceGridAttr':e['gridAttr'],'sourceMapElemOffsetRaw':e['mapElemOffsetRaw'],'sourceFrameOffsetRaw':e['selectedFrameOffset'],'canHide':None,'canDoSpecial':None,'qa':{'sourceVisibleAspect':oa,'generatedVisibleAspect':ga,'relativeAspectDeviation':error,'warnings':warnings}})
    if piece['operation']['type']=='crop-opaque-square-texture-uniform-resize':piece['operation'].update({'originalCropAlphaExtrema':list(crop.getchannel('A').getextrema()),'referenceAlphaExtrema':list(original.getchannel('A').getextrema())})
    piece['warnings']=warnings;write(ROOT/(piece['file']+'.provenance.json'),piece);qa.append({'id':piece['elementId'],'visibleAspectDeviation':error,'binarySpecialUnknown':piece['binaryPropertyEvidence']['canDoSpecial']is None,'binaryHideUnknown':piece['binaryPropertyEvidence']['canHide']is None})
art['pieces'].sort(key=lambda e:e['elementId']);write(manifest,art);write(OUT/f'exports/batch-{key}.local-observations.json',{'scope':'current batch only; not full QA or acceptance','items':qa});print(json.dumps({'family':FAMILY.name,'currentFamilyCandidates':len(art['pieces']),'currentBatch':qa,'accepted':0}))
