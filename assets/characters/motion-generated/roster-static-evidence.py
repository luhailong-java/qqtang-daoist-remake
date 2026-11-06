"""Bounded read-only ZIP text inspection. Never imports or runs inspected code."""
import ast, configparser, hashlib, json, pathlib, re, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8')

ROOT=pathlib.Path(__file__).resolve().parents[3]
ARCHIVE=ROOT/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip'
PREFIX='QQTang-Local/runtime/client-patched/'
MAX_FILE=512_000
MAX_TOTAL=2_000_000

def text_entry(z,name,budget):
    info=z.getinfo(name)
    if info.file_size>MAX_FILE or budget[0]+info.file_size>MAX_TOTAL:
        raise ValueError('Text read size limit exceeded: '+name)
    raw=z.read(info)
    budget[0]+=len(raw)
    if b'\0' in raw: return None, {'archiveEntry':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':'binary_NUL_skipped'}
    for enc in ('utf-8-sig','gb18030'):
        try: value=raw.decode(enc,'strict'); break
        except UnicodeDecodeError: pass
    else: raise ValueError('Not strict UTF8/GB18030 text: '+name)
    return value.replace('\r\n','\n').replace('\r','\n'), {'archiveEntry':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'encoding':enc}

def bounded_literal(node,names,depth=0):
    if depth>16: raise ValueError('AST literal depth exceeded')
    if isinstance(node,ast.Constant) and isinstance(node.value,(str,int,float,bool,type(None))): return node.value
    if isinstance(node,ast.Name) and node.id in names: return names[node.id]
    if isinstance(node,(ast.List,ast.Tuple)):
        if len(node.elts)>2000: raise ValueError('AST collection too large')
        return [bounded_literal(x,names,depth+1) for x in node.elts]
    if isinstance(node,ast.Dict):
        if len(node.keys)>2000: raise ValueError('AST dict too large')
        return {bounded_literal(k,names,depth+1):bounded_literal(v,names,depth+1) for k,v in zip(node.keys,node.values)}
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub): return -bounded_literal(node.operand,names,depth+1)
    raise ValueError('Non-literal AST rejected: '+type(node).__name__)

def assignments_only(text):
    tree=ast.parse(text)
    if sum(1 for _ in ast.walk(tree))>10000: raise ValueError('AST node limit exceeded')
    names={}; locations={}
    for stmt in tree.body:
        if not isinstance(stmt,ast.Assign) or len(stmt.targets)!=1 or not isinstance(stmt.targets[0],ast.Name):
            raise ValueError('Only simple module assignments allowed')
        key=stmt.targets[0].id
        names[key]=bounded_literal(stmt.value,names)
        locations[key]=stmt.lineno
    return names, locations

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'inventory'
    with zipfile.ZipFile(ARCHIVE) as z:
        infos=z.infolist(); budget=[0]
        if mode=='read':
            for name in sys.argv[2:]:
                value,record=text_entry(z,name,budget)
                print(json.dumps(record,ensure_ascii=False))
                print(value if value is not None else '[binary skipped]')
            return
        if mode=='inventory':
            print('SMALL PY/JSON AND BODY ENTRIES')
            for i in infos:
                if not 0<i.file_size<MAX_FILE: continue
                if i.filename.endswith(('.py','.json')) or '/object/body/' in i.filename:
                    print(i.filename+' '+str(i.file_size))
            return
        if mode=='docs-inventory':
            for i in infos:
                if 0<i.file_size<MAX_FILE and i.filename.endswith(('.md','.csv')):
                    print(i.filename+' '+str(i.file_size))
            return
        if mode=='find':
            pattern=re.compile(sys.argv[2],re.I)
            for name in sys.argv[3:]:
                value,record=text_entry(z,name,budget)
                print(json.dumps(record,ensure_ascii=False))
                if value is not None:
                    matches=[(n,line) for n,line in enumerate(value.splitlines(),1) if pattern.search(line)]
                    for n,line in matches[:100]:print(str(n)+': '+line[:500])
                    print('MATCH_COUNT '+str(len(matches)))
            return
        if mode=='audit-player':
            text,record=text_entry(z,PREFIX+'object/player/player.py',budget)
            assignments,locations=assignments_only(text)
            ini=[]
            for i in infos:
                m=re.fullmatch(re.escape(PREFIX)+r'object/player/[Pp]layer(\d+)\.ini',i.filename)
                if not m: continue
                text,source=text_entry(z,i.filename,budget)
                parser=configparser.ConfigParser(interpolation=None,strict=True)
                parser.read_string(text)
                ini.append({'id':int(m.group(1)),'sections':{s:dict(parser[s]) for s in parser.sections()},'source':source})
            out={'scope':'community patched ZIP static player configuration only; not a selectable-roster proof','archive':str(ARCHIVE),'expectedArchiveSha256':'fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7','archiveHashEvidence':'Prior fixed package verification in references/qqtang-map-data/README.md; not rehashed during heavy-resource freeze','executedExternalCode':False,'readLimits':{'perFile':MAX_FILE,'total':MAX_TOTAL,'actual':budget[0]},'playerPy':{'source':record,'assignments':assignments,'lines':locations},'playerIni':sorted(ini,key=lambda r:r['id'])}
            dest=pathlib.Path(__file__).with_name('roster-player-static-evidence.json')
            dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({'output':str(dest),'playerCfgIds':[r['id'] for r in assignments.get('playerCfg',[])],'iniCount':len(ini),'iniIds':sorted(r['id'] for r in ini),'textBytes':budget[0]},ensure_ascii=False))
            return
        raise ValueError('Unknown mode')

if __name__=='__main__': main()
