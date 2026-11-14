"""Export room-extra candidates and replay their original native frame geometry."""
from pathlib import Path
import argparse
import importlib.util
import json

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = load('shop_build_helpers', 'scripts/build-native-login-art.py')
art = load('roomextra_art', 'scripts/native-ui-roomextra-art.py')


def check_palette(source, check):
    globals_ = next(s for s in source['sourceScopes'] if s['module']=='uiMain' and s['scope']=='?')['literalAssignments']
    if globals_['lightColor'] != [255,255,255,255] or globals_['maskColor'] != [51,51,51,255]:
        raise ValueError('Native source text globals changed')
    evidence=[]
    for player in ('player1','player5'):
        player_scope=f'?.UI_children_room.children.{player}.children.name'
        assignment=next(s for s in source['symbolicColorAssignments'] if s['scope']==player_scope and s['target']=='drawcolor')
        if assignment['symbol']!='lightColor':raise ValueError('Native player-name foreground changed')
        evidence.append(assignment)
    match_prefix='?.UI_children_room.children.matchDlg.children.'
    for field in ('systemBillboard','scoreBillboardTitle','scoreBillboard'):
        scope=next(s for s in source['sourceScopes'] if s['module']=='uiRoom' and s['scope']==match_prefix+field)
        if scope['literalAssignments']['drawcolor']!=[255,255,255,255]:raise ValueError('Native match panel foreground changed')
        evidence.append(scope)
    # The sender is broadcastColor=maskColor; words inherit TRichEdit black.
    import zipfile
    helper=load('room_text_inert', (HERE/'build-roster-mapping.py').relative_to(ROOT))
    with zipfile.ZipFile(helper.ARCHIVE) as z:
        raw=z.read('QQTang-Local/runtime/client-patched/res/uiRes/uiMain.pyc')
        main_tree,_=helper.PARSER.decode(raw)
        if main_tree['bytecode'][454:460] != bytes.fromhex('6535005a3900'):
            raise ValueError('Pinned broadcastColor alias instructions changed')
        template_raw=z.read('QQTang-Local/runtime/client-patched/res/uiRes/uiTemplate.pyc')
        template,_=helper.PARSER.decode(template_raw)
        rich=next(r for r in helper.PARSER.collect(template) if r['scope']=='?.TRichEdit')
        color=next(r['literalValue'] for r in rich['literalAssignments'] if r['name']=='drawcolor')
        if [v['value'] for v in color['values']] != [0,0,0,255]:raise ValueError('Rich-edit source foreground changed')
        room_raw=z.read('QQTang-Local/runtime/client-patched/res/uiRes/uiRoom.pyc')
        room_tree,_=helper.PARSER.decode(room_raw)
    def find(n,path):
        scope=helper.PARSER.text_value(n['name'])[0]
        if scope==path[0] and len(path)==1:return n
        if scope==path[0]:
            for c in n['consts']:
                if isinstance(c,dict) and c.get('inertCodeNode'):
                    found=find(c,path[1:])
                    if found is not None:return found
        return None
    parent=find(room_tree,['?','UI_children_room','children','chatArea','children','chatPanel','children','speaker0','children'])
    if parent['bytecode'][31:34]!=bytes.fromhex('650400') or helper.PARSER.text_value(parent['names'][4])[0]!='TRichEdit':
        raise ValueError('Broadcast words template base changed')
    alias={'module':'uiMain','sourceSha256':helper.sha(raw),'byteStart':454,'byteEnd':460,'instructionHex':raw[:0].hex()+main_tree['bytecode'][454:460].hex(),
           'sourceSymbol':'maskColor','targetSymbol':'broadcastColor','resolvedRgba':globals_['maskColor']}
    inherited={'module':'uiRoom','sourceSha256':helper.sha(room_raw),'scope':'?.UI_children_room.children.chatArea.children.chatPanel.children.speaker0.children',
               'baseLoadByteOffset':31,'baseName':'TRichEdit','baseInstructionHex':parent['bytecode'][31:34].hex(),
               'templateModuleSha256':helper.sha(template_raw),'templateScope':rich}
    def luminance(rgb):
        values=[v/255 for v in rgb]
        linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
        return sum(a*b for a,b in zip(linear,(0.2126,0.7152,0.0722),strict=True))
    samples=[]
    points=[('dlg_matchroom',0,'systemBillboard',(120,150),[255,255,255,255]),
            ('dlg_matchroom',0,'scoreBillboardTitle',(120,302),[255,255,255,255]),
            ('dlg_matchroom',0,'scoreBillboard',(120,370),[255,255,255,255])]
    for stem in ('btn_playerUp','btn_playerDown'):
        for index in range(2):
            frame=art.source_frame(stem,index);x,y=frame['frameOffset']
            global_y=15 if stem=='btn_playerUp' else 118
            points.append((stem,index,'player.name',(70-x,global_y-y),[255,255,255,255]))
    for index in range(8):
        points.append(('teamColorStrip',index,'player.name on indexed team strip',(70,10),[255,255,255,255]))
    for stem,index,field,point,foreground in points:
        path=HERE/'candidate'/'decoded'/f'{stem}-{index:02}.png'
        with Image.open(path) as image:
            rgba=image.convert('RGBA').getpixel(point)
        # Worst-case ivory backing if this native surface is translucent.
        bg=[round((v*rgba[3]+b*(255-rgba[3]))/255) for v,b in zip(rgba[:3],(243,234,210),strict=True)]
        a,b=luminance(foreground[:3]),luminance(bg);ratio=(max(a,b)+0.05)/(min(a,b)+0.05)
        if ratio<4.5:raise ValueError(f'Room foreground contrast failed: {stem} {field} {ratio}')
        samples.append({'nativePreview':builder.record(path),'field':field,'samplePixel':list(point),'sourceForegroundRgba':foreground,
                        'sampledNativeRgba':list(rgba),'compositedBackgroundRgb':bg,'contrastRatio':ratio})
    fill=Image.open(HERE/'candidate/decoded/img_popo-00.png').convert('RGBA').getpixel((150,8))
    mask=Image.open(HERE/'candidate/decoded/mask_speaker-00.png').convert('RGBA').getpixel((150,8))
    bg=[round(fill[i]*0.6+mask[i]*0.4) for i in range(3)]
    for field,foreground in [('speaker.name',[51,51,51]),('speaker.words',[0,0,0])]:
        a,b=luminance(foreground),luminance(bg);ratio=(max(a,b)+0.05)/(min(a,b)+0.05)
        if ratio<4.5:raise ValueError('Room broadcast composite contrast failed')
        samples.append({'nativePreviews':[builder.record(HERE/'candidate/decoded/img_popo-00.png'),builder.record(HERE/'candidate/decoded/mask_speaker-00.png')],
                        'field':field,'sourceForegroundRgba':foreground+[255],'nativeFillFactor':0.6,'compositedBackgroundRgb':bg,'contrastRatio':ratio})
    path=HERE/'palette-evidence.json'
    builder.save_json(path,{'schemaVersion':1,'sourceReferences':builder.record(HERE/'manifest.json'),'sourceColorBindings':evidence,
                           'broadcastColorAlias':alias,'broadcastWordsTemplateInheritance':inherited,'samples':samples,'sampleThreshold':4.5,
                           'nativeRuntimeVerified':False,'visualAccepted':False},check)
    return builder.record(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--core-only', action='store_true')
    args = parser.parse_args()
    check = args.check
    paths = {p: value for p, value in art.PATHS.items() if not args.core_only or value[0] != 'roomextra-extra-icon'}
    source_path = HERE / 'manifest.json'
    sources = json.loads(source_path.read_bytes())
    records = {r['nativePath'].lower(): r for r in sources['resources']}
    if set(records) != {p.lower() for p in art.PATHS}:
        raise ValueError('Selected native paths differ from the decoded source evidence')
    if any(path in builder.PATHS and builder.PATHS[path] != value for path, value in art.PATHS.items()):
        raise ValueError('Pet controls conflict with an already registered renderer')
    package = (ROOT / sources['package']['file']).read_bytes()
    if builder.record(ROOT / sources['package']['file']) != sources['package']:
        raise ValueError('Source package changed')
    paint_paths = {k: builder.PAINTS[k] for k in ('panel', 'normal', 'hover', 'pressed')}
    paint_paths.update({k: p for k, p in art.PAINT_INPUTS.items() if not args.core_only or not k.startswith('roomextra-extra-')})
    paints = {k: Image.open(ROOT / p).convert('RGBA') for k, p in paint_paths.items()}
    font = Path('C:/Windows/Fonts/msyh.ttc')
    row_heights = [320 if max(f['nativeSize'][1] for f in records[p.lower()]['frames']) > 100 else 120 for p in paths]
    contact = Image.new('RGB', (1200, sum(row_heights)), '#ede6d4')
    offset_y = 0
    draw = ImageDraw.Draw(contact)
    items = []
    for row, (path, (kind, caption)) in enumerate(paths.items()):
        evidence = records[path.lower()]
        raw, compressed_sha = builder.codec.reader.unpack_resource(package, evidence['packageEntry'])
        if builder.hashlib.sha256(raw).hexdigest() != evidence['sourceSha256'] or compressed_sha != evidence['compressedSha256']:
            raise ValueError('Source DIMG digest differs')
        metadata = evidence['metadata']
        pictures = {f['index']: art.render(kind, caption, f['index'], (f['width'], f['height']),
                                         paints, font, builder.nine_slice, builder.scaled)
                    for f in metadata['frames'] if not f['empty']}
        output, _, frames = builder.codec.replace_frames(raw, pictures)
        destination = HERE / 'candidate' / 'patch' / path
        if check:
            if destination.read_bytes() != output:
                raise ValueError('Encoded room-extra candidate changed')
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(output)
        row_height = row_heights[row]
        draw.text((10, offset_y+5), path, fill='#244f41')
        exports = []
        for frame, image in frames:
            target = HERE / 'candidate' / 'decoded' / f'{Path(path).stem}-{frame["index"]:02}.png'
            builder.save_image(target, image, check)
            index = frame['index']
            ratio = min(2, 250/image.width, (row_height-45)/image.height)
            extent = (max(1, round(image.width*ratio)), max(1, round(image.height*ratio)))
            enlarged = image.resize(extent, Image.Resampling.NEAREST)
            x, y = 15+index*290, offset_y+27
            contact.paste(enlarged, (x, y), enlarged)
            draw.text((x, offset_y+row_height-15), f"f{index} {image.width}x{image.height} offset{frame['frameOffset']}",
                      fill='#244f41')
            alpha_key=None
            if kind in art._EXACT_ALPHA_KINDS:
                stem=Path(path).stem
                alpha_key=f'{stem}-{index}'
                if image.getchannel('A').tobytes()!=art.source_alpha(alpha_key,image.size).tobytes():
                    raise ValueError('Room functional alpha changed after native encoding')
            exports.append({**builder.record(target), 'index': index, 'nativeSize': list(image.size),
                            'frameOffset': frame['frameOffset'], 'pixelMode': frame['pixelMode'],
                            'alphaExtrema': list(image.getchannel('A').getextrema()),
                            'functionalAlphaSource': builder.record(ROOT / art.STRUCTURAL_ALPHA_INPUTS[alpha_key]) if alpha_key else None,
                            'functionalAlphaRetained': True if alpha_key else None})
        spans=[(f['pixelDataOffset'],f['pixelDataOffset']+f['pixelByteLength']) for f in metadata['frames'] if not f['empty']]
        outside_before=bytearray();outside_after=bytearray();cursor=0
        for start,end in sorted(spans):
            outside_before.extend(raw[cursor:start]);outside_after.extend(output[cursor:start]);cursor=end
        outside_before.extend(raw[cursor:]);outside_after.extend(output[cursor:])
        if len(raw)!=len(output) or outside_before!=outside_after:raise ValueError('Non-pixel native bytes changed')
        derived=[]
        if kind in ('roomextra-role-icon','roomextra-role-name','roomextra-role-bust'):
            derived=[builder.record(ROOT/art.PAINT_INPUTS[f'roomextra-role-{caption}'])]
        elif kind=='roomextra-extra-icon':
            own=ROOT/art.PAINT_INPUTS[f'roomextra-extra-{caption}']
            derived=[builder.record(own),builder.record(own.with_suffix('.png.generation.json'))]
        items.append({**builder.record(destination),'nativePath':path,'sourceSha256':evidence['sourceSha256'],
                      'sourceBindings':evidence['sourceBindings'],'rendererKind':kind,'caption':caption,
                      'frames':exports,'nonPixelBytesIdentical':True,
                      'alphaPolicy':'Exact final decoded source functional alpha' if kind in art._EXACT_ALPHA_KINDS else
                                    'Own subject/lettering/panel alpha replaces baked original character or glyph silhouette; original header/geometry retained',
                      'nonPixelBytesSha256':builder.hashlib.sha256(outside_before).hexdigest(),
                      'derivedInputs':derived,'visualAccepted':False,'nativeRuntimeVerified':False})
        offset_y += row_height
    preview = HERE / 'candidate' / 'contact-native.png'
    builder.save_image(preview, contact, check)
    review_previews=[]
    role_board=Image.new('RGB',(1100,1600),'#d8d4c5')
    role_draw=ImageDraw.Draw(role_board)
    roles=list(art._MAPPING['entries'])
    for i,role in enumerate(roles):
        x,y=(i%4)*275,(i//4)*320
        stem=role['nativeAlias']
        native=Image.open(HERE/'candidate/decoded'/f'{stem}-00.png').convert('RGBA')
        frame=art.source_frame(stem,0)
        logical=Image.new('RGBA',(256,271))
        logical.alpha_composite(native,tuple(frame['frameOffset']))
        role_board.paste(logical,(x+5,y+25),logical)
        role_draw.text((x+5,y+5),f'roleID={role["sourceRoleId"]} {stem}',fill='#142c22')
    role_path=HERE/'candidate/role-busts-native.png'
    builder.save_image(role_path,role_board,check)
    review_previews.append(builder.record(role_path))
    faces=list(art._ROLES)
    if not args.core_only:faces+=art._EXTRA
    face_board=Image.new('RGB',(1000,((len(faces)+4)//5)*170),'#263f34')
    face_draw=ImageDraw.Draw(face_board)
    for i,alias in enumerate(faces):
        x,y=(i%5)*200,(i//5)*170
        native=Image.open(HERE/'candidate/decoded'/f'icon_{alias}-00.png').convert('RGBA')
        scale=native.resize((native.width*2,native.height*2),Image.Resampling.NEAREST)
        face_board.paste(scale,(x+20,y+10),scale)
        face_draw.text((x+10,y+130),f'icon_{alias}',fill='#f3ead2')
    face_path=HERE/'candidate/role-icons-native.png'
    builder.save_image(face_path,face_board,check)
    review_previews.append(builder.record(face_path))
    panels=Image.new('RGB',(1050,730),'#d8d4c5')
    panel_draw=ImageDraw.Draw(panels)
    for stem,x,y in [('dlg_helpKB',10,25),('dlg_matchroom',420,25),('dlg_roleAttr',760,25),
                     ('dlg_roleProp',760,150),('mask_equip',10,430),('equipTip',760,300)]:
        native=Image.open(HERE/'candidate/decoded'/f'{stem}-00.png').convert('RGBA')
        panels.paste(native,(x,y),native)
        panel_draw.text((x,y-15),stem,fill='#142c22')
    panel_path=HERE/'candidate/panels-native.png'
    builder.save_image(panel_path,panels,check)
    review_previews.append(builder.record(panel_path))
    palette = check_palette(sources, check)
    portraits_evidence=None
    if not args.core_only:
        portrait_checker=load('room_portrait_checker',(HERE/'check-portraits.py').relative_to(ROOT))
        portrait_checker.build(check)
        portraits_evidence=builder.record(HERE/'portrait-evidence.json')
    candidate = {
        'schemaVersion': 1, 'scope': 'Native room-extra control and own portrait candidates',
        'sourceReferences': builder.record(source_path), 'renderer': builder.record(ROOT / 'scripts/native-ui-roomextra-art.py'),
        'verificationScript': builder.record(Path(__file__).resolve()),
        'buildHelpers': builder.record(ROOT / 'scripts/build-native-login-art.py'),
        'codec': builder.record(ROOT / 'scripts/native-ui-format.py'),
        'paintInputs': [builder.record(ROOT / p) for p in paint_paths.values()],
        'font': {'family': 'Microsoft YaHei', 'sha256': builder.hashlib.sha256(font.read_bytes()).hexdigest()},
        'symbolFont': {'fileName': 'seguisym.ttf', 'sha256': builder.hashlib.sha256(Path(art.FONT_INPUTS['symbols']).read_bytes()).hexdigest()},
        'structuralAlphaInputs': [builder.record(ROOT / p) for p in art.STRUCTURAL_ALPHA_INPUTS.values()],
        'visualMappingAssumptions': art.VISUAL_MAPPING_ASSUMPTIONS,
        'paletteEvidence': palette,
        'portraitEvidence':portraits_evidence,
        'referenceInputs':[builder.record(ROOT/p) for p in art.REFERENCE_INPUTS],
        'sourceArtworkGeneration': [builder.record(ROOT / p) for p in art.ART_GENERATION_RECORDS] if not args.core_only else [],
        'items': items, 'preview': builder.record(preview), 'nativeResources': len(items),
        'reviewPreviews':review_previews,
        'excludedExtraImagePaths':[p for p,v in art.PATHS.items() if args.core_only and v[0]=='roomextra-extra-icon'],
        'sourcePositions': sum(len(item['frames']) for item in items),
        'functionalAlphaRetainedPositions': sum(f['functionalAlphaRetained'] is True for item in items for f in item['frames']),
        'nativeBuildInvokesImageModel': False, 'sourceArtworkNewGeneration': not args.core_only,
        'includedNewExtraIconCandidates': not args.core_only, 'nativeGeometryRetained': True, 'nativeRuntimeVerified': False,
        'visualAccepted': False, 'installedToClient': False,
    }
    builder.save_json(HERE / 'candidate-manifest.json', candidate, check)
    print(json.dumps({'nativeResources': len(items), 'sourcePositions': candidate['sourcePositions'],
                      'nativeGeometryRetained': True, 'pixelReplay': check}))


if __name__ == '__main__':
    main()
