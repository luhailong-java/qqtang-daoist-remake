"""Export one explicitly specified six-cap mother, provenance and two-background diagnostics."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]


def path(value):
    result = (ROOT / value).resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError('All files must remain in this project')
    return result


def rel(value):
    return value.relative_to(ROOT).as_posix()


def digest(value):
    return hashlib.sha256(value.read_bytes()).hexdigest()


def save(target, value):
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True)
    args = parser.parse_args()
    spec_path = path(args.spec)
    spec = json.loads(spec_path.read_bytes())
    if spec['category'] != 'cap' or len(spec['items']) != 6:
        raise ValueError('One explicit six-item cap batch is required')
    folder = spec_path.parent
    contract = json.loads(path(spec['sourceContract']).read_bytes())
    references = {entry['itemId']: entry for entry in contract['items']}
    if set(references) != {entry['itemId'] for entry in spec['items']}:
        raise ValueError('Source IDs differ from selected six-item batch')
    mother_path = path(spec['mother'])
    mother = Image.open(mother_path)
    if mother.mode != 'RGBA':
        raise ValueError('Mother must have its generated RGBA alpha')
    generation_path = path(spec['generationRecord'])
    generation = json.loads(generation_path.read_bytes())
    generation.update(file=rel(mother_path), sha256=digest(mother_path), width=mother.width,
                      height=mother.height, mode=mother.mode, alphaExtrema=list(mother.getchannel('A').getextrema()),
                      cropNote=spec.get('cropNote'), actualModel=None, actualQuality=None)
    save(generation_path, generation)
    output_entries = []
    for selected in spec['items']:
        reference = references[selected['itemId']]
        if digest(path(reference['file'])) != reference['sha256'] or reference['category'] != 'cap':
            raise ValueError('Original inventory reference changed')
        rect = selected['sourceCellRect']
        if not (0 <= rect[0] < rect[2] <= mother.width and 0 <= rect[1] < rect[3] <= mother.height):
            raise ValueError('Invalid mother crop')
        crop = mother.crop(rect)
        alpha = crop.getchannel('A')
        w, h = crop.size
        edges = [(0,0,1,h),(0,0,w,1),(w-1,0,w,h),(0,h-1,w,h)]
        counts = [sum(value >= 8 for value in alpha.crop(edge).get_flattened_data()) for edge in edges]
        if any(counts):
            raise ValueError(f'{selected["itemId"]}: crop cuts visible alpha')
        bbox = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
        if not bbox:
            raise ValueError('Empty selected hat')
        content = crop.crop(bbox)
        scale = 224 / max(content.size)
        size = (round(content.width * scale), round(content.height * scale))
        painted = content.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
        placement = [(256 - size[0]) // 2, (256 - size[1]) // 2]
        output = Image.new('RGBA', (256,256))
        output.alpha_composite(painted, tuple(placement))
        visible = output.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
        if min(visible[0],visible[1],256-visible[2],256-visible[3]) < 16:
            raise ValueError('Visible inset below16px')
        target = folder / f'{selected["itemId"]}-{selected["slug"]}.png'
        output.save(target, optimize=True)
        record = {'itemId': selected['itemId'], 'category': 'cap', 'resourceId': reference['resourceId'],
                  'sourceName': reference['sourceName'], 'sourceDescription': reference['sourceDescription'],
                  'projectDisplayName': selected['name'], 'file': rel(target), 'sha256': digest(target),
                  'width':256,'height':256,'anchor':[128,128],
                  'sourceReference':reference['file'],'sourceReferenceSha256':reference['sha256'],
                  'sourceReferenceRecord':reference['file']+'.source.json',
                  'sourceInventoryNativeFrameSize':reference['nativeFrameSize'],
                  'sourceInventoryFrameOffsetRaw':reference['frameOffsetRaw'],
                  'sourceInventoryShadowNotReproduced':True,
                  'derivedFrom':{'file':rel(mother_path),'sha256':digest(mother_path),'generationRecord':rel(generation_path)},
                  'operation':{'type':'crop-uniform-fit-centred','sourceCellRect':rect,
                    'contentBoxWithinCell':list(bbox),'uniformScale':scale,'placementPx':placement,
                    'resampler':'premultiplied-alpha LANCZOS','newModelGeneration':False,
                    'sourceCropAlpha8EdgeCountsLTRB':counts},
                  'alphaExtrema':list(output.getchannel('A').getextrema()),'alpha8BBox':list(visible),
                  'warnings':[],'visualAccepted':False,'runtimeAdopted':False,'accepted':False,
                  'worldMapped':False,'status':'inventory-only-static-candidate-awaiting-user-review'}
        save(Path(str(target)+'.provenance.json'),record)
        output_entries.append(record)
    save(folder/'art.json',{'schemaVersion':1,'category':'cap','scope':'six explicit inventory candidates only',
         'sourceCategoryTotal':447,'items':output_entries,'accepted':False,'runtimeAdopted':False})
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    native=Image.new('RGB',(1680,676),'#f6f0df');draw=ImageDraw.Draw(native)
    draw.rectangle((840,48,1679,675),fill='#183e37')
    draw.text((16,12),'cap 冠帽库存候选 · 实际256px双底 · 待用户审核，非穿戴/动画验收',font=font,fill='#214a3d')
    mobile=Image.new('RGB',(900,732),'#f6f0df');mdraw=ImageDraw.Draw(mobile)
    mdraw.rectangle((540,72,899,731),fill='#183e37')
    mdraw.text((16,12),'32 / 48 / 64px 诊断预览 · 人审待定 · 非手游尺寸/挂点验收',font=font,fill='#214a3d')
    for ordinal,entry in enumerate(output_entries):
        picture=Image.open(path(entry['file'])).convert('RGBA')
        for side,color in [(0,'#214a3d'),(1,'#f4ead3')]:
            x=side*840+ordinal%3*280+12;y=48+ordinal//3*310
            native.paste(picture,(x,y+10),picture)
            draw.text((x,y+272),f'{entry["itemId"]} · {entry["projectDisplayName"]}',font=font,fill=color)
            for column,size in enumerate([32,48,64]):
                thumb=picture.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
                left=180+side*360+column*120;top=80+ordinal*108
                mobile.paste(thumb,(left+(120-size)//2,top+(64-size)//2),thumb)
                mdraw.text((left+32,top+70),str(size)+'px',font=font,fill=color)
        mdraw.text((12,ordinal*108+102),f'{entry["itemId"]} {entry["projectDisplayName"]}',font=font,fill='#214a3d')
    previews=[]
    for name,picture in [('contact-native-256.png',native),('contact-mobile-32-48-64.png',mobile)]:
        target=folder/name;picture.save(target,optimize=True)
        record={'file':rel(target),'sha256':digest(target),'inputs':[{'itemId':e['itemId'],'file':e['file'],'sha256':e['sha256']} for e in output_entries],
                'newModelGeneration':False,'runtimeScreenshot':False,'userReviewStatus':'pending',
                'operation':'standard alpha composite of real256px exports' if name.startswith('contact-native') else 'premultiplied-alpha equal-aspect32/48/64 downscale and light/dark composite',
                'sizesPx':[256] if name.startswith('contact-native') else [32,48,64]}
        save(Path(str(target)+'.source.json'),record);previews.append(record)
    qa={'schemaVersion':1,'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'category':'cap','itemIds':[e['itemId'] for e in output_entries],'candidatePngs':6,
        'errors':[],'cropNote':spec.get('cropNote'),'nativeMotherSize':list(mother.size),
        'sourceInventoryOnly':True,'actualModel':None,'actualQuality':None,
        'visualAccepted':False,'runtimeAdopted':False,'worldAnimationAccepted':False,'previews':previews}
    save(folder/'technical-qa.json',qa)
    print(json.dumps({'items':qa['itemIds'],'candidatePngs':6,'errors':[],'motherNativeSize':list(mother.size),
                      'nativeContact':rel(folder/'contact-native-256.png'),'mobileContact':rel(folder/'contact-mobile-32-48-64.png')},ensure_ascii=False))


if __name__=='__main__':
    main()
