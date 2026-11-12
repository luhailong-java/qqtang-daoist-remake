"""Validate explicit source positions/rasters; legacy defaults are item114,24/20."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import argparse
from head_world_visual_review import validate_static_visual_review

root=Path(__file__).resolve().parents[1]
folder=root/'assets/items/head-adornments'
parser=argparse.ArgumentParser()
parser.add_argument('--item',type=int,default=114)
parser.add_argument('--expected-count',type=int,default=24)
parser.add_argument('--expected-unique',type=int,default=20)
parser.add_argument('--missing',type=int,nargs='*',default=[])
args=parser.parse_args()
contract=json.loads((folder/f'references/world/{args.item}/source-contract.json').read_text(encoding='utf-8'))
document=json.loads((folder/f'world-{args.item}-art.json').read_text(encoding='utf-8'))
item=document['items'][0]
images={}
errors=[]
approved_static_positions=[]
for label,record in (('manifest',document),('item',item)):
    for key in ('accepted','geometryAccepted','visualAccepted','runtimeAdopted','completeAnimationAccepted'):
        if key in record and record[key]is not False:
            errors.append(f'{label}: unexpected overall {key} claim')
if item.get('animationTimingKnown')is not False:
    errors.append('Item native animation timing is still unverified')
def read_image(path):
    if path not in images:
        images[path]=Image.open(root/path).convert('RGBA')
    return images[path]
def sha(path):
    return hashlib.sha256((root/path).read_bytes()).hexdigest()
expected=[index for index in range(len(contract['frames']))if index not in args.missing]
if item['itemId']!=args.item or len(expected)!=args.expected_count or len(item['frames'])!=args.expected_count or [f['sourceFrameIndex']for f in item['frames']]!=expected:
    errors.append('Candidate positions differ from explicit source coverage')
if len({frame['file']for frame in item['frames']})!=args.expected_unique:
    errors.append('Unexpected unique candidate raster count')
if item['sourceDeclaredFrameCoverageComplete']!=(len(item['frames'])==len(contract['frames'])):
    errors.append('Complete source coverage claimed incorrectly')
representatives={index:group[0]for group in contract['encodedRasterGroups']for index in group}
for frame in item['frames']:
    index=frame['sourceFrameIndex']
    try:
        original=contract['frames'][index]
        if frame['logicalFrameSize']!=original['nativeFrameSize'] or frame['frameOffsetRaw']!=original['frameOffsetRaw']:
            raise ValueError('Native logical size/rawOffset changed')
        if frame['width']!=original['nativeFrameSize'][0]*4 or frame['height']!=original['nativeFrameSize'][1]*4:
            raise ValueError('Density4 is not the original native canvas')
        output=read_image(frame['file'])
        if list(output.size)!=[frame['width'],frame['height']]or sha(frame['file'])!=frame['sha256']:
            raise ValueError('Output size/SHA mismatch')
        if output.getchannel('A').getextrema()[0]!=0:
            raise ValueError('Transparent pixels absent')
        if frame['imagePhaseRepresentativeIndex']!=representatives[index]:
            raise ValueError('Alias is not source payload equality')
        approved_static=validate_static_visual_review(frame,args.item,root)
        if frame.get('frameDurationMs')is not None or frame.get('directionSemantic')is not None:
            raise ValueError('Unknown native timing/direction was invented')
        ref=frame['sourceReference']
        if sha(ref['file'])!=ref['sha256'] or list(read_image(ref['file']).size)!=original['nativeFrameSize']:
            raise ValueError('Source representative size/SHA mismatch')
        mother=frame['derivedFrom']
        if sha(mother['file'])!=mother['sha256']:
            raise ValueError('Mother SHA mismatch')
        generation=json.loads((root/mother['generationRecord']).read_text(encoding='utf-8'))
        if generation['actualModel']is not None or generation['actualQuality']is not None:
            raise ValueError('Unexpected confirmed model/quality claim')
        op=frame['operation'].get('originalPaintOperation',frame['operation'])
        crop=read_image(mother['file']).crop(op['sourceCellRectLTRB']).getchannel('A')
        w,h=crop.size
        if any(any(v>=16 for v in crop.crop(edge).tobytes())for edge in ((0,0,1,h),(w-1,0,w,h),(0,0,w,1),(0,h-1,w,h))):
            raise ValueError('Mother crop cuts visible content')
        if approved_static:approved_static_positions.append(index)
    except Exception as exc:
        errors.append(f'{index}: {exc}')
result={'itemId':args.item,'sourcePositions':len(item['frames']),'sourceDeclaredPositions':len(contract['frames']),
        'missingSourcePositions':args.missing,'uniquePaintedRasters':len({f['file']for f in item['frames']}),
        'sourceAliasGroups':len(contract['encodedRasterGroups']),'sourceOffsetsRetained':True,
        'visibleAspectDeviationRange':[min(f['qa']['relativeAspectDeviation']for f in item['frames']),max(f['qa']['relativeAspectDeviation']for f in item['frames'])],
        'pixelDecodePerformed':True,'errors':errors,
        'aspectWarningSourcePositions':[f['sourceFrameIndex']for f in item['frames']if f['qa']['relativeAspectDeviation']>.1],
        'approvedStaticVisualPositions':approved_static_positions,
        'visualAccepted':False,'visualAcceptanceScope':'whole-item-unapproved',
        'animationTimingKnown':False,'runtimeAdopted':False}
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
