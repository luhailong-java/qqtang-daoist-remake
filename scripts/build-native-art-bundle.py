"""Compose selected native art manifests into one reversible package/loose-file batch."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'assets/native-client-bundle/review-v1'
INPUTS = (
    ('ui','assets/native-client-ui/login-v1/manifest.json'),
    ('inventory','assets/native-client-ui/inventory-v1/manifest.json'),
    ('inventory-phases','assets/native-client-ui/inventory-phases-v1/manifest.json'),
    ('head-world','assets/native-client-heads/world-v1/manifest.json'),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path_for(filename):
    path = (ROOT/filename).resolve(strict=True)
    if not path.is_relative_to(ROOT):
        raise ValueError('Bundle input escapes project')
    return path


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def checked(entry):
    path = path_for(entry['file'])
    if sha(path.read_bytes()) != entry['sha256']:
        raise ValueError(f'Bundle input changed: {path}')
    return path


def write_json(path,data,check):
    if check:
        if json.loads(path.read_bytes()) != data:
            raise ValueError(f'Bundle replay differs: {path}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps-manifest',type=Path,
                        default=Path('assets/native-client-maps/town-common-v1/manifest.json'),
                        help='Map candidates; include only their defaultInstallNativePaths subset')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    inputs = list(INPUTS)
    if args.maps_manifest:
        inputs.append(('maps',args.maps_manifest.as_posix()))
    items, sources, manifests, contracts, groups = {}, {}, [], [], []
    baseline = None
    source_archive = None
    for group,filename in inputs:
        manifest_path = path_for(filename)
        manifest = json.loads(manifest_path.read_bytes())
        contract_path = checked(manifest['sourceContract'])
        contract = json.loads(contract_path.read_bytes())
        if group == 'ui':
            baseline = {key:contract[key] for key in ('sourcePackage','sourceIndex')}
            for entry in baseline.values():
                checked(entry)
            source_archive = contract['sourceArchiveSha256']
        if contract.get('sourceArchiveSha256') != source_archive:
            raise ValueError('Native inputs use different source archives')
        for key in ('sourcePackage','sourceIndex'):
            if key in contract and contract[key]['sha256'] != baseline[key]['sha256']:
                raise ValueError('Native package baselines disagree')
        originals = {e['nativePath'].casefold():e for e in contract['items']}
        selection = None
        if group == 'maps':
            selection = {name.casefold() for name in manifest['defaultInstallNativePaths']}
            if not selection or len(selection) != len(manifest['defaultInstallNativePaths']):
                raise ValueError('Empty or duplicate default map selection')
        selected = []
        for item in manifest['items']:
            key = item['nativePath'].casefold()
            if selection is not None and key not in selection:
                continue
            if item['sourceSha256'] != originals[key]['sourceSha256']:
                raise ValueError('Native item source differs from its contract')
            checked(item)
            for frame in item['frames']:
                if not frame.get('empty',False):
                    checked(frame)
            previous = items.get(key)
            if previous:
                if (previous['sha256'],previous['sourceSha256']) != (item['sha256'],item['sourceSha256']):
                    raise ValueError('Conflicting native destinations on Windows')
                continue
            items[key] = item
            sources[key] = originals[key]
            selected.append(key)
        if selection is not None and set(selected) != selection:
            raise ValueError('Default map selection has missing or overlapping resources')
        groups.append({'group':group,'manifest':record(manifest_path),'nativeResources':len(selected),
                       'sourcePositions':sum(len(items[key]['frames']) for key in selected),
                       'selection':'defaultInstallNativePaths' if selection is not None else 'all prepared items'})
        manifests.append(record(manifest_path))
        contracts.append(record(contract_path))
    contract_output = {'schemaVersion':1,'sourceArchiveSha256':source_archive,**baseline,
                       'inputSourceContracts':contracts,'items':[sources[key] for key in sorted(sources)]}
    write_json(HERE/'source-contract.json',contract_output,args.check)
    result = {'schemaVersion':1,'scope':'Selected Daoist native graphics installation bundle',
              'sourceContract':record(HERE/'source-contract.json'),'inputManifests':manifests,'groups':groups,
              'items':[items[key] for key in sorted(items)],'nativeResources':len(items),
              'sourcePositions':sum(len(item['frames']) for item in items.values()),
              'builder':record(Path(__file__).resolve()),'newModelGeneration':False,
              'fullGameArtComplete':False,'visualAccepted':False,'nativeRuntimeVerified':False}
    write_json(HERE/'manifest.json',result,args.check)
    print(json.dumps({'nativeResources':result['nativeResources'],'sourcePositions':result['sourcePositions'],
                      'groups':groups,'replay':args.check},ensure_ascii=False))


if __name__ == '__main__':
    main()
