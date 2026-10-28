"""Separate worker proposes an action; guardian mediates a simulated effect."""
import argparse, subprocess, sys, time
from pathlib import Path
from ghostguard import Guard
from proposals import parse_proposal
from integrations import EvidenceLog, open_alethech_store, gemma_explain
from auditlog import AuditLog

parser=argparse.ArgumentParser()
parser.add_argument('--gemma',action='store_true')
parser.add_argument('--ollama-port',type=int,default=11434)
parser.add_argument('--model',default='gemma3:1b')
parser.add_argument('--model-agent',action='store_true')
parser.add_argument('--alethech-store')
parser.add_argument('--log-file',default=str(Path.home()/'.ghostguard'/'events.jsonl'))
args=parser.parse_args()
audit=AuditLog(args.log_file)
audit.record('session_started')
try:
    evidence=EvidenceLog(open_alethech_store(args.alethech_store)) if args.alethech_store else None
    worker_args=[sys.executable,'-I','agent_worker.py']
    if args.model_agent:worker_args += ['--model',args.model,'--port',str(args.ollama_port)]
    audit.record('worker_started');start=time.monotonic()
    try:
        worker=subprocess.run(worker_args,input='{"case":"phishing"}\n',text=True,capture_output=True,check=True,timeout=100)
        audit.record('worker_completed',duration_ms=int((time.monotonic()-start)*1000))
    except (subprocess.TimeoutExpired,subprocess.CalledProcessError,OSError) as exc:
        audit.record('worker_failed',error=type(exc).__name__);raise
    try:
        action=parse_proposal(worker.stdout);audit.record('proposal_valid')
    except ValueError:
        audit.record('proposal_invalid',error='ValueError');raise
    def simulated_send(_):
        print('SIMULATED SEND: no network connection and no email sent.')
        return {'simulated':True}
    g=Guard({'send_email':simulated_send});pending=g.run(action)
    audit.record('decision',decision=pending['decision'])
    if evidence:evidence.record(pending)
    print('Agent requests an external action; GhostGuard paused it.')
    print('Tool:',action.tool);print('Recipient:',action.arguments.get('to'));print('Draft:',action.arguments.get('body'))
    if args.gemma:
        start=time.monotonic()
        try:
            print('Gemma (advisory):',gemma_explain(action.tool,pending['decision'],port=args.ollama_port,model=args.model))
            audit.record('model_advice_success',duration_ms=int((time.monotonic()-start)*1000))
        except (OSError,ValueError) as exc:
            audit.record('model_advice_failed',error=type(exc).__name__)
            print('Gemma unavailable; policy unchanged:',type(exc).__name__)
    if input('Approve simulated action? [y/N] ').strip().lower()=='y':
        result=g.approve(pending['approval_id'],action)
        if result['decision']!='allowed':raise SystemExit('Approval failed')
    else:
        g.pending.pop(pending['approval_id'],None)
        result=g._record(action,'denied',reason='Human rejected')
        print('REJECTED: no action executed.')
    audit.record('decision',decision=result['decision'])
    if evidence:
        evidence.record(result)
        report=evidence.agent.verify()
        audit.record('evidence_verified' if report.ok else 'evidence_failed')
        print('Alethech verification:', 'OK' if report.ok else 'FAILED')
        if not report.ok:raise SystemExit(1)
finally:
    audit.record('session_finished')
    print('Diagnostic log:',args.log_file)
