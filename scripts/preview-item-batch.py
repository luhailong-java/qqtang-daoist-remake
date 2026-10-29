"""Render at most six already-exported inventory icons, without scanning other families."""
from pathlib import Path
import json,sys,hashlib
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parents[1];spec_path=root/sys.argv[1]
spec=json.loads(spec_path.read_text(encoding='utf-8'))
if not 1<=len(spec['items'])<=6:raise ValueError('Select one to six explicit icon exports')
manifest=json.loads((root/spec['assetDirectory']/'art.json').read_text(encoding='utf-8'))
by_id={i['itemId']:i for i in manifest['items']}
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
board=Image.new('RGB',(960,640),'#f6f0df');draw=ImageDraw.Draw(board);records=[]
for index,selected in enumerate(spec['items']):
    entry=by_id[selected['itemId']];path=root/entry['file'];raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('Output changed since export')
    im=Image.open(path).convert('RGBA');a=im.getchannel('A');w,h=im.size
    edge=lambda rect:sum(v>=8 for v in a.crop(rect).getdata())
    counts=[edge((0,0,1,h)),edge((0,0,w,1)),edge((w-1,0,w,h)),edge((0,h-1,w,h))]
    if im.size!=(256,256)or any(counts):raise ValueError('Unexpected canvas or visible boundary contact')
    x=index%3*320+32;y=index//3*320
    board.paste(im,(x,y),im)
    label=f"{entry['itemId']} · {entry.get('projectDisplayName',entry['sourceName'])}"
    draw.text((x,y+270),label,font=font,fill='#214a3d')
    records.append({'itemId':entry['itemId'],'file':entry['file'],'sha256':entry['sha256'],'alpha8OuterEdgesLTRB':counts})
out=root/'qa'/(spec_path.stem.replace('-export','')+'-contact-256.png');out.parent.mkdir(exist_ok=True);board.save(out)
out.with_suffix('.png.provenance.json').write_text(json.dumps({'spec':spec_path.relative_to(root).as_posix(),
 'items':records,'operation':'Standard alpha composite of exact256px exports; text labels diagnostic only; no new generation.',
 'visualAccepted':False,'browserVerified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selectedIcons':len(records),'output':out.relative_to(root).as_posix(),'outerEdgesClear':True}))
