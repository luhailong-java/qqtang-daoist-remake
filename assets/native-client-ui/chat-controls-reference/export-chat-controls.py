"""Export/replay the isolated27-resource chat candidate without installing it."""
import argparse
import hashlib
from importlib import util
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = util.spec_from_file_location(name, ROOT / relative)
    value = util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ART = module('chat_art', 'scripts/native-ui-chat-controls-art.py')
HELP = module('chat_export_helpers', 'assets/native-client-ui/common-reference/export-common.py')
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
        raise ValueError('A native chat header, offset, frame slot or nonpixel byte changed')


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

    contract = {
        'schemaVersion': 1, 'sourceEvidence': record(evidence_path),
        'knownDefaults': [find('uiTemplate', '.TEdit'), find('uiTemplate', '.TLabel'), find('uiTemplate', '.TButton')],
        'lightColorAndMaskColorDefinitionUiMain': {
            **{key: value for key, value in find('uiMain', '?').items() if key != 'literalAssignments'},
            'literalAssignments': [a for a in find('uiMain', '?')['literalAssignments'] if a['name'] in ('lightColor', 'maskColor')]},
        'explicitWhitePassword': find('uiRoom', '.selChatBg.children.chatPwd'),
        'explicitWhitePageLabelRoom': find('uiRoom', '.faceDlg.children.pageLab'),
        'explicitWhitePageLabelLobby': find('uiSelRoom', '.faceDlg.children.pageLab'),
        'symbolicWhiteEditRoom': find('uiRoom', '.chatArea.children.chatEdit'),
        'symbolicWhiteEditLobby': find('uiSelRoom', '.chatArea.children.chatEdit'),
        'lobbyChatListExplicitCyan': find('uiSelRoom', '.chatPanel.children.chatList'),
        'roomChatListColorNotDeclared': find('uiRoom', '.chatPanel.children.chatList'),
        'commandMenuBaseRoom': find('uiRoom', '.comDlg.children.profileView'),
        'commandMenuSiblingBaseConstructionRoom': find('uiRoom', '.comDlg.children'),
        'commandMenuBaseLobby': find('uiSelRoom', '.comDlg.children.profileView'),
        'commandMenuSiblingBaseConstructionLobby': find('uiSelRoom', '.comDlg.children'),
        'mapFilterNameExplicitWhite': find('uiSelRoom', '.mapMode0.children.name'),
        'sharedFacePanelAlsoUsedByKinTotem': find('uiMain', '.totemDlg'),
        'backgroundRules': [
            {'nativePath': 'object/ui/chatRoom/dlg_bgPreview.img',
             'rule': 'Password child explicitly white at53,155,100,16: dark jade well; no baked password/value'},
            {'nativePath': 'object/ui/chat/dlg_face.img',
             'rule': 'Room/lobby page labels explicitly white; keep bottom region dark. Face cell coordinates start8,6 at26x26; preserve grid. Shared kin totem use remains pending runtime review.'},
            {'nativePaths': ['object/ui/chat/img_commandPrompt.img', 'object/ui/chat/img_chatMenu.img', 'object/ui/chat/img_cmdChoose.img'],
             'rule': 'Dynamic menu captions not baked. TButton template declares only type, engine caption color unknown. Preserve source dark background polarity. The highlight is also used beneath explicitly white map-filter names.'},
            {'nativePaths': ['object/ui/chatRoom/dlg_chatAreaBig.img', 'object/ui/chatRoom/dlg_chatAreaSmall.img'],
             'rule': 'Retain exact source128 alpha and dark polarity. Messages can receive runtime colors; no all-message contrast acceptance.'},
        ],
        'unknowns': [
            'TButton engine default caption color is not declared in the inspected uiTemplate. No TLabel inheritance is inferred.',
            'TEXTLIST room message colors and per-message updates remain runtime data.',
            'img_chatMenu has no exact static UI binding in the census; export is a source-path candidate only.',
            'State ordering reflects observed raw source art, not an executed engine scheme.',
            'Shared panel use, caption clipping, all interactions and live alpha compositing need original-client review.',
        ],
        'dynamicCaptionColorPatched': False, 'originalPycModified': False,
        'nativeRuntimeVerified': False, 'visualAccepted': False,
    }
    path = HERE / 'contrast-contract.json'
    HELP.write_json(path, contract, check)
    return record(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    source_path = HERE / 'manifest.json'
    source = json.loads(source_path.read_bytes())
    by_path = {r['nativePath']: r for r in source['resources']}
    if set(by_path) != set(ART.PATHS) or sum(ART.SOURCE_COUNTS) != 65:
        raise ValueError('Isolated chat scope differs from all27 source paths')
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
            raise ValueError('Source chat container changed')
        pictures = {f['index']: ART.render(kind, label, f['index'], (f['width'], f['height']), paints,
                     FONT, HELP.nine_slice, HELP.scaled) for f in original['metadata']['frames'] if not f['empty']}
        output, metadata, decoded = CODEC.replace_frames(raw, pictures)
        preserve_nonpixels(raw, output, metadata)
        if output == raw:
            raise ValueError('A selected chat resource was not replaced')
        patch = HERE / 'patch' / path
        if check:
            if patch.read_bytes() != output:
                raise ValueError(f'Native chat replay differs: {path}')
        else:
            patch.parent.mkdir(parents=True, exist_ok=True)
            patch.write_bytes(output)
        frames = []
        for frame, picture in decoded:
            index = frame['index']
            source_frame = original['frames'][index]
            with Image.open(ROOT / source_frame['file']) as before:
                if before.getchannel('A').tobytes() != picture.getchannel('A').tobytes():
                    raise ValueError('Original chat alpha plane changed after native encoding')
            png = HERE / 'decoded' / f'{ART.KIND_SOURCE_STEMS[kind]}-{index:02}.png'
            HELP.png(png, picture, check)
            encoded_start = frame['pixelDataOffset']
            actual = output[encoded_start:encoded_start + frame['pixelByteLength']]
            if CODEC.encode_pixels(picture, frame['pixelMode']) != actual:
                raise ValueError('Native decoded chat pixel re-encoding differs')
            frames.append({**record(png), 'index': index, 'sourceFrameIndex': index,
                           'width': frame['width'], 'height': frame['height'], 'frameOffset': frame['frameOffset'],
                           'pixelMode': frame['pixelMode'], 'decodedRgbaSha256': sha(picture.tobytes()),
                           'structuralAlphaInput': record(ROOT / source_frame['file']),
                           'sourceAlphaSha256': source_frame['decodedAlpha']['sha256'],
                           'candidateAlphaSha256': sha(picture.getchannel('A').tobytes()),
                           'sourceAlphaPlaneExactlyPreserved': True,
                           'observedSourceState': ART.STATE_LAYOUTS.get(kind, ['single'])[index]})
        resources.append({**record(patch), 'nativePath': path, 'rendererKind': kind, 'caption': label,
                          'sourceSha256': original['sourceSha256'], 'sourcePacked': True, 'sourceLoose': False,
                          'frames': frames, 'allNonPixelBytesIdenticalToSource': True,
                          'sourceAlphaPlaneExactlyPreserved': True, 'nativeRuntimeVerified': False, 'visualAccepted': False})
    contrast = contrast_contract(check)
    result = {'schemaVersion': 1, 'scope': 'All27 packed native chat/chatRoom original-art control candidates;65 source positions',
              'sourceReferences': record(source_path), 'contrastEvidence': contrast,
              'items': resources, 'nativeResourceCount': len(resources), 'sourceFramePositions': sum(len(r['frames']) for r in resources),
              'renderer': record(ROOT / 'scripts/native-ui-chat-controls-art.py'), 'exporter': record(Path(__file__)),
              'sourceCaptureScript': record(HERE / 'capture-source.py'), 'nativeCodec': record(ROOT / 'scripts/native-ui-format.py'),
              'exportHelpers': record(ROOT / 'assets/native-client-ui/common-reference/export-common.py'),
              'paintInputs': [{'purpose': key, **record(ROOT / value)} for key, value in paint_inputs.items()],
              'structuralAlphaInputs': [{'purpose': key, **record(ROOT / value)} for key, value in ART.STRUCTURAL_ALPHA_INPUTS.items()],
              'font': {'family': 'Microsoft YaHei', 'sourcePath': str(FONT), 'sha256': sha(FONT.read_bytes())},
              'previews': previews(resources, check), 'newModelGeneration': False, 'originalColorPixelsReused': False,
              'allSourceAlphaPlanesExactlyPreserved': True, 'installedToClient': False,
              'visualAccepted': False, 'nativeRuntimeVerified': False, 'allChatUiComplete': False}
    HELP.write_json(HERE / 'candidate-manifest.json', result, check)
    print(json.dumps({'nativeResources': len(resources), 'sourcePositions': result['sourceFramePositions'],
                      'exactSourceAlphaPlanes': result['sourceFramePositions'], 'allHeadersAndOffsetsRetained': True,
                      'nativeReplayChecked': check, 'installed': False}))


if __name__ == '__main__':
    main()
