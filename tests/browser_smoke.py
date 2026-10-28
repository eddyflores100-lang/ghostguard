"""Optional browser smoke test: real local model, Docker and Alethech.

Install playwright and Alethech separately and set GHOSTGUARD_BROWSER to a
Chromium-compatible executable. Requires a running local Ollama and the built
Docker image. This automated test does not represent a human decision.
"""
import os
import sys
import tempfile
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard import App, make_handler
from integrations import EvidenceLog, open_alethech_store
from playwright.sync_api import sync_playwright

browser_path = os.environ.get('GHOSTGUARD_BROWSER')
if not browser_path:
    raise SystemExit('Set GHOSTGUARD_BROWSER to your browser executable.')
with tempfile.TemporaryDirectory() as directory:
    evidence = EvidenceLog(open_alethech_store(str(Path(directory) / 'store')))
    app = App(agent='sandbox', evidence=evidence)
    token = 'local-browser-test-token'
    server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(app, token))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=browser_path, headless=True)
            page = browser.new_page(viewport={'width':1280, 'height':900})
            page.goto(f'http://127.0.0.1:{server.server_port}/#{token}')
            page.locator('#start').click()
            page.locator('#review').wait_for(state='visible', timeout=150000)
            assert page.locator('#recipient').inner_text().endswith('@example.invalid')
            page.reload()
            page.locator('#review').wait_for(state='visible', timeout=10000)
            page.locator('#reject').click()
            page.get_by_text('Rejected or expired. No action was executed.', exact=False).wait_for(timeout=15000)
            assert 'Signed evidence verified' in page.locator('#message').inner_text()
            print('BROWSER_REAL_MODEL_RELOAD_REJECT_EVIDENCE_OK')
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
