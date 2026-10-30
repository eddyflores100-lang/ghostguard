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
    @patch('dashboard.gemma_explain', return_value='Paused')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_expired_request_is_cleared_and_cannot_block_new_review(self, worker, advice):
        app = App()
        clock = [100.0]
        app.guard.clock = lambda: clock[0]
        calls = []
        app.guard.tools['send_email'] = lambda _: calls.append('executed')
        app.propose()
        clock[0] += app.guard.approval_ttl
        self.assertEqual(app.status()['decision'], 'expired')
        self.assertEqual(calls, [])
        with self.assertRaises(ValueError):
            app.decide('approve')
        self.assertEqual(app.propose()['decision'], 'approval_required')

    @patch('dashboard.gemma_explain', return_value='Paused for review')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_review_reject_and_single_use(self, worker, advice):
        app = App()
        p = app.propose()
        self.assertEqual(p['decision'], 'approval_required')
        self.assertEqual(app.status()['draft'], 'Report phishing')
        self.assertNotIn('approval_id', app.status())
        with self.assertRaises(ValueError): app.propose()
        self.assertEqual(app.decide('reject')['decision'], 'denied')
        self.assertEqual(app.status()['decision'], 'none')
        with self.assertRaises(ValueError): app.decide('approve')

    @patch('dashboard.gemma_explain', return_value='Paused')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_approval_only_simulates(self, worker, advice):
        app = App(); app.propose(); result = app.decide('approve')
        self.assertEqual(result['decision'], 'allowed')
        self.assertTrue(result['simulated'])

    @patch('dashboard.gemma_explain', return_value='Paused')
    @patch('dashboard.subprocess.run', return_value=Worker())
    def test_concurrent_approvals_execute_only_once(self, worker, advice):
        app = App(); app.propose()
        calls = []
        app.guard.tools['send_email'] = lambda _: calls.append('executed') or {'simulated': True}
        barrier = threading.Barrier(3)
        results = []
        def approve():
            barrier.wait()
            try:
                results.append(app.decide('approve')['decision'])
            except ValueError:
                results.append('already consumed')
        threads = [threading.Thread(target=approve) for _ in range(2)]
        for thread in threads: thread.start()
        barrier.wait()
        for thread in threads: thread.join()
        self.assertCountEqual(results, ['allowed', 'already consumed'])
        self.assertEqual(calls, ['executed'])

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

