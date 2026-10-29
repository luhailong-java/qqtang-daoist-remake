"""Verify one explicit inventory batch against source catalog and PNG provenance.

--metadata-only performs byte/header/hash checks without importing Pillow or decoding pixels.
Full mode is for the remote runner while local heavy verification is paused.
"""
from pathlib import Path
import argparse,hashlib,json,struct

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--manifest',required=True);parser.add_argument('--catalog',required=True)
parser.add_argument('--category',required=True);parser.add_argument('--expected',type=int,required=True)
parser.add_argument('--metadata-only',action='store_true')
args=parser.parse_args()
if not args.metadata_only:from PIL import Image
errors=[];byte_cache={};image_cache={}
def relative_file(value):
    if not isinstance(value,str)or'\\'in value or'..'in value.split('/')or value.startswith('/'):
        raise ValueError('Unsafe project-relative file')
    path=(root/value).resolve()
    if not path.is_relative_to(root)or not path.is_file():raise ValueError('Referenced file is absent: '+value)
    return path
def content(value):
    path=relative_file(value)
    if path not in byte_cache:byte_cache[path]=path.read_bytes()
    return byte_cache[path]
def sha(value):return hashlib.sha256(content(value)).hexdigest()
def png_size(value):
    raw=content(value)
    if raw[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Not a real PNG: '+value)
    return list(struct.unpack('>II',raw[16:24]))
def image(value):
    path=relative_file(value)
    if path not in image_cache:image_cache[path]=Image.open(path).convert('RGBA')
    return image_cache[path]
catalog=json.loads(relative_file(args.catalog).read_text(encoding='utf-8'))
source={i['item_id']:i for i in catalog['items']if i['category']==args.category}
data=json.loads(relative_file(args.manifest).read_text(encoding='utf-8'));entries=data['items']
if len(source)!=args.expected or len(entries)!=args.expected:errors.append('Unexpected category or candidate count')
ids=[e['itemId']for e in entries]
if len(set(ids))!=len(ids)or set(ids)!=set(source):errors.append('Candidate IDs do not exactly cover the source category')
for entry in entries:
    ident=entry['itemId']
    try:
        original=source[ident]
        if entry['category']!=args.category or entry['sourceName']!=original['name']or entry['sourceDescription']!=original['description']:
            raise ValueError('Source identity text changed')
        if entry.get('runtimeAdopted')is not False or entry.get('visualAccepted')is not False:
            raise ValueError('Unexpected adoption/acceptance claim')
        if png_size(entry['file'])!=[256,256]or[entry['width'],entry['height']]!=[256,256]:raise ValueError('Output canvas is not256x256')
        if sha(entry['file'])!=entry['sha256']:raise ValueError('Output SHA mismatch')
        if entry.get('warnings'):raise ValueError('Unresolved source crop boundary warning')
        parent=entry['derivedFrom'];generation=json.loads(relative_file(parent['generationRecord']).read_text(encoding='utf-8'))
        if sha(parent['file'])!=parent['sha256']or generation['sha256']!=parent['sha256']:raise ValueError('Parent image SHA mismatch')
        if png_size(parent['file'])!=[generation['width'],generation['height']]:raise ValueError('Native parent dimensions disagree')
        if generation.get('actualModel')is not None or generation.get('actualQuality')is not None:raise ValueError('Unexpected verified model/quality claim')
        rect=entry['operation']['sourceCellRect'];pw,ph=png_size(parent['file'])
        if not(len(rect)==4 and all(isinstance(x,int)for x in rect)and 0<=rect[0]<rect[2]<=pw and 0<=rect[1]<rect[3]<=ph):raise ValueError('Invalid native source crop')
        if png_size(entry['sourceReference'])[0]<=0:raise ValueError('Missing actual source inventory PNG')
        if not args.metadata_only:
            output=image(entry['file']);alpha=output.getchannel('A');box=alpha.point(lambda a:255 if a>=8 else 0).getbbox()
            if not box or min(box[0],box[1],256-box[2],256-box[3])<16:raise ValueError('Output visible inset is below16px')
            if alpha.getextrema()[0]!=0:raise ValueError('Output lacks true transparent pixels')
            crop=image(parent['file']).crop(rect);a=crop.getchannel('A');w,h=crop.size
            edges=[(0,0,1,h),(0,0,w,1),(w-1,0,w,h),(0,h-1,w,h)]
            if any(any(v>=8 for v in a.crop(edge).getdata())for edge in edges):raise ValueError('Native crop cuts a visible silhouette')
    except(Exception)as exc:errors.append(f'{ident}: {exc}')
result={'manifest':args.manifest,'sourceCategory':args.category,'sourceIds':len(source),'candidateEntries':len(entries),
 'uniqueCandidateIds':len(set(ids)),'mode':'metadata-only'if args.metadata_only else'png-specification',
 'pixelDecodePerformed':not args.metadata_only,'errors':errors,'candidateAcceptedCount':0,'runtimeOrCompleteGameAccepted':False}
print(json.dumps(result,ensure_ascii=True,indent=2))
raise SystemExit(1 if errors else 0)
