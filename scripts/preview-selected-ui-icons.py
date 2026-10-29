"""At most six explicit current UI exports; light/dark size diagnostics, not full-page QA."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw,ImageFont

parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+',required=True)
args=parser.parse_args()
if not 1<=len(args.ids)<=6 or len(set(args.ids))!=len(args.ids):raise ValueError('Select one to six distinct IDs')
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'assets/ui/semantic-extra/manifest.json').read_text(encoding='utf-8'))
entries={e['id']:e for e in manifest['entries']}
if any(i not in entries for i in args.ids):raise ValueError('Unknown selected ID')
names={'friends':'好友','add-friend':'添加好友','remove-friend':'删除好友','private-chat':'私聊','forge':'锻造','compose':'合成'}
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
board=Image.new('RGB',(1000,120+len(args.ids)*104),'#f6f0df');draw=ImageDraw.Draw(board)
draw.text((24,12),'灵葫大作战 · 选定图标实际24 / 32 / 48像素对照',font=font,fill='#214a3d')
draw.text((24,42),'保留真实像素大小，不放大；按钮仍需配中文。此图不是浏览器截图。',font=font,fill='#47604d')
draw.rectangle((565,80,999,board.height),fill='#183e37')
records=[]
for row,ident in enumerate(args.ids):
    entry=entries[ident];p=root/entry['file'];im=Image.open(p).convert('RGBA');y=112+row*104
    draw.text((20,y+20),names.get(ident,ident),font=font,fill='#214a3d')
    for left in [170,590]:
        for col,size in enumerate([24,32,48]):
            sample=im.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
            x=left+col*115;board.paste(sample,(x+(48-size)//2,y),sample)
            draw.text((x,y+54),str(size)+'px',font=font,fill='#f4ead3'if left>500 else'#47604d')
    records.append({'id':ident,'source':entry['file'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceCanvas':list(im.size)})
out=root/'qa/ui-selected-social-crafting-actual-sizes.png';out.parent.mkdir(exist_ok=True);board.save(out)
out.with_suffix('.png.provenance.json').write_text(json.dumps({'sources':records,'sizes':[24,32,48],
 'operation':'Uniform premultiplied-alpha downscale and standard alpha composite on light/dark diagnostics; not new art generation.',
 'browserVerified':False,'accepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selectedIcons':len(records),'output':out.relative_to(root).as_posix(),'browserVerified':False}))
