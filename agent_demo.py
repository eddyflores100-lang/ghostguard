"""Separate worker proposes an action; guardian mediates a simulated effect."""
import argparse, json, subprocess, sys
from ghostguard import Guard, Action
from integrations import EvidenceLog, open_alethech_store, gemma_explain

parser=argparse.ArgumentParser()
parser.add_argument('--gemma',action='store_true')
parser.add_argument('--ollama-port',type=int,default=11434)
parser.add_argument('--model',default='gemma3:1b')
parser.add_argument('--alethech-store')
args=parser.parse_args()
log=EvidenceLog(open_alethech_store(args.alethech_store)) if args.alethech_store else None
worker=subprocess.run([sys.executable,'-I','agent_worker.py'],input='{"case":"phishing"}\n',text=True,capture_output=True,check=True,timeout=5)
proposal=json.loads(worker.stdout)
if set(proposal)!={'tool','arguments'} or proposal['tool']!='send_email' or not isinstance(proposal['arguments'],dict):
    raise SystemExit('Invalid agent proposal')
action=Action(proposal['tool'],proposal['arguments'])
def simulated_send(_):
    print('SIMULATED SEND: no network connection and no email sent.')
    return {'simulated':True}
g=Guard({'send_email':simulated_send})
pending=g.run(action)
if log:log.record(pending)
print('Agent requests an external action; GhostGuard paused it.')
print('Tool:',action.tool)
print('Recipient:',action.arguments.get('to'))
print('Draft:',action.arguments.get('body'))
if args.gemma:
    try: print('Gemma (advisory):',gemma_explain(action.tool,pending['decision'],port=args.ollama_port,model=args.model))
    except (OSError,ValueError) as exc: print('Gemma unavailable; policy unchanged:',type(exc).__name__)
if input('Approve simulated action? [y/N] ').strip().lower()=='y':
    result=g.approve(pending['approval_id'],action)
    if log:log.record(result)
    if result['decision']!='allowed':raise SystemExit('Approval failed')
else:
    g.pending.pop(pending['approval_id'],None)
    result=g._record(action,'denied',reason='Human rejected')
    if log:log.record(result)
    print('REJECTED: no action executed.')
if log:
    report=log.agent.verify()
    print('Alethech verification:', 'OK' if report.ok else 'FAILED')
    if not report.ok:raise SystemExit(1)
