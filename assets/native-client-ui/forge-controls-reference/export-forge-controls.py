"""Export/replay the isolated21-resource forge candidate without installing it."""
import argparse
import hashlib
from importlib import util
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ART = module('forge_art', 'scripts/native-ui-forge-controls-art.py')
HELP = module('forge_export_helpers', 'assets/native-client-ui/common-reference/export-common.py')
CODEC = HELP.CODEC
FONT = Path('C:/Windows/Fonts/msyh.ttc')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def preserve_nonpixels(source, output, metadata):
    left, right = bytearray(source), bytearray(output)
    for frame in metadata['frames']:
        if frame['empty']:
            continue
        start, length = frame['pixelDataOffset'], frame['pixelByteLength']
        left[start:start + length] = bytes(length)
        right[start:start + length] = bytes(length)
    if left != right:
        raise ValueError('A native forge header, offset, frame slot or nonpixel byte changed')


def previews(resources, check):
    previews = []
    font = ImageFont.load_default(size=14)
    for page in range(3):
        subset = resources[page * 9:(page + 1) * 9]
        heights = [max(152, min(490, 2 * max(f['height'] for f in r['frames']) + 58)) for r in subset]
        board = Image.new('RGB', (1500, sum(heights)), '#eae3d0')
        draw = ImageDraw.Draw(board)
        y = 0
        for resource, height in zip(subset, heights):
            half = (height - 34) // 2
            draw.rectangle((0, y + 34 + half, 1499, y + height - 1), fill='#193f35')
            draw.text((8, y + 4), resource['nativePath'] + ' / candidate native pixels / pending review', font=font, fill='#214b3c')
            for frame in resource['frames']:
                with Image.open(ROOT / frame['file']) as image:
                    scale = min(2, 350 / image.width, (half - 20) / image.height)
                    picture = HELP.scaled(image, tuple(max(1, round(v * scale)) for v in image.size))
                x = frame['index'] * 372 + 8
                for dy, ink in ((y + 34, '#214b3c'), (y + 34 + half, '#fff3d5')):
                    draw.text((x, dy), f"raw{frame['index']} off{tuple(frame['frameOffset'])}", font=font, fill=ink)
                    board.paste(picture, (x, dy + 18), picture)
            y += height
        path = HERE / f'candidate-all-states-{page + 1}.png'
        HELP.png(path, board, check)
        previews.append({**record(path), 'runtimeScreenshot': False,
                         'operation': 'Decoded native candidate frames composited onto light/dark diagnostic grounds'})
    return previews


def contrast_contract(check):
    evidence_path = HERE / 'text-color-source-evidence.json'
    evidence = json.loads(evidence_path.read_bytes())
    def find(module, suffix):
        source_module = next(m for m in evidence['modules'] if m['module'] == module)
        scope = next(s for s in source_module['scopes'] if s['scope'].endswith(suffix))
        return {'module': module, 'sourceSha256': source_module['sourceSha256'], **scope}
    rects=[]
    for suffix in ['materialItem0','materialItem1','materialItem2','materialItem3','materialItem4',
                   'forgeItem0','forgeItem1','forgeItem2','forgeItem3','forgeItem4',
                   'revertItem0','revertItem1','revertItem2','revertItem3','revertItem4',
                   'sourceMaterial','sourceAvatar','destAvatar','forgeBtn','splitBtn','revertBtn','forgeInfo']:
        rects.append(find('uiShop','.AvatarForgeDlg.children.'+suffix))
    contract={
      'schemaVersion':1,'sourceEvidence':record(evidence_path),
      'knownDefaults':[find('uiTemplate','.TLabel'),find('uiTemplate','.TButton')],
      'sharedGlobalColorDefinitions':{**{k:v for k,v in find('uiMain','?').items() if k!='literalAssignments'},
        'literalAssignments':[a for a in find('uiMain','?')['literalAssignments'] if a['name'] in ('lightColor','zoneChooseColor','maskColor')]},
      'blackTLabelName':find('uiShop','.composeDlg.children.curItemName'),
      'blackTLabelDescription':find('uiShop','.composeDlg.children.curItemInfo'),
      'whiteMaterialBase':find('uiShop','.meterialList.children.meterialInfo0'),
      'whiteMaterialInherited1':find('uiShop','.meterialList.children.meterialInfo1'),
      'whiteMaterialInherited2':find('uiShop','.meterialList.children.meterialInfo2'),
      'brownConfirmation':find('uiShop','.forgeConfirmDlg.children.forgeText'),
      'paleComposeHistory':find('uiShop','.composeDlg.children.composeInfo'),
      'forgeHistoryColorUnspecified':find('uiShop','.AvatarForgeDlg.children.forgeInfo'),
      'categoryCaptionEngineColorUnknown':find('uiShop','.composeDlg.children.itemList0'),
      'sharedPawnshopCaptionEngineColorUnknown':find('uiSelRoom','.pawnshop.children.itemList0'),
      'avatarWidgetGeometry':rects,
      'backgroundRules':[
        {'nativePath':'object/ui/forge/dlg_forge.img','rule':'curItemName270,67,120,12 and curItemInfo270,87,120,60 directly inherit black TLabel: light paper background; all item-list names remain runtime data'},
        {'nativePath':'object/ui/forge/dlg_meterial.img','rule':'meterialInfo0 explicit white;1/2 inherit it by parent BUILD_CLASS windows. Dark jade text region at local x80. No crystals are baked into empty live item slots'},
        {'nativePath':'object/ui/forge/dlg_forgeconfirm.img','rule':'forgeText explicit brown135,113,87 at10,10,180,28: light ivory. No dynamic action/price/caption baked'},
        {'nativePaths':['object/ui/forge/dlg_avatarforge.img','object/ui/forge/dlg_forge.img'],'rule':'History areas keep source dark polarity; composeInfo names zoneChooseColor, defined255,250,236 in uiMain. forgeInfo per-message color not declared. Exact live item/control rects retained; no PYC changed'},
        {'nativePath':'object/ui/forge/dlg_forgeMask.img','rule':'All15 slot alpha holes and transparent separators retained byte-for-byte; no exact active UI binding proven'},
      ],
      'observedSourceStateLayouts':ART.STATE_LAYOUTS,
      'unknowns':['TButton engine caption color absent from inspected template; category/item strip captions remain runtime-readable acceptance pending',
       'TEXTLIST forge history colors and all per-message updates are runtime data',
       'btn_startForge and dlg_forgeMask have no exact static path binding in source census; candidate export only',
       'Pale/colored tab positions and gradient/flat item rows are separate observed families, not unified disabled/hover assumptions',
       'Shared pawnshop usage, runtime text width, native framescheme execution and final visuals are unverified'],
      'dynamicCaptionColorPatched':False,'originalPycModified':False,'nativeRuntimeVerified':False,'visualAccepted':False}
    path=HERE/'contrast-contract.json';HELP.write_json(path,contract,check);return record(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    source_path = HERE / 'manifest.json'
    source = json.loads(source_path.read_bytes())
    by_path = {r['nativePath']: r for r in source['resources']}
    if set(by_path) != set(ART.PATHS) or sum(ART.SOURCE_COUNTS) != 52:
        raise ValueError('Isolated forge scope differs from all21 source paths')
    package_path = ROOT / source['sourcePackage']['file']
    if record(package_path) != source['sourcePackage']:
        raise ValueError('Pinned source package changed')
    package = package_path.read_bytes()
    paint_inputs = {key: value for key, value in HELP.ROOT_PAINTS.items() if key in ('panel', 'normal', 'hover', 'pressed')}
    paint_inputs.update(ART.PAINT_INPUTS)
    paints = {name: Image.open(ROOT / filename).convert('RGBA') for name, filename in paint_inputs.items()}
    resources = []
    for path, (kind, label) in ART.PATHS.items():
        original = by_path[path]
        raw, _ = CODEC.reader.unpack_resource(package, original['packageEntry'])
        if sha(raw) != original['sourceSha256']:
            raise ValueError('Source forge container changed')
        pictures = {f['index']: ART.render(kind, label, f['index'], (f['width'], f['height']), paints,
                     FONT, HELP.nine_slice, HELP.scaled) for f in original['metadata']['frames'] if not f['empty']}
        output, metadata, decoded = CODEC.replace_frames(raw, pictures)
        preserve_nonpixels(raw, output, metadata)
        if output == raw:
            raise ValueError('A selected forge resource was not replaced')
        patch = HERE / 'patch' / path
        if check:
            if patch.read_bytes() != output:
                raise ValueError(f'Native forge replay differs: {path}')
        else:
            patch.parent.mkdir(parents=True, exist_ok=True)
            patch.write_bytes(output)
        frames = []
        for frame, picture in decoded:
            index = frame['index']
            source_frame = original['frames'][index]
            with Image.open(ROOT / source_frame['file']) as before:
                original_alpha = before.getchannel('A')
            candidate_alpha = picture.getchannel('A')
            normalization = ART.ALPHA_NORMALIZATIONS.get(kind)
            difference = ImageChops.difference(original_alpha, candidate_alpha)
            changed_box = difference.getbbox()
            if normalization:
                x0, y0, x1, y1 = normalization['sourceRoiXYXY']
                if not changed_box or not (x0 <= changed_box[0] <= changed_box[2] <= x1 and y0 <= changed_box[1] <= changed_box[3] <= y1):
                    raise ValueError('Forge alpha normalization extends beyond the declared interior ROI')
                if candidate_alpha.crop((x0, y0, x1, y1)).getextrema() != (255, 255):
                    raise ValueError('Old forge confirmation glyph alpha was not fully normalized')
            elif changed_box:
                raise ValueError('An undeclared original forge alpha plane changed')
            png = HERE / 'decoded' / f'{ART.KIND_SOURCE_STEMS[kind]}-{index:02}.png'
            HELP.png(png, picture, check)
            encoded_start = frame['pixelDataOffset']
            actual = output[encoded_start:encoded_start + frame['pixelByteLength']]
            if CODEC.encode_pixels(picture, frame['pixelMode']) != actual:
                raise ValueError('Native decoded forge pixel re-encoding differs')
            frames.append({**record(png), 'index': index, 'sourceFrameIndex': index,
                           'width': frame['width'], 'height': frame['height'], 'frameOffset': frame['frameOffset'],
                           'pixelMode': frame['pixelMode'], 'decodedRgbaSha256': sha(picture.tobytes()),
                           'structuralAlphaInput': record(ROOT / source_frame['file']),
                           'sourceAlphaSha256': source_frame['decodedAlpha']['sha256'],
                           'candidateAlphaSha256': sha(picture.getchannel('A').tobytes()),
                           'sourceAlphaPlaneExactlyPreserved': not normalization,
                           'alphaNormalization': normalization,
                           'changedAlphaBBoxXYXY': list(changed_box) if changed_box else None,
                           'changedAlphaPixelCount': sum(value != 0 for value in difference.tobytes()),
                           'sourceExteriorAlphaExactlyPreserved': True,
                           'observedSourceState': ART.STATE_LAYOUTS.get(kind, ['single'])[index]})
        resources.append({**record(patch), 'nativePath': path, 'rendererKind': kind, 'caption': label,
                          'sourceSha256': original['sourceSha256'], 'sourcePacked': True, 'sourceLoose': False,
                          'frames': frames, 'allNonPixelBytesIdenticalToSource': True,
                          'sourceAlphaPlaneExactlyPreserved': not ART.ALPHA_NORMALIZATIONS.get(kind),
                          'sourceExteriorAlphaExactlyPreserved': True,
                          'nativeRuntimeVerified': False, 'visualAccepted': False})
    contrast = contrast_contract(check)
    result = {'schemaVersion': 1, 'scope': 'All21 packed native forge original-art control candidates;52 source positions',
              'sourceReferences': record(source_path), 'contrastEvidence': contrast,
              'items': resources, 'nativeResourceCount': len(resources), 'sourceFramePositions': sum(len(r['frames']) for r in resources),
              'renderer': record(ROOT / 'scripts/native-ui-forge-controls-art.py'), 'exporter': record(Path(__file__)),
              'sourceCaptureScript': record(HERE / 'capture-source.py'), 'nativeCodec': record(ROOT / 'scripts/native-ui-format.py'),
              'exportHelpers': record(ROOT / 'assets/native-client-ui/common-reference/export-common.py'),
              'paintInputs': [{'purpose': key, **record(ROOT / value)} for key, value in paint_inputs.items()],
              'structuralAlphaInputs': [{'purpose': key, **record(ROOT / value)} for key, value in ART.STRUCTURAL_ALPHA_INPUTS.items()],
              'font': {'family': 'Microsoft YaHei', 'sourcePath': str(FONT), 'sha256': sha(FONT.read_bytes())},
              'previews': previews(resources, check), 'newModelGeneration': False, 'originalColorPixelsReused': False,
              'allSourceAlphaPlanesExactlyPreserved': False,
              'exactSourceAlphaPlaneCount': sum(f['sourceAlphaPlaneExactlyPreserved'] for r in resources for f in r['frames']),
              'normalizedInteriorAlphaPlaneCount': 1,
              'sourceExteriorAlphaExactlyPreserved': True,
              'alphaNormalizations': ART.ALPHA_NORMALIZATIONS,
              'visualMappingAssumptions': ART.VISUAL_MAPPING_ASSUMPTIONS,
              'sourceAlphaDiagnostic': source['sourceAlphaObservation'], 'installedToClient': False,
              'visualAccepted': False, 'nativeRuntimeVerified': False, 'allForgeUiComplete': False}
    HELP.write_json(HERE / 'candidate-manifest.json', result, check)
    print(json.dumps({'nativeResources': len(resources), 'sourcePositions': result['sourceFramePositions'],
                      'exactSourceAlphaPlanes': result['exactSourceAlphaPlaneCount'],
                      'normalizedAlphaInteriors': 1, 'allSourceAlphaExteriorsRetained': True,
                      'allHeadersAndOffsetsRetained': True,
                      'nativeReplayChecked': check, 'installed': False}))


if __name__ == '__main__':
    main()
