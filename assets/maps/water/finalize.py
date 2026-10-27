"""Audit this family and document identical source-picture aliases. No painting."""
import copy
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FAMILY = OUT.name

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

manifest = read(OUT / 'art.json')
source = {p['elementId']: p for p in read(ROOT / 'assets/maps/production-index.json')['elements'] if p['family'] == FAMILY}
painted = {p['elementId']: p for p in manifest['pieces']}
groups = {}
for p in source.values():
    groups.setdefault(p['referencePng']['sha256'], []).append(p['elementId'])
aliases = []
for ids in groups.values():
    representative = next((identity for identity in ids if identity in painted), None)
    if representative is None:
        continue
    for identity in ids:
        if identity == representative:
            continue
        aliases.append({'elementId': identity, 'sourcePictureAliasOfElementId': representative, 'newModelGeneration': False})
        if identity in painted:
            continue
        target, original = source[identity], painted[representative]
        if target['selectedFrameSize'] != source[representative]['selectedFrameSize']:
            raise ValueError('Matching visible picture with different frame extent needs explicit transformation')
        piece = copy.deepcopy(original)
        path = OUT / f'pieces/{identity}-{FAMILY}-source-alias-v1.png'
        if path.exists():
            raise ValueError('Refusing overwrite')
        shutil.copyfile(ROOT / original['file'], path)
        piece.update({'elementId': identity, 'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'sourceReference': target['referencePng'], 'footprintCells': target['footprintCells'], 'sourceGridAttr': target['gridAttr'], 'sourceMapElemOffsetRaw': target['mapElemOffsetRaw'], 'sourceFrameOffsetRaw': target['selectedFrameOffsetRaw'], 'sourcePictureAliasOfElementId': representative, 'newIndependentPainting': False})
        piece['operation'] = {'type': 'reuse-original-ai-painted-candidate-for-identical-source-visible-picture', 'sourcePaintedFile': original['file'], 'sourcePaintedSha256': original['sha256'], 'resampled': False, 'newModelGeneration': False, 'sourceRectLTRB': original['operation']['sourceRectLTRB']}
        piece['qa']['warnings'].append('source-picture-alias-not-an-additional-model-generation')
        write(path.with_suffix('.png.provenance.json'), piece)
        manifest['pieces'].append(piece)
        painted[identity] = piece
manifest['pieces'].sort(key=lambda p: p['elementId'])
manifest['sourcePictureAliases'] = aliases
write(OUT / 'art.json', manifest)

errors, warnings = [], []
for piece in manifest['pieces']:
    identity, path = piece['elementId'], ROOT / piece['file']
    image = Image.open(path)
    original = source[identity]
    checks = {
        'hash': sha(path) == piece['sha256'],
        '4x-original-frame-canvas': image.size == tuple(v*4 for v in original['selectedFrameSize']),
        'rgba-with-transparent-pixels': image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] == 0,
        'provenance': path.with_suffix('.png.provenance.json').exists(),
        'unchanged-footprint': piece['footprintCells'] == original['footprintCells'],
        'unchanged-gridattr': piece['sourceGridAttr'] == original['gridAttr'],
        'unchanged-map-offset': piece['sourceMapElemOffsetRaw'] == original['mapElemOffsetRaw'],
        'unchanged-frame-offset': piece['sourceFrameOffsetRaw'] == original['selectedFrameOffsetRaw'],
        'unaccepted-status': piece['geometryAccepted'] is False,
    }
    errors.extend({'elementId': identity, 'check': name, 'file': piece['file']} for name, ok in checks.items() if not ok)
    if piece['qa']['relativeAspectDeviation'] > .1:
        warnings.append({'elementId': identity, 'check': 'visible-aspect-deviation', 'value': piece['qa']['relativeAspectDeviation'], 'threshold': .1, 'file': piece['file']})
    if piece['qa']['coreTouchesCellEdge']:
        warnings.append({'elementId': identity, 'check': 'generated-cell-edge-core-contact', 'value': True, 'threshold': False, 'file': piece['file']})
    for check in piece['qa'].get('manualUnpassed', []):
        warnings.append({'elementId': identity, 'file': piece['file'], **check})

sheets = []
for path in sorted(OUT.glob('props-*-v1.png.generation.json')):
    record = read(path)
    image_path = ROOT / record['file']
    image = Image.open(image_path)
    if sha(image_path) != record['sha256'] or image.size != (record['width'], record['height']):
        errors.append({'check': 'generated-native-identity', 'file': record['file']})
    if record['actualModel'] is not None or record['actualQuality'] is not None:
        errors.append({'check': 'unexpected-disclosed-metadata', 'file': record['file']})
    for ref in record['references']:
        ref_path = Path(ref['path'])
        if not ref_path.is_absolute():
            ref_path = ROOT / ref_path
        if sha(ref_path) != ref['sha256']:
            errors.append({'check': 'reference-hash', 'file': str(ref_path)})
    if not (ROOT / record['prompt']).exists():
        errors.append({'check': 'prompt-file', 'file': record['prompt']})
    sheets.append({'file': record['file'], 'nativeSize': [image.width, image.height], 'alpha': image.getchannel('A').getextrema(), 'generatedAt': record['generatedAt'], 'generationRecord': path.relative_to(ROOT).as_posix()})
missing = sorted(set(source)-set(painted))
if missing:
    errors.append({'check': 'source-definition-coverage', 'missing': missing})
qa = {'family': FAMILY, 'reviewedOn': '2026-10-26', 'candidateDefinitions': len(painted), 'distinctSourcePictures': len(groups), 'modelGenerations': len(sheets), 'sourcePictureAliases': aliases, 'geometryAccepted': 0, 'exportOperation': 'crop + uniform fit + bottom align on 4x original-frame transparent canvas; not native 4x AI detail', 'identityAndExportErrors': errors, 'unpassedChecks': warnings, 'globalUnpassedChecks': ['source-id-lookup-is-filename-inference-candidate', 'internal-region-boundaries-and-original-footprint-art-match-pending', 'terrain-repeat-and-neighbour-join-verification-pending', 'source-render-anchors-and-offset-placement-pending', 'in-game-visual-validation-not-run-browser-unavailable'], 'generatedSheets': sheets}
write(OUT / 'qa.json', qa)
lines = [f'# {FAMILY} 原创图元候选', '', f"2026-10-26：{len(painted)}/{len(source)} 条定义有候选，来自 {len(groups)} 幅不同源画面；{len(sheets)} 张内置 image_gen 母图，{len(aliases)} 条显式源画面别名。正式几何、锚点和游戏验收通过 0 条。", '', '所有地图坐标、footprint、GridAttr 和源 offset 保留原值。每件导出画布为原始 frame 的 4 倍，只做裁切、等比适配和透明画布放置，不代表模型原生 4 倍细节。', '', '每次实际附上 image 邮件/组队两主图及本批结构联系表。逐图记录保存配置目标、实际参数、返回文件、引用 SHA256 和 UTC 时间；宿主没有披露实际型号/质量，均为 null。', '', '## 文件', '', '- art.json：逐件文件、原始参数、裁切坐标与待验项。', '- props-*-v1.png.generation.json：每次独立生成记录。', '- pieces/*.png.provenance.json：每件派生来源与实际尺寸。', '- references/：带元素 ID、原始 frame 尺寸和占地的结构参考，仅供取证。', '- qa.json：身份/透明/尺寸/元数据验证和完整未通过点。', '- candidate-contact.png：当前候选检查联系表，不是游戏内预览。', '', '## 母图原生尺寸', '', '| 母图 | 实际原生尺寸 | 记录 |', '|---|---|---|']
for s in sheets:
    lines.append(f"| {Path(s['file']).name} | {s['nativeSize'][0]}×{s['nativeSize'][1]} | {Path(s['generationRecord']).name} |")
lines.extend(['', '## 尚未通过', '', '| ID | 检查 | 数值 | 门槛 | 文件 |', '|---|---|---:|---:|---|'])
for w in warnings:
    value = f"{w['value']:.3f}" if isinstance(w['value'], float) else str(w['value'])
    lines.append(f"| {w['elementId']} | {w['check']} | {value} | {w['threshold']} | {Path(w['file']).name} |")
lines.extend(['', '宽高比不超阈值也不等于内部区界、连接口、占地/轮廓与源图匹配已经通过。相邻接缝、重复边、源锚点及实际落位均待验。', '', '源画面别名：' + (', '.join(f"{a['elementId']}→{a['sourcePictureAliasOfElementId']}" for a in aliases) or '无；每幅源画面均独立制作。'), '', '本批没有浏览器或游戏内截图验收，没有修改其他族、全局生产统计或共享 Git。'])
(OUT / 'README.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(json.dumps({'family': FAMILY, 'definitions': len(painted), 'pictures': len(groups), 'generations': len(sheets), 'aliases': len(aliases), 'unpassed': len(warnings), 'errors': errors}))
