"""Read lobby foreground and PICLABEL construction as bounded inert data."""
from pathlib import Path
import hashlib
import importlib.util
import json
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('lobbyextra_inert_reader',ROOT/'scripts/read-legacy-ui-constants.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def lit(value):
    if value['type'] in ('tuple','list'):
        return [lit(v) for v in value['values']]
    return value.get('text',value.get('value'))


def walk(node,parent=''):
    name = parser.text_value(node['name'])[0]
    scope = parent+'.'+name if parent else name
    yield scope,node
    for value in node['consts']:
        if isinstance(value,dict) and value.get('inertCodeNode'):
            yield from walk(value,scope)


def instructions(node):
    raw,offset,extended,rows = node['bytecode'],0,0,[]
    while offset < len(raw):
        start,opcode = offset,raw[offset]
        offset += 1
        argument = None
        if opcode >= 90:
            if offset+2 > len(raw):
                raise ValueError('Truncated inert instruction')
            argument = int.from_bytes(raw[offset:offset+2],'little')+extended
            offset += 2
            extended = 0
        if opcode == 143:
            extended = argument << 16
        row = {'offset':start,'opcode':opcode,'argument':argument}
        if opcode in (90,101):
            row['name'] = parser.text_value(node['names'][argument])[0]
        rows.append(row)
    return rows


def main():
    manifest_path = HERE/'manifest.json'
    source = json.loads(manifest_path.read_bytes())
    modules,nodes = [],{}
    with ZipFile(ROOT/source['source']['archiveFile']) as archive:
        for name in ('uiSelRoom','uiTemplate'):
            member = f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc'
            raw = archive.read(member)
            expected = next(v for v in source['source']['sourceModules'] if v['module']==name)
            if sha(raw) != expected['sha256']:
                raise ValueError('Pinned source UI differs')
            node,count = parser.decode(raw)
            nodes[name] = dict(walk(node))
            modules.append({'module':name,'sourceSha256':sha(raw),'parsedObjects':count,'bytecodeExecuted':False})
    text = nodes['uiSelRoom']['?.UI_children_selRoom.children.chatArea.children.chatPanel.children.chatList']
    text_stores = {a['name']:lit(a['literalValue']) for a in parser.literal_assignments(text)}
    if text_stores['drawcolor'] != [199,242,252,255] or text_stores['type'] != 'TEXTLIST':
        raise ValueError('Expected explicit cyan lobby text list')
    parent = nodes['uiSelRoom']['?.UI_children_selRoom.children.room1.children']
    rows = instructions(parent)
    store = next(i for i,row in enumerate(rows) if row['opcode']==90 and row.get('name')=='no')
    window = rows[store-7:store+1]
    if [(r['opcode'],r.get('name')) for r in window[:3]] != [(101,'TPicLabel'),(101,'Static'),(102,None)]:
        raise ValueError('Expected explicit TPicLabel/Static native number class')
    if window[2]['argument'] != 2 or window[-2]['opcode'] != 89:
        raise ValueError('Expected two-base native number class construction')
    number = nodes['uiSelRoom']['?.UI_children_selRoom.children.room1.children.no']
    number_stores = {a['name']:lit(a['literalValue']) for a in parser.literal_assignments(number)}
    if number_stores['textsize'] != 10 or number_stores['bkimage'] != 'object/ui/selRoom/num.img':
        raise ValueError('Expected native number positions and path')
    template = nodes['uiTemplate']['?.TPicLabel']
    template_stores = {a['name']:lit(a['literalValue']) for a in parser.literal_assignments(template)}
    if template_stores['type'] != 'PICLABEL':
        raise ValueError('Expected native PICLABEL type')
    no_binding = [r['nativePath'] for r in source['resources'] if not r['sourceBindings']]
    result = {'schemaVersion':1,'operation':'Bounded constant-tree reading and static instruction patterns only',
              'sourceModules':modules,'reader':record(ROOT/'scripts/read-legacy-ui-constants.py'),
              'explicitChatForeground':{'scope':'?.UI_children_selRoom.children.chatArea.children.chatPanel.children.chatList',
                 'bytecodeSha256':sha(text['bytecode']),'literalAssignments':text_stores},
              'roomNumber':{'scope':'?.UI_children_selRoom.children.room1.children.no',
                 'bytecodeSha256':sha(number['bytecode']),'literalAssignments':number_stores,
                 'parentScope':'?.UI_children_selRoom.children.room1.children',
                 'parentBytecodeSha256':sha(parent['bytecode']),'classConstruction':window,
                 'classConstructionHex':parent['bytecode'][window[0]['offset']:window[-1]['offset']+3].hex(),
                 'templateScope':'?.TPicLabel','templateBytecodeSha256':sha(template['bytecode']),
                 'templateLiteralAssignments':template_stores,
                 'sourcePositionGlyphOrder':'0123456789','glyphOrderBasis':'All ten decoded source rasters inspected statically; not runtime execution'},
              'pathsWithoutExactBinding':no_binding,
              'candidateTextPolicy':{'chatLists':'Deep jade, retaining source dark polarity and Alpha',
                 'guideBubbles':'Pale original-polarity paper; blank runtime captions are not invented',
                 'roomNumbers':'Own fixed-size 13px font, original ten cropped frames and offsets',
                 'remainingUnknowns':['Message-by-message color overrides','Guide caption colors and runtime bindings',
                    'Native speaker-mask blending','Notification duration and all interactions']},
              'bytecodeExecuted':False,'nativeRuntimeVerified':False,'visualAccepted':False}
    output = HERE/'ui-evidence.json'
    output.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    source['uiEvidence'] = record(output)
    source['uiEvidenceReader'] = record(Path(__file__))
    manifest_path.write_bytes((json.dumps(source,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'explicitChatForeground':text_stores['drawcolor'],'numberClassBases':['TPicLabel','Static'],
                      'sourceGlyphPositions':10,'pathsWithoutExactBinding':no_binding}))


if __name__ == '__main__':
    main()
