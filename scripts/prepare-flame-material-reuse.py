"""Prepare one resource with shared painted material and its own source alpha."""
from pathlib import Path
import json,sys,subprocess
root=Path(__file__).resolve().parents[1];ident=int(sys.argv[1])
if ident not in range(4,10):raise ValueError('Only the six individually inspected golden flame resources4..9 belong to this material reuse group')
subprocess.run([sys.executable,str(root/'scripts/extract-packed-art-reference.py'),*[f'object/flame/flame{ident}_stand.img@{i}'for i in[1,3,4,5,6]]],cwd=root,check=True)
rects={0:[585,560,945,920],1:[1090,560,1450,920],3:[90,90,450,450],4:[585,90,945,450],5:[1090,90,1450,450],6:[90,560,450,920]}
prefix=f'references/qqtang-packed-art/object--flame--flame{ident}_stand-'
spec={'source':'assets/effects/flame-pairs-c-v1.png','materialReuse':True,
    'reuseReason':'shared original-painted gold-sugar-flame material; every resource retains its own original alpha, native dimensions, raw offsets, repeats and empties; not a visual-group alias or new generation',
    'resources':[{'name':f'flame{ident}','sourceRecord':prefix+'first-visible.png.source.json','phases':[{'sourceFrameIndex':i,
        'reference':prefix+('first-visible.png'if i==0 else f'frame-{i:03d}.png'),'textureRect':rects[i]}for i in[0,1,3,4,5,6]]}]}
out=root/f'docs/flame-{ident}-material-reuse-export.json';out.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceResource':ident,'spec':out.relative_to(root).as_posix(),'materialReuse':True,'newModelGeneration':False}))
