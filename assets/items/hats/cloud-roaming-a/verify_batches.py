"""Check only explicit partial cap batches, without claiming all447 inventory candidates exist."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'


def file(value):
    result = (ROOT / value).resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError('File leaves this project')
    return result


def sha(value):
    return hashlib.sha256(value.read_bytes()).hexdigest()


def read(value):
    return json.loads(file(value).read_bytes())


def check_generation(record_path, seen):
    if record_path in seen:
        return
    seen.add(record_path)
    generation = read(record_path)
    assert generation['actualModel'] is None and generation['actualQuality'] is None
    assert sha(file(generation['file'])) == generation['sha256']
    with Image.open(file(generation['file'])) as mother:
        assert list(mother.size) == [generation['width'], generation['height']]
        assert mother.mode == 'RGBA'
    for attempt in generation['attempts']:
        args_file = file(attempt['submittedArgsFile'])
        prompt_file = file(attempt['exactPromptUtf8File'])
        assert sha(args_file) == attempt['submittedArgsSha256']
        assert sha(prompt_file) == attempt['exactPromptUtf8Sha256']
        args = json.loads(args_file.read_bytes())
        assert prompt_file.read_bytes() == args['prompt'].encode('utf-8')
        assert args['transparent_background'] is True
    for reference in generation['references']:
        assert sha(file(reference['file'])) == reference['sha256']
    if generation.get('parentGenerationRecord'):
        check_generation(generation['parentGenerationRecord'], seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifests', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    catalog = read('references/qqtang-item-data/catalog.json')
    source = {entry['item_id']: entry for entry in catalog['items'] if entry['category'] == 'cap'}
    archive_path = file('.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')
    with archive_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == ARCHIVE_SHA
    reader_spec = importlib.util.spec_from_file_location('cap_verification_reader', ROOT / 'scripts/inspect-reference-dimg.py')
    decoder = importlib.util.module_from_spec(reader_spec)
    reader_spec.loader.exec_module(decoder)
    ids, hashes, generations, checks = set(), set(), set(), []
    with zipfile.ZipFile(archive_path) as archive:
        for manifest_path in args.manifests:
            manifest = read(manifest_path)
            assert manifest['category'] == 'cap' and len(manifest['items']) == 6
            for entry in manifest['items']:
                ident = entry['itemId']
                assert ident not in ids
                ids.add(ident)
                original = source[ident]
                assert entry['category'] == 'cap' and entry['sourceName'] == original['name']
                assert entry['sourceDescription'] == original['description']
                assert entry['resourceId'] == original['resource_id']
                assert entry['accepted'] is entry['visualAccepted'] is entry['runtimeAdopted'] is False
                target = file(entry['file'])
                assert sha(target) == entry['sha256']
                assert entry['sha256'] not in hashes
                hashes.add(entry['sha256'])
                with Image.open(target) as output:
                    assert output.mode == 'RGBA' and output.size == (256,256)
                    alpha = output.getchannel('A')
                    box = alpha.point(lambda value:255 if value>=8 else 0).getbbox()
                    assert alpha.getextrema()[0] == 0 and min(box[0],box[1],256-box[2],256-box[3]) >= 16
                    parent = entry['derivedFrom']
                    assert sha(file(parent['file'])) == parent['sha256']
                    with Image.open(file(parent['file'])) as mother:
                        crop = mother.crop(entry['operation']['sourceCellRect'])
                        w,h = crop.size
                        assert all(max(crop.getchannel('A').crop(edge).get_flattened_data()) < 8
                                   for edge in [(0,0,1,h),(0,0,w,1),(w-1,0,w,h),(0,h-1,w,h)])
                        content = crop.crop(entry['operation']['contentBoxWithinCell'])
                        scale = entry['operation']['uniformScale']
                        extent = (round(content.width*scale), round(content.height*scale))
                        resized = content.convert('RGBa').resize(extent,Image.Resampling.LANCZOS).convert('RGBA')
                        replay = Image.new('RGBA',(256,256))
                        replay.alpha_composite(resized,tuple(entry['operation']['placementPx']))
                        assert replay.tobytes() == output.tobytes()
                evidence = read(entry['sourceReferenceRecord'])
                assert evidence['itemId'] == ident and evidence['resourceId'] == original['resource_id']
                assert evidence['category'] == 'cap' and evidence['resourceKind'] == 'explicit inventory icon'
                assert evidence['catalogInstalledFile'] in original['installed_files']
                assert evidence['catalogInstalledFile'].startswith('res/uiRes/icon/cap/')
                assert evidence['sourceMember'] == 'QQTang-Local/runtime/client-patched/'+evidence['catalogInstalledFile']
                raw = archive.read(evidence['sourceMember'])
                assert hashlib.sha256(raw).hexdigest() == evidence['sourceMemberSha256']
                frame = evidence['sourceFrameRecord']
                encoded = raw[frame['pixelDataOffset']:frame['pixelDataOffset']+frame['pixelByteLength']]
                assert hashlib.sha256(encoded).hexdigest() == frame['encodedPixelSha256']
                decoded = decoder.decode_frame_pixels(encoded,frame['pixelMode'],frame['width'],frame['height'])
                with Image.open(file(entry['sourceReference'])) as reference:
                    assert reference.tobytes() == decoded
                assert sha(file(entry['sourceReference'])) == entry['sourceReferenceSha256'] == evidence['sha256']
                check_generation(parent['generationRecord'],generations)
                checks.append({'itemId':ident,'file':entry['file'],'sha256':entry['sha256'],
                               'sourceMember':evidence['sourceMember'],'sourceMemberSha256':evidence['sourceMemberSha256'],
                               'pixelReplayExact':True,'sourceIdentityAndRawDecodeChecked':True})
    result = {'schemaVersion':1,'scope':'explicit partial cap batches only; not full category or game art acceptance',
              'manifests':args.manifests,'sourceCategoryCount':len(source),'candidateCount':len(ids),
              'uniqueCandidatePngs':len(hashes),'generationRecordsIncludingEditParents':len(generations),
              'errors':[],'acceptedCount':0,'runtimeCount':0,'userReviewStatus':'pending','checks':checks}
    file(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key!='checks'},ensure_ascii=False))


if __name__=='__main__':
    main()
