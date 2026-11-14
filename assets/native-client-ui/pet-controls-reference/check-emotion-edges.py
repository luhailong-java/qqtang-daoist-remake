"""Quantify visible saturated-green pixels and composite actual native PNGs."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def record(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def inspect(path):
    with Image.open(path) as opened:
        image = opened.convert('RGBA')
    points = []
    for i, rgba in enumerate(struct.iter_unpack('4B', image.tobytes())):
        r, g, b, a = rgba
        if g >= 150 and g-r > 80 and g-b > 80 and a > 0:
            points.append({'x': i % image.width, 'y': i // image.width, 'rgba': list(rgba)})
    return {**record(path), 'size': list(image.size), 'alphaExtrema': list(image.getchannel('A').getextrema()),
            'saturatedGreenNonzeroAlphaPixels': len(points),
            'saturatedGreenMaxAlpha': max((p['rgba'][3] for p in points), default=0),
            'saturatedGreenAlphaAtLeast8Pixels': sum(p['rgba'][3] >= 8 for p in points),
            'saturatedGreenAlphaAtLeast8Coordinates': [p for p in points if p['rgba'][3] >= 8],
            'saturatedGreenAlphaAtLeast32Pixels': sum(p['rgba'][3] >= 32 for p in points)}


def save_json(path, value, check):
    data = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    if check:
        if path.read_bytes() != data:
            raise ValueError('Emotion edge report differs')
    else:
        path.write_bytes(data)


def build(check=False):
    masters = [inspect(HERE / 'emotions' / f'face{i}-master.png') for i in range(5)]
    native = [inspect(HERE / 'candidate' / 'decoded' / f'face{i}-{phase:02}.png')
              for i in range(5) for phase in range(2)]
    if any(row['saturatedGreenAlphaAtLeast8Pixels'] for row in native):
        raise ValueError('A visible high-saturation green pixel remains in a native emotion frame')
    registration = []
    for emotion in range(5):
        frames = [Image.open(HERE / 'candidate' / 'decoded' / f'face{emotion}-{phase:02}.png').convert('RGBA')
                  for phase in range(2)]
        logical_alpha = []
        for phase, image in enumerate(frames):
            canvas = Image.new('L', (34, 33))
            offset = (0, 0 if phase == 0 or emotion == 2 else 1)
            canvas.paste(image.getchannel('A'), offset)
            logical_alpha.append(canvas)
        if logical_alpha[0].tobytes() != logical_alpha[1].tobytes():
            raise ValueError('Own emotion material states changed registered native alpha')
        if emotion != 2 and logical_alpha[0].crop((0, 0, 34, 1)).getextrema()[1] != 0:
            raise ValueError('A face visible pixel lies outside the two native windows intersection')
        registration.append({'sourceIndex': emotion, 'logicalCanvas': [34, 33],
                             'commonNativeLogicalBox': [0, 0 if emotion == 2 else 1, 34, 33],
                             'nativeAlphaEqualAfterRestoringOriginalOffsets': True,
                             'clippedVisiblePixels': 0,
                             'registeredAlphaSha256': hashlib.sha256(logical_alpha[0].tobytes()).hexdigest()})
    board = Image.new('RGB', (1000, 720))
    draw = ImageDraw.Draw(board)
    for background_index, background in enumerate(('#142720', '#f3ead2')):
        top = background_index*360
        draw.rectangle((0, top, 999, top+359), fill=background)
        for phase in range(2):
            for emotion in range(5):
                image = Image.open(HERE / 'candidate' / 'decoded' / f'face{emotion}-{phase:02}.png').convert('RGBA')
                surface = Image.new('RGBA', image.size, background)
                surface.alpha_composite(image)
                surface = surface.convert('RGB').resize((image.width*4, image.height*4), Image.Resampling.NEAREST)
                x, y = 15+emotion*200, top+12+phase*175
                board.paste(surface, (x, y))
                draw.text((x, y+140), f'face{emotion} f{phase} on {background}',
                          fill='#f3ead2' if background_index == 0 else '#142720')
    diagnostic = HERE / 'candidate' / 'emotions-edge-diagnostic.png'
    if check:
        with Image.open(diagnostic) as existing:
            if existing.convert('RGB').tobytes() != board.tobytes() or existing.size != board.size:
                raise ValueError('Emotion compositing diagnostic differs')
    else:
        board.save(diagnostic)
    report = {'schemaVersion': 1, 'checker': record(Path(__file__).resolve()),
              'criterion': 'G>=150 and G-R>80 and G-B>80; counts exclude fully transparent pixels',
              'visibleAlphaThreshold': 8, 'masters': masters, 'nativeDecodedFrames': native,
              'nativeLogicalRegistration': registration,
              'nativeVisibleSaturatedGreenPixels': sum(row['saturatedGreenAlphaAtLeast8Pixels'] for row in native),
              'diagnostic': record(diagnostic), 'diagnosticMethod': 'Exact RGBA alpha-composite onto deep jade and ivory, then nearest-neighbor 4x display',
              'interpretation': 'Returned mother images contain low-alpha RGB dust; after visible-bounds packing and native quantization, no native pixel meets the selected visible green-contamination criterion.',
              'visualAccepted': False, 'nativeRuntimeVerified': False}
    save_json(HERE / 'edge-evidence.json', report, check)
    print(json.dumps({'masterGreenPixelsAlphaAtLeast8': [r['saturatedGreenAlphaAtLeast8Pixels'] for r in masters],
                      'nativeFrames': len(native), 'nativeGreenPixelsAlphaAtLeast8': report['nativeVisibleSaturatedGreenPixels'],
                      'check': check}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)


if __name__ == '__main__':
    main()
