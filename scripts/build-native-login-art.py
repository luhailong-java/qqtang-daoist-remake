"""Build native UI resources from the project's existing painted art."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'assets/native-client-ui/login-v1'
SOURCE = ROOT / '.artifacts/reference-inputs'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
spec = importlib.util.spec_from_file_location('native_ui_format', ROOT / 'scripts/native-ui-format.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
post_spec = importlib.util.spec_from_file_location('postlogin_art', ROOT/'scripts/native-ui-postlogin-art.py')
postlogin_art = importlib.util.module_from_spec(post_spec)
post_spec.loader.exec_module(postlogin_art)
core_spec = importlib.util.spec_from_file_location('core_art', ROOT/'scripts/native-ui-core-art.py')
core_art = importlib.util.module_from_spec(core_spec)
core_spec.loader.exec_module(core_art)
MODULES = {'common': 'native-ui-common-art.py', 'room-controls': 'native-ui-room-controls-art.py',
           'shop-controls': 'native-ui-shop-controls-art.py', 'game-controls':'native-ui-game-controls-art.py'}
EXTRA_ART = {}
for name, filename in MODULES.items():
    module_spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT/'scripts'/filename)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    EXTRA_ART[name] = module
PATHS = {
    'ui/selSect/bg_login.img': ('background', None),
    'object/ui/login/img_logo.img': ('logo', None),
    'object/ui/login/dlg_login.img': ('panel', None),
    'object/ui/login/btn_login.img': ('button', '登录'),
    'object/ui/login/btn_quit.img': ('button', '离开'),
    'object/ui/login/btn_help.img': ('button', '新手帮助'),
    'object/ui/common/btn_cross.img': ('cross', None),
    'object/ui/common/btn_confirm.img': ('button', '确定'),
    'object/ui/common/btn_cancel.img': ('button', '取消'),
}
PATHS.update(postlogin_art.PATHS)
PATHS.update(core_art.PATHS)
for module in EXTRA_ART.values():
    if PATHS.keys() & module.PATHS.keys():
        raise ValueError('Two UI renderers target the same native resource')
    PATHS.update(module.PATHS)
PAINTS = {
    'background': 'assets/qqtang-world-v2.png',
    'logo': 'assets/branding/linghu-wordmark-login-1024.png',
    'panel': 'assets/ui/window-frame.png',
    'normal': 'assets/ui/primary-normal.png',
    'hover': 'assets/ui/primary-hover.png',
    'pressed': 'assets/ui/primary-pressed.png',
    'cross': 'assets/ui/action-icons-20261112/close.png',
}
for module in EXTRA_ART.values():
    PAINTS.update(getattr(module, 'PAINT_INPUTS', {}))


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def save_json(path, data, check):
    if check:
        if json.loads(path.read_bytes()) != data:
            raise ValueError(f'Metadata replay differs: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def save_image(path, image, check):
    if check:
        with Image.open(path) as previous:
            if previous.mode != image.mode or previous.size != image.size or previous.tobytes() != image.tobytes():
                raise ValueError(f'Pixels differ: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, optimize=True)


def scaled(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def nine_slice(image, size, inset):
    width, height = size
    edge = min(inset, width // 3, height // 3)
    sx = (0, inset, image.width - inset, image.width)
    sy = (0, inset, image.height - inset, image.height)
    dx = (0, edge, width - edge, width)
    dy = (0, edge, height - edge, height)
    out = Image.new('RGBA', size)
    for y in range(3):
        for x in range(3):
            out.alpha_composite(scaled(image.crop((sx[x], sy[y], sx[x+1], sy[y+1])),
                                       (dx[x+1]-dx[x], dy[y+1]-dy[y])), (dx[x], dy[y]))
    return out


def artwork(kind, label, index, size, paints, font_path, frame_count):
    for name, module in EXTRA_ART.items():
        if kind.startswith(name.split('-')[0] + '-'):
            return module.render(kind, label, index, size, paints, font_path, nine_slice, scaled)
    if kind.startswith('core-'):
        return core_art.render(kind, label, index, size, paints, font_path, nine_slice, scaled)
    if kind.startswith('post-'):
        return postlogin_art.render(kind, label, index, size, paints, font_path, nine_slice, scaled)
    state = ('normal', 'hover', 'pressed')[index] if frame_count == 3 else ('normal', 'alternate', 'hover', 'pressed')[min(index, 3)]
    if kind == 'background':
        return ImageOps.fit(paints[kind], size, method=Image.Resampling.LANCZOS).convert('RGBA')
    if kind in ('logo', 'cross'):
        out = Image.new('RGBA', size)
        image = paints[kind]
        fit = min((size[0]-4) / image.width, (size[1]-4) / image.height)
        dimensions = tuple(max(1, round(v*fit)) for v in image.size)
        out.alpha_composite(scaled(image, dimensions), tuple((v-d)//2 for v, d in zip(size, dimensions, strict=True)))
        if kind == 'cross':
            out = ImageEnhance.Brightness(out).enhance({'normal': 1, 'alternate': 0.65, 'hover': 1.15, 'pressed': 0.8}[state])
        return out
    if kind == 'panel':
        out = nine_slice(paints['panel'], size, 72)
        draw = ImageDraw.Draw(out)
        font = ImageFont.truetype(str(font_path), 14)
        title = ImageFont.truetype(str(font_path), 24)
        draw.text((size[0]//2, 49), '登录仙境', font=title, fill='#245c49', anchor='mm')
        # Native id and password controls are at x139,y104/147 with 140x24 extents.
        for y, text in ((104, '账号'), (147, '密码')):
            draw.rounded_rectangle((137, y-2, 281, y+24), radius=4, fill='#25574c', outline='#c6ad6e', width=1)
            draw.text((117, y+11), text, font=font, fill='#285745', anchor='rm')
        small = ImageFont.truetype(str(font_path), 11)
        for index, line in enumerate(('抵制不良游戏  拒绝盗版游戏', '注意自我保护  谨防受骗上当',
                                      '适度游戏益脑  沉迷游戏伤身', '合理安排时间  享受健康生活')):
            draw.text((size[0]//2, 318+index*16), line, font=small, fill='#527463', anchor='mm')
        return out
    style = state if state != 'alternate' else 'normal'
    out = nine_slice(paints[style], size, 42)
    if state == 'alternate':
        out = ImageEnhance.Color(out).enhance(0.25)
        out = ImageEnhance.Brightness(out).enhance(0.75)
    draw = ImageDraw.Draw(out)
    font = ImageFont.truetype(str(font_path), 12 if len(label) > 2 else 13)
    draw.text((size[0]//2, size[1]//2), label, font=font, fill='#fff5d9', anchor='mm',
              stroke_width=1, stroke_fill='#245b45')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    check = parser.parse_args().check
    archive_path = SOURCE / 'QQTang-Local-v1.3.4.zip'
    with archive_path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Reference archive differs from the pinned source')
    package_path, index_path = SOURCE / 'object.pkg', SOURCE / 'object.idx'
    package, index_bytes = package_path.read_bytes(), index_path.read_bytes()
    index = codec.reader.parse_index(index_bytes, len(package))
    by_path = {e['path'].replace('\\', '/').lower(): e for e in index['entries']}
    font_path = Path('C:/Windows/Fonts/msyh.ttc')
    if not font_path.is_file():
        raise ValueError('Native text raster export requires the recorded Microsoft YaHei font')
    paints = {key: Image.open(ROOT/path).convert('RGBA') for key, path in PAINTS.items()}
    declarations_path = ROOT/'references/qqtang-ui-data/constants/uiLogin.json'
    declarations = json.loads(declarations_path.read_bytes())
    postlogin_reference_path = ROOT/'assets/native-client-ui/postlogin-reference/manifest.json'
    postlogin_references = {e['nativePath'].lower():e for e in json.loads(postlogin_reference_path.read_bytes())['resources']}
    core_reference_path = ROOT/'assets/native-client-ui/core-reference/manifest.json'
    core_references = {e['nativePath'].lower():e for e in json.loads(core_reference_path.read_bytes())['resources']}
    extra_reference_paths = {name:ROOT/f'assets/native-client-ui/{name}-reference/manifest.json' for name in EXTRA_ART}
    extra_references = {name:{e['nativePath'].lower():e for e in json.loads(path.read_bytes())['resources']}
                        for name,path in extra_reference_paths.items()}
    sources, items = [], []
    with zipfile.ZipFile(archive_path) as archive:
        for native_path, (kind, label) in PATHS.items():
            member = 'QQTang-Local/runtime/client-patched/' + native_path
            packed = by_path.get(native_path.lower())
            loose = member in archive.namelist()
            original = archive.read(member) if loose else codec.reader.unpack_resource(package, packed)[0]
            if packed and codec.reader.unpack_resource(package, packed)[0] != original:
                raise ValueError('Loose and packaged source art differ')
            metadata, first = codec.reader.inspect_dimg(original)
            artifact_name = native_path.removesuffix('.img').replace('/', '__')
            reference_path = HERE / 'references' / f'{artifact_name}-frame0.png'
            save_image(reference_path, Image.frombytes('RGBA', (first['width'], first['height']), first['pixels']), check)
            pictures = {f['index']: artwork(kind, label, f['index'], (f['width'], f['height']), paints, font_path, metadata['frameCount'])
                        for f in metadata['frames'] if not f['empty']}
            output, _, frames = codec.replace_frames(original, pictures)
            target = HERE / 'patch' / native_path
            if check:
                if target.read_bytes() != output:
                    raise ValueError(f'Native DIMG export differs: {target}')
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(output)
            reference = {'nativePath': native_path, 'sourceSha256': hashlib.sha256(original).hexdigest(),
                         'sourceArchiveMember': member if loose else None, 'packedIndexEntry': packed,
                         'metadata': metadata, 'reference': record(reference_path)}
            reference['staticUiBindings'] = []
            postlogin_reference = postlogin_references.get(native_path.lower())
            if postlogin_reference:
                if postlogin_reference['sourceSha256'] != reference['sourceSha256']:
                    raise ValueError('Post-login reference differs from the packed native source')
                reference['staticPostLoginBindings'] = postlogin_reference['sourceBindings']
            core_reference = core_references.get(native_path.lower())
            if core_reference:
                if core_reference['sourceSha256'] != reference['sourceSha256']:
                    raise ValueError('Core reference differs from the packed native source')
                reference['staticCoreBindings'] = core_reference['sourceBindings']
            for name, references in extra_references.items():
                extra_reference = references.get(native_path.lower())
                if extra_reference:
                    if extra_reference['sourceSha256'] != reference['sourceSha256']:
                        raise ValueError(f'{name} source hash differs from the native resource')
                    reference.setdefault('additionalStaticReferences', []).append({
                        'group':name, 'manifest':record(extra_reference_paths[name]),
                        'sourceBindings':extra_reference.get('sourceBindings', extra_reference.get('bindings', []))})
            for scope in declarations['scopes']:
                literals = {e['name']:e['literalValue'] for e in scope['literalAssignments']}
                if any(c.get('type') == 'bytes' and c.get('text') == native_path for c in scope['constants']):
                    reference['staticUiBindings'].append({'scope':scope['scope'],
                        'rect':literals.get('rect'), 'frameScheme':literals.get('framescheme')})
            sources.append(reference)
            exported = []
            for frame, image in frames:
                path = HERE / 'decoded' / f'{artifact_name}-{frame["index"]:02d}.png'
                save_image(path, image, check)
                exported.append({**record(path), 'index': frame['index'], 'width': image.width, 'height': image.height,
                                 'pixelMode': frame['pixelMode'], 'frameOffset': frame['frameOffset']})
            items.append({**record(target), 'nativePath': native_path, 'sourceSha256': reference['sourceSha256'],
                          'sourceLoose': loose, 'sourcePacked': packed is not None, 'frames': exported,
                          'rendererKind': kind, 'caption': label,
                          'visualAccepted': False, 'nativeRuntimeVerified': False})
    save_json(HERE/'source-contract.json', {'schemaVersion': 1, 'sourceArchiveSha256': ARCHIVE_SHA,
              'sourcePackage': record(package_path), 'sourceIndex': record(index_path),
              'staticUiDeclarations': record(declarations_path), 'staticPostLoginReferences': record(postlogin_reference_path),
              'staticCoreReferences': record(core_reference_path),
              'additionalStaticReferences':[record(path) for path in extra_reference_paths.values()], 'items': sources}, check)
    manifest = {'schemaVersion': 1, 'scope': 'Native QQTang main screens, common controls, room and shop UI',
                'sourceContract': record(HERE/'source-contract.json'), 'items': items,
                'paintInputs': [record(ROOT/path) for path in PAINTS.values()],
                'rendererSources': [record(ROOT/'scripts'/name) for name in (
                    'build-native-login-art.py', 'native-ui-format.py', 'native-ui-postlogin-art.py', 'native-ui-core-art.py',
                    *MODULES.values())],
                'textRasterFont': {'family': 'Microsoft YaHei', 'sha256': hashlib.sha256(font_path.read_bytes()).hexdigest()},
                'additionalRasterFonts': [{'group':name,'purpose':purpose,'filename':Path(filename).name,
                    'sha256':hashlib.sha256(Path(filename).read_bytes()).hexdigest()}
                    for name,module in EXTRA_ART.items() for purpose,filename in getattr(module,'FONT_INPUTS',{}).items()],
                'structuralAlphaInputs': [{'group':name,'purpose':purpose,**record(ROOT/filename)}
                    for name,module in EXTRA_ART.items() for purpose,filename in getattr(module,'STRUCTURAL_ALPHA_INPUTS',{}).items()],
                'operation': 'Existing original painted UI sliced and text rendered at native control dimensions, then encoded into original DIMG pixel modes.',
                'newModelGeneration': False, 'visualAccepted': False, 'nativeRuntimeVerified': False}
    save_json(HERE/'manifest.json', manifest, check)
    print(json.dumps({'nativeResources': len(items), 'sourcePositions': sum(len(e['frames']) for e in items), 'pixelReplay': check}))


if __name__ == '__main__':
    main()
