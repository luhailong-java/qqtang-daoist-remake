"""Copy actual returned builtin PNGs and retain exact prompt/result provenance."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    requests = json.loads((HERE / 'extra-icon-generation-requests.json').read_bytes())['requests']
    for result in json.loads((HERE / 'extra-icon-tool-results.json').read_bytes())['results']:
        i = result['requestIndex']
        request = requests[i]
        match = re.search(r' as ([^\n]+\.png) by default', result['output_hint'])
        if not match:
            raise ValueError('Returned tool output did not identify its actual local PNG')
        source = Path(match.group(1))
        raw = source.read_bytes()
        with Image.open(source) as image:
            image.load()
            if image.mode != 'RGBA' or image.getchannel('A').getextrema() != (0, 255):
                raise ValueError('Returned portrait PNG lacks true RGBA transparency')
            size = list(image.size)
            metadata_keys = sorted(image.info)
            original_bounds = list(image.getchannel('A').getbbox())
        target = ROOT / request['plannedOutput']
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != raw:
            shutil.copyfile(source, target)
        record = {**request, 'file': target.relative_to(ROOT).as_posix(),
                  'sha256': hashlib.sha256(raw).hexdigest(), 'width': size[0], 'height': size[1],
                  'format': 'PNG', 'mode': 'RGBA', 'alphaExtrema': [0, 255], 'originalAlphaBounds': original_bounds,
                  'generatedAt': datetime.datetime.fromtimestamp(source.stat().st_mtime, datetime.timezone.utc).isoformat(),
                  'generatedAtEvidence': 'Actual returned PNG file last-write UTC; server generation time not disclosed',
                  'toolResult': result, 'returnedLocalFile': str(source), 'pngMetadataKeys': metadata_keys,
                  'unverifiedReason': 'Host-managed builtin tool exposes no model/quality selectors and returned no verifiable model/quality metadata.',
                  'visualAccepted': False, 'nativeRuntimeVerified': False}
        target.with_suffix('.png.generation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'requestIndex': i, 'file': record['file'], 'size': size, 'sha256': record['sha256']}))


if __name__ == '__main__':
    main()
