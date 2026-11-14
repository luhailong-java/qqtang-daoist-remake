"""Decode selected native UI references and read their inert literal source bindings."""
from pathlib import Path
import hashlib
import importlib.util
import json
import io
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = ROOT / '.artifacts/reference-inputs'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
PATHS = ('object/ui/guidebar/btn_amend.img', 'object/ui/guidebar/btn_cancel_dismiss.img', 'object/ui/guidebar/btn_check.img', 'object/ui/guidebar/btn_dismiss.img', 'object/ui/guidebar/btn_folderup.img', 'object/ui/guidebar/btn_issue.img', 'object/ui/guidebar/btn_player.img', 'object/ui/guidebar/btn_quitkin.img', 'object/ui/guidebar/btn_top_kin.img', 'object/ui/guidebar/dlg_kinmember.img', 'object/ui/guidebar/dlg_kinmgr.img', 'object/ui/guidebar/dlg_player.img', 'object/ui/guidebar/dlg_record.img', 'object/ui/guidebar/friend/dlg_addfriends.img', 'object/ui/guidebar/friend/dlg_beaddedfriends.img', 'object/ui/guidebar/img_friendmask.img', 'object/ui/guidebar/kin/arrow_0.img', 'object/ui/guidebar/kin/arrow_1.img', 'object/ui/guidebar/kin/arrow_2.img', 'object/ui/guidebar/kin/bg_kin_menu.img', 'object/ui/guidebar/kin/btn_activity.img', 'object/ui/guidebar/kin/btn_honor.img', 'object/ui/guidebar/kin/btn_netcom.img', 'object/ui/guidebar/kin/btn_telecom.img', 'object/ui/guidebar/kin/dlg_createhint.img', 'object/ui/guidebar/kin/dlg_createkin.img', 'object/ui/guidebar/kin/dlg_kininfo.img', 'object/ui/guidebar/kin/dlg_kininvite.img', 'object/ui/guidebar/kin/dlg_topkin.img', 'object/ui/guidebar/kin/img_activity.img', 'object/ui/guidebar/player/btn_lookupkin.img', 'object/ui/guidebar/player/dlg_modeinfo.img', 'object/ui/guidebar/player/dlg_playerinfo.img', 'object/ui/guidebar/player/dlg_pveinfo.img', 'object/ui/guidebar/player/img_bun.img', 'object/ui/guidebar/player/img_expline.img', 'object/ui/guidebar/player/img_expline2.img', 'object/ui/guidebar/player/img_mask.img', 'object/ui/guidebar/player/img_match.img', 'object/ui/guidebar/player/img_modeexpline.img', 'object/ui/guidebar/player/img_sculpture.img', 'object/ui/guidebar/player/mask_demo.img', 'object/ui/guidebar/tab_allkinmember.img', 'object/ui/guidebar/tab_kin.img', 'object/ui/guidebar/tab_kinmatch.img', 'object/ui/guidebar/tab_kinmember.img', 'object/ui/guidebar/tab_kinmgr.img', 'object/ui/guidebar/tab_team.img', 'object/ui/guidebar/tip_entershop.img', 'object/ui/marriage/bg/dlg_chinabg.img', 'object/ui/marriage/bg/dlg_chinaicon.img', 'object/ui/marriage/bg/dlg_westbg.img', 'object/ui/marriage/bg/dlg_westicon.img', 'object/ui/marriage/btn_iaccept.img', 'object/ui/marriage/btn_ireject.img', 'object/ui/marriage/btn_close.img', 'object/ui/marriage/btn_divorce.img', 'object/ui/marriage/btn_divorcecancel.img', 'object/ui/marriage/btn_divorceconfirm.img', 'object/ui/marriage/btn_left.img', 'object/ui/marriage/btn_lookup.img', 'object/ui/marriage/btn_modify.img', 'object/ui/marriage/btn_noring.img', 'object/ui/marriage/btn_right.img', 'object/ui/marriage/btn_save.img', 'object/ui/marriage/btn_spark.img', 'object/ui/marriage/btn_sparkcancel.img', 'object/ui/marriage/btn_sparksend.img', 'object/ui/marriage/btn_startwedding.img', 'object/ui/marriage/dlg_closeline.img', 'object/ui/marriage/dlg_closelinevalue.img', 'object/ui/marriage/dlg_divorce.img', 'object/ui/marriage/dlg_loveword.img', 'object/ui/marriage/dlg_marriageconfirmchina.img', 'object/ui/marriage/dlg_marriageconfirmwest.img', 'object/ui/marriage/dlg_marriageinfo.img', 'object/ui/marriage/dlg_priestchat.img', 'object/ui/marriage/dlg_receivespark.img', 'object/ui/marriage/dlg_setmarriage.img', 'object/ui/marriage/dlg_spark.img', 'object/ui/marriage/dlg_weddingsuccess.img', 'object/ui/marriage/marriagelevel/dlg_coronet.img', 'object/ui/marriage/marriagelevel/dlg_diamond.img', 'object/ui/marriage/marriagelevel/dlg_heart.img', 'object/ui/marriage/priest/dlg_chinapriest.img', 'object/ui/marriage/priest/dlg_chinapriests.img', 'object/ui/marriage/priest/dlg_westpriest.img', 'object/ui/marriage/priest/dlg_westpriests.img', 'object/ui/marriage/ring/ring9021.img', 'object/ui/marriage/ring/ring9022.img', 'object/ui/marriage/ring/ring9023.img', 'object/ui/marriage/ring/ring9024.img', 'object/ui/marriage/ring/ring9025.img', 'object/ui/marriage/ring/ring9026.img')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


reader = module('native_postlogin_dimg', 'scripts/inspect-reference-dimg.py')
codec = module('native_social_codec', 'scripts/native-ui-format.py')
constants = module('native_postlogin_constants', 'scripts/read-legacy-ui-constants.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def literal(value):
    if value['type'] in ('tuple', 'list'):
        return [literal(item) for item in value['values']]
    return value.get('text', value.get('value'))


def main():
    archive_path = INPUTS / 'QQTang-Local-v1.3.4.zip'
    with archive_path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Pinned archive mismatch')
    index_path, package_path = INPUTS / 'object.idx', INPUTS / 'object.pkg'
    index_bytes, package_bytes = index_path.read_bytes(), package_path.read_bytes()
    inventory_path = ROOT / 'references/qqtang-ui-data/native-ui-inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    if sha(index_bytes) != inventory['index']['sha256'] or sha(package_bytes) != inventory['package']['sha256']:
        raise ValueError('Pinned package/index differs')
    entries = reader.parse_index(index_bytes, len(package_bytes))['entries']
    by_path = {entry['path'].replace('\\', '/').lower(): entry for entry in entries}
    resources = {r['canonicalPath']: r for r in inventory['resources'] if r['storage'] == 'packed'}
    source_modules = []
    scopes = []
    with zipfile.ZipFile(archive_path) as archive:
        for name in ('uiMain', 'uiTemplate', 'uiSelRoom', 'uiRoom', 'uiShop', 'uiFunc'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            node, count = constants.decode(raw)
            decoded = constants.collect(node)
            source_modules.append({'module': name, 'archiveMember': member, 'sha256': sha(raw),
                                   'byteLength': len(raw), 'parsedObjects': count, 'scopeCount': len(decoded),
                                   'bytecodeExecuted': False})
            scopes.extend((name, scope) for scope in decoded)
    binding_rows = []
    for name, scope in scopes:
        assignments = {item['name']: literal(item['literalValue']) for item in scope['literalAssignments']}
        values = {item.get('text', '').replace('\\', '/').lower() for item in scope['constants']}
        paths = [path for path in PATHS if path in values]
        for path in paths:
            binding_rows.append({'module': name, 'scope': scope['scope'], 'firstSourceLine': scope['firstLine'],
                                 'bytecodeSha256': scope['bytecodeSha256'], 'nativePath': path,
                                 'literalAssignments': assignments, 'activeControlFlowConfirmed': False})
    output = []
    for path in PATHS:
        entry = by_path[path]
        raw, compressed_sha = reader.unpack_resource(package_bytes, entry)
        if sha(raw) != resources[path]['sourceSha256'] or compressed_sha != resources[path]['compressedSha256']:
            raise ValueError('Pinned resource mismatch')
        image_format = resources[path]['format']
        metadata, _ = codec.inspect_native(raw, metadata_only=True)
        frames = []
        for frame in metadata['frames']:
            if frame['empty']:
                frames.append({'sourceFrameIndex': frame['index'], 'empty': True, 'frameOffsetRaw': frame['frameOffset']})
                continue
            start = frame['pixelDataOffset']
            pixels = codec.decode_native_frame(raw, frame).tobytes()
            image = Image.frombytes('RGBA', (frame['width'], frame['height']), pixels)
            target = HERE / 'frames' / path.removeprefix('object/ui/').removesuffix('.img') / f'frame-{frame["index"]:03}.png'
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            if Image.open(target).convert('RGBA').tobytes() != pixels:
                raise ValueError('Saved source pixels differ')
            frames.append({**record(target), 'sourceFrameIndex': frame['index'], 'empty': False,
                           'nativeSize': list(image.size), 'frameOffsetRaw': frame['frameOffset'], 'pixelMode': frame['pixelMode'],
                           'decodedRgbaSha256': sha(pixels), 'alphaExtrema': list(image.getchannel('A').getextrema())})
        output.append({'format':image_format,'nativePath': path, 'sourceSha256': sha(raw), 'compressedSha256': compressed_sha, 'packageEntry': entry,
                       'metadata': metadata, 'frames': frames, 'sourceBindings': [b for b in binding_rows if b['nativePath'] == path]})
    row_heights = [120*((len(r['frames'])+4)//5) for r in output]
    board = Image.new('RGB', (1200, sum(row_heights)), '#eae3d1')
    draw = ImageDraw.Draw(board)
    top = 0
    for resource,height in zip(output,row_heights,strict=True):
        draw.text((7,top+4),resource['nativePath'],fill='#204638')
        for j,frame in enumerate(resource['frames']):
            image = Image.open(ROOT/frame['file']).convert('RGBA')
            scale = min(2,205/image.width,88/image.height)
            image = image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))),Image.Resampling.NEAREST)
            x,y = 7+(j%5)*238,top+(j//5)*120
            draw.text((x,y+19),str(frame['sourceFrameIndex']),fill='#204638')
            board.paste(image,(x+18,y+27),image)
        top += height
    panel_path = HERE/'source-all-states.png'
    board.save(panel_path)
    source_pages=[]
    for page in range(4):
        rows=output[page*24:(page+1)*24]
        page_board=Image.new('RGB',(1200,150*len(rows)),'#eae3d1');page_draw=ImageDraw.Draw(page_board)
        for n,resource in enumerate(rows):
            y=n*150;page_draw.text((4,y+3),resource['nativePath'],fill='#204638')
            for j,frame in enumerate(resource['frames']):
                im=Image.open(ROOT/frame['file']).convert('RGBA');scale=min(2,260/im.width,112/im.height)
                im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.NEAREST);px=5+j*296
                page_draw.text((px,y+18),str(frame['sourceFrameIndex']),fill='#204638');page_board.paste(im,(px+14,y+35),im)
        page_path=HERE/f'source-page-{page+1}.png';page_board.save(page_path);source_pages.append(record(page_path))
    source = {'archiveSha256': ARCHIVE_SHA, 'archiveFile': archive_path.relative_to(ROOT).as_posix(),
              'package': record(package_path), 'index': record(index_path), 'sourceModules': source_modules,
              'inventory': record(inventory_path)}
    manifest = {'schemaVersion': 1, 'scope': 'Read-only source image and literal UI reference evidence', 'source': source,
                'decodeScript': record(Path(__file__).resolve()), 'nativeCodec': record(ROOT/'scripts/native-ui-format.py'),
                'resources': output, 'resourceCount': len(output), 'decodedNonemptyFrameCount': sum(len(r['frames']) for r in output),
                'previews': [record(panel_path), *source_pages], 'sourcePixelsOnly': True,
                'sourceClientMutated': False, 'nativeRuntimeVerified': False,
                'interpretation': 'Static literal scope and decoded source pixels. Runtime active flow and button-state semantic ordering require further evidence.'}
    save(HERE / 'manifest.json', manifest)
    print(json.dumps({'resources': len(output), 'decodedFrames': manifest['decodedNonemptyFrameCount'],
                      'bindings': len(binding_rows), 'manifest': record(HERE / 'manifest.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
