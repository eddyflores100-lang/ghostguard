import json, tempfile, unittest
from pathlib import Path
from auditlog import AuditLog
class AuditTests(unittest.TestCase):
 def test_records_only_allowlisted_metadata(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'events.jsonl'; log=AuditLog(p)
   log.record('decision',decision='denied',secret='password123',body='private content')
   data=p.read_text(); event=json.loads(data)
   self.assertEqual(event['event'],'decision');self.assertEqual(event['decision'],'denied')
   self.assertNotIn('password123',data);self.assertNotIn('private content',data)
 def test_rejects_invalid_event(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):AuditLog(Path(d)/'a').record('untrusted user string')
