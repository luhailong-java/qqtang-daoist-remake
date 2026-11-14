"""Read social/marriage rectangles and colors as inert constant patterns."""
from pathlib import Path
import hashlib
import importlib.util
import json
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('social_inert_reader',ROOT/'scripts/read-legacy-ui-constants.py')
P=importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
UNKNOWN=object()


def sha(value):return hashlib.sha256(value).hexdigest()
def record(path):return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}


def literal(value):
    if isinstance(value,bytes):return P.text_value(value)[0] if P.text_value(value)[0] is not None else UNKNOWN
    if value is None or type(value)in(int,float,bool,str):return value
    if isinstance(value,(tuple,list)):
        items=[literal(v)for v in value]
        return items if all(v is not UNKNOWN for v in items)else UNKNOWN
    return UNKNOWN


def instructions(node):
    raw,offset,extended,rows=node['bytecode'],0,0,[]
    while offset<len(raw):
        start,op=offset,raw[offset];offset+=1;arg=None
        if op>=90:
            if offset+2>len(raw):raise ValueError('Truncated inert instruction')
            arg=int.from_bytes(raw[offset:offset+2],'little')+extended;offset+=2;extended=0
        if op==143:extended=arg<<16
        row={'offset':start,'opcode':op,'argument':arg}
        if op in(90,101):row['name']=P.text_value(node['names'][arg])[0]
        rows.append(row)
    return rows


def assignments(node,globals_):
    # A bounded recognizer for adjacent literal/name stores and integer +/-.
    # Calls, attribute access, jumps, loops and every other opcode reset it.
    stack,result,origins=[],{},{}
    for row in instructions(node):
        op,arg=row['opcode'],row['argument']
        if op==100:
            value=literal(node['consts'][arg]);stack.append((value,{'kind':'literal','loadByteOffset':row['offset']}))
        elif op==101:
            name=row['name'];stack.append((globals_.get(name,UNKNOWN),{'kind':'symbol','globalName':name,'loadByteOffset':row['offset']}))
        elif op in(102,103):
            if arg>len(stack):stack=[];continue
            values=stack[-arg:]if arg else[]
            if arg:del stack[-arg:]
            if any(v[0]is UNKNOWN for v in values):stack.append((UNKNOWN,{}))
            else:stack.append(([v[0]for v in values],{'kind':'literalConstruction'}))
        elif op in(20,23,24):
            if len(stack)<2:stack=[];continue
            right,left=stack.pop(),stack.pop()
            if type(left[0])not in(int,float)or type(right[0])not in(int,float):stack.append((UNKNOWN,{}))
            else:stack.append((left[0]*right[0]if op==20 else left[0]+right[0]if op==23 else left[0]-right[0],{'kind':'adjacentNumericLiteralExpression'}))
        elif op==90:
            if len(stack)==1 and stack[0][0]is not UNKNOWN:
                result[row['name']]=stack[0][0]
                origins[row['name']]={**stack[0][1],'storeByteOffset':row['offset']}
            stack=[]
        else:stack=[]
    return result,origins


def walk(node,parent=''):
    name=P.text_value(node['name'])[0];scope=parent+'.'+name if parent else name
    yield scope,node
    for value in node['consts']:
        if isinstance(value,dict)and value.get('inertCodeNode'):yield from walk(value,scope)


def class_bases(nodes):
    output={}
    for scope,node in nodes.items():
        rows=instructions(node)
        for i,row in enumerate(rows):
            if row['opcode']!=90 or not i or rows[i-1]['opcode']!=89:continue
            stop=next((j for j in range(i-2,-1,-1)if rows[j]['opcode']==102),None)
            if stop is None:continue
            count=rows[stop]['argument']
            bases=rows[stop-count:stop]if count else[]
            if count>5 or any(v['opcode']!=101 for v in bases):continue
            output[scope+'.'+row['name']]={'bases':[v['name']for v in bases],
                'parentScope':scope,'storeByteOffset':row['offset'],
                'instructionHex':node['bytecode'][bases[0]['offset']if bases else rows[stop]['offset']:row['offset']+3].hex()}
    return output


def main():
    source_path=HERE/'manifest.json';source=json.loads(source_path.read_bytes());modules={};receipts=[]
    with ZipFile(ROOT/source['source']['archiveFile'])as archive:
        for expected in source['source']['sourceModules']:
            raw=archive.read(expected['archiveMember'])
            if sha(raw)!=expected['sha256']:raise ValueError('Pinned source UI module changed')
            node,count=P.decode(raw);modules[expected['module']]=dict(walk(node))
            receipts.append({'module':expected['module'],'sha256':sha(raw),'parsedObjects':count,'bytecodeExecuted':False})
    globals_,_=assignments(modules['uiMain']['?'],{})
    if globals_['lightColor']!=[255,255,255,255]or globals_['zoneChooseColor']!=[255,250,236,255]:
        raise ValueError('Expected shared source foregrounds')
    base_maps={name:class_bases(nodes)for name,nodes in modules.items()}
    stores={name:{scope:assignments(node,globals_)for scope,node in nodes.items()}for name,nodes in modules.items()}
    templates=stores['uiTemplate']

    def resolved(module,scope,key,seen=()):
        if (module,scope,key)in seen:return None
        current=stores[module].get(scope)
        if current and key in current[0]:return {'value':current[0][key],'scope':scope,'origin':current[1][key],'module':module}
        # A store that this limited recognizer cannot resolve is an override,
        # not evidence that the template/base value is still effective.
        if scope in modules[module] and any(r['opcode']==90 and r.get('name')==key for r in instructions(modules[module][scope])):
            return None
        construction=base_maps[module].get(scope,{})
        for base in construction.get('bases',[]):
            parent=scope.rsplit('.',1)[0]
            while parent:
                candidate=parent+'.'+base
                if candidate in stores[module]:
                    result=resolved(module,candidate,key,seen+((module,scope,key),))
                    if result:return result
                if '.'not in parent:break
                parent=parent.rsplit('.',1)[0]
            if '?'+'.'+base in templates:
                result=resolved('uiTemplate','?.'+base,key,seen+((module,scope,key),))
                if result:return result
        return None

    aliases={
      'object/ui/guidebar/dlg_kinmember.img':('uiMain','?.UI.children.socialityDlg',(0,0),'.children.kinDlg.children.kinmemberDlg'),
      'object/ui/guidebar/dlg_kinmgr.img':('uiMain','?.UI.children.socialityDlg',(0,0),'.children.kinDlg.children.kinmanagerDlg'),
      'object/ui/guidebar/player/dlg_playerinfo.img':('uiMain','?.UI.children.playerInfoDlg',(10,16),None),
      'object/ui/marriage/dlg_marriageconfirmchina.img':('uiMain','?.UI.children.marriageConfirmDlg',(0,0),None),
      'object/ui/marriage/dlg_marriageconfirmwest.img':('uiMain','?.UI.children.marriageConfirmDlg',(0,0),None),
    }
    resources=[]
    for resource in source['resources']:
        native=resource['nativePath'];fields=[];bindings=[]
        selected=list(resource['sourceBindings'])
        if native in aliases:
            module,scope,delta,selection=aliases[native]
            selected.append({'module':module,'scope':scope,'firstSourceLine':modules[module][scope]['firstLine'],
                'bytecodeSha256':sha(modules[module][scope]['bytecode']),'layoutAssociation':True,
                'delta':delta,'selectionPrefix':selection})
        for bind in selected:
            name,scope=bind['module'],bind['scope']
            declared=stores[name].get(scope,({},{}))[0]
            if not bind.get('layoutAssociation') and not any(isinstance(declared.get(k),str)and declared[k].replace('\\','/').casefold()==native for k in('bkimage','hotcover')):continue
            bindings.append({'module':name,'scope':scope,'sourceFirstLine':bind['firstSourceLine'],
                             'bytecodeSha256':bind['bytecodeSha256'],'literalAssignments':declared,
                             'layoutAssociation':bind.get('layoutAssociation',False),'delta':bind.get('delta',[0,0]),
                             'associationBasis':'Kin callbacks name alternate background; player mask rect(-10,-16); marriage backgrounds occur in same dialog module'if bind.get('layoutAssociation')else'Exact background literal store'})
            prefix=scope+'.children.'
            for child,node in modules[name].items():
                if not child.startswith(prefix):continue
                if bind.get('selectionPrefix') and not child.startswith(scope+bind['selectionPrefix']):continue
                if native=='object/ui/guidebar/dlg_player.img' and child.startswith(scope+'.children.kinDlg.'):continue
                leaf=stores[name][child][0]
                color=resolved(name,child,'drawcolor')
                type_=resolved(name,child,'type')
                rect=resolved(name,child,'rect')
                if not rect or not isinstance(rect['value'],list)or len(rect['value'])!=4 or not all(type(v)is int for v in rect['value']):continue
                if not color or not isinstance(color['value'],list)or len(color['value'])!=4:continue
                if type_ and type_['value']in('STATIC','RADIO','SCROLL','PICLABEL','NUMLABEL'):continue
                if type_ and type_['value']=='BUTTON' and leaf.get('bkimage'):continue
                segments=child[len(prefix):].split('.children.')
                if any('.'in segment for segment in segments):continue
                x,y,w,h=rect['value'];x+=bind.get('delta',(0,0))[0];y+=bind.get('delta',(0,0))[1];coordinatesKnown=True;blocked=False;parent=scope
                for segment in segments[:-1]:
                    parent+='.children.'+segment
                    pfields=stores[name].get(parent,({},{}))[0]
                    if pfields.get('bkimage'):blocked=True;break
                    r=resolved(name,parent,'rect')
                    if not r or not isinstance(r['value'],list)or len(r['value'])!=4:coordinatesKnown=False;break
                    x+=r['value'][0];y+=r['value'][1]
                if blocked or not coordinatesKnown or w<1 or h<1 or max(abs(v)for v in(x,y,w,h))>4096:continue
                fields.append({'module':name,'scope':child,'rectInBackgroundLogicalSpace':[x,y,w,h],
                     'sourceLocalRect':rect,'sourceForeground':color,'sourceType':type_,
                     'sourceBytecodeSha256':sha(node['bytecode']),'captionLiteral':leaf.get('caption'),
                     'textSize':resolved(name,child,'textsize'),'activeControlFlowConfirmed':False})
        resources.append({'nativePath':native,'format':resource['format'],'declaredCanvas':resource['metadata']['declaredCanvas'],
            'frames':[{'index':f['index'],'width':f.get('width'),'height':f.get('height'),'frameOffset':f['frameOffset'],'pixelMode':f['pixelMode'],'empty':f['empty']}for f in resource['metadata']['frames']],
            'backgroundBindings':bindings,'textFields':fields,
            'interpretation':'Recognized literal rectangles and foregrounds, inherited via observed BUILD_CLASS names; no runtime flow or shared namespace execution verified'})
    output={'schemaVersion':1,'operation':'Bounded inert UI trees and adjacent literal/name/integer-expression store patterns; client bytecode never executed',
        'reader':record(ROOT/'scripts/read-legacy-ui-constants.py'),'evidenceReader':record(Path(__file__)),
        'sourceModules':receipts,'sharedColorDefinitions':{k:globals_[k]for k in('lightColor','zoneChooseColor','darkColor','maskColor')},
        'resources':resources,'classConstructionEvidence':[{ 'module':name,'scope':scope,**data}for name,values in base_maps.items()for scope,data in values.items()if any(scope.startswith(b['scope'])for r in resources for b in r['backgroundBindings']if b['module']==name)],
        'nativeRuntimeVerified':False,'visualAccepted':False}
    output_path=HERE/'layout-evidence.json';output_path.write_bytes((json.dumps(output,ensure_ascii=False,indent=2)+'\n').encode())
    source['layoutEvidence']=record(output_path);source['layoutEvidenceReader']=record(Path(__file__))
    source_path.write_bytes((json.dumps(source,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'resources':len(resources),'recognizedTextFields':sum(len(r['textFields'])for r in resources),
      'backgroundBindings':sum(len(r['backgroundBindings'])for r in resources),'sourceColors':output['sharedColorDefinitions']}))


if __name__=='__main__':main()
