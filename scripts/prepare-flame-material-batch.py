"""Prepare one bounded six-patch material batch; never calls an image model."""
from pathlib import Path
import sys,json,subprocess
root=Path(__file__).resolve().parents[1]
label,current,next_id,previous,rect0,rect1=sys.argv[1:];current=int(current);next_id=int(next_id)
previous_rects=[list(map(int,r.split(',')))for r in[rect0,rect1]]
if not label.isalpha()or not 1<=current<=255 or not 1<=next_id<=255:raise ValueError('Explicit bounded batch arguments required')
requests=[f'object/flame/flame{current}_stand.img@{i}'for i in[3,4,5,6]]+[f'object/flame/flame{next_id}_stand.img',f'object/flame/flame{next_id}_stand.img@1']
subprocess.run([sys.executable,str(root/'scripts/extract-packed-art-reference.py'),*requests],cwd=root,check=True)
prefix='references/qqtang-packed-art/'
references=[f'{prefix}object--flame--flame{current}_stand-frame-{i:03d}.png'for i in[3,4,5,6]]+[f'{prefix}object--flame--flame{next_id}_stand-first-visible.png',f'{prefix}object--flame--flame{next_id}_stand-frame-001.png']
board=f'{prefix}flame-pair-{label}-structure.png'
subprocess.run([sys.executable,str(root/'scripts/make-reference-art-board.py'),board,*references],cwd=root,check=True)
source=f'assets/effects/flame-pairs-{label}-v1.png';rects=[[90,90,450,450],[585,90,945,450],[1090,90,1450,450],[90,560,450,920],[585,560,945,920],[1090,560,1450,920]]
phases=[{'sourceFrameIndex':i,'source':previous,'reference':f'{prefix}object--flame--flame{current}_stand-'+('first-visible.png'if i==0 else'frame-001.png'),'textureRect':previous_rects[i]}for i in[0,1]]
phases.extend({'sourceFrameIndex':i,'reference':references[n],'textureRect':rects[n]}for n,i in enumerate([3,4,5,6]))
spec={'source':source,'resources':[{'name':f'flame{current}','sourceRecord':f'{prefix}object--flame--flame{current}_stand-first-visible.png.source.json','phases':phases}]}
(root/f'docs/flame-pairs-{label}-export.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prompt=f'''Create SIX original fine-HD HAND-PAINTED DAOIST CHIBI effect-material patches,1536x1024 transparent,3columns x2rows,512square cells. Exactly six400x400 OPAQUE square material patches centred in their cells, full square corners and fully filled edges, empty transparent gutters. Image1 gives actual source effect color, flow and order ONLY, not pixel style; images2/3 give approved fine rounded Daoist cloud painting, ivory and restrained jade reflection; image4 gives our adopted material paint scale and finish. No text, UI frame, scene, character, border, smoky outer glow, photorealism, plastic, noise or pixel art.
Each patch is flowing golden sugar-flame energy in the source color family, rich amber-gold and creamy ivory hot curls with restrained pale jade reflected edges. Clear broad soft hand-painted flowing curves, no holes or transparent areas inside material squares. Actual alpha decay is applied later from exact source frames, so even a sparse source reference gets a fully filled material patch rather than isolated sparks.
Top-left is flame{current} phase3, connected bright flowing curls following its source direction. Top-middle is flame{current} phase4, warmer and less bright with longer slender ivory curls. Top-right is flame{current} phase5, thinning ivory curves over amber rolling light. Bottom-left is flame{current} phase6, final gentle amber/ivory flickers as a full square material. Bottom-middle is flame{next_id} phase0, bright coherent stream and broad curls matching the next source effect's flow direction. Bottom-right is flame{next_id} phase1, the same next stream advanced slightly, consistent colors and scale.
These are distinct material phases, all six square patches remain fully opaque edge-to-edge. No extra phases, animation labels, detached sparks, decorative rims, floor perspective or inter-cell glow. Preserve the source effect category through fine Daoist hand painting. Later honest cropping/resampling and source-alpha composition will preserve every original frame's canvas, offset, repeats or empties; this generation does not change gameplay geometry or claim verified timing.'''
(root/f'docs/flame-pairs-{label}-v1.prompt.txt').write_text(prompt+'\n',encoding='utf-8')
print(json.dumps({'batch':label,'completesSourceResource':current,'startsSourceResource':next_id,'board':board,'source':source,'previousMaterial':previous,'noModelCalled':True}))
