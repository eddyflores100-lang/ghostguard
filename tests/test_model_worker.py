import json, subprocess, sys, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
  self.server.received=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  content=json.dumps({'tool':'send_email','arguments':{'to':'abuse@example.invalid','body':'Investigate suspicious offer.'}})
  data=json.dumps({'response':content}).encode()
  self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
class ModelWorkerTests(unittest.TestCase):
 def test_worker_requests_model_and_outputs_proposal(self):
  s=HTTPServer(('127.0.0.1',0),Handler);t=threading.Thread(target=s.handle_request);t.start()
  try:
   p=subprocess.run([sys.executable,'agent_worker.py','--model','gemma3:1b','--port',str(s.server_port)],input='{"case":"phishing"}\n',text=True,capture_output=True,check=True,timeout=5)
   self.assertEqual(json.loads(p.stdout)['tool'],'send_email')
   self.assertEqual(s.received['model'],'gemma3:1b')
  finally:t.join(timeout=5);s.server_close()
