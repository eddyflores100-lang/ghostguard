import json, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from integrations import gemma_explain, EvidenceLog

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        body=json.dumps({'response':'Review this request.'}).encode()
        self.send_response(200); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self,*args): pass

class IntegrationTests(unittest.TestCase):
    def test_gemma_receives_only_tool_metadata(self):
        s=HTTPServer(('127.0.0.1',0),Handler)
        t=threading.Thread(target=s.handle_request);t.start()
        try:
            reply=gemma_explain('send_email','approval_required',port=s.server_port)
            t.join(timeout=5)
            self.assertEqual(reply,'Review this request.')
            self.assertEqual(s.payload['model'],'gemma4')
            self.assertNotIn('secret',json.dumps(s.payload))
        finally:s.server_close()
    def test_unsupported_tool_metadata_is_rejected(self):
        with self.assertRaises(ValueError):gemma_explain('secret body','allowed')
    def test_evidence_records_only_decision_metadata(self):
        class Fake:
            def __init__(self):self.data=[]
            def commit(self,data):self.data.append(data)
        a=Fake(); EvidenceLog(a).record({'tool':'send_email','decision':'denied','action_hash':'abc','secret':'do not save'})
        self.assertEqual(a.data,[{'type':'ghostguard_decision','tool':'send_email','decision':'denied','action_hash':'abc'}])
