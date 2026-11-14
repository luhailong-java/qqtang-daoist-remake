"""Audit native source-path coverage from any number of explicit export manifests."""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_bytes())


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def key(path):
    return path.replace('\\', '/').casefold()


def frame_count(resource):
    if resource['format'] == 'QQF/DIMG':
        return resource['metadata']['frameCount']
    return resource.get('frameCount')


def image_resource(resource):
    return resource['format'] in ('QQF/DIMG', 'TGA', 'GIF')


def broad_group(path):
    if path.startswith('res/uires/icon/'):
        return 'res/uiRes/icon'
    if path.startswith('res/uires/'):
        return 'res/uiRes other'
    if path.startswith('object/ui/'):
        return 'object/ui'
    return 'ui'


def detail_group(resource):
    path = resource['path']
    parts = path.split('/')
    prefix = resource['storage'] + '/'
    if key(path).startswith('object/ui/'):
        return prefix + '/'.join(parts[:3])
    if key(path).startswith('res/uires/icon/'):
        return prefix + '/'.join(parts[:4])
    return prefix + '/'.join(parts[:-1])


def summarize(source, converted, installed):
    paths = {r['canonicalPath'] for r in source}
    images = {r['canonicalPath'] for r in source if image_resource(r)}
    return {
        'sourceResourcePaths': len(paths), 'sourceImagePaths': len(images),
        'sourceDeclaredImagePositions': sum(frame_count(r) or 0 for r in source),
        'convertedPaths': len(paths & converted.keys()),
        'convertedImagePaths': len(images & converted.keys()),
        'installedReceiptPaths': len(paths & installed.keys()),
        'installedReceiptImagePaths': len(images & installed.keys()),
        'remainingUnconvertedPaths': len(paths - converted.keys()),
        'remainingUnconvertedImagePaths': len(images - converted.keys()),
        'remainingNotInInstalledReceiptPaths': len(paths - installed.keys()),
        'installedMatchingCurrentExportPaths': sum(path in installed and installed[path]['installedSha256'] == item['sha256']
                                                  for path, item in converted.items() if path in paths),
    }


def renderer_paths():
    declared = defaultdict(list)
    for path in sorted((ROOT / 'scripts').glob('native-ui-*-art.py')):
        tree = ast.parse(path.read_bytes(), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.Assign) or not any(isinstance(t, ast.Name) and t.id == 'PATHS' for t in node.targets):
                continue
            values = ast.literal_eval(node.value)
            for native, definition in values.items():
                declared[key(native)].append({'renderer': record(path), 'nativePath': native,
                                              'rendererKind': definition[0], 'caption': definition[1]})
    return declared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', action='append', required=True, type=Path)
    parser.add_argument('--installation', action='append', default=[], type=Path)
    parser.add_argument('--source', type=Path, default=Path('references/qqtang-ui-data/native-ui-inventory.json'))
    parser.add_argument('--output-json', type=Path, default=Path('docs/native-ui-remaining-20261114.json'))
    parser.add_argument('--output-md', type=Path, default=Path('docs/NATIVE_UI_REMAINING_20261114.md'))
    args = parser.parse_args()
    source_path = ROOT / args.source
    census = read(source_path)
    source = census['resources']
    by_path = {r['canonicalPath']: r for r in source}
    converted, installed, outside_receipt_resources = {}, {}, []
    manifests, receipts, pending = [], [], []
    for relative in args.manifest:
        path = ROOT / relative
        manifest = read(path)
        manifests.append(record(path))
        pending.extend({'manifest': relative.as_posix(), **item} for item in manifest.get('pendingItems', []))
        for item in manifest['items']:
            native = key(item['nativePath'])
            if native not in by_path:
                raise ValueError(f'Export path is outside the source UI census: {native}')
            previous = converted.get(native)
            if previous and previous['sha256'] != item['sha256']:
                raise ValueError(f'Conflicting export manifests for {native}')
            output = ROOT / item['file']
            if record(output)['sha256'] != item['sha256']:
                raise ValueError(f'Export file changed: {output}')
            if item['sourceSha256'] != by_path[native]['sourceSha256']:
                raise ValueError(f'Source identity differs: {native}')
            converted[native] = {**item, 'manifest': relative.as_posix()}
    for relative in args.installation:
        path = ROOT / relative
        receipt = read(path)
        receipts.append({**record(path), 'verifiedOn': receipt.get('verifiedOn'),
                         'nativeRuntimeVerified': receipt.get('nativeRuntimeVerified'),
                         'userVisualAccepted': receipt.get('userVisualAccepted')})
        for item in receipt['resources']:
            native = key(item['nativePath'])
            if native not in by_path:
                outside_receipt_resources.append({**item,'receipt':relative.as_posix(),
                    'scope':'Outside the UI source census; excluded from all UI totals'})
                continue
            if item['sourceSha256'] != by_path[native]['sourceSha256']:
                raise ValueError(f'Installed receipt source differs: {native}')
            # Later explicit receipts supersede earlier receipt snapshots for the same path.
            installed[native] = {**item, 'receipt': relative.as_posix()}

    grouped = defaultdict(list)
    for resource in source:
        grouped[detail_group(resource)].append(resource)
    rows = []
    for name, resources in sorted(grouped.items()):
        rows.append({'group': name, **summarize(resources, converted, installed),
                     'remainingImagePaths': sorted(r['path'] for r in resources
                         if image_resource(r) and r['canonicalPath'] not in converted)})
    broad = []
    for name in ('object/ui', 'ui', 'res/uiRes/icon', 'res/uiRes other'):
        broad.append({'group': name, **summarize([r for r in source if broad_group(r['canonicalPath']) == name],
                                               converted, installed)})
    ready_renderers = []
    for native, definitions in renderer_paths().items():
        if native not in converted and native in by_path:
            ready_renderers.append({'nativePath': by_path[native]['path'], 'sourceSha256': by_path[native]['sourceSha256'],
                                    'sourcePositions': frame_count(by_path[native]), 'rendererDefinitions': definitions,
                                    'status': 'renderer-defined; native export and visual checks pending'})
    pending = [item for item in pending if key(item.get('nativePath', '')) not in converted]
    body = {
        'schemaVersion': 1, 'capturedOn': '2026-11-14', 'auditScript': record(Path(__file__)),
        'sourceCensus': record(source_path), 'exportManifests': manifests, 'installedReceipts': receipts,
        'sourceScope': 'Native object/ui, ui and res/uiRes graphic/resource paths from the pinned archive',
        'summary': summarize(source, converted, installed), 'broadGroups': broad, 'detailGroups': rows,
        'convertedPaths': sorted(converted), 'installedReceiptPaths': sorted(installed),
        'outsideSourceCensusInstalledReceiptResources': outside_receipt_resources,
        'convertedNotMatchingCurrentInstalledReceipt': [
            {'nativePath': item['nativePath'], 'exportSha256': item['sha256'],
             'installedSha256': installed.get(path, {}).get('installedSha256'), 'manifest': item['manifest']}
            for path, item in sorted(converted.items())
            if installed.get(path, {}).get('installedSha256') != item['sha256']],
        'existingPaintedInventoryCandidatesPendingNativeExport': pending,
        'existingRendererPathsPendingNativeExport': ready_renderers,
        'acceptanceOutsideThisPathDenominator': [
            {'surface': 'QQTang-Launcher.exe title, labels, icon and other launcher branding', 'status': 'unknown; outside source graphic path census'},
            {'surface': 'Client native system-window title and executable VERSIONINFO/brand strings', 'status': 'unknown; outside source graphic path census'},
            {'surface': 'PYC literal captions and dynamic native text, including original product/currency labels', 'status': 'pending text audit; image-path replacement does not prove these strings changed'},
            {'surface': 'Native font atlas res/GBK12.bmp and compiled glyph/text rendering', 'status': 'unknown; outside the selected directory census'},
            {'surface': 'Real running page behavior, tooltip placement, state transition, text contrast and original flow', 'status': 'pending runtime and user visual acceptance'},
            {'surface': 'All characters, equipped world frames, maps, monsters, effects and audio', 'status': 'separate full-game scope; inventory UI icons do not establish world-art completion'},
        ],
        'limitations': [
            'The source census counts file paths and declared image positions, not distinct pages or accepted states.',
            'Installed counts come from explicit static readback receipts. This audit does not launch or inspect the user client.',
            'Native icons are a separate source group. They are not added to the non-icon UI page count.',
            'Original art inputs without an exact native path/state plan require binding before native export.',
        ],
        'fullNativeUiAccepted': False,
    }
    (ROOT / args.output_json).write_bytes((json.dumps(body, ensure_ascii=False, indent=2) + '\n').encode())
    summary = body['summary']
    lines = ['# 原生 UI 剩余覆盖', '',
        f"本次显式读取 {len(manifests)} 份转换清单和 {len(receipts)} 份静态安装回执。源目录共 {summary['sourceResourcePaths']} 个路径，其中 {summary['sourceImagePaths']} 份图像。当前有 {summary['convertedPaths']} 个同名原生资源导出，安装回执覆盖 {summary['installedReceiptPaths']} 个路径，其中 {summary['installedMatchingCurrentExportPaths']} 个与当前导出 SHA 一致。", '',
        '| 来源组 | 源图像路径 | 已转换 | 回执已装 | 图像仍待转换 |', '|---|---:|---:|---:|---:|']
    for row in broad:
        lines.append(f"| {row['group']} | {row['sourceImagePaths']} | {row['convertedImagePaths']} | {row['installedReceiptImagePaths']} | {row['remainingUnconvertedImagePaths']} |")
    lines += ['', '图标行统计物品库存、角色头像等图像路径；其余三行统计界面图像。文件路径覆盖与整页、所有控件状态、动态文字和实际交互分别验收。静态安装回执也保留运行与用户画面审核的待验状态。', '',
              '| 原生子组 | 源图像 | 已转换 | 回执已装 | 待转换 |', '|---|---:|---:|---:|---:|']
    for row in rows:
        if row['sourceImagePaths']:
            lines.append(f"| {row['group']} | {row['sourceImagePaths']} | {row['convertedImagePaths']} | {row['installedReceiptImagePaths']} | {row['remainingUnconvertedImagePaths']} |")
    lines += ['', f"现有绘制资源中，{len(ready_renderers)} 个原生路径已有独立 renderer 定义、尚未出现在本次转换清单里；{len(pending)} 件库存候选仍在转换器的 pendingItems 中。对应精确路径、源尺寸和原因见机器清单。数值会随新增模块和转换清单变化，脚本接受多个 --manifest 与 --installation 参数后重算。", '',
              '启动器标题／品牌、原生系统窗口标题、PYC 文案、运行时动态文字和 GBK12.bmp 字库均需单独核对。它们的替换状态保持 unknown 或 pending，本路径统计没有证明这些内容已换完。角色佩戴、地图、怪物、特效与音频属于整款游戏的另一个制作分母。', '',
              '[完整机器清单](native-ui-remaining-20261114.json)保留输入哈希、逐路径差额、待转候选和审核边界。', '', '```powershell',
              'python -B scripts/audit-native-ui-remaining.py `',
              *[f'  --manifest {entry["file"]} `' for entry in manifests],
              *[f'  --installation {entry["file"]}' + (' `' if index + 1 < len(receipts) else '') for index, entry in enumerate(receipts)],
              '```', '']
    if not receipts:
        lines[-3] = lines[-3].removesuffix(' `')
    (ROOT / args.output_md).write_bytes(('\n'.join(lines)).encode())
    print(json.dumps({'summary': summary, 'readyRendererPaths': len(ready_renderers), 'pendingInventoryItems': len(pending),
                      'json': record(ROOT / args.output_json), 'markdown': record(ROOT / args.output_md)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
