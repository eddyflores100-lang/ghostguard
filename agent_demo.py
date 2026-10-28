"""Separate worker proposes an action; guardian mediates a simulated effect."""
import json, subprocess, sys
from ghostguard import Guard, Action

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
print('Agent requests an external action; GhostGuard paused it.')
print('Tool:',action.tool)
print('Recipient:',action.arguments.get('to'))
print('Draft:',action.arguments.get('body'))
if input('Approve simulated action? [y/N] ').strip().lower()=='y':
    result=g.approve(pending['approval_id'],action)
    if result['decision']!='allowed':raise SystemExit('Approval failed')
else:
    g.pending.pop(pending['approval_id'],None)
    print('REJECTED: no action executed.')
