"""Complete missing textual provenance fields only; no image read or resave."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for path in OUT.glob('sequence-v*.png.generation.json'):
    record=json.loads(path.read_text(encoding='utf-8'))
    for reference in record['references']:
        file=reference['file'].replace('\\','/')
        reference['role']=('primary Daoist Q hand-painted style'if '/image/designs/'in file else
                           'all4 actual source frame positions, NN4x reference only'if file.endswith('four-source-structure.png')else
                           'existing own identity/material master; old narrow geometry is not accepted'if file.endswith('3050-dragon-lantern.png')else
                           'exact prior native four-frame atlas being AI edited')
    save(path,record)
path=OUT/'sequence.json';record=json.loads(path.read_text(encoding='utf-8'));record['sourceGridAttrAsExisting']=[0]
record['sourceDefinitionRecord']='references/qqtang-map-data/motion-contract/elements.json#elementId=3050'
for frame in record['frames']:
    frame['sourceGridAttr']=[0]
    for export in frame['exports'].values():
        export['sourceGridAttr']=[0]
save(path,record)
for folder in ['frames-logical-x1','frames-compatible-x4']:
    for path in(OUT/folder).glob('*.source.json'):
        record=json.loads(path.read_text(encoding='utf-8'));record['sourceGridAttr']=[0];save(path,record)
print(json.dumps({'textualProvenanceCompleted':True,'imageReads':0,'imageResaves':0,'mainArtChanged':False}))
