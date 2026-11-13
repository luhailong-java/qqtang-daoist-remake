"""Verify the two actual mother images and export six diagnostic-only RGBA poses."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path, PureWindowsPath
import json
import sys

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from painted_crop_gate import validate_visible_boundaries

CONFIG = ROOT / 'config/image-generation.json'
CANVAS = 804
OUTPUT = 256
ANCHOR = (128, 232)
BASELINE = 674
# Approximate diagnostic hip x positions within each 724px cell.
HIP_X = (427, 415, 409, 419, 408, 409)


def digest(data):
    return sha256(data).hexdigest()


def save_json(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def read_json(path):
    return json.loads(path.read_bytes())


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}


def alpha_box(image):
    return image.getchannel('A').point(lambda value: 255 if value >= 8 else 0).getbbox()


def generation_record(version, path, image):
    submission = BASE / f'submission-{version}.json'
    returned = BASE / f'result-{version}.json'
    sent = read_json(submission)['input']
    output = read_json(returned)
    reference_roles = ['own identity', 'source pose structure', 'source feet and sleeve timing order only',
                       'Daoist Q hand-painted style', 'Daoist Q hand-painted style']
    refs = []
    for sent_path, role in zip(sent['referenced_image_paths'], reference_roles, strict=True):
        path_text = PureWindowsPath(sent_path).as_posix().split('/qqtang-daoist-remake/', 1)[1]
        refs.append({**record(ROOT / path_text), 'role': role})
    prompt = sent['prompt']
    sidecar = path.with_suffix('.png.generation.json')
    save_json(sidecar, {
        'schemaVersion': 1, **record(path), 'width': image.width, 'height': image.height,
        'format': 'PNG', 'art_source': 'host_image', 'tool': 'image_gen.imagegen', 'route': 'builtin',
        'configSource': record(CONFIG), 'configSnapshot': read_json(CONFIG),
        'exactPrompt': prompt, 'submittedPromptSha256': digest(prompt.encode('utf-8')),
        'submittedParameters': {**{k: v for k, v in sent.items() if k != 'prompt'}, 'model': None, 'quality': None},
        'actualModel': None, 'actualQuality': None, 'actualParametersEvidence': 'Builtin output did not disclose model/quality.',
        'references': refs, 'submission': record(submission), 'returnedMetadata': record(returned),
        'hostSource': output['hostSource'], 'returnedFields': output['returnedFields'],
        'hostFileModifiedTimeUtc': datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        'timeEvidence': 'Native file modification time; actual model-side generation time undisclosed.',
        'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False,
    })
    return record(sidecar)


def uniform_resize(image, extent):
    return image.convert('RGBa').resize(extent, Image.Resampling.LANCZOS).convert('RGBA')


def main():
    evidence_path = BASE / 'source-east-evidence.json'
    evidence = read_json(evidence_path)
    for key in ('directionEvidence', 'phaseBoard', 'lowerBodyBoard'):
        expected = evidence[key]
        if record(ROOT / expected['file']) != expected:
            raise ValueError(f'Source reference evidence changed: {key}')
    if evidence['sourceDirectionGroupIndex'] != 0 or evidence['declaredCanvas'] != [100, 100]:
        raise ValueError('Expected declared role-22 source direction and geometry')
    if [position['frameIndex'] for position in evidence['positions']] != list(range(6)):
        raise ValueError('Expected six ordered original positions')
    if any(len(position['layers']) != 6 for position in evidence['positions']):
        raise ValueError('Expected exact diagnostic layer count')
    frames_dir = BASE / 'frames'
    frames_dir.mkdir(exist_ok=True)
    frames = []
    contact = Image.new('RGBA', (1280, 440), '#f6f0df')
    lower = Image.new('RGBA', (1440, 740), '#f6f0df')
    contact_draw, lower_draw = ImageDraw.Draw(contact), ImageDraw.Draw(lower)
    contact_draw.rectangle((0, 220, 1279, 439), fill='#173e36')
    contact_draw.text((16, 12), 'Yueying / east walk / visual review pending', fill='#26463c')
    contact_draw.text((16, 232), 'Same source order / dark background / no timing inferred', fill='#f6f0df')
    generation = []
    lower_inputs = []

    for version, start in (('a-v1', 0), ('b-v1', 3)):
        mother = BASE / f'mother-{version}.png'
        with Image.open(mother) as image:
            if image.size != (2172, 724) or image.mode != 'RGBA':
                raise ValueError('Actual native 2172×724 true-alpha PNG required')
            cells = [(i*724, 0, (i+1)*724, 724) for i in range(3)]
            validate_visible_boundaries(image, cells, threshold=8)
            generated = generation_record(version, mother, image)
            generation.append(generated)
            for column, rect in enumerate(cells):
                index = start + column
                cell = image.crop(rect)
                box = alpha_box(cell)
                if box is None or cell.getchannel('A').getextrema()[0] != 0:
                    raise ValueError('Empty or opaque sample')
                placement = (CANVAS//2-HIP_X[index], round(ANCHOR[1]*CANVAS/OUTPUT)-BASELINE)
                if not (0 <= box[0]+placement[0] < box[2]+placement[0] <= CANVAS and
                        0 <= box[1]+placement[1] < box[3]+placement[1] <= CANVAS):
                    raise ValueError('Unsafe registration')
                work = Image.new('RGBA', (CANVAS, CANVAS))
                work.paste(cell, placement)
                sample = uniform_resize(work, (OUTPUT, OUTPUT))
                validate_visible_boundaries(sample, [(0, 0, OUTPUT, OUTPUT)], threshold=8)
                target = frames_dir / f'phase-{index}.png'
                sample.save(target)
                provenance = target.with_suffix('.png.provenance.json')
                frame = {
                    **record(target), 'sourceFrameIndex': index, 'sourceDirectionGroupIndex': 0,
                    'sourceDeclaredCanvas': [100, 100],
                    'sourceLayers': [{k: layer[k] for k in ('layer', 'member', 'sourceDimgSha256', 'width', 'height',
                                                           'frameOffset', 'encodedPixelSha256', 'decodedRgbaSha256')}
                                     for layer in evidence['positions'][index]['layers']],
                    'originalFrameDurationMs': None, 'nativeActorAnchor': None,
                    'derivedFrom': record(mother), 'generationRecord': generated, 'width': OUTPUT, 'height': OUTPUT,
                    'alphaExtrema': list(sample.getchannel('A').getextrema()),
                    'outputAlpha8BBox': list(alpha_box(sample)),
                    'operation': {'sourceRectLTRB': list(rect), 'sourceCellAlpha8BBox': list(box),
                                  'placement': list(placement), 'diagnosticHipX': HIP_X[index],
                                  'diagnosticSourceBaseline': BASELINE, 'workingCanvas': [CANVAS, CANVAS],
                                  'sharedScale': OUTPUT/CANVAS, 'diagnosticAnchor': list(ANCHOR),
                                  'resampler': 'premultiplied-alpha LANCZOS', 'newModelGeneration': False},
                    'visualAccepted': False, 'runtimeAdopted': False, 'accepted': False, 'userReviewStatus': 'pending',
                }
                save_json(provenance, frame)
                frames.append({**frame, 'provenance': record(provenance)})

                x = 16 + index * 210
                for y, ink in ((0, '#26463c'), (220, '#f6f0df')):
                    contact_draw.text((x, y+34), f'f{index}  112px and 64px', fill=ink)
                    contact.alpha_composite(uniform_resize(sample, (112, 112)), (x, y+60))
                    contact.alpha_composite(uniform_resize(sample, (64, 64)), (x+112, y+108))
                detail_rect = (140, 296, 620, 700)
                detail = cell.crop(detail_rect)
                detail.thumbnail((480, 330), Image.Resampling.LANCZOS)
                lower.alpha_composite(detail, (column*480+30, (index//3)*370+30))
                lower_draw.text((column*480+12, (index//3)*370+10), f'f{index} / lower body and hand layers', fill='#26463c')
                lower_inputs.append({**record(mother), 'cellRectLTRB': list(rect), 'detailRectLTRB': list(detail_rect),
                                     'sourceFrameIndex': index})

    if len({frame['sha256'] for frame in frames}) != 6:
        raise ValueError('The six source phases require different image candidates')
    contact_path, lower_path = BASE / 'review-light-dark.png', BASE / 'lower-body-diagnostic.png'
    contact.convert('RGB').save(contact_path)
    lower.convert('RGB').save(lower_path)
    for path, inputs, op in (
        (contact_path, [record(ROOT / frame['file']) for frame in frames], 'Dual-background 112px and 64px composites'),
        (lower_path, lower_inputs, 'Diagnostic lower-body crops at 330px height'),
    ):
        save_json(path.with_suffix('.png.source.json'), {
            **record(path), 'derivedFrom': inputs, 'operation': op, 'newModelGeneration': False,
            'userReviewStatus': 'pending',
        })
    save_json(BASE / 'manifest.json', {
        'schemaVersion': 1, 'status': 'six-east-walk-diagnostic-poses', 'characterId': 'moon-shadow',
        'sourceRoleId': 22, 'direction': 'E', 'sourceDirectionGroupIndex': 0, 'sourceFrameOrder': list(range(6)),
        'sourceDeclaredCanvas': [100, 100], 'sourceEvidence': record(evidence_path),
        'originalFrameDurationMs': None, 'originalLoop': None, 'nativeActorAnchor': None,
        'frames': frames, 'exportCanvas': [OUTPUT, OUTPUT], 'generatedMothers': generation,
        'preview': record(contact_path), 'lowerBodyPreview': record(lower_path),
        'motionContinuityConfirmed': False, 'visualAccepted': False, 'runtimeAdopted': False,
        'accepted': False, 'userReviewStatus': 'pending',
    })
    print(json.dumps({'poses': len(frames), 'actualMotherCount': len(generation),
                      'sourceLayersPerPose': 6, 'allDistinct': True, 'alphaThreshold': 8,
                      'humanReview': 'pending'}))


if __name__ == '__main__':
    main()
