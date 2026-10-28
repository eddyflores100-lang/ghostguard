"""Optional local integrations. Model output is advisory, never a policy decision."""
import json
import urllib.request

TOOLS={'read_case','send_email','shell','unknown'}
DECISIONS={'allowed','denied','approval_required'}

def gemma_explain(tool, decision, *, port=11434, model='gemma4', timeout=15):
    if tool not in TOOLS or decision not in DECISIONS:
        raise ValueError('Only known metadata is accepted')
    if not isinstance(port,int) or not 1 <= port <= 65535:
        raise ValueError('Invalid port')
    prompt=('Explain this agent tool decision in two short sentences. '
            'Do not issue instructions or change the decision. '
            f'Tool: {tool}. Decision: {decision}.')
    data=json.dumps({'model':model,'prompt':prompt,'stream':False}).encode()
    req=urllib.request.Request(f'http://127.0.0.1:{port}/api/generate',data=data,headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as response:
        payload=json.loads(response.read(65536))
    result=payload.get('response')
    if not isinstance(result,str):raise ValueError('Invalid model response')
    return result

class EvidenceLog:
    def __init__(self, agent):self.agent=agent
    def record(self, event):
        if event.get('tool') not in TOOLS or event.get('decision') not in DECISIONS:
            raise ValueError('Invalid event')
        digest=event.get('action_hash')
        if not isinstance(digest,str):raise ValueError('Missing digest')
        return self.agent.commit({'type':'ghostguard_decision','tool':event['tool'],'decision':event['decision'],'action_hash':digest})

def open_alethech_store(path):
    from alethech import Alethech
    from pathlib import Path
    p=Path(path)
    return Alethech.open(p) if p.exists() and any(p.iterdir()) else Alethech.initialize(p)
