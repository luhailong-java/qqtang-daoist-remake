"""Inventory original product-name literals in pinned UI data, without execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
ARCHIVE_SHA = 'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7'
PREFIX = 'QQTang-Local/runtime/client-patched/res/uiRes/'
MARKERS = ('QQ堂', 'QQTang', '腾讯', '酷比')
spec = importlib.util.spec_from_file_location('brand_inert_reader', ROOT/'scripts/read-legacy-ui-constants.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(), 'sha256':digest(path.read_bytes())}


def values(value, location):
    if value.get('type') in ('tuple','list'):
        for index, item in enumerate(value['values']):
            yield from values(item, f'{location}[{index}]')
    elif isinstance(value.get('text'), str):
        yield location, value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('docs/native-ui-brand-text-20261114.json'))
    args = parser.parse_args()
    with ARCHIVE.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest() != ARCHIVE_SHA:
            raise ValueError('Pinned source archive differs')
    modules, hits = [], []
    with zipfile.ZipFile(ARCHIVE) as archive:
        members = sorted(n for n in archive.namelist() if n.startswith(PREFIX)
                         and '/' not in n[len(PREFIX):] and n.endswith('.pyc'))
        for member in members:
            raw = archive.read(member)
            tree, count = reader.decode(raw)
            scopes = reader.collect(tree)
            module = member[len(PREFIX):-4]
            modules.append({'module':module, 'archiveMember':member, 'sha256':digest(raw),
                            'byteLength':len(raw), 'parsedObjects':count, 'scopeCount':len(scopes)})
            for scope in scopes:
                for index, value in enumerate(scope['constants']):
                    for location, literal in values(value, f'constant[{index}]'):
                        text = literal['text']
                        markers = [m for m in MARKERS if m.casefold() in text.casefold()]
                        if not markers:
                            continue
                        assignments = [item['name'] for item in scope['literalAssignments']
                                       if item['literalValue']==value]
                        hits.append({'module':module, 'scope':scope['scope'],
                                     'sourceBytecodeSha256':scope['bytecodeSha256'], 'location':location,
                                     'literal':literal, 'matchedMarkers':markers,
                                     'adjacentLiteralAssignedAttributes':assignments,
                                     'displayUseConfirmed':False,
                                     'review':'Trace display use and available width before replacing data; code identifiers and paths must be distinguished from captions.'})
    result = {'schemaVersion':1, 'capturedOn':'2026-11-14',
              'scope':'Only top-level res/uiRes/*.pyc constants in the fixed source archive; no client execution or mutation.',
              'script':record(Path(__file__).resolve()), 'parser':record(ROOT/'scripts/read-legacy-ui-constants.py'),
              'sourceArchiveSha256':ARCHIVE_SHA, 'sourceModules':modules, 'markers':list(MARKERS),
              'literalOccurrences':hits, 'occurrenceCount':len(hits),
              'distinctLiteralTextCount':len({h['literal']['text'] for h in hits}),
              'limitations':['Source archive baseline only; this is not the current installed PYC tree.',
                             'Executable window titles, launcher controls, images, fonts, server messages and runtime-computed strings are outside this scan.',
                             'A matching constant does not prove an active display path or supply a replacement rule. This tool does not rewrite client text.'],
              'allNativeUiBrandingComplete':False, 'bytecodeExecuted':False, 'clientMutated':False}
    output=(ROOT/args.output).resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError('Public audit output escapes project')
    output.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'modules':len(modules), 'occurrences':len(hits),
                      'distinctText':result['distinctLiteralTextCount'], 'output':record(output)},ensure_ascii=False))


if __name__=='__main__':
    main()
