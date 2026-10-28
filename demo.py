"""Controlled example: outbound email is a local simulation only."""
import json
from ghostguard import Guard, Action

def fake_send(args):
    return {'simulated':True,'message':'No email was sent'}

g=Guard({'read_case':lambda _: 'A suspicious job offer asks for a terminal command.', 'send_email':fake_send})
for a in [Action('read_case',{}),Action('shell',{'command':'untrusted command'}),Action('send_email',{'to':'abuse@example.invalid','body':'Report draft'})]:
    result=g.run(a)
    print(json.dumps(result,ensure_ascii=False))
    if result['decision']=='approval_required':
        print('Stopped: human approval required. Demo will not approve or send.')
