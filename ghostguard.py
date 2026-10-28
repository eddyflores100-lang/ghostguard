"""Local, in-process demonstration guard. Not an operating-system sandbox."""
from dataclasses import dataclass
from hashlib import sha256
import json, secrets

@dataclass(frozen=True)
class Action:
    tool: str
    arguments: dict

def digest(action):
    return sha256(json.dumps({'tool':action.tool,'arguments':action.arguments},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

class Guard:
    def __init__(self, tools):
        self.tools=tools
        self.pending={}
        self.events=[]
    def _record(self, action, decision, **extra):
        entry={'tool':action.tool,'action_hash':digest(action),'decision':decision,**extra}
        self.events.append(entry)
        return entry
    def run(self, action):
        if action.tool not in self.tools or action.tool not in {'read_case','send_email'}:
            return self._record(action,'denied',reason='Tool is not allowlisted')
        if action.tool=='send_email':
            token=secrets.token_urlsafe(32)
            self.pending[token]=digest(action)
            return self._record(action,'approval_required',approval_id=token,reason='External action requires explicit approval')
        return self._record(action,'allowed',result=self.tools[action.tool](action.arguments))
    def approve(self, token, action):
        expected=self.pending.pop(token,None)
        if expected is None or expected != digest(action):
            return self._record(action,'denied',reason='Approval missing, already used, or bound to different action')
        if action.tool!='send_email' or action.tool not in self.tools:
            return self._record(action,'denied',reason='Tool no longer available')
        return self._record(action,'allowed',result=self.tools[action.tool](action.arguments))
