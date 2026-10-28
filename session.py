"""Interactive, simulated human-review flow; not an isolation boundary."""
from ghostguard import Action, Guard

class GuardianSession:
    def __init__(self, send):
        self.guard=Guard({'read_case':lambda _: 'Suspicious recruitment email.','send_email':send})
        self._pending=None
    def request_report(self, recipient, body):
        if self._pending is not None:raise RuntimeError('A request is already pending')
        action=Action('send_email',{'to':recipient,'body':body})
        result=self.guard.run(action)
        self._pending=(action,result['approval_id'])
    def review(self):
        if self._pending is None:return 'No pending action'
        action,_=self._pending
        return f"Tool: {action.tool}\nRecipient: {action.arguments['to']}\nDraft: {action.arguments['body']}"
    def approve(self):
        if self._pending is None:return False
        action,token=self._pending
        self._pending=None
        return self.guard.approve(token,action)['decision']=='allowed'
    def reject(self):
        if self._pending is not None:
            _,token=self._pending
            self.guard.pending.pop(token,None)
            self._pending=None
