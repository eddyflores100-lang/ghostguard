import json, subprocess, sys, unittest

class BridgeTests(unittest.TestCase):
    def test_worker_does_not_obtain_approval_capability(self):
        p=subprocess.run([sys.executable,'agent_worker.py'],input=json.dumps({'case':'phishing'})+'\n',text=True,capture_output=True,check=True)
        request=json.loads(p.stdout)
        self.assertEqual(request['tool'],'send_email')
        self.assertNotIn('approval_id',request)
    def test_agent_action_rejected_never_executes(self):
        p=subprocess.run([sys.executable,'agent_demo.py'],input='n\n',text=True,capture_output=True,check=True)
        self.assertIn('REJECTED',p.stdout)
        self.assertNotIn('SIMULATED SEND',p.stdout)
    def test_agent_action_approved_is_simulated(self):
        p=subprocess.run([sys.executable,'agent_demo.py'],input='y\n',text=True,capture_output=True,check=True)
        self.assertIn('SIMULATED SEND',p.stdout)
        self.assertNotIn('approval_id',p.stdout)
