"""Audit this family's candidates and document explicit source-picture aliases.

No painting, source geometry changes, global inventory changes, or Git operations.
"""
import copy
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


manifest = read(OUT / 'art.json')
source = {item['elementId']: item for item in read(ROOT / 'assets/maps/production-index.json')['elements'] if item['family'] == 'mine'}
painted = {item['elementId']: item for item in manifest['pieces']}

for alias_id, original_id in [(4017, 4014), (4023, 4019)]:
    if alias_id in painted:
        continue
    original, target = painted[original_id], source[alias_id]
    if source[original_id]['referencePng']['sha256'] != target['referencePng']['sha256']:
        raise ValueError('The supposed source picture alias does not match')
    if source[original_id]['selectedFrameSize'] != target['selectedFrameSize']:
        raise ValueError('Different frame canvas requires a separately documented transform')
    item = copy.deepcopy(original)
    item['elementId'] = alias_id
    destination = OUT / f'pieces/{alias_id}-mine-source-alias-v1.png'
    if destination.exists():
        raise ValueError('Refusing to replace an existing candidate')
    shutil.copyfile(ROOT / original['file'], destination)
    item['file'] = destination.relative_to(ROOT).as_posix()
    item['sha256'] = sha(destination)
    item['operation'] = {
        'type': 'reuse-original-ai-painted-candidate-for-identical-source-visible-picture',
        'sourcePaintedFile': original['file'],
        'sourcePaintedSha256': original['sha256'],
        'resampled': False,
        'newModelGeneration': False,
        'sourceRectLTRB': original['operation']['sourceRectLTRB'],
    }
    item['sourceReference'] = target['referencePng']
    item['footprintCells'] = target['footprintCells']
    item['sourceGridAttr'] = target['gridAttr']
    item['sourceMapElemOffsetRaw'] = target['mapElemOffsetRaw']
    item['sourceFrameOffsetRaw'] = target['selectedFrameOffsetRaw']
    item['sourcePictureAliasOfElementId'] = original_id
    item['newIndependentPainting'] = False
    item['qa']['warnings'].extend([
        'source-picture-alias-not-an-additional-model-generation',
        'independent-offset-and-in-game-validation-required',
    ])
    write(destination.with_suffix('.png.provenance.json'), item)
    manifest['pieces'].append(item)
    painted[alias_id] = item

manifest['pieces'].sort(key=lambda item: item['elementId'])
manifest['sourcePictureAliases'] = [
    {'elementId': a, 'sourcePictureAliasOfElementId': b, 'newModelGeneration': False}
    for a, b in [(4017, 4014), (4023, 4019)]
]
write(OUT / 'art.json', manifest)

errors = []
warnings = []
for item in manifest['pieces']:
    identity = item['elementId']
    path = ROOT / item['file']
    image = Image.open(path)
    expected_size = tuple(size * 4 for size in source[identity]['selectedFrameSize'])
    checks = {
        'hash': sha(path) == item['sha256'],
        '4x-original-frame-canvas': image.size == expected_size,
        'real-rgba-with-transparent-pixels': image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] == 0,
        'provenance': path.with_suffix('.png.provenance.json').exists(),
        'unchanged-footprint': item['footprintCells'] == source[identity]['footprintCells'],
        'unchanged-gridattr': item['sourceGridAttr'] == source[identity]['gridAttr'],
        'unchanged-map-offset': item['sourceMapElemOffsetRaw'] == source[identity]['mapElemOffsetRaw'],
        'unchanged-frame-offset': item['sourceFrameOffsetRaw'] == source[identity]['selectedFrameOffsetRaw'],
        'unaccepted-status': item['geometryAccepted'] is False,
    }
    errors.extend({'elementId': identity, 'check': name, 'file': item['file']} for name, ok in checks.items() if not ok)
    if item['qa']['relativeAspectDeviation'] > .1:
        warnings.append({'elementId': identity, 'check': 'visible-aspect-deviation', 'value': item['qa']['relativeAspectDeviation'], 'threshold': .1, 'file': item['file']})
    if item['qa']['coreTouchesCellEdge']:
        warnings.append({'elementId': identity, 'check': 'generated-cell-edge-core-contact', 'value': True, 'threshold': False, 'file': item['file']})

sheets = []
for path in sorted(OUT.glob('props-*-v1.png.generation.json')):
    record = read(path)
    image_path = ROOT / record['file']
    image = Image.open(image_path)
    if sha(image_path) != record['sha256'] or [image.width, image.height] != [record['width'], record['height']]:
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

missing = sorted(set(source) - set(painted))
if missing:
    errors.append({'check': 'source-definition-coverage', 'missing': missing})

qa = {
    'family': 'mine', 'reviewedOn': '2026-10-26',
    'candidateDefinitions': len(painted), 'distinctSourcePictures': 68,
    'modelGenerations': len(sheets), 'sourcePictureAliases': manifest['sourcePictureAliases'],
    'geometryAccepted': 0,
    'exportOperation': 'crop + uniform fit + bottom align on 4x original-frame transparent canvas; not native 4x AI detail',
    'identityAndExportErrors': errors,
    'unpassedChecks': warnings,
    'globalUnpassedChecks': [
        'source-id-lookup-is-filename-inference-candidate',
        'internal-region-boundaries-and-original-footprint-art-match-pending',
        'terrain-repeat-and-neighbour-join-verification-pending',
        'source-render-anchors-and-offset-placement-pending',
        'in-game-visual-validation-not-run-browser-unavailable',
    ],
    'generatedSheets': sheets,
}
write(OUT / 'qa.json', qa)

lines = [
    '# 矿洞族原创图元候选', '',
    '2026-10-26：70 条定义已形成候选，来自 68 幅不同源画面；11 张内置 image_gen 母图，2 条源画面别名。正式几何、锚点和游戏验收通过 0 条。', '',
    '所有地图坐标、footprint、GridAttr 与源 offset 保持原值。每件导出画布是原始 frame 的 4 倍；操作只有裁切、等比适配和透明画布放置，不代表模型原生 4 倍细节。', '',
    '每次实际附上 image 邮件/组队两主图及对应结构联系表。逐图记录保存配置目标、实际参数、工具输出、引用 SHA256 和 UTC 时间；宿主没有披露实际型号/质量，均为 null。', '',
    '## 文件', '',
    '- art.json：70 条定义的逐件文件、原始参数、裁切坐标与未通过点。',
    '- props-[a-k]-v1.png.generation.json：11 次独立生成记录。',
    '- pieces/*.png.provenance.json：每件派生来源。',
    '- references/：结构参考联系表，包含元素 ID、原始 frame 尺寸与占地；不作为运行时原创素材。',
    '- qa.json：完整校验数值与未通过状态。', '',
    '## 母图原生尺寸', '',
    '| 母图 | 实际原生尺寸 | 生成记录 |', '|---|---|---|',
]
for sheet in sheets:
    label = Path(sheet['file']).name
    lines.append(f"| {label} | {sheet['nativeSize'][0]}×{sheet['nativeSize'][1]} | {Path(sheet['generationRecord']).name} |")
lines.extend(['', '## 尚未通过', '', '| ID | 检查 | 数值 | 门槛 | 文件 |', '|---|---|---:|---:|---|'])
for warning in warnings:
    value = warning['value']
    value = f'{value:.3f}' if isinstance(value, float) else str(value)
    lines.append(f"| {warning['elementId']} | {warning['check']} | {value} | {warning['threshold']} | {Path(warning['file']).name} |")
lines.extend([
    '',
    '宽高比数值不超阈值也不代表内部区界、出口/连接口、图元占地已经通过。地砖纹样和坑壁区域还需按源位置匹配，重复/相邻接缝、墙柱连接、特殊复合结构内部区域以及锚点均未通过。', '',
    '4017 复用 4014，4023 复用 4019；仅因源画面 SHA256 相同，不计作新增独立绘制。保留各自原始 offset、GridAttr、footprint 和待验状态。', '',
    '本批没有浏览器或游戏内截图验收。没有修改 town、snow、全局统计或共享 Git。',
])
(OUT / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'definitions': len(painted), 'pictures': 68, 'generations': len(sheets), 'aliases': 2, 'unpassed': len(warnings), 'errors': errors}))
