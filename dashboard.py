"""Loopback-only demonstration dashboard; all effects remain simulated.

The token limits accidental browser-origin access; this is not a sandbox or
protection from other processes running as the same OS user.
"""
import argparse
import json
import secrets
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ghostguard import Guard
from proposals import parse_proposal
from integrations import EvidenceLog, gemma_explain, open_alethech_store
from sandbox import sandbox_proposal

ROOT = Path(__file__).resolve().parent
MAX_BODY = 4096

class App:
    def __init__(self, *, model='gemma3:1b', port=11434, evidence=None, agent='minimal'):
        self.model, self.port = model, port
        if agent not in ('minimal', 'smolagents', 'sandbox'): raise ValueError('Unknown agent')
        self.agent = agent
        self.guard = Guard({'send_email': lambda _: {'simulated': True}})
        self.evidence = evidence
        self.pending = None
        self.lock = threading.Lock()

    def propose(self):
        with self.lock:
            if self.pending is not None:
                raise ValueError('Resolve the pending request first.')
            if self.agent == 'sandbox':
                action = sandbox_proposal(model=self.model, port=self.port)
            else:
                worker = subprocess.run([sys.executable, '-I', str(ROOT / ('smol_worker.py' if self.agent == 'smolagents' else 'agent_worker.py')),
                    '--model', self.model, '--port', str(self.port)], input='{"case":"phishing"}\n',
                    text=True, capture_output=True, check=True, timeout=100, cwd=str(ROOT))
                action = parse_proposal(worker.stdout)
            decision = self.guard.run(action)
            if decision['decision'] != 'approval_required':
                raise ValueError('The action was not eligible for review.')
            if self.evidence:
                try:
                    self.evidence.record(decision)
                except Exception:
                    self.guard.pending.pop(decision['approval_id'], None)
                    raise
            self.pending = (action, decision['approval_id'])
            try:
                advice = gemma_explain(action.tool, decision['decision'], port=self.port, model=self.model)
            except (OSError, ValueError):
                advice = 'Local advisory model unavailable. The action remains paused.'
            return {'tool': action.tool, 'recipient': action.arguments['to'], 'draft': action.arguments['body'],
                    'advice': advice, 'decision': 'approval_required'}

    def decide(self, choice):
        if choice not in ('approve', 'reject'):
            raise ValueError('Invalid decision.')
        with self.lock:
            if self.pending is None:
                raise ValueError('No request is pending.')
            action, token = self.pending
            self.pending = None
            if choice == 'approve':
                result = self.guard.approve(token, action)
            else:
                self.guard.pending.pop(token, None)
                result = self.guard._record(action, 'denied', reason='Human rejected')
            if self.evidence:
                self.evidence.record(result)
                if not self.evidence.agent.verify().ok:
                    raise RuntimeError('Evidence verification failed.')
            return {'decision': result['decision'], 'simulated': choice == 'approve' and result['decision'] == 'allowed',
                    'evidence_verified': bool(self.evidence)}


def make_handler(app, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def _send(self, status, data, kind='application/json; charset=utf-8'):
            raw = data if isinstance(data, bytes) else json.dumps(data).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(raw)
        def _host_ok(self):
            return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'
        def do_GET(self):
            if not self._host_ok(): return self._send(403, {'error':'Invalid host'})
            assets = {'/': ('dashboard.html', 'text/html; charset=utf-8'),
                      '/dashboard.css': ('dashboard.css', 'text/css; charset=utf-8'),
                      '/dashboard.js': ('dashboard.js', 'text/javascript; charset=utf-8')}
            if self.path not in assets: return self._send(404, {'error':'Not found'})
            name, mime = assets[self.path]
            return self._send(200, (ROOT / 'ui' / name).read_bytes(), mime)
        def do_POST(self):
            expected_origin = f'http://127.0.0.1:{self.server.server_port}'
            if not self._host_ok() or self.headers.get('Origin') != expected_origin or not secrets.compare_digest(self.headers.get('X-GhostGuard-Token', ''), token):
                return self._send(403, {'error':'Unauthorized'})
            if self.headers.get('Content-Type', '').split(';', 1)[0] != 'application/json':
                return self._send(415, {'error':'JSON required'})
            try:
                size = int(self.headers.get('Content-Length', '-1'))
                if not 0 <= size <= MAX_BODY: raise ValueError('Invalid request size')
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict): raise ValueError('Invalid body')
                if self.path == '/api/propose' and body == {}:
                    return self._send(200, app.propose())
                if self.path == '/api/decide' and set(body) == {'decision'}:
                    return self._send(200, app.decide(body['decision']))
                return self._send(404, {'error':'Unknown request'})
            except ValueError as exc:
                return self._send(400, {'error': str(exc)})
            except (OSError, subprocess.SubprocessError):
                return self._send(503, {'error':'The local model or worker is unavailable.'})
            except Exception:
                return self._send(500, {'error':'Unable to complete request. See local configuration.'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description='Run a local simulated GhostGuard review dashboard')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--ollama-port', type=int, default=11434)
    parser.add_argument('--model', default='gemma3:1b')
    parser.add_argument('--agent', choices=('minimal', 'smolagents', 'sandbox'), default='minimal')
    parser.add_argument('--alethech-store')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535 or not 1 <= args.ollama_port <= 65535:
        parser.error('invalid port')
    evidence = EvidenceLog(open_alethech_store(args.alethech_store)) if args.alethech_store else None
    app, token = App(model=args.model, port=args.ollama_port, evidence=evidence, agent=args.agent), secrets.token_urlsafe(32)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(app, token))
    server.daemon_threads = True
    url = f'http://127.0.0.1:{server.server_port}/#{token}'
    print('Open this private local URL:', url, flush=True)
    if not args.no_browser: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == '__main__':
    main()
