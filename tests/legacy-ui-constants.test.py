"""Inert legacy format fixtures; local hold/remote results are recorded separately."""
from pathlib import Path
import importlib.util,struct,unittest

spec=importlib.util.spec_from_file_location('our_inert_legacy_reader',Path(__file__).resolve().parents[1]/'scripts/read-legacy-ui-constants.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)

def string(value):return b's'+struct.pack('<i',len(value))+value
def integer(value):return b'i'+struct.pack('<i',value)
def tuple_value(values):return b'('+struct.pack('<i',len(values))+b''.join(values)
def instruction(opcode,argument):return bytes([opcode])+struct.pack('<H',argument)
def module_fixture(code,consts,names):
    empty=tuple_value([])
    return bytes.fromhex('3bf20d0a')+b'\0'*4+b'c'+struct.pack('<4i',0,0,8,0)+string(code)+tuple_value(consts)+tuple_value([string(n)for n in names])+empty*3+string(b'fixture.py')+string(b'UI')+struct.pack('<i',1)+string(b'')

class InertUiConstantTests(unittest.TestCase):
    def test_raw_rect_literal_keeps_order_and_signed_values(self):
        code=b''.join(instruction(100,i)for i in range(4))+instruction(102,4)+instruction(90,0)+bytes([83])
        node,_=reader.decode(module_fixture(code,[integer(v)for v in [437,-112,346,429]],[b'rect']))
        assignments=reader.literal_assignments(node)
        self.assertEqual(len(assignments),1)
        self.assertEqual(assignments[0]['name'],'rect')
        self.assertEqual([v['value']for v in assignments[0]['literalValue']['values']],[437,-112,346,429])
        self.assertEqual(assignments[0]['storeByteOffset'],15)

    def test_client_call_result_is_never_promoted_to_literal(self):
        code=instruction(101,0)+instruction(100,0)+instruction(131,1)+instruction(90,1)+bytes([83])
        node,_=reader.decode(module_fixture(code,[string(b'object/ui/not-a-verified-result.img')],[b'client_function',b'bkimage']))
        self.assertEqual(reader.literal_assignments(node),[])

    def test_python_looking_input_stays_plain_inert_bytes(self):
        payload=b'__import__("os").system("this must never execute")'
        code=instruction(100,0)+instruction(90,0)+bytes([83])
        node,_=reader.decode(module_fixture(code,[string(payload)],[b'label']))
        self.assertIs(type(node),dict)
        self.assertTrue(node['inertCodeNode'])
        self.assertEqual(node['consts'],(payload,))
        self.assertEqual(reader.literal_assignments(node)[0]['literalValue']['text'],payload.decode())

    def test_magic_truncation_trailing_and_unknown_tag_fail_closed(self):
        valid=module_fixture(bytes([83]),[b'N'],[])
        cases=[b'bad!'+valid[4:],valid[:-1],valid+b'\0',valid[:8]+b'R',valid[:8]+b'('+struct.pack('<i',100001)]
        for data in cases:
            with self.subTest(data=data[:10]):
                with self.assertRaises(ValueError):reader.decode(data)

    def test_partial_dynamic_tuple_and_invalid_constant_index_do_not_become_rect(self):
        code=instruction(101,0)+instruction(100,0)+instruction(102,2)+instruction(90,1)+bytes([83])
        node,_=reader.decode(module_fixture(code,[integer(10)],[b'dynamic',b'rect']))
        self.assertEqual(reader.literal_assignments(node),[])
        node['bytecode']=instruction(100,9)
        with self.assertRaises(ValueError):reader.literal_assignments(node)

if __name__=='__main__':unittest.main()
