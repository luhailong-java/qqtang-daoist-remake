"""Refine the historical opaque GSA entry using a bounded inert DIMG parse."""
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    spec=importlib.util.spec_from_file_location('cursor_codec',ROOT/'scripts/native-ui-format.py')
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    path=ROOT/'references/qqtang-ui-data/native-ui-inventory.json';census=json.loads(path.read_bytes())
    resource=next(r for r in census['resources'] if r['canonicalPath']=='object/ui/cursor/fight.gsa')
    archive=ROOT/census['sourceArchive']['file']
    if record(archive)['sha256']!=census['sourceArchive']['sha256']:raise ValueError('Pinned source archive differs')
    with zipfile.ZipFile(archive) as z:raw=z.read(resource['archiveMember'])
    if hashlib.sha256(raw).hexdigest()!=resource['sourceSha256']:raise ValueError('Historical cursor bytes differ')
    metadata,_=codec.inspect_native(raw,True)
    if metadata['frameCount']!=9 or not metadata['strictDeclaredStructureAccepted'] or metadata['trailingByteLength']:
        raise ValueError('GSA cursor is not a complete bounded nine-frame DIMG')
    package=(ROOT/census['package']['file']).read_bytes();index=(ROOT/census['index']['file']).read_bytes()
    if hashlib.sha256(package).hexdigest()!=census['package']['sha256'] or hashlib.sha256(index).hexdigest()!=census['index']['sha256']:
        raise ValueError('Pinned package/index baseline differs')
    entry=next(e for e in codec.reader.parse_index(index,len(package))['entries'] if e['path'].replace('\\','/').lower()=='object/ui/cursor/arror.img')
    if codec.reader.unpack_resource(package,entry)[0]!=raw:raise ValueError('Packed/loose cursor alias differs')
    report={'schemaVersion':1,'sourceCensus':record(path),'script':record(Path(__file__)),
      'scope':'Historical inventory refinement only; no original code or client execution',
      'codec':record(ROOT/'scripts/native-ui-format.py'),
      'refinements':[{'canonicalPath':resource['canonicalPath'],'sourceSha256':resource['sourceSha256'],
        'previousFormat':resource['format'],'format':'QQF/DIMG','metadata':metadata,'metadataVerified':True,
        'exactSourceByteAlias':'object/ui/cursor/arror.img',
        'decodedFrameRgbaSha256':[hashlib.sha256(codec.decode_native_frame(raw,f).tobytes()).hexdigest() for f in metadata['frames']],
        'reason':'Full DIMG header, nine frames, pixel planes and exact EOF accepted irrespective of .gsa suffix'}],
      'nativeRuntimeVerified':False}
    output=ROOT/'references/qqtang-ui-data/native-ui-format-refinements-20261114.json'
    output.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'refinedImagePaths':1,'additionalDeclaredPositions':9}))


if __name__=='__main__':main()
