"""Run the untrusted framework in a no-network Docker container.

Host model and guardian remain outside. Docker's security depends on its host,
daemon configuration and kernel; this is a demonstration, not a hostile-code guarantee.
"""
import subprocess
import json
import sys
from pathlib import Path
from proposals import parse_proposal

ROOT=Path(__file__).resolve().parent
IMAGE='ghostguard-agent:local'

def sandbox_proposal(*, model='gemma3:1b', port=11434):
    model_worker=subprocess.run([sys.executable,'-I',str(ROOT/'agent_worker.py'),'--model',model,'--port',str(port)],
                                input='{"case":"phishing"}\n',text=True,capture_output=True,check=True,timeout=100,cwd=str(ROOT))
    # Validate before giving model output to the agent and again at the guardian.
    parse_proposal(model_worker.stdout)
    command=['docker','run','--rm','--interactive','--network','none','--read-only',
             '--cap-drop','ALL','--security-opt','no-new-privileges',
             '--pids-limit','64','--memory','512m','--cpus','1',
             '--user','65532:65532','--tmpfs','/tmp:rw,noexec,nosuid,size=32m',
             IMAGE,'python','-I','/app/smol_worker.py','--proposal-stdin']
    worker=subprocess.run(command,input=json.dumps(json.loads(model_worker.stdout), ensure_ascii=True)+'\n',text=True,capture_output=True,check=True,timeout=120,cwd=str(ROOT))
    return parse_proposal(worker.stdout)
