"""Controlled CLI example. External actions are always simulated."""
import argparse
import json
from ghostguard import Guard, Action
from integrations import EvidenceLog, open_alethech_store, gemma_explain

parser=argparse.ArgumentParser()
parser.add_argument('--gemma',action='store_true',help='Explain decisions using local Ollama gemma4')
parser.add_argument('--alethech-store',help='Write signed decision metadata to this local store')
args=parser.parse_args()
log=EvidenceLog(open_alethech_store(args.alethech_store)) if args.alethech_store else None

def fake_send(_):return {'simulated':True,'message':'No email was sent'}

g=Guard({'read_case':lambda _: 'A suspicious job offer asks for a terminal command.', 'send_email':fake_send})
for a in [Action('read_case',{}),Action('shell',{'command':'untrusted command'}),Action('send_email',{'to':'abuse@example.invalid','body':'Report draft'})]:
    result=g.run(a)
    print(json.dumps({k:v for k,v in result.items() if k!='approval_id'},ensure_ascii=False))
    if log:log.record(result)
    if args.gemma:
        try:print('Gemma (advisory):',gemma_explain(a.tool,result['decision']))
        except (OSError, ValueError) as exc: print('Gemma unavailable; policy unchanged:',type(exc).__name__)
    if result['decision']=='approval_required':print('Stopped: human approval required. Demo will not approve or send.')
if log:
    report=log.agent.verify()
    print('Alethech verification:', 'OK' if report.ok else 'FAILED')
    if not report.ok:raise SystemExit(1)
