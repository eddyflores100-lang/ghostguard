import unittest
from ghostguard import Guard, Action

class GuardTests(unittest.TestCase):
    def test_unknown_and_external_actions_are_not_executed(self):
        calls=[]
        g=Guard({'send_email':lambda a:calls.append(a)})
        result=g.run(Action('send_email', {'to':'x@example.com'}))
        self.assertEqual(result['decision'],'approval_required')
        self.assertEqual(calls,[])
        self.assertEqual(g.run(Action('unknown',{}))['decision'],'denied')
    def test_read_allowed_and_approved_payload_is_bound(self):
        calls=[]
        g=Guard({'read_case':lambda a:'case', 'send_email':lambda a:calls.append(a)})
        self.assertEqual(g.run(Action('read_case',{}))['result'],'case')
        action=Action('send_email',{'to':'x@example.com'})
        pending=g.run(action)
        self.assertEqual(g.approve(pending['approval_id'],Action('send_email',{'to':'y@example.com'}))['decision'],'denied')
        self.assertEqual(calls,[])
        pending=g.run(action)
        self.assertEqual(g.approve(pending['approval_id'],action)['decision'],'allowed')
        self.assertEqual(len(calls),1)
        self.assertEqual(g.approve(pending['approval_id'],action)['decision'],'denied')
    def test_blocked_shell_never_invoked(self):
        calls=[]
        g=Guard({'shell':lambda a:calls.append(a)})
        self.assertEqual(g.run(Action('shell',{'command':'ls'}))['decision'],'denied')
        self.assertEqual(calls,[])

if __name__=='__main__':unittest.main()
