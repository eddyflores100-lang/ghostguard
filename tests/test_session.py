import unittest
from session import GuardianSession

class SessionTests(unittest.TestCase):
    def test_only_reviewed_action_is_executed_after_approval(self):
        calls=[]
        s=GuardianSession(lambda a:calls.append(a))
        s.request_report('abuse@example.invalid','Safety report')
        self.assertEqual(calls,[])
        self.assertIn('abuse@example.invalid',s.review())
        self.assertTrue(s.approve())
        self.assertEqual(len(calls),1)
        self.assertFalse(s.approve())
    def test_reject_discards_request(self):
        calls=[]
        s=GuardianSession(lambda a:calls.append(a))
        s.request_report('abuse@example.invalid','Safety report')
        s.reject()
        self.assertFalse(s.approve())
        self.assertEqual(calls,[])
    def test_new_request_cannot_overwrite_pending(self):
        s=GuardianSession(lambda a:None)
        s.request_report('a@example.invalid','First')
        with self.assertRaises(RuntimeError):s.request_report('b@example.invalid','Second')
