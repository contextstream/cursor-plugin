"""Offline transport tests. Fakes do not establish live MCP/Grok compatibility."""
import io
import json
from pathlib import Path
import sys
import subprocess
from unittest.mock import patch
import unittest
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import probe_mcp as m

class Response(io.BytesIO):
    def __init__(self, value=b"", status=200, headers=None, url=m.ENDPOINT):
        super().__init__(json.dumps(value).encode() if not isinstance(value, bytes) else value)
        self.headers = headers or {"Content-Type": "application/json"}
        self.status, self.url = status, url
    def geturl(self):
        return self.url

class Opener:
    def __init__(self, replies):
        self.replies, self.requests = iter(replies), []
    def open(self, request, timeout):
        self.requests.append(request)
        value = next(self.replies)
        if isinstance(value, Exception):
            raise value
        return value

def rpc(result, id=1):
    return {"jsonrpc": "2.0", "id": id, "result": result}

def tool(name):
    return {"name": name, "inputSchema": {"type": "object"}}

def setup(tools=None, result=None, init=None):
    return [Response(rpc(init or {"protocolVersion": m.PROTOCOL, "capabilities": {"tools": {}}}),
                     headers={"Content-Type": "application/json", "Mcp-Session-Id": "synthetic-session"}),
            Response(status=202), Response(rpc(result or {"tools": [tool(n) for n in (tools or ["context", "search"])]},2))]

class ProbeTests(unittest.TestCase):
    def test_protocol_success_is_not_workflow_success(self):
        o=Opener(setup(["context","search","session","graph","answer","help"]))
        report=m.probe(m.Transport(opener=o))
        self.assertEqual(report['status'],'protocol_ok')
        self.assertIn('project_access', report['not_verified'])
        self.assertEqual([json.loads(r.data)['method'] for r in o.requests],
                         ['initialize','notifications/initialized','tools/list'])
        self.assertTrue(report['advertised_features']['graph'])
    def test_session_and_protocol_forwarded_without_logging(self):
        o=Opener(setup())
        report=m.probe(m.Transport('synthetic-credential',o))
        headers={k.lower():v for k,v in o.requests[-1].headers.items()}
        self.assertEqual(headers['mcp-session-id'],'synthetic-session')
        self.assertEqual(headers['mcp-protocol-version'],m.PROTOCOL)
        self.assertEqual(headers['authorization'],'Bearer synthetic-credential')
        self.assertNotIn('synthetic',json.dumps(report))
    def test_tool_call_is_forbidden(self):
        with self.assertRaises(m.ProbeError): m.Transport(opener=Opener([])).request('tools/call',{},1)
    def test_invalid_tokens(self):
        for token in ['', 'x\r\nInjected: yes', 'with space', 'é', 'x'*8193]:
            with self.subTest(token_length=len(token)), self.assertRaises(m.ProbeError): m.Transport(token,Opener([]))
    def test_pagination(self):
        replies=setup(result={'tools':[tool('context')],'nextCursor':'one'})
        replies.append(Response(rpc({'tools':[tool('search')]},3)))
        o=Opener(replies)
        self.assertEqual(m.probe(m.Transport(opener=o))['tool_count'],2)
        self.assertEqual(json.loads(o.requests[-1].data)['params'],{'cursor':'one'})
    def test_repeated_cursor(self):
        replies=setup(result={'tools':[tool('context')],'nextCursor':'one'})
        replies.append(Response(rpc({'tools':[tool('search')],'nextCursor':'one'},3)))
        with self.assertRaisesRegex(m.ProbeError,'cursor'): m.probe(m.Transport(opener=Opener(replies)))
    def test_page_limit(self):
        replies=setup(result={'tools':[tool('context'),tool('search')],'nextCursor':'0'})
        replies.extend(Response(rpc({'tools':[],'nextCursor':str(i)},i+2)) for i in range(1,m.MAX_PAGES))
        with self.assertRaisesRegex(m.ProbeError,'pagination limit'): m.probe(m.Transport(opener=Opener(replies)))
    def test_missing_required_tool(self):
        with self.assertRaisesRegex(m.ProbeError,'context/search'): m.probe(m.Transport(opener=Opener(setup(['context']))))
    def test_optional_tools_not_required(self):
        report=m.probe(m.Transport(opener=Opener(setup())))
        self.assertFalse(report['advertised_features']['graph'])
    def test_bad_advertisements(self):
        values=[{'tools':{}},{'tools':[{'name':'bad\nname'}]}, {'tools':[tool('context'),tool('context')]}, {'tools':[{'name':'context','inputSchema':{}}]}, {'tools':[],'nextCursor':''},{'tools':[],'nextCursor':5}]
        for value in values:
            with self.subTest(value=value), self.assertRaises(m.ProbeError): m.probe(m.Transport(opener=Opener(setup(result=value))))
    def test_tool_count_limit(self):
        with self.assertRaisesRegex(m.ProbeError,'count limit'): m.probe(m.Transport(opener=Opener(setup([f'tool{i}' for i in range(m.MAX_TOOLS+1)]))))
    def test_unsupported_protocol(self):
        with self.assertRaisesRegex(m.ProbeError,'protocol'): m.probe(m.Transport(opener=Opener(setup(init={'protocolVersion':'future','capabilities':{'tools':{}}}))))
    def test_missing_tools_capability(self):
        with self.assertRaisesRegex(m.ProbeError,'capability'): m.probe(m.Transport(opener=Opener(setup(init={'protocolVersion':m.PROTOCOL,'capabilities':{}}))))
    def test_invalid_session_header(self):
        replies=setup(); replies[0].headers['Mcp-Session-Id']='unsafe\nheader'
        with self.assertRaisesRegex(m.ProbeError,'session header'): m.probe(m.Transport(opener=Opener(replies)))
    def test_http_errors_do_not_leak(self):
        for code in [301,302,307,308,401,403,429,500]:
            err=HTTPError(m.ENDPOINT,code,'secret message',{},io.BytesIO(b'secret payload'))
            with self.subTest(code=code), self.assertRaises(m.ProbeError) as caught: m.Transport(opener=Opener([err])).request('initialize',{},1)
            self.assertNotIn('secret',str(caught.exception))
    def test_redirect_handler_refuses(self): self.assertIsNone(m.NoRedirect().redirect_request(None,None,302,'',{},'https://example.invalid'))
    def test_response_location(self):
        with self.assertRaisesRegex(m.ProbeError,'location'): m.Transport(opener=Opener([Response(rpc({}),url='https://example.invalid')])).request('initialize',{},1)
    def test_network_error_sanitized(self):
        with self.assertRaises(m.ProbeError) as caught: m.Transport(opener=Opener([URLError('secret')])).request('initialize',{},1)
        self.assertNotIn('secret',str(caught.exception))
    def test_sse_matching_event(self):
        body=b': heartbeat\n\ndata: '+json.dumps({'jsonrpc':'2.0','method':'notifications/message','params':{}}).encode()+b'\n\n'
        body+=b'data: '+json.dumps(rpc({'ok':True})).encode()+b'\n\n'
        self.assertEqual(m.read_result(Response(body,headers={'Content-Type':'text/event-stream'}),1),{'ok':True})
    def test_sse_partial_event_is_not_success(self):
        with self.assertRaisesRegex(m.ProbeError,'ended'): m.read_result(Response(b'data: {"jsonrpc":"2.0"}',headers={'Content-Type':'text/event-stream'}),1)
    def test_sse_wrong_id(self):
        with self.assertRaisesRegex(m.ProbeError,'ID mismatch'): m.read_result(Response(b'data: '+json.dumps(rpc({},2)).encode()+b'\n\n',headers={'Content-Type':'text/event-stream'}),1)
    def test_size_caps(self):
        for content_type in ['application/json','text/event-stream']:
            with self.subTest(content_type=content_type),self.assertRaisesRegex(m.ProbeError,'size limit'): m.read_result(Response(b'x'*(m.MAX_BYTES+1),headers={'Content-Type':content_type}),1)
    def test_bad_json_and_duplicate_keys(self):
        for raw in [b'{',b'{"a":1,"a":2}',b'{"x":NaN}',b'\xff']:
            with self.subTest(raw=raw),self.assertRaises(m.ProbeError): m.read_result(Response(raw),1)
    def test_invalid_envelopes(self):
        for value in [[],{'id':1,'result':{}},rpc([],1),rpc({},True),{'jsonrpc':'2.0','id':1,'error':{'message':'secret'}}]:
            with self.subTest(value=value),self.assertRaises(m.ProbeError) as caught: m.read_result(Response(value),1)
            self.assertNotIn('secret',str(caught.exception))
    def test_notification_not_accepted(self):
        with self.assertRaisesRegex(m.ProbeError,'notification'): m.Transport(opener=Opener([Response(status=200)])).request('notifications/initialized')
    def test_unsupported_content_type(self):
        with self.assertRaisesRegex(m.ProbeError,'Content-Type'): m.read_result(Response(b'<html/>',headers={'Content-Type':'text/html'}),1)

class AdditionalProtocolTests(unittest.TestCase):
    def test_no_network_without_opt_in(self):
        run=subprocess.run([sys.executable,str(Path(m.__file__))],capture_output=True,text=True,timeout=5)
        self.assertEqual(run.returncode,2)
        self.assertIn('No network request made',run.stderr)
    def test_protocol_wrong_type(self):
        for version in [[],{},True,None]:
            with self.subTest(version=version),self.assertRaises(m.ProbeError): m.probe(m.Transport(opener=Opener(setup(init={'protocolVersion':version,'capabilities':{'tools':{}}}))))
    def test_sse_line_endings(self):
        for sep in [b'\n',b'\r\n',b'\r']:
            with self.subTest(sep=sep):
                body=b'data: '+json.dumps(rpc({'ok':True})).encode()+sep+sep
                self.assertEqual(m.read_result(Response(body,headers={'Content-Type':'text/event-stream'}),1),{'ok':True})
    def test_response_deadline(self):
        with patch.object(m.time,'monotonic',side_effect=[0,m.TIMEOUT+1]):
            with self.assertRaisesRegex(m.ProbeError,'time limit'): m.read_result(Response(rpc({})),1)
    def test_sse_multiline_data(self):
        body=b'data: {"jsonrpc":"2.0",\ndata: "id":1,"result":{}}\n\n'
        self.assertEqual(m.read_result(Response(body,headers={'Content-Type':'text/event-stream'}),1),{})

if __name__ == '__main__': unittest.main()