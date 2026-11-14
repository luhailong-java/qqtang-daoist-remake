"""Copy the actual host generation and bind the exact submitted arguments."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from shutil import copyfile

from PIL import Image

from prepare_sources import HERE, ROOT, fingerprint, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('host_png', type=Path)
    parser.add_argument('take', choices=('background', 'layers', 'dragon-fix'))
    parser.add_argument('--requested-canvas', type=int, nargs=2, required=True)
    parser.add_argument('--reference-roles', nargs='+', required=True)
    args = parser.parse_args()
    exact_args = HERE / f'builtin-{args.take}-submission.json'
    submitted = json.loads(exact_args.read_bytes())
    prompt = HERE / f'entry-{args.take}.prompt.txt'
    prompt.write_bytes(submitted['input']['prompt'].encode())
    native = HERE / f'entry-{args.take}.png'
    copyfile(args.host_png, native)
    cfg = ROOT / 'config/image-generation.json'
    generation = HERE / f'{native.name}.generation.json'
    references = [
        {**fingerprint(Path(path)), 'role': role, 'actuallyViewed': True}
        for path, role in zip(submitted['input']['referenced_image_paths'], args.reference_roles, strict=True)
    ]
    with Image.open(native) as mother:
        alpha = mother.getchannel('A').getextrema() if mother.mode == 'RGBA' else None
        save(generation, {
            'schemaVersion': 1, **fingerprint(native), 'generationRecord': generation.relative_to(ROOT).as_posix(),
            'width': mother.width, 'height': mother.height, 'format': mother.format,
            'mode': mother.mode, 'alphaExtrema': alpha,
            'generatedAtUTC': datetime.fromtimestamp(args.host_png.stat().st_mtime, timezone.utc).isoformat(),
            'timeEvidence': 'Host file modification time',
            'tool': submitted['tool'], 'route': submitted['route'], 'newModelGeneration': True,
            'configuredTarget': json.loads(cfg.read_bytes()),
            'configuredTargetSha256': fingerprint(cfg)['sha256'],
            'modelQualityReverifiedOn': '2026-11-13',
            'actualModel': None, 'actualQuality': None,
            'actualEvidence': 'Host image generation returned an image and local file path only.',
            'hostResponseFields': ['image_url', 'output_hint'], 'hostOutputFile': str(args.host_png),
            'submittedParameters': {'model': None, 'quality': None,
                                    **{k: v for k, v in submitted['input'].items() if k != 'prompt'}},
            'exactSubmittedArgs': fingerprint(exact_args), 'exactPromptUtf8': fingerprint(prompt),
            'requestedCanvasViaPrompt': args.requested_canvas, 'references': references,
        })
    print(json.dumps(fingerprint(generation)))


if __name__ == '__main__':
    main()
