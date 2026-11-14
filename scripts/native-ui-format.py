"""Encode replacement DIMG pixel planes while retaining native headers and frame geometry."""
import importlib.util
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native_ui_reader', ROOT / 'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def encode_pixels(image, mode):
    image = image.convert('RGBA')
    values = struct.iter_unpack('4B', image.tobytes())
    if mode in (3, 0x11000000):
        colors = bytearray()
        alpha = bytearray()
        for red, green, blue, opacity in values:
            value = ((red * 31 + 127) // 255 << 11) | ((green * 63 + 127) // 255 << 5) | ((blue * 31 + 127) // 255)
            colors.extend(struct.pack('<H', value))
            alpha.append((opacity * 32 + 127) // 255)
        return bytes(colors + alpha)
    if mode == 8:
        return bytes(component for red, green, blue, opacity in values for component in (blue, green, red, opacity))
    if mode == 16:
        if image.getchannel('A').getextrema() != (255, 255):
            raise ValueError('An opaque native frame requires opaque replacement art')
        return bytes(component for red, green, blue, _ in values for component in (blue, green, red))
    raise ValueError(f'Unsupported native pixel mode {mode}')


def replace_frames(original, pictures):
    metadata, _ = reader.inspect_dimg(original, metadata_only=True)
    if not metadata['strictDeclaredStructureAccepted']:
        raise ValueError('Unparsed native image framing')
    expected = {f['index'] for f in metadata['frames'] if not f['empty']}
    if set(pictures) != expected:
        raise ValueError('Every nonempty native position needs one replacement picture')
    result = bytearray(original)
    previews = []
    for frame in metadata['frames']:
        if frame['empty']:
            continue
        image = pictures[frame['index']]
        if image.size != (frame['width'], frame['height']):
            raise ValueError('Replacement frame dimensions differ from the source')
        encoded = encode_pixels(image, frame['pixelMode'])
        if len(encoded) != frame['pixelByteLength']:
            raise ValueError('Replacement plane length differs from the source')
        start = frame['pixelDataOffset']
        result[start:start + len(encoded)] = encoded
        pixels = reader.decode_frame_pixels(encoded, frame['pixelMode'], frame['width'], frame['height'])
        previews.append((frame, Image.frombytes('RGBA', image.size, pixels)))
    inspected, _ = reader.inspect_dimg(bytes(result), metadata_only=True)
    for before, after in zip(metadata['frames'], inspected['frames'], strict=True):
        keys = ('index', 'offset', 'rawMarker', 'frameOffset', 'pixelMode', 'empty', 'width', 'height', 'unknownImageHeaderWord')
        if any(before.get(k) != after.get(k) for k in keys):
            raise ValueError('Native frame structure changed')
    return bytes(result), metadata, previews
