import json, subprocess, sys, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

class ModelHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.calls.append(body)
        if len(self.server.calls)==1:
            response=json.dumps({'tool':'send_email','arguments':{'to':'abuse@example.invalid','body':'Please review this suspicious offer.'}})
        else: response='A proposed email requires your review.'
        out=json.dumps({'response':response}).encode()
        self.send_response(200);self.send_header('Content-Length',str(len(out)));self.end_headers();self.wfile.write(out)
    def log_message(self,*args):pass

class EndToEndTests(unittest.TestCase):
    def test_model_proposal_advice_and_human_denial(self):
        server=HTTPServer(('127.0.0.1',0),ModelHandler);server.calls=[]
        def run():
            for _ in range(2):server.handle_request()
        thread=threading.Thread(target=run,daemon=True);thread.start()
        try:
            p=subprocess.run([sys.executable,'agent_demo.py','--model-agent','--gemma','--ollama-port',str(server.server_port)],input='n\n',text=True,capture_output=True,timeout=10,check=True)
            self.assertIn('A proposed email requires your review.',p.stdout)
            self.assertIn('REJECTED',p.stdout)
            self.assertNotIn('SIMULATED SEND',p.stdout)
            self.assertEqual(len(server.calls),2)
            self.assertNotIn('suspicious offer',server.calls[1]['prompt'])
        finally:server.server_close()

class MaliciousHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers['Content-Length']))
        out=json.dumps({'response':json.dumps({'tool':'shell','arguments':{'command':'malicious'}})}).encode()
        self.send_response(200);self.send_header('Content-Length',str(len(out)));self.end_headers();self.wfile.write(out)
    def log_message(self,*args):pass

class MaliciousProposalTests(unittest.TestCase):
    def test_model_attempt_to_change_tool_fails_closed(self):
        server=HTTPServer(('127.0.0.1',0),MaliciousHandler)
        thread=threading.Thread(target=server.handle_request,daemon=True);thread.start()
        try:
            p=subprocess.run([sys.executable,'agent_demo.py','--model-agent','--ollama-port',str(server.server_port)],input='y\n',text=True,capture_output=True,timeout=10)
            self.assertNotEqual(p.returncode,0)
            self.assertNotIn('SIMULATED SEND',p.stdout)
            self.assertNotIn('Approve simulated action',p.stdout)
        finally:server.server_close()
