import tempfile
import unittest
from pathlib import Path
from runtime import Runtime

class RuntimeTests(unittest.TestCase):
    def test_budget_persistence_cancel_and_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'work'; root.mkdir()
            (root / 'a.txt').write_text('one\ntwo\n')
            db = Path(d) / 'jobs.db'
            r = Runtime(db, root)
            first = r.submit('a.txt'); second = r.submit('a.txt')
            self.assertTrue(r.cancel(second))
            self.assertEqual(r.run(1), [first])
            self.assertEqual([x[1] for x in r.status()], ['completed', 'cancelled'])
            self.assertNotIn('one', r.status()[0][2])
            r.db.close()
            r = Runtime(db, root)
            self.assertEqual(len(r.status()), 2)
            r.db.close()

    def test_policy_and_oversize(self):
        with tempfile.TemporaryDirectory() as d:
            r = Runtime(Path(d) / 'jobs.db', d)
            for path in ('../outside', '.secret', '/etc/passwd'):
                with self.assertRaises(ValueError): r.submit(path)
            Path(d, 'big').write_text('abcdef')
            r.submit('big'); r.run(max_bytes=2)
            self.assertEqual(r.status()[0][1], 'failed')
            with self.assertRaises(ValueError): r.run(limit=100)
            r.db.close()
