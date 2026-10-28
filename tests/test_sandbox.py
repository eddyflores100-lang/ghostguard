import json, subprocess, unittest
from unittest.mock import patch
from sandbox import sandbox_proposal

class SandboxTests(unittest.TestCase):
    def test_valid_proposal_runs_without_network_or_privileges(self):
        output=json.dumps({'tool':'send_email','arguments':{'to':'abuse@example.invalid','body':'Review'}})
        fake=subprocess.CompletedProcess([],0,stdout=output,stderr='')
        with patch('sandbox.subprocess.run',side_effect=[fake,fake]) as run:
            result=sandbox_proposal()
        self.assertEqual(result.tool,'send_email')
        args=run.call_args_list[1].args[0]
        for flag in ['--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65532:65532']:
            self.assertIn(flag,args)
        self.assertNotIn('--privileged',args)
        self.assertNotIn('--volume',args)

    def test_invalid_model_output_never_starts_container(self):
        fake=subprocess.CompletedProcess([],0,stdout='{"tool":"shell","arguments":{}}',stderr='')
        with patch('sandbox.subprocess.run',return_value=fake) as run:
            with self.assertRaises(ValueError): sandbox_proposal()
        self.assertEqual(run.call_count,1)
