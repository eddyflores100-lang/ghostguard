import unittest
from proposals import parse_proposal
class ProposalTests(unittest.TestCase):
 def test_valid_proposal(self):
  action=parse_proposal('{"tool":"send_email","arguments":{"to":"abuse@example.invalid","body":"Review this case"}}')
  self.assertEqual(action.tool,'send_email')
 def test_reject_extra_tools_and_unexpected_fields(self):
  for data in ['{"tool":"shell","arguments":{}}','{"tool":"send_email","arguments":{"to":"a","body":"b","bcc":"c"}}','{"tool":"send_email","arguments":{"to":"a\\nb","body":"b"}}']:
   with self.assertRaises(ValueError):parse_proposal(data)
