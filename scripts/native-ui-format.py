"""Encode own DIMG/TGA/GIF art, retaining native geometry and format-specific semantics."""
import importlib.util
import hashlib
import io
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native_ui_reader', ROOT / 'scripts/inspect-reference-dimg.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def inspect_native(data, metadata_only=False):
    """Read DIMG or bounded uncompressed true-color TGA without executing code."""
    if data.startswith(b'QQF\x1aDIMG'):
        return reader.inspect_dimg(data, metadata_only=metadata_only)
    if data.startswith(b'GIF89a'):
        return inspect_gif(data, metadata_only)
    if len(data) < 18:
        raise ValueError('Unknown native image container')
    identifier, color_map, kind = data[:3]
    width, height, depth, descriptor = struct.unpack_from('<HHBB', data, 12)
    if (identifier or color_map or kind != 2 or depth not in (24,32) or descriptor & 0xcf != (8 if depth==32 else 0)
            or data[3:12] != b'\0'*9 or not 0 < width <= 4096 or not 0 < height <= 4096):
        raise ValueError('Unsupported native TGA framing')
    end = 18 + width*height*(depth//8)
    suffix = data[end:]
    if len(data) != end+26 or suffix != b'\0'*8+b'TRUEVISION-XFILE.\0':
        raise ValueError('Unsupported native TGA footer or pixel length')
    frame = {'index':0,'offset':0,'rawMarker':None,'frameOffset':[0,0], 'pixelMode':8 if depth==32 else 16,
             'width':width,'height':height,'unknownImageHeaderWord':None,'empty':False,
             'pixelDataOffset':18,'pixelByteLength':width*height*(depth//8),'tgaDescriptor':descriptor}
    metadata = {'format':'TGA','byteLength':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                'version':f'TGA-uncompressed-{depth}','frameInfoSize':18,'frameCount':1,'directions':1,
                'declaredCanvas':[width,height],'unknownHeaderWordsAt24And28':[],
                'strictDeclaredStructureAccepted':True,'frames':[frame],
                'nonPixelPrefixHex':data[:18].hex(),'nonPixelSuffixHex':suffix.hex()}
    first = None if metadata_only else {'width':width,'height':height,
                                       'pixels':decode_native_frame(data,frame).tobytes()}
    return metadata,first


def inspect_gif(data,metadata_only=False):
    """Bounded, single full-canvas opaque GIF89a; no executable content is loaded."""
    if len(data)<14 or len(data)>4*1024*1024:raise ValueError('Unsupported GIF length')
    if data[12]!=0:raise ValueError('Unsupported GIF pixel aspect ratio')
    width,height=struct.unpack_from('<HH',data,6)
    if not 0<width<=4096 or not 0<height<=4096:raise ValueError('Unsupported GIF canvas')
    cursor=13+(3*(2**((data[10]&7)+1)) if data[10]&128 else 0)
    images=[];loop_extensions=0;control_extensions=0;control_reserved=0;control_flags_offset=None
    def blocks(pos):
        while True:
            if pos>=len(data):raise ValueError('Truncated GIF data blocks')
            length=data[pos];pos+=1
            if length==0:return pos
            pos+=length
            if pos>len(data):raise ValueError('Truncated GIF block')
    while cursor<len(data):
        marker=data[cursor];cursor+=1
        if marker==0x3b:
            if cursor!=len(data):raise ValueError('Trailing GIF data')
            break
        if marker==0x21:
            if cursor>=len(data):raise ValueError('Truncated GIF extension')
            label=data[cursor];cursor+=1
            if label==0xf9:
                if (cursor+6>len(data) or data[cursor]!=4 or data[cursor+5]!=0
                        or data[cursor+1]&3 or data[cursor+1]&0xe0 not in (0,0xc0) or control_extensions):
                    raise ValueError('Unsupported GIF graphic control extension')
                control_reserved=data[cursor+1]&0xe0
                control_flags_offset=cursor+1
                control_extensions+=1;cursor+=6
            elif label==0xff:
                if (cursor+17>len(data) or data[cursor:cursor+14]!=b'\x0bNETSCAPE2.0\x03\x01'
                        or data[cursor+16]!=0 or loop_extensions):
                    raise ValueError('Unsupported GIF application extension')
                loop_extensions+=1;cursor+=17
            else:raise ValueError('Unsupported GIF extension')
        elif marker==0x2c:
            if cursor+9>len(data):raise ValueError('Truncated GIF image descriptor')
            x,y,w,h,flags=struct.unpack_from('<HHHHB',data,cursor);cursor+=9
            if flags&0x18:raise ValueError('Unsupported GIF image descriptor flags')
            if (x,y,w,h)!=(0,0,width,height):raise ValueError('Only full-canvas GIF images are supported')
            images.append(bool(flags&64))
            cursor+=3*(2**((flags&7)+1)) if flags&128 else 0
            if cursor>=len(data) or not 2<=data[cursor]<=8:raise ValueError('Unsupported GIF LZW minimum code size')
            cursor=blocks(cursor+1)
        else:raise ValueError('Unknown GIF structure')
    else:raise ValueError('Missing GIF trailer')
    if len(images)!=1:raise ValueError('Only one-frame native GIFs are supported')
    with Image.open(io.BytesIO(data)) as gif:
        if getattr(gif,'n_frames',1)!=1 or 'transparency' in gif.info:raise ValueError('Unsupported animated or transparent GIF')
        properties={'duration':gif.info.get('duration',0),'loop':gif.info.get('loop'),
                    'disposal':getattr(gif,'disposal_method',0),'background':gif.info.get('background',0),
                    'interlace':images[0]}
        picture=gif.convert('RGBA')
    if properties['loop'] is None:raise ValueError('Native GIF loop extension must be explicit')
    frame={'index':0,'offset':0,'rawMarker':None,'frameOffset':[0,0],'pixelMode':16,
           'width':width,'height':height,'unknownImageHeaderWord':None,'empty':False,
           'pixelDataOffset':0,'pixelByteLength':len(data),'gifFrame':True}
    metadata={'format':'GIF','byteLength':len(data),'sha256':hashlib.sha256(data).hexdigest(),
              'version':'GIF89a','frameInfoSize':0,'frameCount':1,'directions':1,
              'declaredCanvas':[width,height],'unknownHeaderWordsAt24And28':[],
              'strictDeclaredStructureAccepted':True,'gifProperties':properties,
              'gifControlReservedBits':control_reserved,'gifControlFlagsOffset':control_flags_offset,'frames':[frame]}
    return metadata,None if metadata_only else {'width':width,'height':height,'pixels':picture.tobytes()}


def orient_tga(image, descriptor):
    if not descriptor & 0x20:
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if descriptor & 0x10:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return image


def decode_native_frame(data, frame):
    if frame.get('gifFrame'):
        with Image.open(io.BytesIO(data)) as gif:return gif.convert('RGBA')
    start = frame['pixelDataOffset']
    raw = data[start:start+frame['pixelByteLength']]
    pixels = reader.decode_frame_pixels(raw,frame['pixelMode'],frame['width'],frame['height'])
    image = Image.frombytes('RGBA',(frame['width'],frame['height']),pixels)
    return orient_tga(image,frame['tgaDescriptor']) if 'tgaDescriptor' in frame else image


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
    metadata, _ = inspect_native(original, metadata_only=True)
    if not metadata['strictDeclaredStructureAccepted']:
        raise ValueError('Unparsed native image framing')
    expected = {f['index'] for f in metadata['frames'] if not f['empty']}
    if set(pictures) != expected:
        raise ValueError('Every nonempty native position needs one replacement picture')
    if metadata.get('format')=='GIF':
        picture=pictures[0].convert('RGBA')
        if list(picture.size)!=metadata['declaredCanvas'] or picture.getchannel('A').getextrema()!=(255,255):
            raise ValueError('Native GIF replacement needs the original opaque canvas')
        palette=picture.convert('RGB').quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
        properties=metadata['gifProperties'];stream=io.BytesIO()
        palette.save(stream,format='GIF',save_all=False,optimize=False,**properties)
        output=stream.getvalue()
        if metadata['gifControlReservedBits']:
            # Both pinned legacy profile GIFs carry 0xc0 in GCE reserved bits.
            # Keep those exact bits rather than silently standardizing them away.
            generated,_=inspect_native(output,metadata_only=True)
            flags_offset=generated['gifControlFlagsOffset']
            if flags_offset is None:raise ValueError('Cannot retain legacy GIF graphic-control bits')
            amended=bytearray(output);amended[flags_offset]|=metadata['gifControlReservedBits'];output=bytes(amended)
        after,_=inspect_native(output,metadata_only=True)
        if after['gifProperties']!=properties:raise ValueError('Native GIF semantic properties changed')
        if after['gifControlReservedBits']!=metadata['gifControlReservedBits']:raise ValueError('Native GIF legacy control bits changed')
        return output,metadata,[(after['frames'][0],decode_native_frame(output,after['frames'][0]))]
    result = bytearray(original)
    previews = []
    for frame in metadata['frames']:
        if frame['empty']:
            continue
        image = pictures[frame['index']]
        if image.size != (frame['width'], frame['height']):
            raise ValueError('Replacement frame dimensions differ from the source')
        stored = orient_tga(image,frame['tgaDescriptor']) if 'tgaDescriptor' in frame else image
        encoded = encode_pixels(stored, frame['pixelMode'])
        if len(encoded) != frame['pixelByteLength']:
            raise ValueError('Replacement plane length differs from the source')
        start = frame['pixelDataOffset']
        result[start:start + len(encoded)] = encoded
        previews.append((frame,decode_native_frame(bytes(result),frame)))
    inspected, _ = inspect_native(bytes(result), metadata_only=True)
    for before, after in zip(metadata['frames'], inspected['frames'], strict=True):
        keys = ('index', 'offset', 'rawMarker', 'frameOffset', 'pixelMode', 'empty', 'width', 'height', 'unknownImageHeaderWord')
        if any(before.get(k) != after.get(k) for k in keys):
            raise ValueError('Native frame structure changed')
    return bytes(result), metadata, previews
