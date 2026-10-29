"""Read six CPython2.3-compatible constant trees as inert data.

No marshal/import/exec/eval of client bytes, no CodeType construction and no
client control-flow/call execution. A static recognizer records literal stores.
Unknown tags, trailing bytes and bounds fail closed.
Format evidence: CPython v2.3.7 Python/{import,marshal}.c, linked in the receipt.
"""
from pathlib import Path
import struct,hashlib,json,zipfile,sys,datetime

NULL=object()
class Reader:
    def __init__(self,data):self.data=data;self.offset=0;self.objects=0
    def take(self,size):
        if type(size)is not int or size<0 or size>1024*1024 or self.offset+size>len(self.data):raise ValueError('Invalid or truncated bounded field')
        value=self.data[self.offset:self.offset+size];self.offset+=size;return value
    def integer(self):return struct.unpack('<i',self.take(4))[0]
    def count(self):
        size=self.integer()
        if not 0<=size<=100000:raise ValueError('Invalid bounded container count')
        return size
    def object(self,depth=0):
        self.objects+=1
        if depth>96 or self.objects>100000:raise ValueError('Constant tree limit')
        tag=self.take(1)
        if tag==b'0':return NULL
        if tag==b'N':return None
        if tag in [b'F',b'T']:return tag==b'T'
        if tag in [b'S',b'.']:return {'inertSingleton':'StopIteration'if tag==b'S'else'Ellipsis'}
        if tag==b'i':return self.integer()
        if tag==b'I':return struct.unpack('<q',self.take(8))[0]
        if tag in [b'f',b'x']:
            values=[float(self.take(self.take(1)[0]).decode('ascii'))for _ in range(2 if tag==b'x'else 1)]
            return {'inertComplex':values}if tag==b'x'else values[0]
        if tag==b'l':
            count=self.integer()
            if abs(count)>1024:raise ValueError('Oversize long integer')
            digits=struct.unpack('<'+'H'*abs(count),self.take(abs(count)*2))
            if any(d>32767 for d in digits):raise ValueError('Invalid15-bit long digit')
            value=sum(d<<(15*i)for i,d in enumerate(digits));return -value if count<0 else value
        if tag in [b's',b'u']:
            value=self.take(self.count());return value.decode('utf-8')if tag==b'u'else value
        if tag in [b'(',b'[']:
            values=[self.object(depth+1)for _ in range(self.count())]
            if any(v is NULL for v in values):raise ValueError('Null outside dictionary terminator')
            return tuple(values)if tag==b'('else values
        if tag==b'{':
            values=[]
            while True:
                key=self.object(depth+1)
                if key is NULL:break
                value=self.object(depth+1)
                if value is NULL:raise ValueError('Invalid dictionary value')
                values.append([key,value])
                if len(values)>100000:raise ValueError('Oversize dictionary')
            return {'inertDictionaryPairs':values}
        if tag==b'c':
            record={'inertCodeNode':True}
            for name in ['argcount','nlocals','stacksize','flags']:record[name]=self.integer()
            if any(record[name]<0 for name in ['argcount','nlocals','stacksize']):raise ValueError('Invalid code header')
            for name in ['bytecode','consts','names','varnames','freevars','cellvars','filename','name']:record[name]=self.object(depth+1)
            record['firstLine']=self.integer();record['lineTable']=self.object(depth+1)
            if not isinstance(record['bytecode'],bytes)or not isinstance(record['lineTable'],bytes):raise ValueError('Invalid inert code byte fields')
            if any(not isinstance(record[name],tuple)for name in ['consts','names','varnames','freevars','cellvars']):raise ValueError('Invalid inert code tuple fields')
            if not isinstance(record['name'],bytes)or not isinstance(record['filename'],bytes):raise ValueError('Invalid inert code identity fields')
            return record
        raise ValueError(f'Unsupported marshal tag {tag.hex()} at {self.offset-1}; no compatibility guess')

def decode(data):
    if len(data)>1024*1024 or data[:4]!=bytes.fromhex('3bf20d0a'):raise ValueError('Expected bounded62011 magic file')
    reader=Reader(data[8:]);node=reader.object()
    if reader.offset!=len(reader.data)or not isinstance(node,dict)or not node.get('inertCodeNode'):raise ValueError('Incomplete module constant tree')
    return node,reader.objects

def text_value(value):
    if isinstance(value,str):return value,'unicode'
    if not isinstance(value,bytes):return None,None
    for encoding in ['utf-8','gb18030']:
        try:text=value.decode(encoding)
        except UnicodeDecodeError:continue
        if all(c.isprintable()or c in '\n\r\t'for c in text):return text,encoding
    return None,None

def constant(value,level=0):
    if isinstance(value,bytes):
        text,encoding=text_value(value)
        return {'type':'bytes','length':len(value),'sha256':hashlib.sha256(value).hexdigest(),'text':text,'textEncodingCandidate':encoding}
    if isinstance(value,dict)and value.get('inertCodeNode'):
        return {'type':'code-reference','name':text_value(value['name'])[0],'firstLine':value['firstLine']}
    if isinstance(value,(tuple,list)):
        return {'type':'tuple'if isinstance(value,tuple)else'list','values':[constant(v,level+1)for v in value]}
    if isinstance(value,dict):return {k:[constant(v,level+1)for v in values]if isinstance(values,list)else values for k,values in value.items()}
    return {'type':type(value).__name__,'value':value}

def literal_assignments(node):
    # CPython2.3: HAVE_ARGUMENT90, LOAD_CONST100, STORE_NAME90,
    # BUILD_TUPLE102, BUILD_LIST103, EXTENDED_ARG143. No calls/jumps run.
    data=node['bytecode'];offset=0;extended=0;pending=[];assignments=[]
    while offset<len(data):
        start=offset;opcode=data[offset];offset+=1;argument=None
        if opcode>=90:
            if offset+2>len(data):raise ValueError('Truncated static instruction')
            argument=int.from_bytes(data[offset:offset+2],'little')+extended;offset+=2;extended=0
        if opcode==143:
            extended=argument<<16
            continue
        if opcode==100:
            if argument>=len(node['consts']):raise ValueError('Invalid static constant index')
            pending.append(node['consts'][argument])
        elif opcode in [102,103]:
            if argument>len(pending):pending=[];continue
            values=pending[-argument:]if argument else[]
            if argument:del pending[-argument:]
            pending.append(tuple(values)if opcode==102 else values)
        elif opcode==90:
            if argument>=len(node['names']):raise ValueError('Invalid static name index')
            if len(pending)==1:
                assignments.append({'storeByteOffset':start,'name':text_value(node['names'][argument])[0],
                    'literalValue':constant(pending[0]),'scope':'adjacent literal construction and STORE_NAME only; not executed or guaranteed active'})
            pending=[]
        else:pending=[]
    if extended:raise ValueError('Dangling extended argument')
    return assignments

def collect(node,parent=None):
    name=text_value(node['name'])[0];scope=(parent+'.'if parent else'')+name
    rows=[{'scope':scope,'sourceFilename':text_value(node['filename'])[0],'firstLine':node['firstLine'],
        'bytecodeLength':len(node['bytecode']),'bytecodeSha256':hashlib.sha256(node['bytecode']).hexdigest(),
        'bytecodeExecuted':False,'names':[text_value(v)[0]for v in node['names']],
        'constants':[constant(v)for v in node['consts']],'literalAssignments':literal_assignments(node)}]
    for value in node['consts']:
        if isinstance(value,dict)and value.get('inertCodeNode'):rows+=collect(value,scope)
    return rows

def main():
    root=Path(__file__).resolve().parents[1]
    names=sys.argv[1:]
    allowed={'uiLogin','uiMain','uiRoom','uiShop','uiGame','uiTemplate'}
    if not 1<=len(names)<=6 or len(set(names))!=len(names)or any(n not in allowed for n in names):raise ValueError('Choose1–6 explicitly authorized UI source modules')
    folder=root/'references/qqtang-ui-data/constants';folder.mkdir(exist_ok=True)
    receipts=[]
    with zipfile.ZipFile(root/'.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip')as z:
        for name in names:
            member=f'QQTang-Local/runtime/client-patched/res/uiRes/{name}.pyc';raw=z.read(member)
            node,count=decode(raw);scopes=collect(node)
            record={'module':name,'sourceMember':member,'sourceBytes':len(raw),'sourceSha256':hashlib.sha256(raw).hexdigest(),
                'operation':'independent bounded data-only constant-tree parsing and static literal-store recognition; no bytecode execution/import/CodeType',
                'magicHex':raw[:4].hex(),'formatCompatibility':'CPython62011 magic/2.3-family grammar; exact vendor interpreter build unknown',
                'grammarSources':[{'url':'https://github.com/python/cpython/blob/v2.3.7/Python/import.c','gitBlob':'3ca10beabaf74320f5e9ff340a880413802a787a'},
                    {'url':'https://github.com/python/cpython/blob/v2.3.7/Python/marshal.c','gitBlob':'5aaa3821b42cf7a01f737bdc47d47ee87f2c6393'},
                    {'url':'https://github.com/python/cpython/blob/v2.3.7/Lib/opcode.py','gitBlob':'cfde5f803bf7c14472e6f15cf391a8c8ec2ac7b7'}],
                'parsedObjects':count,'completeByteConsumption':True,'scopes':scopes,'runtimeImported':False,
                'interpretation':'Literal occurrence and code scope only; not executed UI behavior, active-page existence, control-coordinate semantics or visual acceptance.'}
            (folder/(name+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
            receipts.append({'module':name,'sourceBytes':len(raw),'constantTreeObjects':count,'scopes':len(scopes)})
    print(json.dumps(receipts))
if __name__=='__main__':main()
