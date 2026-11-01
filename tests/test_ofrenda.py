import json
import tempfile
import unittest
from pathlib import Path

from ofrenda import DEFAULT_DATA, ENFORCED, check, load_incidents, render


class OfrendaDataTests(unittest.TestCase):
    def test_bundled_incidents_are_valid(self):
        incidents = load_incidents(DEFAULT_DATA)
        self.assertGreaterEqual(len(incidents), 1)
        self.assertGreaterEqual(len(incidents[0]["lessons"]), 1)

    def test_every_candle_maps_to_enforced_mechanism(self):
        self.assertEqual(check(load_incidents(DEFAULT_DATA)), [])

    def test_every_mechanism_is_honored_by_some_candle(self):
        incidents = load_incidents(DEFAULT_DATA)
        used = {lesson["enforced_by"] for incident in incidents for lesson in incident["lessons"]}
        self.assertEqual(used, set(ENFORCED))


class OfrendaCheckTests(unittest.TestCase):
    def test_unknown_mechanism_fails_closed(self):
        incidents = load_incidents(DEFAULT_DATA)
        incidents[0]["lessons"][0]["enforced_by"] = "good_intentions"
        self.assertTrue(any("good_intentions" in problem for problem in check(incidents)))

    def test_orphan_mechanism_fails(self):
        incidents = load_incidents(DEFAULT_DATA)
        for lesson in incidents[0]["lessons"]:
            lesson["enforced_by"] = "allowlist"
        problems = check(incidents)
        self.assertTrue(any("honored by no candle" in problem for problem in problems))

    def test_corrupt_data_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "incidents.json"
            path.write_text('{"incidents": []}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_incidents(path)
            path.write_text("not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_incidents(path)
            path.write_text(json.dumps({"incidents": [{"id": "x"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_incidents(path)


class OfrendaRenderTests(unittest.TestCase):
    def test_render_contains_incident_candles_and_mechanisms(self):
        text = render(load_incidents(DEFAULT_DATA))
        for expected in ("O F R E N D A", "taikotalent.xyz", "IN MEMORIAM", "CANDLES",
                         "IDENTIFIED IS NOT AUTHORIZED", "human_approval", "OFFERINGS", "cempasuchil"):
            self.assertIn(expected, text)

    def test_render_is_plain_ascii_within_width(self):
        text = render(load_incidents(DEFAULT_DATA))
        self.assertTrue(all(ord(ch) < 128 for ch in text), "ofrenda must stay plain ASCII")
        self.assertTrue(all(len(line) <= 68 for line in text.splitlines()))


if __name__ == "__main__":
    unittest.main()
