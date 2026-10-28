import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from dashboard import App, make_handler

PROPOSAL = '{"tool":"send_email","arguments":{"to":"abuse@example.invalid","body":"Report phishing"}}'
class Worker:
    stdout = PROPOSAL

class AppTests(unittest.TestCase):
    @patch('dashboard.gemma_explain', return_value='Paused for review')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_review_reject_and_single_use(self, worker, advice):
        app = App()
        p = app.propose()
        self.assertEqual(p['decision'], 'approval_required')
        with self.assertRaises(ValueError): app.propose()
        self.assertEqual(app.decide('reject')['decision'], 'denied')
        with self.assertRaises(ValueError): app.decide('approve')

    @patch('dashboard.gemma_explain', return_value='Paused')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_approval_only_simulates(self, worker, advice):
        app = App(); app.propose(); result = app.decide('approve')
        self.assertEqual(result['decision'], 'allowed')
        self.assertTrue(result['simulated'])

    @patch('dashboard.gemma_explain', return_value='Paused')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_smolagents_is_mediated_by_same_guard(self, worker, advice):
        app = App(agent='smolagents'); app.propose()
        self.assertTrue(worker.call_args.args[0][2].endswith('smol_worker.py'))
        self.assertEqual(app.decide('reject')['decision'], 'denied')

    @patch('dashboard.subprocess.run')
    def test_invalid_proposal_fails_closed(self, worker):
        worker.return_value.stdout = '{"tool":"shell","arguments":{}}'
        app = App()
        with self.assertRaises(ValueError): app.propose()
        self.assertIsNone(app.pending)

class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(App(),'test-token'))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.port=self.server.server_port
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def request(self, headers):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        c.request('POST','/api/decide',json.dumps({'decision':'approve'}),headers)
        response=c.getresponse(); response.read(); c.close(); return response.status
    def test_requires_token_origin_and_host(self):
        base={'Content-Type':'application/json','Origin':f'http://127.0.0.1:{self.port}', 'X-GhostGuard-Token':'test-token'}
        self.assertEqual(self.request(base),400) # authorized, but no pending request
        self.assertEqual(self.request({**base,'Origin':'http://evil.example'}),403)
        self.assertEqual(self.request({**base,'X-GhostGuard-Token':'bad'}),403)
        self.assertEqual(self.request({**base,'Host':'evil.example'}),403)
