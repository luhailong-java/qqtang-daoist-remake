"""Deterministic reference contacts/provenance/crops only; never generates art.
All painting is performed separately through the host's built-in image_gen.
"""
import argparse
import datetime
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/maps/mine'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path):return Path(path).relative_to(ROOT).as_posix()
def box(image,threshold=16):return image.getchannel('A').point(lambda v:255 if v>threshold else 0).getbbox()

def reference(args):
    ids=[int(value)for value in args.ids.split(',')]
    by={item['elementId']:item for item in read(ROOT/'assets/maps/production-index.json')['elements']}
    sheet=Image.new('RGB',(args.width,args.height),(238,238,232));draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=13 if args.cols>=5 else 18)
    records=[];cw=args.width//args.cols;ch=args.height//args.rows
    for i,identity in enumerate(ids):
        item=by[identity];x=(i%args.cols)*cw;y=(i//args.cols)*ch
        draw.rectangle((x+3,y+3,x+cw-4,y+ch-4),outline=(155,160,150),width=2)
        fw,fh=item['selectedFrameSize'];w,h=item['footprintCells']
        draw.text((x+12,y+9),f'ID {identity} | frame {fw}x{fh}',fill=(20,35,24),font=font)
        draw.text((x+12,y+34),f'footprint {w}x{h}; SOURCE ONLY',fill=(90,45,30),font=font)
        image=Image.open(ROOT/item['referencePng']['file']).convert('RGBA');scale=min(4,(cw-40)/image.width,(ch-90)/image.height)
        size=(round(image.width*scale),round(image.height*scale));display=image.resize(size,Image.Resampling.NEAREST)
        px=x+(cw-display.width)//2;py=y+70+(ch-80-display.height)//2;sheet.paste(display,(px,py),display)
        records.append({'elementId':identity,'sourceReference':item['referencePng'],'nativeFrameSize':[fw,fh],'footprintCells':[w,h],'imageOffsetRaw':item['mapElemOffsetRaw'],'frameOffsetRaw':item['selectedFrameOffsetRaw'],'gridAttr':item['gridAttr'],'contactCellLTRB':[x,y,x+cw,y+ch],'inspectionScale':scale,'inspectionImageRectLTRB':[px,py,px+display.width,py+display.height]})
    destination=OUT/f'references/mine-batch-{args.batch}-structure.png';sheet.save(destination)
    write(destination.with_suffix('.json'),{'file':rel(destination),'sha256':sha(destination),'operation':'source-frame-labelled-contact-only-nearest-inspection-enlargement','mapping':'candidate-filename-inference','sourcePixelsAreRuntimeArt':False,'rows':args.rows,'cols':args.cols,'items':records})
    print(json.dumps({'file':rel(destination),'ids':ids,'size':sheet.size}))

def adopt(args):
    source=Path(args.image);destination=OUT/f'props-{args.batch}-v1.png'
    if destination.exists():raise ValueError('New version required: destination exists')
    shutil.copyfile(source,destination)
    image=Image.open(destination).convert('RGBA');contact=read(OUT/f'references/mine-batch-{args.batch}-structure.json')
    primary=['D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']
    refs=[{'path':path,'sha256':sha(path),'purpose':'primary-user-confirmed-art-style'}for path in primary]+[{'path':contact['file'],'sha256':contact['sha256'],'purpose':'source-structure-aspect-and-footprint-only'}]
    record={'file':rel(destination),'sha256':sha(destination),'generatedAt':args.time,'timeEvidence':'clock-tool-after-host-result','width':image.width,'height':image.height,'format':'PNG','mode':'RGBA','art_source':'host_image','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read('D:/work/image/config/image-generation.json'),'officialRecheckedOn':'2026-10-26','submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[r['path']for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际模型/质量；无model/quality选择参数。','evidence':{'toolOutputFile':source.as_posix(),'resultId':source.stem,'toolOutputFields':['image_url','output_hint'],'explicitModelOrQualityReturned':False},'prompt':f'assets/maps/mine/batch-{args.batch}.prompt.txt','references':refs,'nativeAlphaExtrema':image.getchannel('A').getextrema(),'nativeDimensionsNotExportDimensions':True}
    write(destination.with_suffix('.png.generation.json'),record)
    print(json.dumps({'file':rel(destination),'nativeSize':image.size,'alpha':record['nativeAlphaExtrema']}))

def extract(args):
    source=OUT/f'props-{args.batch}-v1.png';image=Image.open(source).convert('RGBA');record=read(source.with_suffix('.png.generation.json'));contact=read(OUT/f'references/mine-batch-{args.batch}-structure.json')
    rows=args.rows or contact.get('rows',2);cols=args.cols or contact.get('cols',3)
    measured=read(Path(args.boxes)) if args.boxes else None
    cw=image.width/cols;ch=image.height/rows;pieces=[]
    for index,item in enumerate(contact['items']):
        if measured:left,top,right,bottom=measured[index]
        else:left=round((index%cols)*cw);top=round((index//cols)*ch);right=round((index%cols+1)*cw);bottom=round((index//cols+1)*ch)
        if not(0<=left<right<=image.width and 0<=top<bottom<=image.height):raise ValueError('Crop bounds outside native image')
        cell=image.crop((left,top,right,bottom));core=box(cell)
        if not core:raise ValueError(f'Blank generated cell {index}')
        bounds=(max(0,core[0]-2),max(0,core[1]-2),min(cell.width,core[2]+2),min(cell.height,core[3]+2))
        absolute=[left+bounds[0],top+bounds[1],left+bounds[2],top+bounds[3]];crop=image.crop(absolute)
        fw,fh=item['nativeFrameSize'];target=(fw*4,fh*4);scale=min(target[0]/crop.width,target[1]/crop.height);size=(round(crop.width*scale),round(crop.height*scale));art=crop.resize(size,Image.Resampling.LANCZOS)
        placement=((target[0]-size[0])//2,target[1]-size[1]);canvas=Image.new('RGBA',target,(0,0,0,0));canvas.alpha_composite(art,placement)
        destination=OUT/f"pieces/{item['elementId']}-mine-v1.png"
        if destination.exists():raise ValueError('Refusing overwrite: '+str(destination))
        canvas.save(destination)
        original=Image.open(ROOT/item['sourceReference']['file']).convert('RGBA');ob=box(original);gb=box(crop)
        oa=(ob[2]-ob[0])/(ob[3]-ob[1]);ga=(gb[2]-gb[0])/(gb[3]-gb[1]);deviation=abs(ga/oa-1)
        warnings=['source-id-lookup-and-render-anchor-unverified','original-map-geometry-and-in-game-validation-pending']
        if deviation>.10:warnings.append(f'generated-visible-aspect-deviation-{deviation:.3f}-exceeds-0.100-review-required')
        edge=core[0]==0 or core[1]==0 or core[2]==cell.width or core[3]==cell.height
        if edge:warnings.append('visible-core-touches-generated-cell-edge-review-required')
        piece={'elementId':item['elementId'],'idMapping':'candidate-filename-inference','file':rel(destination),'sha256':sha(destination),'width':target[0],'height':target[1],'worldFrameWidth':fw,'worldFrameHeight':fh,'exportDensity':4,
               'derivedFrom':{'file':rel(source),'sha256':record['sha256'],'generationRecord':rel(source.with_suffix('.png.generation.json'))},
               'operation':{'type':'crop-uniform-fit-bottom-align','sourceRectLTRB':absolute,'uniformScale':scale,'placementPx':list(placement),'resampled':True,'newModelGeneration':False,'boxPolicy':'measured-separated-objects-after-host-layout-deviation' if measured else 'nominal-grid-then-measured-alpha-core'},
               'sourceReference':item['sourceReference'],'footprintCells':item['footprintCells'],'sourceGridAttr':item['gridAttr'],'sourceMapElemOffsetRaw':item['imageOffsetRaw'],'sourceFrameOffsetRaw':item['frameOffsetRaw'],'alphaExtrema':canvas.getchannel('A').getextrema(),'geometryAccepted':False,'status':'painted-candidate-awaiting-source-lookup-anchor-and-in-game-validation','seamlessVerified':None,
               'qa':{'sourceVisibleAspect':oa,'generatedVisibleAspect':ga,'relativeAspectDeviation':deviation,'generatedCellLTRB':[left,top,right,bottom],'coreTouchesCellEdge':edge,'warnings':warnings}}
        write(destination.with_suffix('.png.provenance.json'),piece);pieces.append(piece)
    manifest=read(OUT/'art.json') if (OUT/'art.json').exists() else {'schemaVersion':1,'tilePixels':40,'tilePixelEvidence':'community logic constant; official specification unverified','status':'production-candidates','pieces':[]}
    existing={piece['elementId'] for piece in manifest['pieces']}
    if any(piece['elementId']in existing for piece in pieces):raise ValueError('Duplicate element assignment')
    manifest['pieces'].extend(pieces);manifest['pieces'].sort(key=lambda piece:piece['elementId']);write(OUT/'art.json',manifest)
    print(json.dumps([{'id':p['elementId'],'size':[p['width'],p['height']],'aspectDeviation':round(p['qa']['relativeAspectDeviation'],3),'edge':p['qa']['coreTouchesCellEdge']}for p in pieces]))

parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
p=sub.add_parser('reference');p.add_argument('--batch',required=True);p.add_argument('--ids',required=True);p.add_argument('--rows',type=int,default=2);p.add_argument('--cols',type=int,default=3);p.add_argument('--width',type=int,default=1536);p.add_argument('--height',type=int,default=1024)
p=sub.add_parser('adopt');p.add_argument('--batch',required=True);p.add_argument('--image',required=True);p.add_argument('--time',required=True)
p=sub.add_parser('extract');p.add_argument('--batch',required=True);p.add_argument('--rows',type=int);p.add_argument('--cols',type=int);p.add_argument('--boxes')
args=parser.parse_args();{'reference':reference,'adopt':adopt,'extract':extract}[args.command](args)
